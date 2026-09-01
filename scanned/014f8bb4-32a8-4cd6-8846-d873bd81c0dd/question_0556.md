# Q556: exchange_token — error branch reveals verdict via dest-controlled host

## Question
If an unprivileged attacker submits the `dest` claim, which becomes `dest_shop` and then `Session.new(shop: dest_shop)` and then the request host, with no `ShopValidator` call to `ShopifyAPI::Auth::TokenExchange.exchange_token(session_token:, requested_token_type:, shop:)`, reached from any embedded route that trades a session token for an access token, does `TokenExchange.exchange_token` end up acting on a value that was never authenticated, because distinguishing `invalid_subject_token` from other 400s creates an oracle over token validity? Close the question on CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted and on Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/auth/token_exchange.rb` -> `TokenExchange.exchange_token`
- Entrypoint: `ShopifyAPI::Auth::TokenExchange.exchange_token(session_token:, requested_token_type:, shop:)`, reached from any embedded route that trades a session token for an access token
- Attacker controls: the `dest` claim, which becomes `dest_shop` and then `Session.new(shop: dest_shop)` and then the request host, with no `ShopValidator` call
- Exploit idea: distinguishing `invalid_subject_token` from other 400s creates an oracle over token validity
- Invariant to test: CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `exchange_token` sanitises `dest_shop` the same way `migrate_to_expiring_token` sanitises its `shop:` argument
