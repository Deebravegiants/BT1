# Q81: initialize — no single-use via unicode normalisation

## Question
Can a value that normalises differently between the browser, the framework and `URI.encode_www_form`, supplied by an unprivileged attacker at `AuthQuery.new(code:, shop:, timestamp:, state:, host:, hmac:)`, built by the host app directly from the callback query string, make `AuthQuery#initialize` and the code consuming its result disagree, given that nothing marks a signed callback as consumed? The binding to test is SIGNATURE COVERAGE: every value acted on downstream is inside the string handed to `HmacValidator` via `to_signable_string`; the impact to prove is Critical - exfiltration of the app's `client_secret` and/or the OAuth authorization `code`.

## Target
- File/function: `lib/shopify_api/auth/oauth/auth_query.rb` -> `AuthQuery#initialize`
- Entrypoint: `AuthQuery.new(code:, shop:, timestamp:, state:, host:, hmac:)`, built by the host app directly from the callback query string
- Attacker controls: a value that normalises differently between the browser, the framework and `URI.encode_www_form`
- Exploit idea: nothing marks a signed callback as consumed
- Invariant to test: SIGNATURE COVERAGE: every value acted on downstream is inside the string handed to `HmacValidator` via `to_signable_string`
- Expected Immunefi impact: Critical - exfiltration of the app's `client_secret` and/or the OAuth authorization `code` (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: build the query two ways, assert `HmacValidator.validate` accepts both, and diff the two `to_signable_string` outputs
