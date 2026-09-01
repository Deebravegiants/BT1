# Q4600: myshopify_domain_from_unified_admin — parse/resolve divergence via dotless name

## Question
Starting from `myshopify_domain_from_unified_admin`, which returns `"#{uri.path.split('/').last}.myshopify.com"` from an unvalidated path segment, can an unprivileged attacker supply a dotless shop name that takes the `name += ".#{myshopify_domain}"` branch only when `myshopify_domain` is present, yielding a different verdict for the same input so that what `Addressable::URI` reports as `host`/`domain` differs from the authority HTTParty finally connects to? Determine whether CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted still holds through `ShopValidator.myshopify_domain_from_unified_admin`, and whether the result reaches Critical - exfiltration of the app's `client_secret` and/or the OAuth authorization `code`.

## Target
- File/function: `lib/shopify_api/utils/shop_validator.rb` -> `ShopValidator.myshopify_domain_from_unified_admin`
- Entrypoint: `myshopify_domain_from_unified_admin`, which returns `"#{uri.path.split('/').last}.myshopify.com"` from an unvalidated path segment
- Attacker controls: a dotless shop name that takes the `name += ".#{myshopify_domain}"` branch only when `myshopify_domain` is present, yielding a different verdict for the same input
- Exploit idea: what `Addressable::URI` reports as `host`/`domain` differs from the authority HTTParty finally connects to
- Invariant to test: CREDENTIAL DESTINATION: `client_secret`, the authorization `code` and `X-Shopify-Access-Token` leave only for a host `ShopValidator` accepted
- Expected Immunefi impact: Critical - exfiltration of the app's `client_secret` and/or the OAuth authorization `code` (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest + WebMock: stub_request on the attacker host, call the flow, and `assert_not_requested` any host outside `TRUSTED_SHOPIFY_DOMAINS`
