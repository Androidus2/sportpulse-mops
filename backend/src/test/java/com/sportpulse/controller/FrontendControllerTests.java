package com.sportpulse.controller;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ValueSource;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.webmvc.test.autoconfigure.WebMvcTest;
import org.springframework.test.web.servlet.MockMvc;

@WebMvcTest({ FrontendController.class, HealthController.class })
class FrontendControllerTests {

	@Autowired
	private MockMvc mvc;

	@ParameterizedTest
	@ValueSource(strings = { "/", "/standings", "/favorites", "/login", "/matches/42",
			"/matches/football/42", "/matches/basketball/42", "/matches/hockey/42" })
	void directFrontendLinksForwardToTheAngularEntryPoint(String path) throws Exception {
		mvc.perform(get(path)).andExpect(status().isOk()).andExpect(forwardedUrl("/index.html"));
	}

	@Test
	void theHealthEndpointStillReturnsJson() throws Exception {
		mvc.perform(get("/api/health")).andExpect(status().isOk()).andExpect(jsonPath("$.status").value("UP"));
	}

	@ParameterizedTest
	@ValueSource(strings = { "/api/missing", "/missing-bundle.js", "/.env" })
	void missingApiAndAssetPathsAreNotForwardedToTheFrontend(String path) throws Exception {
		mvc.perform(get(path)).andExpect(status().isNotFound()).andExpect(forwardedUrl(null));
	}
}
