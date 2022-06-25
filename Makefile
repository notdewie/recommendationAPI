dev-up:
	docker-compose -f docker-compose.yml up -d --remove-orphans
down:
	docker-compose -f docker-compose.yml down
build:
	docker-compose -f docker-compose.yml build