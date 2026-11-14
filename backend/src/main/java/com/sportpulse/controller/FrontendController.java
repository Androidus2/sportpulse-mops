package com.sportpulse.controller;

import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.GetMapping;

@Controller
public class FrontendController {

	// Keep these paths aligned with Angular's app.routes.ts. API and asset paths
	// must retain their own responses, including 404 for missing resources.
	@GetMapping({ "/", "/standings", "/favorites", "/login", "/matches/{id}", "/matches/{sport}/{id}" })
	public String index() {
		return "forward:/index.html";
	}
}
