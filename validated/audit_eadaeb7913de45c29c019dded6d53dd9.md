### Title
Non-embedded `current_session_id` trusts the raw `shopify_app_session` cookie value as an unsigned, predictable session key, enabling cross-tenant session impersonation - (File: `lib/shopify_api/utils/session_utils.rb`)

### Summary
`SessionUtils.current_session_id` for non-embedded apps (and for the embedded fallback branch) calls `cookie_session_id`, which returns the raw `shopify_app_session` cookie value verbatim as the session-storage lookup key [1](#0-0) . That value is never re-derived from or checked against anything authenticated under `Context.api_secret_key` at read time; it is accepted as-is [2](#0-1) . Because the value the server originally placed in that cookie is itself a predictable string (`session.id`, e.g. `offline_#{shop}` for offline sessions), an attacker who sends a request with a forged `Cookie: shopify_app_session=offline_<victim-shop>.myshopify.com` header causes the host app to look up and act as the victim merchant's session.

### Finding Description
The invariant that should hold is: `session_key == f(bytes authenticated by Context.api_secret_key)`. For the JWT path this holds — `session_id_from_shopify_id_token` derives the key from `Auth::JwtPayload`, whose `sub`/`shop` claims come from a JWT signed with `Context.api_secret_key` [3](#0-2) . For the cookie path, this invariant is broken: `cookie_session_id` simply returns `cookies[SESSION_COOKIE_NAME]` [2](#0-1) , and `current_session_id`'s non-embedded branch (and the embedded fallback branch) uses this value directly as the session-storage key with no re-validation [4](#0-3) .

Tracing the value's provenance: in `Oauth.validate_auth_callback`, once the OAuth callback HMAC is validated (`Utils::HmacValidator.validate(auth_query)`), the server sets the cookie's `value` to `session.id` for non-embedded apps [5](#0-4) . `session.id` for offline sessions is `"offline_#{shop}"` and for online sessions is `"#{shop}_#{user_id}"` (per `jwt_session_id`/`offline_session_id`) [6](#0-5) . Both formats are fully predictable strings built from the public shop domain (and, for online, a `sub`/user id that is also often enumerable), containing no random unguessable component and no HMAC/signature binding the value to the specific session it was minted for.

Because the cookie is a plain string equal to a predictable identifier rather than a signed/opaque token, and `cookie_session_id` performs zero verification when reading it back, an attacker who can set HTTP headers on their own request (permitted by the rules) can present `Cookie: shopify_app_session=offline_victim-shop.myshopify.com` directly to the app. `current_session_id` will happily return `"offline_victim-shop.myshopify.com"` as the "current" session id, which the host app then uses to fetch the stored `Session` (containing the victim's access token) from its session storage and serve the request as that shop. No component in this gem — not `HmacValidator.validate`, not `ShopValidator.sanitize!`, not `JwtPayload`'s `aud` check, not `Context.setup?`/`private?`/`embedded?` — is invoked on this code path to verify that the cookie value was actually issued by the server for this browser or that it matches any authenticated claim of the current request.

### Impact Explanation
Any unprivileged attacker who knows (or guesses) a victim merchant's `myshopify.com` domain — which is generally public/discoverable — can construct the exact offline session id and present it as their own session cookie to a non-embedded app built on this gem. If the host app's session storage returns a match, the attacker's request is serviced using the victim's stored access token, i.e., full cross-tenant read/write access to the victim merchant's data. This is repeatable against any shop whose domain is known and requires no interaction with the victim, matching the "Critical - cross-tenant access" category.

### Likelihood Explanation
Preconditions: the host app must be a non-embedded app (or hit the embedded fallback-to-cookie branch) using this gem's default `current_session_id` cookie flow, and must have previously completed OAuth for the victim shop so a session exists in storage under the predictable id. Attacker cost is trivial — setting one HTTP header — and shop domains are typically public information; for online sessions the `user_id` suffix adds friction (may need to be guessed/enumerated) but offline sessions have no such barrier. This makes the offline-session case highly feasible and directly repeatable against arbitrary shops that use the app.

### Recommendation
Do not use a predictable value as the session cookie's content. Store a cryptographically random, unguessable session token in the cookie, or HMAC-sign the cookie value (e.g., `HMAC(api_secret_key, session.id)`) and verify that signature in `cookie_session_id` before trusting it as a session key. Additionally, after loading the session, assert `session.shop` matches the shop context established independently for the current request (e.g., from a validated `shop` param or host header) before using its access token.

### Proof of Concept
```ruby
# test/utils/session_utils_test.rb (additional test)
def test_cookie_session_id_accepts_forged_predictable_offline_session_id
  ShopifyAPI::Context.stubs(:embedded?).returns(false)

  victim_shop = "victim-shop.myshopify.com"
  forged_session_id = "offline_#{victim_shop}" # attacker never saw this cookie; derives it purely from public shop domain

  cookies = { ShopifyAPI::Auth::Oauth::SessionCookie::SESSION_COOKIE_NAME => forged_session_id }

  # No signature/HMAC check is performed; the attacker-chosen cookie value is
  # returned verbatim and would be used to look up the victim's stored Session
  # (containing the victim's access token) in the host app's session storage.
  returned_id = ShopifyAPI::Utils::SessionUtils.current_session_id(nil, cookies, false)

  assert_equal(forged_session_id, returned_id)
  # Demonstrates: session key derivation did not require any bytes authenticated
  # under Context.api_secret_key -- it is the raw, attacker-supplied cookie value.
end
```
This confirms `current_session_id` → `cookie_session_id` returns exactly the attacker-controlled, unsigned cookie value with no cross-check against `Context.api_secret_key`-authenticated data, violating the required session-derivation invariant.

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

**File:** lib/shopify_api/utils/session_utils.rb (L45-56)
```ruby
        def session_id_from_shopify_id_token(id_token:, online:)
          raise Errors::MissingJwtTokenError, "Missing Shopify ID Token" if id_token.nil? || id_token.empty?

          payload = Auth::JwtPayload.new(id_token)
          shop = payload.shop

          if online
            jwt_session_id(shop, T.must(payload.sub))
          else
            offline_session_id(shop)
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

**File:** lib/shopify_api/auth/oauth.rb (L100-110)
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
```
