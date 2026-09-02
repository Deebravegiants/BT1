This confirms the design: `Session.from` (`lib/shopify_api/auth/session.rb:107-140`) generates the session `id` as exactly `"#{shop}_#{associated_user.id}"` or `"offline_#{shop}"` [1](#0-0) , and `Oauth.validate_auth_callback` stores that same `session.id` verbatim as the plaintext, unsigned `SessionCookie` value for non-embedded apps [2](#0-1) . `SessionUtils.cookie_session_id` then returns whatever value is present under the `shopify_app_session` cookie key with no signature, MAC, or freshness check [3](#0-2) .### Title
Non-embedded session cookie value is a fully-predictable, unsigned session ID accepted verbatim as an authenticated identity - (File: lib/shopify_api/utils/session_utils.rb)

### Summary
For non-embedded apps, `ShopifyAPI::Utils::SessionUtils.current_session_id` returns the raw, unverified value of the `shopify_app_session` cookie as the caller's session identity, with no signature, HMAC, or freshness check. Because `Session.from` deterministically derives session IDs as `"offline_#{shop}"` or `"#{shop}_#{user_id}"` from publicly known values, and `Oauth.validate_auth_callback` stores exactly that string as the plaintext cookie value, any attacker who knows or guesses a target shop's domain (and user id, for online sessions) can construct the same string and present it as their own cookie to impersonate that shop's session lookup key.

### Finding Description
The broken binding: the caller treats `current_session_id(...) == <trusted lookup key bound to the original authenticated user/shop>`. In reality, for the non-embedded branch, `current_session_id` reduces to `cookie_session_id(cookies)`, which is just `cookies[SESSION_COOKIE_NAME]` returned unchanged: [4](#0-3) [3](#0-2) .

The value this cookie is expected to hold is generated deterministically by `Session.from`: `"#{shop}_#{associated_user.id}"` for online sessions, `"offline_#{shop}"` for offline sessions [1](#0-0) . This exact string is what `Oauth.validate_auth_callback` writes as the cookie's plaintext value for non-embedded apps: `SessionCookie.new(value: session.id, expires: ...)` [2](#0-1) . There is no HMAC, signature, or random nonce embedded in this value — it is exactly `shop` and `user_id`, both derivable from public information (a shop's `.myshopify.com` domain, and, for online sessions, a numeric Shopify user id).

The test suite confirms `current_session_id` performs zero validation of the cookie content — it returns whatever string is present verbatim: `test_non_embedded_app_current_session_id_returns_id_from_cookie` asserts `current_session_id(nil, {SESSION_COOKIE_NAME => "cookie_value"}, true)` returns `"cookie_value"` unchanged [5](#0-4) .

None of the existing guards apply to this path: `HmacValidator.validate` and the `state` comparison only run during the OAuth callback (`Oauth.validate_auth_callback`) [6](#0-5) , not on subsequent authenticated requests. `JwtPayload`'s `aud`/JWT checks only apply to the embedded (`Context.embedded?`) branch, not the cookie branch. The non-embedded branch has no cryptographic check at all before returning the ID as the trusted lookup key.

Exploit flow: an attacker learns or guesses a target shop's `.myshopify.com` domain (and, for online-session impersonation, a target user id — often just `1` or small integers). They send a direct HTTP request to the app with `Cookie: shopify_app_session=offline_targetshop.myshopify.com`. `current_session_id` returns this string unchanged. If the calling application (per this gem's own documented pattern) uses this returned ID to fetch a persisted `Session` object from its session storage, and a session for that shop already exists (because the target shop legitimately installed the app), the attacker's request is served using that shop's real access token — a cross-tenant authentication bypass with no possession proof required.

### Impact Explanation
An attacker gains authenticated access to another merchant's session/access token by supplying a computed cookie value, with no need to observe, intercept, or brute-force any secret — the "credential" is fully derivable from shop domain and (for online sessions) user id. This is repeatable against any shop that has installed the app and is a cross-tenant compromise (Critical - authentication bypass / cross-tenant access), since the session lookup key carries no cryptographic binding to the browser or user that originally received it.

### Likelihood Explanation
Requires the app to be configured `is_embedded: false` (cookie is the only credential path) and to follow this gem's own documented pattern of writing the returned `SessionCookie.value` directly as a plain cookie (as shown in `docs/usage/oauth.md`), which does not use `cookies.signed`/`cookies.encrypted`. The attacker needs no privileged access, secret, or victim interaction — just knowledge of a shop domain (often discoverable) and, for online sessions, a small/guessable user id. Feasibility is high and the attack is trivially repeatable against arbitrary shops that have previously installed the app.

### Recommendation
Never use the deterministic session ID (`offline_#{shop}` / `#{shop}_#{user_id}`) as the literal cookie value trusted for authentication. Instead, generate a cryptographically random, unguessable session token (e.g., `SecureRandom.uuid`/`hex`) to store in the cookie, and use that opaque token purely as a lookup key that is separately validated (e.g., signed/encrypted cookie, or a server-side random nonce bound to the session) rather than a value derivable from public shop/user identifiers. At minimum, `SessionUtils.cookie_session_id` should require the cookie value to match a signed/HMAC'd token rather than accepting any raw string.

### Proof of Concept
```ruby
# test/utils/session_utils_test.rb (additional case)
def test_non_embedded_cookie_accepts_any_predictable_value_without_verification
  ShopifyAPI::Context.stubs(:embedded?).returns(false)

  forged_shop = "victim-shop.myshopify.com"
  forged_offline_id = "offline_#{forged_shop}"  # fully derivable from public shop domain

  cookies = { ShopifyAPI::Auth::Oauth::SessionCookie::SESSION_COOKIE_NAME => forged_offline_id }

  # No signature, HMAC, or ownership check is performed - the gem returns the
  # attacker-supplied, publicly-derivable string verbatim as the trusted session id.
  result = ShopifyAPI::Utils::SessionUtils.current_session_id(nil, cookies, false)

  assert_equal(forged_offline_id, result)
  # If the host app's session storage has a persisted Session for "offline_victim-shop.myshopify.com"
  # (i.e., the victim shop installed the app), this ID will be used to fetch that Session's
  # real access_token, authenticating the attacker's request as the victim shop with zero proof
  # of possession.
end
```
This demonstrates that `current_session_id` provides no barrier against a forged, publicly-computable cookie value being accepted as a valid session identity for non-embedded apps.

### Citations

**File:** lib/shopify_api/auth/session.rb (L107-117)
```ruby
        sig { params(shop: String, access_token_response: Oauth::AccessTokenResponse).returns(Session) }
        def from(shop:, access_token_response:)
          is_online = access_token_response.online_token?

          if is_online
            associated_user = T.must(access_token_response.associated_user)
            associated_user_scope = access_token_response.associated_user_scope
            id = "#{shop}_#{associated_user.id}"
          else
            id = "offline_#{shop}"
          end
```

**File:** lib/shopify_api/auth/oauth.rb (L64-71)
```ruby
          raise Errors::InvalidOauthError, "Invalid OAuth callback." unless Utils::HmacValidator.validate(auth_query)
          raise Errors::UnsupportedOauthError, "Cannot perform OAuth for private apps." if Context.private?

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

**File:** lib/shopify_api/utils/session_utils.rb (L31-36)
```ruby
          else
            raise Errors::CookieNotFoundError, "Session cookie not found for app" unless
              cookies && cookies[Auth::Oauth::SessionCookie::SESSION_COOKIE_NAME]

            cookie_session_id(cookies)
          end
```

**File:** lib/shopify_api/utils/session_utils.rb (L68-71)
```ruby
        sig { params(cookies: T::Hash[String, String]).returns(T.nilable(String)) }
        def cookie_session_id(cookies)
          cookies[Auth::Oauth::SessionCookie::SESSION_COOKIE_NAME]
        end
```

**File:** test/utils/session_utils_test.rb (L80-89)
```ruby
      def test_non_embedded_app_current_session_id_returns_id_from_cookie
        ShopifyAPI::Context.stubs(:embedded?).returns(false)
        expected_session_id = "cookie_value"
        cookies = { ShopifyAPI::Auth::Oauth::SessionCookie::SESSION_COOKIE_NAME => expected_session_id }

        assert_equal(
          expected_session_id,
          ShopifyAPI::Utils::SessionUtils.current_session_id(nil, cookies, true),
        )
      end
```
