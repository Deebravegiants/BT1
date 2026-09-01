# Q399: subscription_args — scheme-carrying path trusted via response-controlled callbackUrl

## Question
Can an unprivileged attacker reach `Registrations::Http#subscription_args` through `subscription_args`, which forwards `callbackUrl`, `includeFields`, `metafieldNamespaces` and `filter` while supplying the `callbackUrl` returned by the check query, compared against the desired address to decide whether to re-register, so that a path that already looks like a URL is used verbatim as the delivery destination for the merchant's webhook data, breaking the requirement that CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted, and ending in High - credential or token leakage into log output or error messages?

## Target
- File/function: `lib/shopify_api/webhooks/registrations/http.rb` -> `Registrations::Http#subscription_args`
- Entrypoint: `subscription_args`, which forwards `callbackUrl`, `includeFields`, `metafieldNamespaces` and `filter`
- Attacker controls: the `callbackUrl` returned by the check query, compared against the desired address to decide whether to re-register
- Exploit idea: a path that already looks like a URL is used verbatim as the delivery destination for the merchant's webhook data
- Invariant to test: CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted
- Expected Immunefi impact: High - credential or token leakage into log output or error messages (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: set `Context.host_name` and assert `callback_address` rejects a path whose prefix merely matches it
