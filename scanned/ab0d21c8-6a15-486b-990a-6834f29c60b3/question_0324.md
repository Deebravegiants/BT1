# Q324: subscription_args — GraphQL by interpolation via filter/fields strings

## Question
Does `Registrations::Http#subscription_args` collapse two distinct identities into one when an unprivileged attacker submits `filter`, `includeFields` and `metafieldNamespaces` values interpolated into the mutation at `subscription_args`, which forwards `callbackUrl`, `includeFields`, `metafieldNamespaces` and `filter`? Show that topic and argument strings are concatenated into the document rather than passed as variables, that CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted is violated, and that the consequence is Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/webhooks/registrations/http.rb` -> `Registrations::Http#subscription_args`
- Entrypoint: `subscription_args`, which forwards `callbackUrl`, `includeFields`, `metafieldNamespaces` and `filter`
- Attacker controls: `filter`, `includeFields` and `metafieldNamespaces` values interpolated into the mutation
- Exploit idea: topic and argument strings are concatenated into the document rather than passed as variables
- Invariant to test: CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: set `Context.host_name` and assert `callback_address` rejects a path whose prefix merely matches it
