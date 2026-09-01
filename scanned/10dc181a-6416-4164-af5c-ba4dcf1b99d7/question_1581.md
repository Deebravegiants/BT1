# Q1581: build_check_query — scheme-carrying path trusted via filter/fields strings

## Question
Is there a reachable state in which an unprivileged attacker, controlling `filter`, `includeFields` and `metafieldNamespaces` values interpolated into the mutation at `build_check_query`, which interpolates `@topic` into a GraphQL document, makes `Registrations::Http#build_check_query` return a result the caller treats as authenticated, given that a path that already looks like a URL is used verbatim as the delivery destination for the merchant's webhook data? Test CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted and quantify High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host.

## Target
- File/function: `lib/shopify_api/webhooks/registrations/http.rb` -> `Registrations::Http#build_check_query`
- Entrypoint: `build_check_query`, which interpolates `@topic` into a GraphQL document
- Attacker controls: `filter`, `includeFields` and `metafieldNamespaces` values interpolated into the mutation
- Exploit idea: a path that already looks like a URL is used verbatim as the delivery destination for the merchant's webhook data
- Invariant to test: CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted
- Expected Immunefi impact: High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: set `Context.host_name` and assert `callback_address` rejects a path whose prefix merely matches it
