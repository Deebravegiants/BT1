# Q1140: exchange_token — client_secret sent to a derived host via attacker id token

## Question
Is there a reachable state in which an unprivileged attacker, controlling a session token the attacker legitimately holds for their own shop, since one `api_secret_key` validates tokens for every install at `ShopifyAPI::Auth::TokenExchange.exchange_token(session_token:, requested_token_type:, shop:)`, reached from any embedded route that trades a session token for an access token, makes `TokenExchange.exchange_token` return a result the caller treats as authenticated, given that the POST body carries `client_id` and `client_secret` to `https://#{dest_shop}/admin/oauth/access_token`? Test CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted and quantify Critical - exfiltration of the app's `client_secret` and/or the OAuth authorization `code`.

## Target
- File/function: `lib/shopify_api/auth/token_exchange.rb` -> `TokenExchange.exchange_token`
- Entrypoint: `ShopifyAPI::Auth::TokenExchange.exchange_token(session_token:, requested_token_type:, shop:)`, reached from any embedded route that trades a session token for an access token
- Attacker controls: a session token the attacker legitimately holds for their own shop, since one `api_secret_key` validates tokens for every install
- Exploit idea: the POST body carries `client_id` and `client_secret` to `https://#{dest_shop}/admin/oauth/access_token`
- Invariant to test: CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted
- Expected Immunefi impact: Critical - exfiltration of the app's `client_secret` and/or the OAuth authorization `code` (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest + WebMock: mint a token whose `dest` is a non-Shopify host, call `exchange_token`, and assert no request carrying `client_secret` left for that host
