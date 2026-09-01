# Q171: callback_address — GraphQL by interpolation via path with scheme

## Question
If an unprivileged attacker submits a registration `path` already carrying `http://` or `https://`, returned verbatim as the callback address to `callback_address`, which returns `@path` as-is when it matches `%r{^https?://}`, prefixes the scheme when it matches `Context.host_name`, and otherwise appends to `Context.host`, does `Registrations::Http#callback_address` end up acting on a value that was never authenticated, because topic and argument strings are concatenated into the document rather than passed as variables? Close the question on CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted and on High - credential or token leakage into log output or error messages.

## Target
- File/function: `lib/shopify_api/webhooks/registrations/http.rb` -> `Registrations::Http#callback_address`
- Entrypoint: `callback_address`, which returns `@path` as-is when it matches `%r{^https?://}`, prefixes the scheme when it matches `Context.host_name`, and otherwise appends to `Context.host`
- Attacker controls: a registration `path` already carrying `http://` or `https://`, returned verbatim as the callback address
- Exploit idea: topic and argument strings are concatenated into the document rather than passed as variables
- Invariant to test: CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted
- Expected Immunefi impact: High - credential or token leakage into log output or error messages (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: set `Context.host_name` and assert `callback_address` rejects a path whose prefix merely matches it
