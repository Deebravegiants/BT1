### Title
Session identifier used as the sole authentication cookie is deterministically derived from the public shop domain (and Shopify's numeric user id), enabling cross-tenant session hijacking - ([File: lib/shopify_api/auth/session.rb])

### Summary
`ShopifyAPI::Auth::Session.from` generates the `Session#id` deterministically from public, attacker-known values (the shop domain, or shop + Shopify user id) instead of a random/secret value. For non-embedded apps, `ShopifyAPI::Auth::Oauth.validate_auth_callback` sets this exact, unsigned, predictable `id` as the value of the `shopify_app_session` cookie, and `ShopifyAPI::Utils::SessionUtils.cookie_session_id` later returns that raw cookie value as the trusted session identifier used to look up a merchant's stored access token. This breaks the binding "session id ⇔ secret possessed only by the legitimate session holder" — an attacker who merely knows a target shop's domain can construct/forge the identical cookie value and be treated as that shop's authenticated session by any host app that follows this gem's documented flow.

### Finding Description
For the offline OAuth flow, the session id is computed as: [1](#0-0) 

`id = "offline_#{shop}"` for offline tokens, or `id = "#{shop}_#{associated_user.id}"` for online tokens — both fully deterministic and computable by anyone who knows the shop's `myshopify.com` domain (which is public/guessable) and, for online sessions, the merchant's small numeric Shopify user id.

In the Authorization Code Grant callback handler, for non-embedded apps this exact value is used as the entire content of the session cookie handed back to the browser: [2](#0-1) 

The cookie is a plain opaque string (`SessionCookie`), with no HMAC, signature, or server-side secret binding it to the browser that completed OAuth: [3](#0-2) 

When the host application later needs to identify "who is calling", this gem's own utility trusts that raw cookie value verbatim as the session identifier, without any signature check: [4](#0-3) 

`current_session_id` returns `cookie_session_id(cookies)`, which is simply `cookies[SESSION_COOKIE_NAME]` — an unvalidated, attacker-settable string. The same deterministic construction (`offline_session_id`, `jwt_session_id`) is reused as the canonical lookup key for retrieving a merchant's persisted `Session`/access token, as documented in `docs/getting_started.md` and `docs/usage/oauth.md`.

The equality that should hold is:
`session_id (used to fetch access_token) == a value only derivable by whoever completed a genuine, HMAC-verified OAuth callback for that specific shop`

Instead it holds:
`session_id == f(shop domain [, numeric user id])`, a value with no secret entropy — anyone can compute it for any target shop.

### Impact Explanation
Because `offline_#{shop}` (or `#{shop}_#{user_id}`) is the only artifact stored in the browser cookie and the only key applications use (per this gem's documented, intended usage pattern) to retrieve a shop's persisted access token, an unauthenticated attacker who knows or guesses a target merchant's shop domain can set this value as their own session cookie. If the host application follows this gem's documented API (`current_session_id` → `SessionRepository.retrieve_session_for_shop`/equivalent) without adding its own independent, cryptographically signed session mechanism, the attacker is treated as an authenticated user of the target's shop and gains access to that shop's stored access token / API session — a cross-tenant authentication bypass, meeting the "Critical: cross-tenant access" bar.

### Likelihood Explanation
Likelihood is high for any non-embedded app (Authorization Code Grant, explicitly documented as "suitable for non-embedded apps") that follows this gem's documented cookie/session flow as-is: shop domains are public, and the id format (`offline_#{shop}`) is published in this repo's own docs and source. No credentials, tokens, or privileged access are required — only knowledge of a target's `*.myshopify.com` domain, which is routinely public (visible in storefront URLs, app listings, etc.).

### Recommendation
Do not use a deterministic, secret-free value as the sole bearer credential in the session cookie. Either:
- Bind the cookie value to a signed/HMAC'd token (e.g., sign `session.id` with `Context.api_secret_key`, verify the signature in `cookie_session_id` before trusting it), or
- Generate `Session#id` with a cryptographically random component (e.g., `SecureRandom`) that is stored server-side, rather than deriving it purely from `shop`/user id, and require any subsequent lookup to validate that random component.

### Proof of Concept
1. Attacker learns victim's shop domain `victim-shop.myshopify.com` (publicly discoverable).
2. Host app built per this gem's documented flow (`lib/shopify_api/auth/oauth.rb#validate_auth_callback`, non-embedded/offline) stores merchant access tokens keyed by `Session#id`, retrieved via `ShopifyAPI::Utils::SessionUtils.current_session_id`.
3. Attacker sets browser cookie `shopify_app_session=offline_victim-shop.myshopify.com` (exact format from `lib/shopify_api/auth/session.rb` line ~116, matching `SessionCookie::SESSION_COOKIE_NAME` from `lib/shopify_api/auth/oauth/session_cookie.rb` line 10).
4. Any request to the host app calls `SessionUtils.current_session_id` → `cookie_session_id` → returns `"offline_victim-shop.myshopify.com"` unchanged (`lib/shopify_api/utils/session_utils.rb` lines 68-71).
5. Host app looks up the merchant session/access token using this attacker-supplied id and treats the attacker as the authenticated session for `victim-shop`, granting access to the victim's stored access token / API session.

### Citations

**File:** lib/shopify_api/auth/session.rb (L107-121)
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

          if access_token_response.expires_in
            expires = Time.now + access_token_response.expires_in.to_i
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

**File:** lib/shopify_api/auth/oauth/session_cookie.rb (L7-14)
```ruby
      class SessionCookie < T::Struct
        extend T::Sig

        SESSION_COOKIE_NAME = "shopify_app_session"

        const :name, String, default: SESSION_COOKIE_NAME
        const :value, String
        const :expires, T.nilable(Time)
```

**File:** lib/shopify_api/utils/session_utils.rb (L19-71)
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

        sig do
          params(
            id_token: T.nilable(String),
            online: T::Boolean,
          ).returns(String)
        end
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

        sig { params(shop: String, user_id: String).returns(String) }
        def jwt_session_id(shop, user_id)
          "#{shop}_#{user_id}"
        end

        sig { params(shop: String).returns(String) }
        def offline_session_id(shop)
          "offline_#{shop}"
        end

        sig { params(cookies: T::Hash[String, String]).returns(T.nilable(String)) }
        def cookie_session_id(cookies)
          cookies[Auth::Oauth::SessionCookie::SESSION_COOKIE_NAME]
        end
```
