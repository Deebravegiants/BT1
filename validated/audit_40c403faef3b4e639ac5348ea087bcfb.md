### Title
Non-embedded session cookie stores the raw, predictable `session.id` as an unsigned lookup key, enabling cross-tenant session hijack - (File: lib/shopify_api/utils/session_utils.rb)

### Summary
For non-embedded apps (and for embedded apps that fall back to the cookie path), `SessionUtils.current_session_id` returns the session-cookie value verbatim with no cryptographic verification that it was actually issued to this browser for this shop. Because `Auth::Oauth.validate_auth_callback` sets that cookie's value to exactly `session.id` (`"offline_#{shop}"` or `"#{shop}_#{user_id}"`), the cookie is a plaintext, fully predictable database lookup key rather than a signed credential.

### Finding Description
The binding that should hold is: `session_id_returned_by_gem == session_id_of_a_session_that_was_actually_authenticated_for_this_browser`. Tracing the code shows this binding is never enforced.

- During callback, `Auth::Oauth.validate_auth_callback` builds the cookie for non-embedded apps as: [1](#0-0) 
i.e. `SessionCookie.new(value: session.id, ...)`, and `session.id` is deterministic and public, as shown by the test fixtures `id: "offline_#{@shop}"` and `id: "#{@shop}_#{...[:id]}"`: [2](#0-1) [3](#0-2) 

- Later, `SessionUtils.current_session_id` for the non-embedded path (and the embedded-without-token fallback path) does nothing but read this raw cookie value and hand it back: [4](#0-3) [5](#0-4) 

There is no HMAC, signature, or JWT check on the cookie value itself — `HmacValidator.validate` is only applied to the OAuth callback query string, and `Auth::JwtPayload`'s `aud`/`iss`/`sub` checks only apply to the embedded `shopify_id_token` path. The cookie path has no equivalent integrity check.

**Exploit flow**: The attacker installs the app on their own shop A, completing a legitimate OAuth flow and receiving cookie `shopify_app_session=offline_shopA.myshopify.com`. Because the format `offline_#{shop}` (or `#{shop}_#{user_id}` for online sessions) is fully deducible from public documentation and this gem's own source, the attacker edits the cookie value on their own outgoing request to `offline_shopB.myshopify.com` (or guesses/enumerates other installed shop domains). The host application calls `SessionUtils.current_session_id(nil, cookies, false)`, which returns this attacker-chosen string unmodified, and the host app then does `SessionStorage.load_session(session_id)` (as documented as the intended integration pattern) — returning shop B's real session, including its offline `access_token`, to the attacker.

None of the existing guards intercept this: `HmacValidator.validate`, `ShopValidator.sanitize!`, and the OAuth `state` comparison only run during the initial `begin_auth`/`validate_auth_callback` handshake, not on subsequent authenticated requests using the cookie; `JwtPayload`'s `aud` check is irrelevant to the cookie branch; `HttpRequest#verify` and `Context.setup?/private?/embedded?` don't touch session-id derivation at all.

### Impact Explanation
Any user who has ever obtained a legitimate offline (or online) session cookie for their own shop can trivially forge the session ID string for any other shop and, if the host application follows this gem's documented lookup pattern (`SessionStorage.load_session(current_session_id)`), retrieve that other shop's persisted offline/online access token — a direct cross-tenant credential theft. This is repeatable against any shop whose domain the attacker can guess or discover, with no rate limiting or additional verification in this code path, matching the "Critical - cross-tenant access / theft of a merchant access token" category.

### Likelihood Explanation
Preconditions: the app must be non-embedded (or embedded but using the cookie fallback because no `shopify_id_token`/`Authorization` header is sent), and must use cookie-based session lookup as documented in `docs/getting_started.md`. Attacker cost is trivial: sign up for a free/dev store, install the app once to get a legitimately-issued cookie, learn the deterministic `offline_#{shop}` / `#{shop}_#{user_id}` format from this gem's public source, and replay a modified cookie value. No secrets, TLS interception, or victim interaction are required.

### Recommendation
Do not use the raw, predictable session id as the cookie's plaintext value. Instead, store an unguessable, per-session random opaque token in the cookie (as is already done for the OAuth `state` nonce via `SecureRandom.alphanumeric`), and have session storage map that opaque token to the real `session.id`/shop, or sign the cookie value (e.g., HMAC-tag it with `api_secret_key`) and verify the signature in `SessionUtils.cookie_session_id` before trusting it, ensuring the shop encoded in the returned identifier can only have been produced by this gem's own OAuth completion for that browser.

### Proof of Concept
```ruby
# test/utils/session_utils_test.rb (new test)
def test_non_embedded_cookie_id_is_forgeable_across_shops
  ShopifyAPI::Context.stubs(:embedded?).returns(false)

  # Attacker's own legitimately-issued cookie for shop A
  attacker_cookie_value = ShopifyAPI::Utils::SessionUtils.offline_session_id("shop-a.myshopify.com")
  assert_equal("offline_shop-a.myshopify.com", attacker_cookie_value)

  # Attacker edits the cookie client-side to target shop B, purely by string substitution
  forged_cookie_value = ShopifyAPI::Utils::SessionUtils.offline_session_id("shop-b.myshopify.com")
  cookies = { ShopifyAPI::Auth::Oauth::SessionCookie::SESSION_COOKIE_NAME => forged_cookie_value }

  # No verification occurs: the gem returns the forged id unchanged
  returned_id = ShopifyAPI::Utils::SessionUtils.current_session_id(nil, cookies, false)
  assert_equal("offline_shop-b.myshopify.com", returned_id)

  # A host app following documented pattern would now do:
  #   session = MySessionStorage.load_session(returned_id)
  # returning shop B's real access_token with no proof shop B ever authenticated this attacker.
end
```
This demonstrates that `SessionUtils.current_session_id` performs no binding check between the cookie's claimed shop and any proof of authentication for that shop, confirming the vulnerability purely via existing gem code with no live shop or secrets required.

### Citations

**File:** lib/shopify_api/auth/oauth.rb (L105-110)
```ruby
          else
            SessionCookie.new(
              value: session.id,
              expires: session.expires ? session.expires : nil,
            )
          end
```

**File:** test/auth/oauth_test.rb (L186-198)
```ruby
        expected_session = ShopifyAPI::Auth::Session.new(
          id: "offline_#{@shop}",
          shop: @shop,
          access_token: @offline_token_response[:access_token],
          scope: @offline_token_response[:scope],
          expires: @stubbed_time_now + @online_token_response[:expires_in].to_i,
          refresh_token: @expiring_offline_token_response[:refresh_token],
          refresh_token_expires: @stubbed_time_now + @expiring_offline_token_response[:refresh_token_expires_in].to_i,
        )
        expected_cookie = ShopifyAPI::Auth::Oauth::SessionCookie.new(
          value: "offline_#{@shop}",
          expires: expected_session.expires,
        )
```

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

**File:** lib/shopify_api/utils/session_utils.rb (L63-66)
```ruby
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
