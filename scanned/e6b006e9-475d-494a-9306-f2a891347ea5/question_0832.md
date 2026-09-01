# Q832: myshopify_domain_from_unified_admin — path segment trusted as identity via dotless name

## Question
Is there a reachable state in which an unprivileged attacker, controlling a dotless shop name that takes the `name += ".#{myshopify_domain}"` branch only when `myshopify_domain` is present, yielding a different verdict for the same input at `myshopify_domain_from_unified_admin`, which returns `"#{uri.path.split('/').last}.myshopify.com"` from an unvalidated path segment, makes `ShopValidator.myshopify_domain_from_unified_admin` return a result the caller treats as authenticated, given that the unified-admin branch trusts `uri.path` even though only the host was matched against `TRUSTED_SHOPIFY_DOMAINS`? Test CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted and quantify High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host.

## Target
- File/function: `lib/shopify_api/utils/shop_validator.rb` -> `ShopValidator.myshopify_domain_from_unified_admin`
- Entrypoint: `myshopify_domain_from_unified_admin`, which returns `"#{uri.path.split('/').last}.myshopify.com"` from an unvalidated path segment
- Attacker controls: a dotless shop name that takes the `name += ".#{myshopify_domain}"` branch only when `myshopify_domain` is present, yielding a different verdict for the same input
- Exploit idea: the unified-admin branch trusts `uri.path` even though only the host was matched against `TRUSTED_SHOPIFY_DOMAINS`
- Invariant to test: CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted
- Expected Immunefi impact: High - SSRF: an authenticated request carrying the app's credentials is driven to an unintended host (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest + WebMock: stub_request on the attacker host, call the flow, and `assert_not_requested` any host outside `TRUSTED_SHOPIFY_DOMAINS`
