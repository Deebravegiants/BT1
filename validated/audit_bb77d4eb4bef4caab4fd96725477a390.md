## Title
Session id used to retrieve a merchant's stored access token is a predictable, unsigned value trusted directly from unauthenticated cookie bytes — enables cross-tenant session hijacking (`lib/shopify_api/utils/session_utils.rb`, `lib/shopify_api/auth/session.rb`, `lib/shopify_api/auth/oauth.rb`)

### Summary
For non-embedded apps (and for embedded apps falling back when no session token is supplied), `ShopifyAPI::Utils::SessionUtils.current_session_id` returns the raw session-cookie value with no cryptographic verification, and that value is a deterministic, guessable string derived purely from the public shop domain (and, for online sessions, the merchant's user id) rather than an unforgeable, unpredictable token bound to a completed HMAC-verified OAuth exchange.

### Finding Description
The equality that must hold for a session-lookup key to be safely trusted from an incoming cookie is:

`session_id_presented_by_client == unforgeable_identifier_bound_to_a_verified_OAuth_completion`

Instead, the gem produces and trusts:

`session_id == "offline_#{shop}"` (offline) or `"#{shop}_#{associated_user.id}"` (online) [1](#0-0) 

and this exact string is written verbatim as the browser session cookie's value after `validate_auth_callback`: [2](#0-1) 

On subsequent requests, the cookie is read back and used as the session id with **no HMAC, signature, or JWT verification at all** — `cookie_session_id` returns the raw cookie bytes directly: [3](#0-2) [4](#0-3) 

Because the shop's `.myshopify.com` domain is public information (visible in the storefront URL, embedded app `host` param, etc.), and the online-session id additionally only depends on the (often small, sequential) Shopify `associated_user.id`, an attacker who knows or guesses a target shop's domain can compute the exact session id string without ever possessing the app's `client_secret`, an access token, or any privileged credential. The documented integration pattern in `docs/usage/oauth.md` stores this cookie with a plain (non-encrypted, non-signed) `cookies[...] = { value: ... }` call and the resulting id is handed directly to the host app's session repository to retrieve the stored `access_token`, so trusting this id is exactly what the gem's own documented flow does — the vulnerability is not contingent on the host app ignoring the library's guidance.

This is the "session id derived from unauthenticated bytes" class of bug from the audit report's hint: just as Compound/Beta trusted a stale, unverified interest-accrual value instead of the true state, this gem trusts an unauthenticated, predictable cookie value as if it were proof of a completed, HMAC-bound OAuth handshake.

### Impact Explanation
An attacker who never completed OAuth for a shop, and holds no access token, `client_secret`, or privileged account, can set this predictable value as their own session cookie and have the host app's session store return the real, previously-issued access token for that shop — a cross-tenant access / credential theft outcome matching the "Critical: cross-tenant access, theft ... of a merchant access token" category.

### Likelihood Explanation
Likelihood is high wherever an app is non-embedded (or an embedded app allows cookie fallback) and follows the documented cookie-storage pattern exactly as shown in `docs/usage/oauth.md`. No secret material or social engineering is required — only knowledge of the target's `myshopify.com` domain (and, for online sessions, a merchant user id, which for many stores is a small guessable integer).

### Recommendation
Do not use a deterministic, publicly-derivable string as the value stored in/read from the client-facing session cookie. Either:
- Store a cryptographically random, unpredictable token as the cookie value and use it only as an opaque lookup key that is separately mapped (server-side) to the deterministic session id, or
- Sign/HMAC the cookie value with `Context.api_secret_key` and verify it in `SessionUtils.cookie_session_id` before use, analogous to how `AuthQuery`/`Webhooks::Request` are HMAC-validated.

### Proof of Concept
1. Determine (publicly) that a shop `victim-shop.myshopify.com` has an app installed and uses offline access (common for background/API access).
2. Compute the deterministic offline session id string exactly as the gem does: `"offline_victim-shop.myshopify.com"` — see `Session.from` at [5](#0-4)  and the confirmed cookie value in tests: `expected_cookie = SessionCookie.new(value: "offline_#{@shop}", expires: nil)`.
3. In the attacker's own browser, set the app's session cookie (`ShopifyAPI::Auth::Oauth::SessionCookie::SESSION_COOKIE_NAME`) to this computed value.
4. Send any request to the host app; the app calls `SessionUtils.current_session_id`, which for non-embedded flow just returns the raw cookie bytes unverified [6](#0-5) .
5. The host app looks up this id in its session repository (per the documented pattern) and retrieves the real stored `Session` for `victim-shop.myshopify.com`, including its `access_token`, granting the attacker authenticated access to the victim shop's data.

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

**File:** lib/shopify_api/utils/session_utils.rb (L68-71)
```ruby
        sig { params(cookies: T::Hash[String, String]).returns(T.nilable(String)) }
        def cookie_session_id(cookies)
          cookies[Auth::Oauth::SessionCookie::SESSION_COOKIE_NAME]
        end
```
