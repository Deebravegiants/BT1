### Title
Session Fixation / Cross-Tenant Session Hijacking via Predictable, Unsigned Session Cookie Value - (File: lib/shopify_api/utils/session_utils.rb)

### Summary
`ShopifyAPI::Utils::SessionUtils.current_session_id` treats the raw value of the `shopify_app_session` cookie as an authenticated session identifier with no cryptographic verification, and that value is a deterministic, guessable string (`offline_{shop}` or `{shop}_{user_id}`) rather than a random secret bound to the authenticated browser. This breaks the identity binding "session id returned to the app == session id cryptographically tied to a specific authenticated browser/user," instead reducing it to "session id == unauthenticated bytes supplied by whoever sets the cookie."

### Finding Description
When an app is not embedded, or is embedded but has no session token available, `current_session_id` falls back to `cookie_session_id`, which simply returns the cookie's value verbatim with **no signature, no encryption, and no binding check**: [1](#0-0) [2](#0-1) 

That cookie's value is set, during `begin_auth`/`validate_auth_callback`, to `session.id` verbatim: [3](#0-2) 

And `session.id` itself is fully deterministic, derived only from public/semi-public data — the shop domain and (for online sessions) the associated Shopify user id: [4](#0-3) [5](#0-4) 

Because `SessionCookie` carries no HMAC/signature of its own (unlike `AuthQuery`/`Webhooks::Request`, both of which implement `Utils::VerifiableQuery` and are validated through `Utils::HmacValidator`), the gem hands the host application a value it labels as "the session id" that is actually just attacker-controllable, unauthenticated bytes: [6](#0-5) 

The documented consumption pattern instructs the host app to store the returned `Session` under `session.id` and later re-fetch it using exactly this `current_session_id` value: [7](#0-6) 

Equality between the shop-authenticated identity ("the shop that completed OAuth and whose access token is stored under id `offline_{shop}` / `{shop}_{user_id}`") and the shop trusted via the cookie ("whatever value the client sends back for `shopify_app_session`") is never re-verified — no server-side random nonce, no signature, no CSRF-style token is checked against the value before it's used as the storage lookup key.

### Impact Explanation
Any unprivileged internet user who can set a `shopify_app_session` cookie scoped to the app's origin (e.g., a malicious merchant installing the same multi-tenant app, or any actor able to write a cookie to that origin) can compute or guess a victim shop's deterministic session id — `offline_{victim-shop}.myshopify.com` for offline access, which requires only knowledge of the victim's `myshopify.com` domain, a value that is frequently public (storefront URL, App Store listing, partner directories, etc.). Setting that cookie value and issuing a request causes the host application (following this gem's documented pattern) to resolve the victim's stored `Session`, including its real Shopify **access token**, and use it on the attacker's behalf. This is a cross-tenant access / credential misuse vulnerability directly enabled by the gem trusting unauthenticated cookie bytes as a session identity.

### Likelihood Explanation
High for non-embedded apps (this is the primary session mechanism) and for any embedded app that falls back to cookie auth when no `shopify_id_token` is present. The only prerequisite is knowledge of the target's `myshopify.com` domain (offline sessions) — no secret, access token, or privileged access is required, satisfying the "unprivileged internet user" threat model.

### Recommendation
Do not use a deterministic, unsigned value as the session cookie/session-id. Either:
1. Sign/HMAC the cookie value with `api_secret_key` (or a server-side secret) and verify that signature in `cookie_session_id` before trusting it, or
2. Use an opaque, cryptographically random token (already available via `SecureRandom.uuid` used elsewhere in `Session#initialize`) as the cookie value, mapped server-side to the deterministic session id, rather than exposing the deterministic id directly to the client.

### Proof of Concept
1. Attacker installs the target app on their own store (or otherwise obtains a valid session with the app) so requests reach the app's authenticated routes.
2. Attacker learns/guesses `victim-shop.myshopify.com` (public storefront domain).
3. Attacker sets the browser cookie `shopify_app_session=offline_victim-shop.myshopify.com` for the app's origin.
4. Attacker issues a request to a route that calls `ShopifyAPI::Utils::SessionUtils.current_session_id(nil, cookies, false)`; per [1](#0-0)  this returns `"offline_victim-shop.myshopify.com"` unchanged.
5. The host application (per the documented pattern in `docs/usage/oauth.md`) looks up the stored `Session` for that id and uses its `access_token` to serve the request — granting the attacker the victim shop's authenticated context.

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

**File:** lib/shopify_api/auth/oauth/session_cookie.rb (L1-27)
```ruby
# typed: strict
# frozen_string_literal: true

module ShopifyAPI
  module Auth
    module Oauth
      class SessionCookie < T::Struct
        extend T::Sig

        SESSION_COOKIE_NAME = "shopify_app_session"

        const :name, String, default: SESSION_COOKIE_NAME
        const :value, String
        const :expires, T.nilable(Time)

        alias_method :eql?, :==
        sig { params(other: T.nilable(SessionCookie)).returns(T::Boolean) }
        def ==(other)
          return false unless other

          name == other.name &&
            value == other.value &&
            expires == other.expires
        end
      end
    end
  end
```

**File:** docs/usage/oauth.md (L217-228)
```markdown
##### Output
This method returns a hash containing the new session and a cookie to be set in the browser in form of:
```ruby
{
    session: ShopifyAPI::Auth::Session,
    cookie: ShopifyAPI::Auth::Oauth::SessionCookie,
}
```
| Key | Type | Notes |
|-----|------|-------|
|`session`|`ShopifyAPI::Auth::Session`|A session object that contains necessary information to identify the session like `shop`, `access_token`, `scope`, etc.|
|`cookie` |`ShopifyAPI::Auth::Oauth::SessionCookie`|A session cookie to store on the user's browser. |
```
