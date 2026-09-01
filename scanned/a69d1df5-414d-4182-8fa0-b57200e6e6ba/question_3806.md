# Q3806: process — GraphQL built by interpolation via unsigned topic header

## Question
Trace `Webhooks::Registry.process` from `ShopifyAPI::Webhooks::Registry.process(request)`, the entry point of every app's public webhook route with the topic, taken from an unsigned header, used both to select the handler and to build GraphQL documents: because topic and `webhook_id` are concatenated into query documents rather than passed as variables, does the value that was verified stop being the value that is used? Prove the break against SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source and map it to Critical - cross-user access inside one shop: one staff user's online session is served to another.

## Target
- File/function: `lib/shopify_api/webhooks/registry.rb` -> `Webhooks::Registry.process`
- Entrypoint: `ShopifyAPI::Webhooks::Registry.process(request)`, the entry point of every app's public webhook route
- Attacker controls: the topic, taken from an unsigned header, used both to select the handler and to build GraphQL documents
- Exploit idea: topic and `webhook_id` are concatenated into query documents rather than passed as variables
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - cross-user access inside one shop: one staff user's online session is served to another (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert a topic containing GraphQL metacharacters cannot alter the document sent by `get_webhook_id`
