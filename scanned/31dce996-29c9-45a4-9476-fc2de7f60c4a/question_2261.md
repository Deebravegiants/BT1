# Q2261: setup — host header decoupled from connection via expiring_offline_access_tokens

## Question
Can an unprivileged attacker reach `Context.setup` through `ShopifyAPI::Context.setup(...)`, which stores every security-relevant global including `api_secret_key`, `old_api_secret_key`, `host`, `api_host` and `scope` while supplying the `expiring_offline_access_tokens` flag, which changes token lifetime and the `expiring` body field, so that with `api_host` set, `Host` is `session.shop` while the socket goes elsewhere, breaking the requirement that SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key`, and ending in Critical - cross-user access inside one shop: one staff user's online session is served to another?

## Target
- File/function: `lib/shopify_api/context.rb` -> `Context.setup`
- Entrypoint: `ShopifyAPI::Context.setup(...)`, which stores every security-relevant global including `api_secret_key`, `old_api_secret_key`, `host`, `api_host` and `scope`
- Attacker controls: the `expiring_offline_access_tokens` flag, which changes token lifetime and the `expiring` body field
- Exploit idea: with `api_host` set, `Host` is `session.shop` while the socket goes elsewhere
- Invariant to test: SESSION DERIVATION: a session id is derived only from bytes authenticated under `Context.api_secret_key`
- Expected Immunefi impact: Critical - cross-user access inside one shop: one staff user's online session is served to another (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: assert a crafted `api_version` cannot make `load_rest_resources` touch a path outside `lib/shopify_api/rest/resources`
