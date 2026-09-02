### Title
`current_session_id` trusts an unsigned `shopify_app_session` cookie as a session identity, allowing session/access-token theft - (File: `lib/shopify_api/utils/session_utils.rb`)

### Summary
`SessionUtils.current_session_id` derives the session key either from a Shopify-signed id token (JWT, verified against `Context.api_secret_key`) or, whenever that header is missing, from the raw value of the `shopify_app_session` cookie with no cryptographic check at all. Because session ids are predictable, deterministic strings (`"offline_#{shop}"` or `"#{shop}_#{user_id}"`), an attacker who simply omits the id-token header and supplies a crafted cookie value can make the function return another merchant's session id, which the host app then uses to load that merchant's `Session` (including `access_token`) from storage.

### Finding Description
The binding that should hold is: **the returned session id must only be derived from bytes authenticated under `Context.api_secret_key`** (i.e., only from a validated `Auth::JwtPayload`, whose signature is checked in `Auth::JwtPayload.new`). Concretely: [1](#0-0) 

- If `shopify_id_token` is present, the id is built from `Auth::JwtPayload`, which validates the JWT signature/claims against `Context.api_secret_key` — this path is safe.
- If `shopify_id_token` is absent — even for `Context.embedded?` apps — the code falls back to `cookie_session_id(cookies)`, which simply returns `cookies[SESSION_COOKIE_NAME]` verbatim: [2](#0-1) 

For non-embedded apps, this cookie value is set by the gem itself during OAuth callback to literally equal `session.id` (e.g. `offline_shop.myshopify.com` or `shop.myshopify.com_12345`), with **no HMAC, signature, or encryption** applied to it: [3](#0-2) [4](#0-3) 

Session ids follow a fixed, guessable format: [5](#0-4) 

Because a Shopify shop domain is public information (`{shop}.myshopify.com`), an attacker can construct the exact session id string for any victim shop (offline sessions) simply by knowing/guessing the shop name — no signature, secret, or prior request from the victim is required. If the host app (as documented — see `docs/getting_started.md`, "Cookie based authentication ... Non-embedded apps are able to use cookies for session storage/retrieval") takes the string returned by `current_session_id` and passes it straight to a session storage `load_session(id)` call (the pattern this gem's docs instruct developers to use), the attacker's forged cookie value causes the app to load and use the victim's `Session`, exposing `session.access_token` for subsequent Admin API calls made on the attacker's behalf.

None of the existing guards prevent this:
- `HmacValidator.validate` only protects the OAuth callback query string, not the session cookie.
- `JwtPayload`'s `aud`/signature checks only apply on the id-token branch, which is entirely bypassed by omitting the header.
- `Context.embedded?` does not block the cookie fallback; it is used for *both* embedded (when id token is missing) and non-embedded apps.
- There is no code in `SessionUtils` or `Oauth` that re-validates the cookie against anything derived from `api_secret_key` before returning it as the session id.

### Impact Explanation
Any caller that treats the value returned by `current_session_id` as an authenticated session key (the exact and documented usage pattern for this gem) will load whatever session that string maps to. Since offline session ids are deterministically derived from the public shop domain (`offline_#{shop}`), an attacker can enumerate/target arbitrary merchants and, by sending a request with a forged `shopify_app_session` cookie, cause the app to operate under that merchant's `access_token` — i.e., theft/misuse of a merchant's Admin API access token. This is a Critical-class impact (unauthenticated value trusted as an authenticated identity, enabling cross-tenant session takeover) and is repeatable against any shop whose domain is known.

### Likelihood Explanation
- No secret material is required by the attacker — they only need the target shop's public `.myshopify.com` domain to construct the offline session id.
- The attacker needs to reach an endpoint of a host app built on this gem that (a) is non-embedded, or (b) is embedded but the request lacks the `Authorization`/id-token header (any of the attacker's own direct HTTP requests naturally lack it, since they don't hold a valid signed token for another shop).
- The cookie is just an HTTP header value the attacker fully controls on requests they send themselves; no XSS or browser trickery is needed to "set" it for their own outbound request.
- The only host-app-side mitigation would be to additionally validate that the loaded session's shop matches an independently authenticated identity — which is exactly what the JWT path is supposed to guarantee, but the cookie fallback skips it.

### Recommendation
Do not treat the `shopify_app_session` cookie value as a self-authenticating identity. At minimum:
1. Sign/HMAC the session cookie value using `Context.api_secret_key` when it is set in `Oauth.validate_auth_callback`, and verify that HMAC in `SessionUtils.cookie_session_id` before returning the id.
2. Ensure the cookie is set with `HttpOnly`, `Secure`, and `SameSite=Strict/Lax` attributes (defense in depth, though this alone doesn't stop an attacker crafting their own direct requests).
3. Never allow the cookie fallback for `Context.embedded?` apps when the id-token header is simply absent — embedded apps should hard-fail rather than silently degrade to an unauthenticated cookie check.

### Proof of Concept
```ruby
# test/utils/session_utils_test.rb (illustrative addition)
def test_cookie_fallback_accepts_forged_session_id_for_offline_session
  ShopifyAPI::Context.setup(..., is_embedded: false)
  forged_cookie = { "shopify_app_session" => "offline_victim-shop.myshopify.com" }

  # Binding under test: returned id must only originate from bytes signed with api_secret_key.
  returned_id = ShopifyAPI::Utils::SessionUtils.current_session_id(nil, forged_cookie, false)

  # No signature was ever checked, yet the attacker-chosen string is returned verbatim
  # and is indistinguishable from a legitimately-issued offline session id format.
  assert_equal "offline_victim-shop.myshopify.com", returned_id
  # Demonstrate downstream trust: if the host app does
  #   session = MySessionStorage.load_session(returned_id)
  # it will load the victim's session (and access_token) without ever validating
  # an HMAC/JWT signed by Context.api_secret_key.
end
```
This confirms the divergence: `current_session_id` returns attacker-chosen bytes as a session identity with no dependency on `Context.api_secret_key`, violating the required SESSION DERIVATION invariant.

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

**File:** lib/shopify_api/auth/oauth/session_cookie.rb (L10-14)
```ruby
        SESSION_COOKIE_NAME = "shopify_app_session"

        const :name, String, default: SESSION_COOKIE_NAME
        const :value, String
        const :expires, T.nilable(Time)
```
