### Title
`SessionUtils.current_session_id` trusts an unauthenticated cookie as the session identifier for embedded apps - ([File: lib/shopify_api/utils/session_utils.rb])

### Summary
`SessionUtils.offline_session_id` and `jwt_session_id` build session IDs by bare string interpolation (`"offline_#{shop}"`, `"#{shop}_#{user_id}"`) from values that are public (the shop domain) or attacker-controlled (`sub`/`user_id` inside a JWT the attacker can obtain for their own dev shop). `current_session_id` falls back to a raw, unsigned cookie value whenever no `Authorization` header/id_token is supplied, even in the embedded branch. Because the ID space is guessable and the cookie fallback performs no cryptographic check, an attacker who can influence a request's cookie jar (and omit the `Authorization` header) can force `current_session_id` to return exactly the string a victim's legitimately-authenticated request would have produced.

### Finding Description
The claimed binding is: `session_id == HMAC_authenticated_value_derived_under(Context.api_secret_key)`. Tracing the code shows this binding does not hold for the cookie fallback path.

`offline_session_id(shop)` and `jwt_session_id(shop, user_id)` are pure string interpolations with no cryptographic input [1](#0-0) . In `session_id_from_shopify_id_token`, these are only reached after a `JwtPayload` is constructed and verified (which internally checks the JWT signature against `Context.api_secret_key`) [2](#0-1) . That path is safe: the `shop`/`sub` values used to build the ID are authenticated by the JWT signature.

The unsafe path is `current_session_id`: for an embedded app, if the caller does not supply a `shopify_id_token` (e.g., the Authorization header is simply omitted from the request), the code falls back to `cookie_session_id(cookies)`, which returns the raw cookie value with **no signature or HMAC verification at all** [3](#0-2) [4](#0-3) . This is confirmed by the test suite itself: `test_embedded_app_current_session_id_returns_id_from_auth_header_even_with_cookies` shows the JWT path takes precedence *when present*, but by construction, when it's absent the code falls through to the cookie branch, which for embedded apps is only guarded by "cookie exists," not "cookie is cryptographically bound to this shop/session" [5](#0-4) .

Because `offline_session_id(shop)` is `"offline_#{shop}"`, an attacker who knows (or brute-forces from public `.myshopify.com` domains) a victim shop's domain can set their own request's `shopify_app_session` cookie to `offline_<victim>.myshopify.com` and omit the Authorization header. `current_session_id` will return that exact string. If the host application then uses this returned ID to look up a `Session` object from its own session storage (the documented purpose of this method per `docs/getting_started.md`), the attacker receives the lookup result for the victim's session key — including the victim's stored `access_token` — without ever presenting a valid signed JWT or any secret. Note the gem itself does not set a cookie to a predictable value in the embedded flow (`oauth.rb` explicitly clears the cookie to `""` for embedded apps after OAuth) [6](#0-5) ; the vulnerability is that `current_session_id` itself provides no defense if the *host application* (or a proxy, CDN cache, or any code path) ever calls it with attacker-supplied cookies and a missing/omitted Authorization header — there is no assertion inside this library that embedded apps must reject cookie-only requests.

Existing guards do not close this gap: `HmacValidator.validate` and `JwtPayload`'s `aud`/signature checks protect the OAuth callback and JWT-token paths respectively, but they are never invoked on the cookie fallback branch of `current_session_id`. `Context.embedded?` only selects *which* branch runs; it does not force JWT-only behavior when a cookie happens to be present and no header is sent.

### Impact Explanation
If a host application relies on `current_session_id`'s return value as a trusted lookup key into its session store without independently confirming the request carried a validated JWT, an attacker can retrieve or act as another merchant's offline (or online, given a leaked/guessed `user_id`) session, exposing that merchant's `access_token` and enabling cross-tenant data access/mutation — Critical severity, matching "cross-tenant access: one shop's request reads or mutates another merchant's data." The blast radius covers every shop whose domain is known or guessable (shop domains are typically public, e.g., visible in storefront URLs), and the attack is trivially repeatable per victim by just changing the cookie value.

### Likelihood Explanation
This requires the host application to invoke `current_session_id` in a code path reachable by an unauthenticated/unheadered request (e.g., a controller that reads cookies before checking for the Authorization header, or a proxy/CDN that strips the header) and to use the returned string directly as a session-storage key without further validation. The gem's own documented usage pattern encourages exactly this: call `current_session_id(auth_header, cookies, online)` and use the result to fetch a `Session`. The attacker's cost is minimal — set a cookie, omit a header — and no secret or privileged access is required, satisfying the "unprivileged attacker" model. Whether this is exploitable end-to-end depends on the specific host app's controller wiring, which is outside this gem's code; I cannot confirm from this repo alone whether the shipped Rails-engine-less usage guarantees the Authorization header is always present for embedded requests.

### Recommendation
In `current_session_id`, for embedded apps, do not silently fall back to an unauthenticated cookie value as the session ID. Either (a) require a valid `shopify_id_token`/JWT for all embedded-app session lookups and drop the cookie fallback entirely for `Context.embedded? == true`, or (b) sign/HMAC the session cookie value under `Context.api_secret_key` when it is set, and verify that HMAC before trusting the cookie's value as a session ID, mirroring the protection already given to the OAuth `state` cookie and JWT paths.

### Proof of Concept
```ruby
# test/utils/session_utils_test.rb (additional test)
def test_embedded_app_current_session_id_trusts_forged_cookie_without_auth_header
  ShopifyAPI::Context.stubs(:embedded?).returns(true)

  victim_shop = "victim-shop.myshopify.com"
  forged_offline_id = "offline_#{victim_shop}" # == SessionUtils.offline_session_id(victim_shop)
  cookies = { ShopifyAPI::Auth::Oauth::SessionCookie::SESSION_COOKIE_NAME => forged_offline_id }

  # Attacker sends no Authorization header (shopify_id_token: nil) and a cookie
  # they set themselves, matching exactly the ID the gem would mint for the victim.
  returned_id = ShopifyAPI::Utils::SessionUtils.current_session_id(nil, cookies, false)

  assert_equal(
    ShopifyAPI::Utils::SessionUtils.offline_session_id(victim_shop),
    returned_id,
    "Cookie-only, unauthenticated request produced the same session id " \
    "as a legitimately-authenticated offline session for the victim shop",
  )
end
```
This demonstrates that `current_session_id` returns a string indistinguishable from the value a legitimate, JWT-authenticated request for the victim shop would produce, purely from an attacker-supplied cookie with no `Authorization` header and no knowledge of `Context.api_secret_key`. Whether this is fully exploitable end-to-end depends on how a specific host application wires this return value into its session storage lookup, which is outside this gem and not something I can verify further from the available index.

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

**File:** test/utils/session_utils_test.rb (L91-104)
```ruby
      def test_embedded_app_current_session_id_raises_cookie_not_found_error
        ShopifyAPI::Context.stubs(:embedded?).returns(true)

        [
          nil,
          {},
          { "not-session-cookie-name": "not-this-cookie" },
        ].each do |cookies|
          error = assert_raises(ShopifyAPI::Errors::CookieNotFoundError) do
            ShopifyAPI::Utils::SessionUtils.current_session_id(nil, cookies, true)
          end
          assert_equal("JWT token or Session cookie not found for app", error.message)
        end
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
