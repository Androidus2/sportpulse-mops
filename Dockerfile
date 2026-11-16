FROM node:24-bookworm-slim AS frontend-build
WORKDIR /app/frontend
ENV NG_CLI_ANALYTICS=false

COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build -- --configuration production --output-path=dist/frontend

FROM eclipse-temurin:21-jdk AS backend-build
WORKDIR /app/backend

COPY backend/ ./
COPY --from=frontend-build /app/frontend/dist/frontend/browser/ ./src/main/resources/static/
RUN sed -i 's/\r$//' mvnw && sh ./mvnw -B -ntp -DskipTests package

FROM eclipse-temurin:21-jre
WORKDIR /app
ENV JAVA_TOOL_OPTIONS="-XX:MaxRAMPercentage=60.0 -XX:+ExitOnOutOfMemoryError"

COPY --from=backend-build /app/backend/target/*.jar ./app.jar
USER 10001:10001
EXPOSE 8080
ENTRYPOINT ["java", "-jar", "/app/app.jar"]
