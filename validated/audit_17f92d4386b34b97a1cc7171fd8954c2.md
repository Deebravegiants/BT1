### Title
Unsigned, attacker-controllable `shopify_app_session` cookie is used as a raw, unverified session storage key, enabling cross-tenant session/token theft - ([File: lib/shopify_api/utils/session_utils.rb])

### Summary
`SessionUtils.cookie_session_id` performs a pure passthrough of the `shopify_app_session` cookie value with zero cryptographic verification, and that same value is the literal, deterministic session id (`"offline_#{shop}"` or `"#{shop}_#{user_id}"`) that the host app's storage uses to look up a persisted `Session`/access token. Since the cookie is never re-derived from or checked against anything authenticated under `Context.api_secret_key`, any attacker who can send a raw HTTP request with a crafted `Cookie` header can impersonate another tenant's session id and cause the host's storage to hand back that tenant's access token.

### Finding Description
Binding claimed (SESSION_DERIVATION): `session_id_used_for_storage_lookup == f(bytes authenticated by Context.api_secret_key)`.

Actual code: [1](#0-0) 
`cookie_session_id` returns `cookies[SESSION_COOKIE_NAME]` verbatim - no HMAC, no JWT signature check, no comparison against any secret-derived value.

This is reached from `current_session_id`, both for non-embedded apps and as the embedded fallback path when no `shopify_id_token` is present: [2](#0-1) 

Critically, the session id format is fully deterministic and public knowledge: [3](#0-2) 
- Offline: `"offline_#{shop}"` - trivially derivable from any known `shop.myshopify.com` domain.
- Online: `"#{shop}_#{user_id}"` - derivable if the numeric Shopify user id is known/guessed.

The cookie is set to exactly this value by the gem itself after OAuth completes, and the documented Rails usage stores it as a **plain, non-signed, non-encrypted** cookie (`cookies[:name] = { value:, secure:, http_only: }`, not `cookies.signed`/`cookies.encrypted`): [4](#0-3) 

The one place a cryptographic/secret-bound check ever touches this cookie is during the *initial* OAuth callback, where the cookie value is compared to `auth_query.state` as CSRF protection for the authorization-code exchange: [5](#0-4) 
That check only guards the one-time code exchange. It does **not** apply to subsequent requests where `current_session_id`/`cookie_session_id` is called to resolve "who is calling now" for ordinary authenticated API requests - at that point the cookie is treated as a trusted, self-authenticating session pointer with no re-validation.

Attacker flow:
1. Attacker learns/guesses a victim shop's domain (public knowledge, e.g. `victim-shop.myshopify.com`).
2. Attacker sends a request to the host app's route that resolves sessions via `ShopifyAPI::Utils::SessionUtils.current_session_id`, with header `Cookie: shopify_app_session=offline_victim-shop.myshopify.com`.
3. `cookie_session_id` returns that string unchanged; `current_session_id` returns it as the session id.
4. The host app's session storage (as documented, e.g. keyed lookup by `session.id`) retrieves the victim's persisted `Session`, including `access_token`.
5. The app now performs Admin API calls on the attacker's behalf using the victim's access token - full cross-tenant access.

No existing guard intercepts this: `HmacValidator.validate` and the `state` comparison only apply during the OAuth callback, not to later cookie-based session resolution; `JwtPayload`'s `aud`/signature checks only apply to the `shopify_id_token` branch, which is bypassed entirely when the attacker supplies a cookie instead of a token; `Context.setup?`/`private?`/`embedded?` gate configuration, not cookie authenticity; Sorbet only enforces the value's *type* (`String`), not its provenance.

### Impact Explanation
A successful request yields the persisted access token (and refresh token, if expiring tokens are enabled) of an arbitrary victim merchant, which the attacker's session can then use for authenticated Admin API calls - this is direct cross-tenant access and access-token theft, matching the Critical category in the rubric. It is repeatable against any shop domain the attacker can name (for offline sessions, this is just the shop's own domain - always known/public), with no rate limit or additional secret required per attempt.

### Likelihood Explanation
- Requires: a host app built as documented (non-signed/non-encrypted cookie storing the plain session id; non-embedded app, or embedded app's cookie-fallback path), and a route where the app resolves `current_session_id` from cookies without an additional authorization check tying the resolved session back to the request's own authenticated context.
- Attacker cost: none beyond knowing/guessing the target shop domain; no credentials, no TLS interception, no XSS needed since the attacker crafts the HTTP request directly with an arbitrary `Cookie` header.
- Feasibility: high for offline sessions, since the id is exactly `"offline_" + shop`, and shop domains are generally public/enumerable.

### Recommendation
Do not use a raw, attacker-suppliable value as a direct session-storage key. Bind the cookie value to something verifiable under `Context.api_secret_key` (e.g., sign/HMAC the session id placed in the cookie and verify the signature in `cookie_session_id` before returning it), or require the host to use a framework-level signed/encrypted cookie store (`cookies.signed`/`cookies.encrypted` in Rails) and document this as mandatory, and additionally require that the resolved session's `shop`/`access_token` be re-validated against another authenticated signal (e.g., a fresh HMAC-validated request or JWT) before being trusted for API calls.

### Proof of Concept
```ruby
# test/utils/session_utils_test.rb (new test)
def test_cookie_session_id_is_pure_passthrough_of_attacker_controlled_cookie
  attacker_supplied_cookie_value = "offline_victim-shop.myshopify.com"
  cookies = { ShopifyAPI::Auth::Oauth::SessionCookie::SESSION_COOKIE_NAME => attacker_supplied_cookie_value }

  # No HMAC/signature check occurs - the value is returned verbatim.
  assert_equal(
    attacker_supplied_cookie_value,
    ShopifyAPI::Utils::SessionUtils.cookie_session_id(cookies),
  )

  # Demonstrates equality holds both "before" (attacker's raw cookie) and "after"
  # (value handed to host storage lookup) with no transformation/validation in between.
  ShopifyAPI::Context.stubs(:embedded?).returns(false)
  assert_equal(
    attacker_supplied_cookie_value,
    ShopifyAPI::Utils::SessionUtils.current_session_id(nil, cookies, false),
  )
end
```
This confirms `cookie_session_id`/`current_session_id` never verify that the cookie value was produced from bytes authenticated under `Context.api_secret_key`, and would hand an arbitrary, attacker-crafted session id straight to the host's session storage lookup.

### Citations

**File:** lib/shopify_api/utils/session_utils.rb (L19-37)
```ruby
        def current_session_id(shopify_id_token, cookies, online)
          if Context.embedded?
            if shopify_id_token
              id_token = shopify_id_token.gsub("Bearer ", "")
              session_id_from_shopify_id_token(id_token: id_token, online: online)
            else
              # falling back to session cookie
              raise Errors::CookieNotFoundError, "JWT token or Session cookie not found for app" unless
                cookies && cookies[Auth::Oauth::SessionCookie::SESSION_COOKIE_NAME]

              cookie_session_id(cookies)
            end
          else
            raise Errors::CookieNotFoundError, "Session cookie not found for app" unless
              cookies && cookies[Auth::Oauth::SessionCookie::SESSION_COOKIE_NAME]

            cookie_session_id(cookies)
          end
        end
```

**File:** lib/shopify_api/utils/session_utils.rb (L58-66)
```ruby
        sig { params(shop: String, user_id: String).returns(String) }
        def jwt_session_id(shop, user_id)
          "#{shop}_#{user_id}"
        end

        sig { params(shop: String).returns(String) }
        def offline_session_id(shop)
          "offline_#{shop}"
        end
```

**File:** lib/shopify_api/utils/session_utils.rb (L68-71)
```ruby
        sig { params(cookies: T::Hash[String, String]).returns(T.nilable(String)) }
        def cookie_session_id(cookies)
          cookies[Auth::Oauth::SessionCookie::SESSION_COOKIE_NAME]
        end
```

**File:** lib/shopify_api/auth/oauth.rb (L67-71)
```ruby
          state = cookies[SessionCookie::SESSION_COOKIE_NAME]
          raise Errors::NoSessionCookieError unless state

          raise Errors::InvalidOauthError,
            "Invalid state in OAuth callback." unless state == auth_query.state
```

**File:** lib/shopify_api/auth/oauth.rb (L100-112)
```ruby
          cookie = if Context.embedded?
            SessionCookie.new(
              value: "",
              expires: Time.now,
            )
          else
            SessionCookie.new(
              value: session.id,
              expires: session.expires ? session.expires : nil,
            )
          end

          { session: session, cookie: cookie }
```
