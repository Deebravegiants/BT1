# Q118: process — tenant identity handed over unverified via unsigned topic header

## Question
Is there a reachable state in which an unprivileged attacker, controlling the topic, taken from an unsigned header, used both to select the handler and to build GraphQL documents at `ShopifyAPI::Webhooks::Registry.process(request)`, the entry point of every app's public webhook route, makes `Webhooks::Registry.process` return a result the caller treats as authenticated, given that `WebhookMetadata#shop` is the raw header value the host app uses to choose whose records to touch? Test SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source and quantify Critical - cross-user access inside one shop: one staff user's online session is served to another.

## Target
- File/function: `lib/shopify_api/webhooks/registry.rb` -> `Webhooks::Registry.process`
- Entrypoint: `ShopifyAPI::Webhooks::Registry.process(request)`, the entry point of every app's public webhook route
- Attacker controls: the topic, taken from an unsigned header, used both to select the handler and to build GraphQL documents
- Exploit idea: `WebhookMetadata#shop` is the raw header value the host app uses to choose whose records to touch
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - cross-user access inside one shop: one staff user's online session is served to another (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert a topic containing GraphQL metacharacters cannot alter the document sent by `get_webhook_id`
