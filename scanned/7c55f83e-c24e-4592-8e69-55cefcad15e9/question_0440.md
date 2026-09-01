# Q440: migrate_to_expiring_token — client_secret sent to a derived host via error-path body

## Question
Is there a reachable state in which an unprivileged attacker, controlling a 400 response whose `error` field steers the `invalid_subject_token` branch at `migrate_to_expiring_token(shop:, non_expiring_offline_token:)`, makes `TokenExchange.migrate_to_expiring_token` return a result the caller treats as authenticated, given that the POST body carries `client_id` and `client_secret` to `https://#{dest_shop}/admin/oauth/access_token`? Test CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted and quantify Critical - exfiltration of the app's `client_secret` and/or the OAuth authorization `code`.

## Target
- File/function: `lib/shopify_api/auth/token_exchange.rb` -> `TokenExchange.migrate_to_expiring_token`
- Entrypoint: `migrate_to_expiring_token(shop:, non_expiring_offline_token:)`
- Attacker controls: a 400 response whose `error` field steers the `invalid_subject_token` branch
- Exploit idea: the POST body carries `client_id` and `client_secret` to `https://#{dest_shop}/admin/oauth/access_token`
- Invariant to test: CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted
- Expected Immunefi impact: Critical - exfiltration of the app's `client_secret` and/or the OAuth authorization `code` (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: pass a validated `shop:` that differs from `dest` and assert the code raises rather than silently preferring `dest`
