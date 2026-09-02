## Finding

### Title
Cross-Tenant Session Hijacking via Predictable, Unsigned `shopify_app_session` Cookie — (File: `lib/shopify_api/utils/session_utils.rb`)

### Summary
For non-embedded (and JWT-less embedded) requests, `ShopifyAPI::Utils::SessionUtils.current_session_id` treats the raw, unauthenticated `shopify_app_session` cookie value as a trusted session identifier, with no cryptographic binding to prove it was actually issued by this library for the shop/user in question. Because session ids for this gem are fully deterministic (`"offline_#{shop}"` or `"#{shop}_#{associated_user_id}"`), and the cookie carries no signature/MAC, any client that can present that header value is treated as if it owned that session — allowing cross-tenant retrieval of another shop's stored access token.

### Finding Description
When OAuth completes, `Oauth.validate_auth_callback` sets the browser cookie's value to the deterministic `session.id`: [1](#0-0) 

That id is computed with no secret material at all — just the shop domain (offline) or shop + numeric user id (online): [2](#0-1) 

The cookie itself is a bare struct (`name`, `value`, `expires`) with no signature or MAC field: [3](#0-2) 

When the host app later calls `SessionUtils.current_session_id`/`cookie_session_id`, the gem returns whatever bytes are present in the `shopify_app_session` cookie **verbatim**, without any verification step: [4](#0-3) [5](#0-4) 

This is in stark contrast to the sibling embedded/JWT path in the very same method, `session_id_from_shopify_id_token`, which cryptographically verifies the token via `Auth::JwtPayload` (HMAC-SHA256 with `Context.api_secret_key`, `aud` check, expiry, etc.) before deriving the same style of id: [6](#0-5) 

The two branches of `current_session_id` are supposed to answer the same question — "what session does this identity belong to?" — but only one path binds the returned id to a cryptographic proof of authenticity. The cookie path answers permissively: `returned_session_id == raw_cookie_bytes`, with no equality check against `HMAC(secret, cookie_bytes)` or any Shopify-issued proof. Per the documented usage flow (`docs/getting_started.md`), the host application takes this returned id and looks up the corresponding `Session` (including `access_token`) in its own session store — exactly the intended, documented use of this API: [7](#0-6) 

Since the shop domain is public (attacker knows or can enumerate `{shop}.myshopify.com`) and online user ids are small sequential integers, an attacker can construct a target session id such as `offline_victim-shop.myshopify.com` or `victim-shop.myshopify.com_1` and present it as the `shopify_app_session` cookie value on a direct request to the app (cookies are plain request headers fully controlled by any HTTP client making a direct call, independent of same-origin browser restrictions). Because the gem never verifies the cookie bytes are authentic, this forged id is returned as if it were a legitimately established session identifier for that browser.

### Impact Explanation
This breaks the identity binding "session id trusted by the app == session id actually established through OAuth for that browser/shop." Any unprivileged actor who can control the `Cookie` header can spoof another merchant's deterministic session id and cause the host application to retrieve and use that merchant's stored `Session` (including `access_token`), resulting in cross-tenant access to another shop's Admin API credentials — a Critical-severity outcome per the rubric (cross-tenant access / access-token exfiltration), reachable through this gem's own documented `SessionUtils.current_session_id` API without any privileged information, TLS interception, or social engineering.

### Likelihood Explanation
High. No secret is required to construct the forged identifier — only the target shop's public `.myshopify.com` domain (or a small guessable numeric user id for online sessions). The vulnerable path (`cookie_session_id`) is the exact, documented API surface recommended for non-embedded apps and as a JWT fallback for embedded apps, so it is reachable by design rather than through misuse.

### Recommendation
Do not trust the raw cookie bytes as an authoritative session identifier. Either:
- Sign/MAC the cookie value with `Context.api_secret_key` when it is set in `validate_auth_callback`, and verify that signature in `cookie_session_id`/`current_session_id` before returning the id, mirroring the verification already done for the JWT path in `Auth::JwtPayload`; or
- Store an unguessable, cryptographically random token in the cookie value (mapped server-side to the deterministic session id) instead of the deterministic id itself.

### Proof of Concept
1. Attacker learns/guesses the target shop's domain, e.g. `victim-shop.myshopify.com` (public information; store domains are not secret) and computes the expected offline session id: `offline_victim-shop.myshopify.com` (per `Utils::SessionUtils.offline_session_id`).
2. Attacker issues a direct HTTP request to the target app with header:
   `Cookie: shopify_app_session=offline_victim-shop.myshopify.com`
3. The host app calls `ShopifyAPI::Utils::SessionUtils.current_session_id(nil, cookies, false)`, which returns `"offline_victim-shop.myshopify.com"` unchanged and unverified (`lib/shopify_api/utils/session_utils.rb:19-37,68-71`).
4. The host app looks up its session store using this id (as documented) and retrieves the victim shop's `Session`, including its Admin API `access_token`, granting the attacker cross-tenant access without ever completing OAuth for that shop.

### Citations

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

**File:** lib/shopify_api/auth/oauth/session_cookie.rb (L1-25)
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

**File:** lib/shopify_api/auth/jwt_payload.rb (L23-45)
```ruby
      sig { params(token: String).void }
      def initialize(token)
        payload_hash = begin
          decode_token(token, Context.api_secret_key)
        rescue ShopifyAPI::Errors::InvalidJwtTokenError
          raise unless Context.old_api_secret_key

          decode_token(token, T.must(Context.old_api_secret_key))
        end

        @iss = T.let(payload_hash["iss"], String)
        @dest = T.let(payload_hash["dest"], String)
        @aud = T.let(payload_hash["aud"], String)
        @sub = T.let(payload_hash["sub"], T.nilable(String))
        @exp = T.let(payload_hash["exp"], Integer)
        @nbf = T.let(payload_hash["nbf"], Integer)
        @iat = T.let(payload_hash["iat"], Integer)
        @jti = T.let(payload_hash["jti"], String)
        @sid = T.let(payload_hash["sid"], T.nilable(String))

        raise ShopifyAPI::Errors::InvalidJwtTokenError,
          "Session token had invalid API key" unless @aud == Context.api_key
      end
```

**File:** docs/getting_started.md (L47-52)
```markdown
#### Cookie
Cookie based authentication is not supported for embedded apps due to browsers dropping support for third party cookies due to security concerns. Non-embedded apps are able to use cookies for session storage/retrieval.

For *non-embedded* apps, you can pass the cookies into:
 - `ShopifyAPI::Utils::SessionUtils.current_session_id(nil, cookies, true)` for online (user) sessions or
 - `ShopifyAPI::Utils::SessionUtils.current_session_id(nil, cookies, false)` for offline (store) sessions.
```
