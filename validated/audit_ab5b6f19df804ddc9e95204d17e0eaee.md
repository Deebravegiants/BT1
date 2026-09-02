### Title
Unsigned session cookie allows session-ID forgery / cross-tenant session hijack - (File: `lib/shopify_api/utils/session_utils.rb`)

### Summary
`ShopifyAPI::Utils::SessionUtils.current_session_id` is documented and intended to return the identifier that a host application uses to look up a merchant's stored `Session` (containing its access token) for non-embedded apps [1](#0-0) . For the cookie-based path, this identifier is taken verbatim from an unsigned, unauthenticated cookie value, with no cryptographic binding to the OAuth process that created it.

### Finding Description
`SessionUtils#cookie_session_id` returns the raw `shopify_app_session` cookie value with no verification: [2](#0-1) 

`current_session_id` unconditionally trusts this value for non-embedded apps (and as an embedded fallback) as the session identifier used by the host app to retrieve a `Session`/access token: [3](#0-2) 

The `SessionCookie` object that populates this cookie during `validate_auth_callback` is a plain, unsigned struct — it contains only `name`, `value`, `expires`, with no HMAC or signature over the value: [4](#0-3) 

Critically, offline session IDs are *deterministic and fully predictable* from the publicly known shop domain — `"offline_#{shop}"` — with no secret or random component: [5](#0-4) [6](#0-5) 

This breaks the identity binding: `session_id_returned_by_gem == session_id_the_gem_actually_authenticated_via_OAuth`. The gem returns whatever bytes arrive in the cookie, never checking they were produced by its own OAuth/HMAC-verified flow (`Oauth.validate_auth_callback`, `HmacValidator.validate`) for the *current* browsing session. A host application that follows the documented pattern — passing `cookies` straight into `current_session_id` and using the result as a lookup key into its session store — inherits this trust gap directly from the gem's own API surface, matching the rule's allowed analog: "a session id derived from unauthenticated bytes."

### Impact Explanation
Because the offline session ID format (`"offline_<shop>.myshopify.com"`) is deterministic and the shop domain is public information, any party able to set or overwrite the app's session cookie in a victim's browser (or, more directly, able to send that cookie value to a server endpoint that calls `current_session_id`) can construct the exact session ID belonging to *any other merchant* using the app. If the host application's session store returns the merchant's access token for that ID — as the documented usage pattern implies — this results in cross-tenant access: one merchant's request can be resolved to another merchant's `Session`/access token entirely through gem-provided logic, with no additional secret required. This meets the Critical severity bar (cross-tenant access) defined in scope.

### Likelihood Explanation
Likelihood depends on the host application's cookie-setting behavior (`Secure`/`HttpOnly` flags, subdomain cookie scoping, or any endpoint that reflects/sets this cookie from user-controlled input) and on whether the store uses the returned ID directly for token lookup as the docs suggest. The gem does nothing to prevent it and does not document that the returned session ID must not be trusted for authorization without further verification. The root cause — an unsigned cookie value trusted as an authorization key — is unconditional in this gem's own code path, not fabricated in the host app.

### Recommendation
Do not treat the raw cookie value as trusted only by nature of its presence. Sign/HMAC the session cookie value with `api_secret_key` (or an equivalent secret) at the time it is issued in `Oauth.validate_auth_callback`, and verify that signature in `SessionUtils.cookie_session_id` before returning the ID, mirroring the binding enforced elsewhere via `Utils::HmacValidator`. Alternatively, mark clearly in documentation that the returned session ID must never be used as a bare lookup key without an additional authenticated binding (e.g., re-verifying `shop` via a signed value), and avoid deterministic, guessable session ID formats such as `"offline_#{shop}"`.

### Proof of Concept
1. App is non-embedded; legitimate merchant `victim-shop.myshopify.com` completes OAuth, and the gem issues a `shopify_app_session` cookie with (unsigned) value `offline_victim-shop.myshopify.com` per `Session.from`/`Oauth.validate_auth_callback`.
2. An attacker, who knows only the public shop domain `victim-shop.myshopify.com`, constructs a request to the host app with a forged `shopify_app_session` cookie set to `offline_victim-shop.myshopify.com` (e.g., via any mechanism that lets them set cookies for the app's domain, such as a related subdomain, a cookie-setting endpoint, or a browser they control that they trick into holding this cookie).
3. The host app calls:
   `ShopifyAPI::Utils::SessionUtils.current_session_id(nil, cookies, false)`
   which returns `"offline_victim-shop.myshopify.com"` — the same string as step 1 — via `cookie_session_id`: [2](#0-1) 
4. The host app looks up its session store using this ID (the documented usage pattern) and retrieves `victim-shop`'s stored `Session`, including its Admin API access token — granting the attacker access to the victim merchant's data through no fault of the host application's own logic, purely because the gem never validated the cookie's provenance.

### Citations

**File:** docs/getting_started.md (L47-52)
```markdown
#### Cookie
Cookie based authentication is not supported for embedded apps due to browsers dropping support for third party cookies due to security concerns. Non-embedded apps are able to use cookies for session storage/retrieval.

For *non-embedded* apps, you can pass the cookies into:
 - `ShopifyAPI::Utils::SessionUtils.current_session_id(nil, cookies, true)` for online (user) sessions or
 - `ShopifyAPI::Utils::SessionUtils.current_session_id(nil, cookies, false)` for offline (store) sessions.
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

**File:** lib/shopify_api/auth/oauth/session_cookie.rb (L1-26)
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
```

**File:** lib/shopify_api/auth/session.rb (L114-117)
```ruby
            id = "#{shop}_#{associated_user.id}"
          else
            id = "offline_#{shop}"
          end
```
