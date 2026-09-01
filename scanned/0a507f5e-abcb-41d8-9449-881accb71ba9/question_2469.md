# Q2469: setup — thread-local, not request-local via rest_disabled

## Question
Trace `Context.setup` from `ShopifyAPI::Context.setup(...)`, which stores every security-relevant global including `api_secret_key`, `old_api_secret_key`, `host`, `api_host` and `scope` with the `rest_disabled` flag, which decides whether the REST client raises: because `active_session` is thread-local; on a pooled server a session can outlive the request that set it, does the value that was verified stop being the value that is used? Prove the break against SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key` and map it to Critical - cross-user access inside one shop: one staff user's online session is served to another.

## Target
- File/function: `lib/shopify_api/context.rb` -> `Context.setup`
- Entrypoint: `ShopifyAPI::Context.setup(...)`, which stores every security-relevant global including `api_secret_key`, `old_api_secret_key`, `host`, `api_host` and `scope`
- Attacker controls: the `rest_disabled` flag, which decides whether the REST client raises
- Exploit idea: `active_session` is thread-local; on a pooled server a session can outlive the request that set it
- Invariant to test: SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key`
- Expected Immunefi impact: Critical - cross-user access inside one shop: one staff user's online session is served to another (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: run two threads through `Session.temp` and assert neither observes the other's active session
