# Q610: Oauth::SessionCookie — session id published to the browser via expiry

## Question
Starting from `ShopifyAPI::Auth::Oauth::SessionCookie`, the `T::Struct` holding `name`, `value` and `expires` for `shopify_app_session`, can an unprivileged attacker supply the 60-second `expires` set at `begin_auth`, which the callback never re-checks so that in the non-embedded branch the cookie hands the storage key to the client? Determine whether SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host still holds through `Oauth::SessionCookie`, and whether the result reaches Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/auth/oauth/session_cookie.rb` -> `Oauth::SessionCookie`
- Entrypoint: `ShopifyAPI::Auth::Oauth::SessionCookie`, the `T::Struct` holding `name`, `value` and `expires` for `shopify_app_session`
- Attacker controls: the 60-second `expires` set at `begin_auth`, which the callback never re-checks
- Exploit idea: in the non-embedded branch the cookie hands the storage key to the client
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: minitest: assert the callback rejects a cookie whose value is a well-formed session id rather than the nonce it issued
