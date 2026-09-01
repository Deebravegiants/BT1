# Q3145: shop — rotation widens acceptance via sub variants

## Question
Does `JwtPayload#shop` collapse two distinct identities into one when an unprivileged attacker submits a `sub` claim that is absent, non-numeric, negative, zero-padded, or huge, changing `user_id_sub?` and the `#{shop}_#{sub}` key at `JwtPayload#shop`, computed as `@dest.gsub("https://", "")`? Show that the rescue-and-retry under `old_api_secret_key` doubles the set of tokens accepted, with no expiry, that SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key` is violated, and that the consequence is Critical - cross-tenant access: one shop's request reads or mutates another merchant's data.

## Target
- File/function: `lib/shopify_api/auth/jwt_payload.rb` -> `JwtPayload#shop`
- Entrypoint: `JwtPayload#shop`, computed as `@dest.gsub("https://", "")`
- Attacker controls: a `sub` claim that is absent, non-numeric, negative, zero-padded, or huge, changing `user_id_sub?` and the `#{shop}_#{sub}` key
- Exploit idea: the rescue-and-retry under `old_api_secret_key` doubles the set of tokens accepted, with no expiry
- Invariant to test: SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key`
- Expected Immunefi impact: Critical - cross-tenant access: one shop's request reads or mutates another merchant's data (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert `JwtPayload.new` raises for a `dest` outside `TRUSTED_SHOPIFY_DOMAINS`; if it does not, assert the resulting `HttpClient` base URI under WebMock
