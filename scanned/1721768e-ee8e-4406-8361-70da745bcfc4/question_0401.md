# Q401: == — parsing is lossy via unauthenticated_ prefix

## Question
Does `Auth::AuthScopes#==` collapse two distinct identities into one when an unprivileged attacker submits an `unauthenticated_write_*` scope, which manufactures `unauthenticated_read_*` at `AuthScopes#==` and `hash`, which compare only `compressed_scopes`? Show that splitting and stripping can merge or drop entries so the parsed set differs from the granted grant, that SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source is violated, and that the consequence is Critical - cross-user access inside one shop: one staff user's online session is served to another.

## Target
- File/function: `lib/shopify_api/auth/auth_scopes.rb` -> `Auth::AuthScopes#==`
- Entrypoint: `AuthScopes#==` and `hash`, which compare only `compressed_scopes`
- Attacker controls: an `unauthenticated_write_*` scope, which manufactures `unauthenticated_read_*`
- Exploit idea: splitting and stripping can merge or drop entries so the parsed set differs from the granted grant
- Invariant to test: SINGLE IDENTITY: exactly one shop identity exists per request, and every component derives it from the same authenticated source
- Expected Immunefi impact: Critical - cross-user access inside one shop: one staff user's online session is served to another (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `==` distinguishes two scope sets whose expanded permissions differ
