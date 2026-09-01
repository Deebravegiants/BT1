# Q897: to_signable_string — no freshness via array-style parameters

## Question
Starting from `AuthQuery#to_signable_string`, the only bytes `HmacValidator` ever sees for an OAuth callback, can an unprivileged attacker supply `shop[]=` / `state[]=` style keys that a Rack parse turns into arrays before they reach `AuthQuery.new` so that nothing bounds the age of a signed callback, so a captured one stays valid indefinitely? Determine whether SIGNATURE COVERAGE: every value acted on downstream is inside the string handed to `HmacValidator` via `to_signable_string` still holds through `AuthQuery#to_signable_string`, and whether the result reaches Critical - exfiltration of the app's `client_secret` and/or the OAuth authorization `code`.

## Target
- File/function: `lib/shopify_api/auth/oauth/auth_query.rb` -> `AuthQuery#to_signable_string`
- Entrypoint: `AuthQuery#to_signable_string`, the only bytes `HmacValidator` ever sees for an OAuth callback
- Attacker controls: `shop[]=` / `state[]=` style keys that a Rack parse turns into arrays before they reach `AuthQuery.new`
- Exploit idea: nothing bounds the age of a signed callback, so a captured one stays valid indefinitely
- Invariant to test: SIGNATURE COVERAGE: every value acted on downstream is inside the string handed to `HmacValidator` via `to_signable_string`
- Expected Immunefi impact: Critical - exfiltration of the app's `client_secret` and/or the OAuth authorization `code` (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: build the query two ways, assert `HmacValidator.validate` accepts both, and diff the two `to_signable_string` outputs
