# Q274: callback_address — re-register decision from response via path with scheme

## Question
Starting from `callback_address`, which returns `@path` as-is when it matches `%r{^https?://}`, prefixes the scheme when it matches `Context.host_name`, and otherwise appends to `Context.host`, can an unprivileged attacker supply a registration `path` already carrying `http://` or `https://`, returned verbatim as the callback address so that whether the callback address is overwritten is decided by comparing against attacker-influenceable response content? Determine whether SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source still holds through `Registrations::Http#callback_address`, and whether the result reaches Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/webhooks/registrations/http.rb` -> `Registrations::Http#callback_address`
- Entrypoint: `callback_address`, which returns `@path` as-is when it matches `%r{^https?://}`, prefixes the scheme when it matches `Context.host_name`, and otherwise appends to `Context.host`
- Attacker controls: a registration `path` already carrying `http://` or `https://`, returned verbatim as the callback address
- Exploit idea: whether the callback address is overwritten is decided by comparing against attacker-influenceable response content
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `callback_address` never returns a host outside the app's own origin
