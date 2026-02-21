# Makefile for Power Theft Detection System
# ============================================
# Provides convenient shortcuts for common development and deployment tasks

.PHONY: help install test run run-prod dev clean docker docker-run docker-push lint format

PYTHON := python
PIP := pip
VENV_DIR := venv
DOCKER_IMAGE := power-theft-detector
DOCKER_REGISTRY := 

# Colors for output
RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[1;33m
NC := \033[0m # No Color

help: ## Show this help message
	@echo "$(GREEN)Power Theft Detection System - Makefile Commands$(NC)"
	@echo ""
	@echo "$(YELLOW)Setup & Installation:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(YELLOW)Examples:$(NC)"
	@echo "  make install        # Create venv and install dependencies"
	@echo "  make test           # Run all tests"
	@echo "  make run            # Start API server (development)"
	@echo "  make docker-run     # Run in Docker container"
	@echo ""

install: ## Create virtual environment and install dependencies
	@if [ ! -d "$(VENV_DIR)" ]; then \
		echo "$(YELLOW)Creating virtual environment...$(NC)"; \
		$(PYTHON) -m venv $(VENV_DIR); \
	fi
	@echo "$(YELLOW)Upgrading pip...$(NC)"
	@. $(VENV_DIR)/bin/activate && $(PIP) install --upgrade pip setuptools wheel
	@echo "$(YELLOW)Installing dependencies...$(NC)"
	@. $(VENV_DIR)/bin/activate && $(PIP) install -r requirements.txt
	@echo "$(GREEN)Installation complete!$(NC)"

test: ## Run tests
	@echo "$(YELLOW)Running tests...$(NC)"
	@. $(VENV_DIR)/bin/activate && $(PYTHON) test_deployment.py

lint: ## Run code quality checks
	@echo "$(YELLOW)Running linting...$(NC)"
	@. $(VENV_DIR)/bin/activate && pylint power_theft_detector.py app.py config.py || true

format: ## Format code with black
	@echo "$(YELLOW)Formatting code...$(NC)"
	@. $(VENV_DIR)/bin/activate && black power_theft_detector.py app.py config.py || true

run: ## Start API server (development mode)
	@echo "$(YELLOW)Starting API server on http://localhost:5000$(NC)"
	@. $(VENV_DIR)/bin/activate && $(PYTHON) app.py

run-prod: ## Start API server (production mode with Gunicorn)
	@echo "$(YELLOW)Starting API server in production mode...$(NC)"
	@. $(VENV_DIR)/bin/activate && gunicorn -w 4 -b 0.0.0.0:5000 app:app

dev: install lint test ## Full development setup (install, lint, test)
	@echo "$(GREEN)Development environment ready!$(NC)"

clean: ## Remove virtual environment and cache files
	@echo "$(YELLOW)Cleaning up...$(NC)"
	@rm -rf $(VENV_DIR)
	@find . -type d -name __pycache__ -exec rm -rf {} + || true
	@find . -type f -name "*.pyc" -delete || true
	@find . -type f -name ".pytest_cache" -delete || true
	@rm -f power_theft.log
	@echo "$(GREEN)Cleanup complete!$(NC)"

docker-build: ## Build Docker image
	@echo "$(YELLOW)Building Docker image: $(DOCKER_IMAGE)$(NC)"
	@docker build -t $(DOCKER_IMAGE):latest .
	@echo "$(GREEN)Docker image built successfully!$(NC)"

docker-run: docker-build ## Run Docker container locally
	@echo "$(YELLOW)Starting Docker container on http://localhost:5000$(NC)"
	@docker run -p 5000:5000 --rm --name power-theft-detector $(DOCKER_IMAGE):latest

docker-stop: ## Stop running Docker container
	@echo "$(YELLOW)Stopping Docker container...$(NC)"
	@docker stop power-theft-detector || true
	@echo "$(GREEN)Container stopped!$(NC)"

docker-push: docker-build ## Push Docker image to registry (requires DOCKER_REGISTRY set)
	@if [ -z "$(DOCKER_REGISTRY)" ]; then \
		echo "$(RED)Error: DOCKER_REGISTRY not set. Usage: make docker-push DOCKER_REGISTRY=<registry>$(NC)"; \
		exit 1; \
	fi
	@echo "$(YELLOW)Tagging image for registry...$(NC)"
	@docker tag $(DOCKER_IMAGE):latest $(DOCKER_REGISTRY)/$(DOCKER_IMAGE):latest
	@echo "$(YELLOW)Pushing to registry...$(NC)"
	@docker push $(DOCKER_REGISTRY)/$(DOCKER_IMAGE):latest
	@echo "$(GREEN)Push complete!$(NC)"

compose-up: ## Start full stack with Docker Compose
	@echo "$(YELLOW)Starting full stack...$(NC)"
	@docker-compose up -d
	@echo "$(GREEN)Stack started!$(NC)"
	@echo "API: http://localhost:5000"
	@echo "Prometheus: http://localhost:9090"
	@echo "Kibana: http://localhost:5601"

compose-down: ## Stop Docker Compose stack
	@echo "$(YELLOW)Stopping stack...$(NC)"
	@docker-compose down
	@echo "$(GREEN)Stack stopped!$(NC)"

compose-logs: ## View Docker Compose logs
	@docker-compose logs -f

check-health: ## Check API health endpoint
	@echo "$(YELLOW)Checking API health...$(NC)"
	@curl -s http://localhost:5000/health | $(PYTHON) -m json.tool || echo "$(RED)API not responding$(NC)"

check-models: ## Verify model artifacts exist
	@echo "$(YELLOW)Checking model artifacts...$(NC)"
	@if [ -d "models_artifacts" ]; then \
		echo "$(GREEN)✓ models_artifacts directory exists$(NC)"; \
		ls -lh models_artifacts/; \
	else \
		echo "$(RED)✗ models_artifacts directory not found$(NC)"; \
		exit 1; \
	fi

verify-deps: ## Verify all dependencies are installed
	@echo "$(YELLOW)Verifying dependencies...$(NC)"
	@. $(VENV_DIR)/bin/activate && $(PYTHON) -c "import sklearn, pandas, numpy, flask, joblib; print('$(GREEN)All dependencies OK$(NC)')" || echo "$(RED)Missing dependencies$(NC)"

backup: ## Create backup of current state
	@echo "$(YELLOW)Creating backup...$(NC)"
	@tar -czf backup_$(shell date +%Y%m%d_%H%M%S).tar.gz \
		--exclude=venv --exclude=__pycache__ --exclude=.git --exclude=*.pyc .; \
	@echo "$(GREEN)Backup created!$(NC)"

docs: ## Generate documentation
	@echo "$(YELLOW)Documentation available:$(NC)"
	@echo "  - README.md - Project overview"
	@echo "  - DEPLOYMENT_GUIDE.md - Deployment procedures"
	@echo "  - QUICKSTART.md - Quick start guide"
	@echo "  - Jupyter notebooks - Data analysis and training"

.DEFAULT_GOAL := help
