# Q1741: subscription_args — regex injection via topic string

## Question
Trace `Registrations::Http#subscription_args` from `subscription_args`, which forwards `callbackUrl`, `includeFields`, `metafieldNamespaces` and `filter` with the `@topic` value interpolated into `build_check_query` unquoted: because an unescaped interpolation into a `Regexp` changes what the match accepts, does the value that was verified stop being the value that is used? Prove the break against SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source and map it to High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host.

## Target
- File/function: `lib/shopify_api/webhooks/registrations/http.rb` -> `Registrations::Http#subscription_args`
- Entrypoint: `subscription_args`, which forwards `callbackUrl`, `includeFields`, `metafieldNamespaces` and `filter`
- Attacker controls: the `@topic` value interpolated into `build_check_query` unquoted
- Exploit idea: an unescaped interpolation into a `Regexp` changes what the match accepts
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `callback_address` never returns a host outside the app's own origin
