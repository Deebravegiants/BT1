Confirmed: `ShopifyAPI::Utils::SessionUtils.cookie_session_id` at [1](#0-0)  returns the raw, client-supplied cookie value as the session lookup key with zero cryptographic verification, and `SessionCookie` at [2](#0-1)  is a plain unsigned struct — this is the strongest match.

### Title
Unauthenticated, Predictable Session-ID Cookie Enables Cross-Tenant Session Hijacking - (File: `lib/shopify_api/utils/session_utils.rb`)

### Summary
For non-embedded apps (and as the JWT fallback path for embedded apps), `ShopifyAPI::Utils::SessionUtils.current_session_id` derives the session lookup key entirely from an unauthenticated, unsigned browser cookie value, while the session ID itself is a predictable, deterministic string built only from the public shop domain (and, for online sessions, a small integer user id). This breaks the identity binding `cookie value == cryptographically-authenticated session identity`; instead the gem trusts `cookie value == session identity` with no verification at all.

### Finding Description
`SessionUtils.current_session_id` falls back to `cookie_session_id(cookies)` whenever no JWT/id-token is supplied: [3](#0-2)  This helper does nothing but read the raw cookie value:

```ruby
def cookie_session_id(cookies)
  cookies[Auth::Oauth::SessionCookie::SESSION_COOKIE_NAME]
end
``` [1](#0-0) 

There is no HMAC, no signature, no encryption applied to this cookie anywhere in the gem — `SessionCookie` is a plain `T::Struct` with a bare `value: String` field: [2](#0-1) 

Critically, the value the gem itself puts in that cookie during OAuth completion (`session.id`) is *deterministic and guessable*, not a random opaque token: [4](#0-3) 

```ruby
def jwt_session_id(shop, user_id)
  "#{shop}_#{user_id}"
end

def offline_session_id(shop)
  "offline_#{shop}"
end
``` [5](#0-4) 

For offline (store-level, i.e. highest-privilege) sessions, the ID is simply `"offline_#{shop}"` — derived solely from the target's public `.myshopify.com` domain, with no secret material whatsoever. For online sessions it is `"#{shop}_#{user_id}"`, where `user_id` is a small, easily enumerable integer (Shopify admin user IDs).

This is the direct analog of the report's bug class: the report flags `AssetController._relayTransfer` for acting on `fees[i]` values that are never checked against a verified total (`msg.value`), letting an attacker's unverified input drive privileged behavior. Here, the gem's session-resolution logic acts on a client-supplied cookie *value* that is never checked against any verified/signed quantity — the equality that should hold, `cookie value == HMAC-or-signature-verified session identity`, is never enforced; only `cookie value == raw browser input` holds. This is precisely the "session id derived from unauthenticated bytes" and "shop authenticated versus the shop stored as a session key" analog classes named in the rules.

### Impact Explanation
If the host application (as documented and intended, e.g. the getting-started guide directing non-embedded apps to call `current_session_id(nil, cookies, ...)`) uses the returned ID to look up a stored `ShopifyAPI::Auth::Session` (containing that shop's live access token) from shared storage, any unprivileged internet user can set their own `shopify_app_session` cookie to a guessed/known value such as `offline_victim-shop.myshopify.com` and have the application load and act using the victim shop's real offline access token — full cross-tenant access to another merchant's data and Shopify Admin API privileges, without ever needing the app's `client_secret`, a stolen token, or any secret at all. This satisfies the Critical "cross-tenant access" impact bar.

### Likelihood Explanation
Exploitation requires no cryptographic material and no interaction with Shopify's OAuth flow — only knowledge of the victim shop's public storefront domain (trivially discoverable) is needed to construct the offline session id. Because the gem computes this identifier deterministically and never binds the cookie to any signature, likelihood is high wherever a host app follows the documented cookie-based session flow described in `docs/getting_started.md` and `docs/usage/oauth.md`.

### Recommendation
Do not trust the raw cookie value as a session lookup key. Either (a) store a cryptographically random, opaque session token in the cookie instead of the deterministic `shop`/`shop_userid` identifier and require the host app to map that opaque token to session records server-side, or (b) sign/HMAC the cookie value (binding it to `api_secret_key`) and verify that signature in `cookie_session_id` before returning it, mirroring the HMAC-verified integrity applied elsewhere in the gem (`Utils::HmacValidator`).

### Proof of Concept
1. Determine the target's storefront domain, e.g. `victim-shop.myshopify.com` (public information).
2. As any unprivileged visitor to the vulnerable app, set the browser cookie `shopify_app_session=offline_victim-shop.myshopify.com`.
3. Send a normal request to the app; it calls `ShopifyAPI::Utils::SessionUtils.current_session_id(nil, cookies, false)`, which returns `"offline_victim-shop.myshopify.com"` unmodified from the cookie [3](#0-2) .
4. The host app looks up that ID in its session store (per the documented pattern in `docs/usage/oauth.md`) and retrieves the victim shop's real `Session` (with live access token), then performs Shopify Admin API calls on the attacker's behalf using the victim's credentials — cross-tenant access achieved purely by cookie forgery, with no signature check ever performed.

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

**File:** lib/shopify_api/auth/oauth/session_cookie.rb (L7-14)
```ruby
      class SessionCookie < T::Struct
        extend T::Sig

        SESSION_COOKIE_NAME = "shopify_app_session"

        const :name, String, default: SESSION_COOKIE_NAME
        const :value, String
        const :expires, T.nilable(Time)
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
