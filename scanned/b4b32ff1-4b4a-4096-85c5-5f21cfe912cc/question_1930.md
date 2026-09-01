# Q1930: callback_address — scheme-carrying path trusted via regex metacharacters in host

## Question
Trace `Registrations::Http#callback_address` from `callback_address`, which returns `@path` as-is when it matches `%r{^https?://}`, prefixes the scheme when it matches `Context.host_name`, and otherwise appends to `Context.host` with a `Context.host_name` containing regex metacharacters, since it is interpolated into a pattern unescaped: because a path that already looks like a URL is used verbatim as the delivery destination for the merchant's webhook data, does the value that was verified stop being the value that is used? Prove the break against SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source and map it to Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/webhooks/registrations/http.rb` -> `Registrations::Http#callback_address`
- Entrypoint: `callback_address`, which returns `@path` as-is when it matches `%r{^https?://}`, prefixes the scheme when it matches `Context.host_name`, and otherwise appends to `Context.host`
- Attacker controls: a `Context.host_name` containing regex metacharacters, since it is interpolated into a pattern unescaped
- Exploit idea: a path that already looks like a URL is used verbatim as the delivery destination for the merchant's webhook data
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `callback_address` never returns a host outside the app's own origin
