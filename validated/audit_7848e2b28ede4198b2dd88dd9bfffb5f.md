### Title
Predictable, Unsigned Session Cookie Values Enable Cross-Tenant Session Hijacking - (File: `lib/shopify_api/auth/oauth.rb`, `lib/shopify_api/utils/session_utils.rb`, `lib/shopify_api/auth/session.rb`)

### Summary
For non-embedded (cookie-based) apps, the session identifier that `ShopifyAPI::Auth::Oauth.validate_auth_callback` stores in the browser cookie is the plain, deterministic `Session#id` (e.g. `"offline_{shop}"`), with no cryptographic binding (HMAC/signature) tying that value to the authenticated OAuth exchange that produced it. `ShopifyAPI::Utils::SessionUtils.current_session_id` / `cookie_session_id` then trusts this raw cookie value verbatim as the lookup key applications use to retrieve the merchant's stored `Session` (containing the access token).

### Finding Description
`Session.from` derives `id` deterministically from public information only: [1](#0-0) 

For offline sessions the id is `"offline_#{shop}"` — fully computable by anyone who knows (or guesses) the target shop's `*.myshopify.com` domain, which is not secret.

After a real OAuth callback completes, `Oauth.validate_auth_callback` sets this deterministic id directly as the value of the app's session cookie, unsigned: [2](#0-1) 

`SessionUtils` then reads this cookie value back and hands it out as the authoritative "current session id" that the host application uses to fetch the stored `Session`/access token, with no verification step at all: [3](#0-2) [4](#0-3) 

Compare this to the JWT-based (embedded) path, where the session id is only ever derived from a value that was verified inside a signed token (`Auth::JwtPayload`, HS256 with `Context.api_secret_key`): [5](#0-4) 

The cookie path has no equivalent binding. The identity equality that should hold is:
`session_id_trusted_by_app == session_id_cryptographically_bound_to_a_completed_OAuth_exchange_for_that_shop`

What actually holds is:
`session_id_trusted_by_app == raw_unauthenticated_cookie_bytes_supplied_by_the_client`

Because the id itself is a deterministic function of the public shop domain (`offline_#{shop}`), and the cookie carrying it is not signed, any party who can place that cookie value into a victim admin's browser context (or, more directly, present that cookie value on their own requests to the app, since the app relies purely on the cookie value to select whose session data — including access token — to load) can cause the application to resolve session lookups for a shop the requester never completed OAuth for.

### Impact Explanation
This breaks the tenant boundary the gem is responsible for maintaining: the shop-to-access-token binding delivered to the host application is not tied to proof of a completed OAuth handshake, only to a predictable string. A host application faithfully using the gem's documented `SessionUtils.current_session_id` / cookie-based session flow (exactly as the gem intends for non-embedded apps) can be made to serve one merchant's stored access token/session to a party impersonating a different shop — cross-tenant access to a merchant's stored credentials, which is a Critical-severity outcome under this program's scope.

### Likelihood Explanation
Exploitability depends on how easily an attacker can present or fixate the target cookie value in a request (e.g., cookie injection/fixation via subdomain trust, shared parent domain, or lack of `Secure`/`HttpOnly`/`SameSite` enforcement by the deploying app, or simply because the value is fully predictable and needs no secret to construct). No cryptographic secret (`api_secret_key`, access token) is required to *construct* the value — only the target's public shop domain, which is knowable/guessable in the vast majority of cases (many stores expose it in checkout/storefront URLs). This is a design gap in the gem's own session-id derivation and cookie-issuance code, not a misuse of the documented API by the host app.

### Recommendation
Do not use a deterministic, unsigned value as the externally-facing session cookie identifier. Either:
- Sign/HMAC the cookie value (e.g., wrap `session.id` in a MAC keyed by `Context.api_secret_key`, verified on every read in `SessionUtils.cookie_session_id`), or
- Use an unguessable, randomly generated token as the cookie value and store the mapping to the deterministic `Session#id` server-side, so knowledge of a shop domain alone can never produce a valid session cookie.

### Proof of Concept
1. Attacker learns/guesses the target's shop domain, e.g. `victim-shop.myshopify.com` (publicly discoverable via the store's storefront/checkout URLs).
2. Attacker computes the offline session id exactly as the gem does: `"offline_victim-shop.myshopify.com"` (`lib/shopify_api/auth/session.rb`, `offline_session_id` logic mirrored in `lib/shopify_api/utils/session_utils.rb:64-66`).
3. Attacker sets this value as their own `ShopifyAPI::Auth::Oauth::SessionCookie::SESSION_COOKIE_NAME` cookie (no signature required — the gem never validates the cookie's authenticity) and calls an app endpoint that uses `SessionUtils.current_session_id(nil, cookies, false)`.
4. `SessionUtils.cookie_session_id` returns the attacker-supplied string unmodified as the trusted session id; the host application (following the gem's documented pattern) loads `victim-shop`'s stored `Session`, including its access token, for the attacker's request.

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
