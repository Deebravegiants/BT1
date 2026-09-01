# Q200: client_credentials — sanitised value is the only guard via validator bypass string

## Question
Can a shop string that survives `sanitize!` but resolves elsewhere (trailing dot, port, unified-admin path, dev domain), supplied by an unprivileged attacker at `ShopifyAPI::Auth::ClientCredentials.client_credentials(shop:)`, reached from any host-app route that mints a token for a shop named in the request, make `Auth::ClientCredentials.client_credentials` and the code consuming its result disagree, given that everything downstream trusts `sanitize!`, so any bypass in it becomes credential exfiltration here? The binding to test is SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key`; the impact to prove is Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/auth/client_credentials.rb` -> `Auth::ClientCredentials.client_credentials`
- Entrypoint: `ShopifyAPI::Auth::ClientCredentials.client_credentials(shop:)`, reached from any host-app route that mints a token for a shop named in the request
- Attacker controls: a shop string that survives `sanitize!` but resolves elsewhere (trailing dot, port, unified-admin path, dev domain)
- Exploit idea: everything downstream trusts `sanitize!`, so any bypass in it becomes credential exfiltration here
- Invariant to test: SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key`
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest + WebMock: call with a validator-bypass shop string and assert no request containing `client_secret` left for a non-Shopify host
