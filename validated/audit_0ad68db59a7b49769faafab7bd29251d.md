### Title
Embedded-app session ID derivation trusts unauthenticated `Cookie: shopify_app_session` value instead of requiring the verified JWT - (File: lib/shopify_api/utils/session_utils.rb)

### Summary
`SessionUtils.current_session_id` is documented as the way host apps derive the "authenticated" session identifier for a request. In the embedded branch, when no `shopify_id_token` is present it silently falls back to returning the raw, attacker-controlled `shopify_app_session` cookie value with zero cryptographic verification, even though this gem's own `Oauth.validate_auth_callback` never sets a meaningful (non-empty) value for that cookie on embedded apps.

### Finding Description
The intended binding is: for embedded apps, `session_id == verified_JWT(shop, sub)` where the JWT is signed with `Context.api_secret_key` and validated by `Auth::JwtPayload`. Instead, the code implements: [1](#0-0) 

When `shopify_id_token` is `nil`/blank, `current_session_id` requires only that *some* cookie be present, then returns it verbatim via `cookie_session_id`: [2](#0-1) 

There is no HMAC, no signature, no relationship checked between this cookie value and any verified identity — the raw bytes an attacker sends in the `Cookie` header become the "authenticated" session id returned to the caller (which the host app then uses to look up a stored, privileged session).

Critically, this gem's own OAuth flow never legitimately populates that cookie with a usable value for embedded apps — `validate_auth_callback` explicitly sets the cookie to an empty, immediately-expired value when `Context.embedded?` is true: [3](#0-2) 

Only the non-embedded path stores `session.id` as the cookie value. This means: for embedded apps, any non-empty `shopify_app_session` cookie value reaching `current_session_id` was never set by this gem's own callback logic and is therefore attacker-supplied.

Session IDs are also predictable/enumerable, since they are simple string concatenations rather than random tokens: [4](#0-3) 

An attacker who knows (or guesses) a victim shop's domain and an associated user id (`"#{shop}_#{user_id}"`) or simply the shop domain (`"offline_#{shop}"`) can send a request with no `Authorization` header and `Cookie: shopify_app_session=<guessed_or_known_id>`, causing `current_session_id` to return that value as if it were authenticated. No guard in this file — `HmacValidator`, `ShopValidator`, `JwtPayload`'s `aud` check, or `Context.embedded?`/`private?` — intervenes on this fallback path; those checks only fire on the JWT branch or during OAuth callback, not here.

### Impact Explanation
The value returned by `current_session_id` is meant to key into the host app's session storage to retrieve a `Session` object containing a live `access_token`. If a host app trusts this return value (as documented), an attacker can cause the app to load and act as an arbitrary victim's session — a cross-tenant/cross-user session hijack (Critical: authentication bypass / cross-tenant access), repeatable against any shop/user id the attacker can construct or enumerate, with no attacker privilege required beyond sending an HTTP request.

### Likelihood Explanation
Preconditions: `Context.embedded?` must be `true` (typical for embedded Shopify apps) and the caller must invoke `current_session_id` with no/blank `shopify_id_token` but a `shopify_app_session` cookie present — a state trivially reachable by simply omitting the `Authorization` header on an otherwise normal request while supplying a crafted `Cookie` header. The attacker needs no secret, no signed artifact, and no privileged access — only the ability to send arbitrary headers, which any internet client has. Session ids are deterministic strings built from shop domain and user id, making them guessable rather than requiring theft of a real cookie in many cases.

### Recommendation
Remove (or gate behind strict, cryptographically-verified conditions) the cookie fallback in the embedded branch of `current_session_id`. For embedded apps, session id derivation should be sourced only from a JWT verified via `Auth::JwtPayload`; if a legacy-cookie fallback must remain for pre-App-Bridge-redirect flows, it must be tied to a value this gem itself set and can verify (e.g., HMAC-signed or matched against a server-side nonce store), never trusted as raw client input.

### Proof of Concept
```ruby
# test/utils/session_utils_test.rb (new test)
def test_embedded_app_current_session_id_trusts_forged_cookie
  ShopifyAPI::Context.stubs(:embedded?).returns(true)
  forged_id = "victim-shop.myshopify.com_123456789"
  cookies = { ShopifyAPI::Auth::Oauth::SessionCookie::SESSION_COOKIE_NAME => forged_id }

  # No Authorization header / shopify_id_token supplied, no JWT verification path invoked
  result = ShopifyAPI::Utils::SessionUtils.current_session_id(nil, cookies, true)

  assert_equal(forged_id, result) # attacker-controlled value returned as "authenticated" session id
end
```
This demonstrates that `Auth::JwtPayload.new` / `Context.api_secret_key` verification is never invoked on this path, and the attacker-chosen cookie string is returned unmodified as the session id.

### Citations

**File:** lib/shopify_api/utils/session_utils.rb (L19-30)
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
