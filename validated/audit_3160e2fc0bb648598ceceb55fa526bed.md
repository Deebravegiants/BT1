### Title
Non-embedded OAuth session cookie carries a deterministic, unsigned session id, enabling session fixation / cross-tenant session hijack - ([File: lib/shopify_api/auth/oauth.rb])

### Summary
For non-embedded (or non-JWT) app flows, `ShopifyAPI::Auth::Oauth.validate_auth_callback` sets a `SessionCookie` whose `value` is exactly the deterministic session id (`offline_<shop>` or `<shop>_<user_id>`), with no cryptographic binding (HMAC/signature) tying that value to the specific OAuth exchange that produced it. Any consumer of this gem that stores/looks up sessions keyed by this id (as `ShopifyAPI::Utils::SessionUtils.cookie_session_id` does) will treat possession of this predictable string as proof of identity for a given shop.

### Finding Description
The identity binding that should hold is:
`cookie.value == session.id` **and** `session.id` should only be reconstructable by someone who has completed OAuth for that shop.

In `lib/shopify_api/auth/oauth.rb`, `validate_auth_callback` builds the cookie directly from `session.id`: [1](#0-0) 

`session.id` itself is deterministically derived only from the (public) shop domain and, for online tokens, the associated user id: [2](#0-1) 

The `SessionCookie` struct carries this value with no signature, MAC, or nonce of its own — it is a bare `String`: [3](#0-2) 

On subsequent requests, `SessionUtils.cookie_session_id` reads this cookie value back and returns it verbatim as the session id used to look up the stored session/access token — no re-derivation from a signed source, no comparison against anything server-side that was generated at OAuth-callback time: [4](#0-3) 

Because `offline_<shop>` (or `<shop>_<user_id>`) is fully predictable from public information (the shop's `myshopify.com` domain, and for online sessions a user id that can often be observed/guessed), an attacker does not need to intercept any secret to know what the victim's post-OAuth cookie value will be. This breaks the intended equality "cookie value authenticates a specific completed OAuth session" down to "cookie value == a public string."

### Impact Explanation
This matches the High-impact category "session fixation or forced OAuth completion." An attacker who can set this exact cookie value in a victim's browser (or who simply sets it in their own browser after knowing/guessing the target shop domain) causes the host application's session storage — keyed by this predictable id — to be accessed as if it were the legitimate merchant's session, yielding cross-tenant access to that merchant's stored offline access token via the app's own APIs. No `api_secret_key`, access token, or privileged access is required to construct the target cookie value; only knowledge of the target shop's domain (or a guessable online-session user id) is needed.

### Likelihood Explanation
Moderate-to-high for apps using the documented non-embedded/cookie-based flow of this gem (`docs/usage/oauth.md`), since the vulnerable pattern (unsigned, deterministic session id doubling as the cookie value) is baked into the gem's own `Oauth.validate_auth_callback` and `SessionUtils` — not something the host app opts into by misusing the API. Exploitation requires only a cookie-injection vector (e.g., subdomain cookie, network position, or the attacker directly using the known id in their own client) rather than any secret material.

### Recommendation
- Do not use `session.id` (or any value derivable purely from public shop/user identifiers) as the session cookie's *value*. Generate a random, unguessable session token at OAuth-callback time, store the mapping `token -> session.id` server-side, and set that random token as the cookie value.
- Alternatively, HMAC-sign the cookie value (e.g., `session.id` + timestamp) with `Context.api_secret_key` and validate the signature in `SessionUtils.cookie_session_id` before trusting it, mirroring the binding already used for `AuthQuery`/`Webhooks::Request` via `Utils::HmacValidator`.

### Proof of Concept
1. Merchant installs the app on `victim-shop.myshopify.com` using the non-embedded OAuth flow; `Oauth.validate_auth_callback` returns a `SessionCookie` with `value: "offline_victim-shop.myshopify.com"`. [5](#0-4) 
2. Attacker, knowing (or guessing) the target's shop domain, sets a cookie `shopify_app_session=offline_victim-shop.myshopify.com` in a browser they control (or injects it into the victim's browser via any cookie-setting vector).
3. On the next request, the host app calls `ShopifyAPI::Utils::SessionUtils.current_session_id` → `cookie_session_id`, which returns `"offline_victim-shop.myshopify.com"` verbatim with no verification: [6](#0-5) 
4. The host app's session storage resolves this id to the merchant's real stored access token, and the attacker's request is now served using the victim shop's credentials — cross-tenant session hijack achieved without ever possessing `api_secret_key` or the access token directly.

### Citations

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

**File:** lib/shopify_api/auth/oauth/session_cookie.rb (L7-14)
```ruby
      class SessionCookie < T::Struct
        extend T::Sig

        SESSION_COOKIE_NAME = "shopify_app_session"

        const :name, String, default: SESSION_COOKIE_NAME
        const :value, String
        const :expires, T.nilable(Time)
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

**File:** lib/shopify_api/utils/session_utils.rb (L63-71)
```ruby
        sig { params(shop: String).returns(String) }
        def offline_session_id(shop)
          "offline_#{shop}"
        end

        sig { params(cookies: T::Hash[String, String]).returns(T.nilable(String)) }
        def cookie_session_id(cookies)
          cookies[Auth::Oauth::SessionCookie::SESSION_COOKIE_NAME]
        end
```
