# Q423: build_check_query — regex injection via response-controlled callbackUrl

## Question
If an unprivileged attacker submits the `callbackUrl` returned by the check query, compared against the desired address to decide whether to re-register to `build_check_query`, which interpolates `@topic` into a GraphQL document, does `Registrations::Http#build_check_query` end up acting on a value that was never authenticated, because an unescaped interpolation into a `Regexp` changes what the match accepts? Close the question on CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted and on High - credential or token leakage into log output or error messages.

## Target
- File/function: `lib/shopify_api/webhooks/registrations/http.rb` -> `Registrations::Http#build_check_query`
- Entrypoint: `build_check_query`, which interpolates `@topic` into a GraphQL document
- Attacker controls: the `callbackUrl` returned by the check query, compared against the desired address to decide whether to re-register
- Exploit idea: an unescaped interpolation into a `Regexp` changes what the match accepts
- Invariant to test: CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted
- Expected Immunefi impact: High - credential or token leakage into log output or error messages (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: set `Context.host_name` and assert `callback_address` rejects a path whose prefix merely matches it
