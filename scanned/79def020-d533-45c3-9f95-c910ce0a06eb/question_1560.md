# Q1560: migrate_to_expiring_token — session keyed by claim via non-embedded / private config

## Question
Is there a reachable state in which an unprivileged attacker, controlling an app configuration that flips the `Context.private?` and `Context.embedded?` guards at `migrate_to_expiring_token(shop:, non_expiring_offline_token:)`, makes `TokenExchange.migrate_to_expiring_token` return a result the caller treats as authenticated, given that `Session.from(shop: dest_shop, ...)` mints the storage key from the same unvalidated claim? Test CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted and quantify Critical - exfiltration of the app's `client_secret` and/or the OAuth authorization `code`.

## Target
- File/function: `lib/shopify_api/auth/token_exchange.rb` -> `TokenExchange.migrate_to_expiring_token`
- Entrypoint: `migrate_to_expiring_token(shop:, non_expiring_offline_token:)`
- Attacker controls: an app configuration that flips the `Context.private?` and `Context.embedded?` guards
- Exploit idea: `Session.from(shop: dest_shop, ...)` mints the storage key from the same unvalidated claim
- Invariant to test: CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted
- Expected Immunefi impact: Critical - exfiltration of the app's `client_secret` and/or the OAuth authorization `code` (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest + WebMock: mint a token whose `dest` is a non-Shopify host, call `exchange_token`, and assert no request carrying `client_secret` left for that host
