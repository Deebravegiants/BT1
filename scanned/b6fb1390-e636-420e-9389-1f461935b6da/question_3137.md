# Q3137: initialize — prefix re-rooting via tries argument

## Question
Starting from `Rest::Admin.new(session:, api_version:)`, including the `Context.rest_disabled` guard and the version-override branch, can an unprivileged attacker supply a `tries:` value that lengthens the retry loop around an authenticated request so that the `admin/` branch discards the versioned base path, so a caller-influenced path reaches a different API surface with the same token? Determine whether AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right still holds through `Clients::Rest::Admin#initialize`, and whether the result reaches High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host.

## Target
- File/function: `lib/shopify_api/clients/rest/admin.rb` -> `Clients::Rest::Admin#initialize`
- Entrypoint: `Rest::Admin.new(session:, api_version:)`, including the `Context.rest_disabled` guard and the version-override branch
- Attacker controls: a `tries:` value that lengthens the retry loop around an authenticated request
- Exploit idea: the `admin/` branch discards the versioned base path, so a caller-influenced path reaches a different API surface with the same token
- Invariant to test: AUTHORIZATION TRUTH: `covers?`, `expired?`, the `state` comparison and the proxy gate never answer permissively for a session lacking the right
- Expected Immunefi impact: High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert a user-supplied resource id containing `/`, `?` or `#` cannot change the recorded request path beyond one segment
