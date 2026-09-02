Confirmed: the gem's own documented usage pattern (`docs/getting_started.md` lines 47-52) instructs non-embedded apps to derive the session lookup id directly from the raw browser cookie via `SessionUtils.current_session_id(nil, cookies, ...)`, with no cryptographic verification of that cookie value in the gem's code path.

### Title
Cookie-derived session ID is unauthenticated and predictable, allowing cross-tenant session/access-token hijack for non-embedded apps - (File: `lib/shopify_api/utils/session_utils.rb`, `lib/shopify_api/auth/session.rb`, `lib/shopify_api/auth/oauth.rb`)

### Summary
For non-embedded apps, the gem's documented session-lookup helper `ShopifyAPI::Utils::SessionUtils.current_session_id` resolves the tenant identity by reading the raw `shopify_app_session` cookie value verbatim, with no signature, HMAC, or origin check binding that value to the requester [1](#0-0) . That cookie value is itself set by `ShopifyAPI::Auth::Oauth.validate_auth_callback` to the plain `Session#id`, which for offline sessions is the fully deterministic, publicly-derivable string `"offline_#{shop}"` [2](#0-1) [3](#0-2) . This is the broken identity binding analogous to the TWAP bug: `session identity used to fetch a Session/access_token == session identity actually authenticated by the requester's credentials` should hold, but instead the returned "session id" is unauthenticated bytes trivially reproducible by anyone who knows the target's `myshopify.com` domain.

### Finding Description
The intended invariant is: *the session id returned by `current_session_id` should only ever match the id of a session actually established by the party currently making the request.* This holds for the embedded/JWT path — `session_id_from_shopify_id_token` requires a `Auth::JwtPayload.new(id_token)` to succeed, which cryptographically verifies the token's HS256 signature against `Context.api_secret_key` before trusting the `shop`/`sub` claims used to build the id [4](#0-3) [5](#0-4) .

The non-embedded cookie path breaks this invariant: `cookie_session_id` just does `cookies[Auth::Oauth::SessionCookie::SESSION_COOKIE_NAME]` and returns it unverified as the session id [6](#0-5) . There is no HMAC, no signature, and no server-side nonce binding this cookie to the browser that legitimately completed OAuth. Worse, the value itself is not a random opaque token: `Session.from` sets `id = "offline_#{shop}"` for offline (store-level) sessions — a value entirely computable from the public shop domain, with no secret material involved [7](#0-6) . `validate_auth_callback` then sets this exact id as the cookie's value for non-embedded apps [3](#0-2) .

Following the gem's own documented flow in `docs/getting_started.md` (lines 47-52), a host application calls `SessionUtils.current_session_id(nil, cookies, false)` for offline sessions and uses the returned string to look up the stored `Session` (containing the merchant's real `access_token`) from its session storage. Since the "authentication" performed by this gem for that lookup key is merely "does a cookie header with this name exist", any unprivileged caller who sets that cookie header to a guessed value receives the same lookup key as a legitimate session.

### Impact Explanation
This is a session-fixation / cross-tenant access class issue (High per the given rubric: "session fixation or forced OAuth completion" and effectively enabling cross-tenant access to another merchant's stored access token). An attacker who knows or guesses a target `{shop}.myshopify.com` domain (routinely public/discoverable) can set `shopify_app_session=offline_{shop}.myshopify.com` in their own browser and, when the host app calls the gem's documented `current_session_id` helper and loads the corresponding stored `Session`, the attacker's request will be treated as belonging to that shop's offline session — exposing/using the victim shop's real access token for Admin API calls made on the attacker's behalf.

### Likelihood Explanation
Likelihood is high for apps following the gem's documented non-embedded cookie pattern verbatim, since: (1) no credential is required to construct the cookie value — only knowledge of the target's public shop domain; (2) the gem performs zero cryptographic verification on this path, unlike the JWT path; (3) the attack requires only a normal HTTP request with a forged cookie header, fully within reach of an unprivileged internet user.

### Recommendation
Do not use predictable, secret-free values (`"offline_#{shop}"`, `"#{shop}_#{user_id}"`) as bearer-style session identifiers trusted from an unauthenticated cookie. Either (a) sign/HMAC the cookie value (e.g., with `Context.api_secret_key`) and verify that signature in `cookie_session_id` before returning it, or (b) use a cryptographically random opaque session id (as already done via `SecureRandom.uuid` when no id is explicitly passed to `Session.new`) instead of the deterministic `offline_#{shop}` / `#{shop}_#{user_id}` scheme, and verify cookie integrity server-side before trusting it as a storage lookup key.

### Proof of Concept
1. Merchant `victim-shop.myshopify.com` installs the app; `Oauth.validate_auth_callback` completes and sets cookie `shopify_app_session=offline_victim-shop.myshopify.com` in the merchant's browser [3](#0-2) .
2. Attacker, with no credentials, sends a request to the host app with header `Cookie: shopify_app_session=offline_victim-shop.myshopify.com`.
3. Host app calls `ShopifyAPI::Utils::SessionUtils.current_session_id(nil, {"shopify_app_session" => "offline_victim-shop.myshopify.com"}, false)` per documented usage, which returns `"offline_victim-shop.myshopify.com"` unchecked [1](#0-0) .
4. Host app loads the stored `Session` for that id (containing `victim-shop`'s real offline `access_token`) and uses it to serve the attacker's request — cross-tenant access achieved without ever presenting a valid credential.

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

**File:** lib/shopify_api/utils/session_utils.rb (L45-56)
```ruby
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
```

**File:** lib/shopify_api/utils/session_utils.rb (L68-71)
```ruby
        sig { params(cookies: T::Hash[String, String]).returns(T.nilable(String)) }
        def cookie_session_id(cookies)
          cookies[Auth::Oauth::SessionCookie::SESSION_COOKIE_NAME]
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
