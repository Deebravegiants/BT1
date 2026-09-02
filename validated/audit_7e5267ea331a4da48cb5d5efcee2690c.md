### Title
Session ID trusted directly from an unsigned cookie value, allowing cross-tenant session hijacking - (File: lib/shopify_api/utils/session_utils.rb)

### Summary
`ShopifyAPI::Utils::SessionUtils.current_session_id` and its helper `cookie_session_id` return the raw, unsigned value of the `shopify_app_session` cookie as the trusted session identifier, with no cryptographic verification that this value was actually issued by Shopify to the requesting browser. This breaks the intended binding `session_id == identity established by Shopify (HMAC/JWT-verified)`, replacing it with `session_id == whatever bytes the client sent in a cookie`.

### Finding Description
During OAuth completion, `ShopifyAPI::Auth::Oauth.validate_auth_callback` builds a `SessionCookie` whose `value` is simply `session.id` (e.g. `"{shop}_{user_id}"` for online sessions or `"offline_{shop}"` for offline sessions), in plaintext, with no signature or MAC attached: [1](#0-0) 

The gem's own documented integration pattern stores this value in a plain (not Rails-signed/encrypted) cookie: [2](#0-1) 

Later, when the host app wants to resolve "who is calling me", it calls `SessionUtils.current_session_id`. For non-embedded apps (and for embedded apps that fall back when no JWT/id token is present), the method simply reads the cookie value back out and returns it, unverified: [3](#0-2) [4](#0-3) 

Contrast this with the two other identity-establishing mechanisms in the same file/class:
- `session_id_from_shopify_id_token` derives the session id only from a `JwtPayload`, which is decoded and its signature verified against `Context.api_secret_key` before any field is trusted: [5](#0-4) 
- The OAuth callback itself binds `shop`/`state`/`code`/`host` via an HMAC computed with `Context.api_secret_key` before they are trusted: [6](#0-5) 

The cookie path has none of this protection: `cookie_session_id` performs a bare hash lookup on attacker-controlled input (`cookies[Auth::Oauth::SessionCookie::SESSION_COOKIE_NAME]`) and hands it straight back as the trusted `session_id`, which downstream host applications use as the storage key to retrieve a `ShopifyAPI::Auth::Session` object containing a live `access_token` for a specific shop.

**Equality that should hold:** `session_id returned to the host app == identity cryptographically attested by Shopify` (via signed JWT or HMAC-verified OAuth callback).
**Equality that actually holds:** `session_id returned to the host app == bytes present in a client-supplied cookie`, with zero cryptographic binding.

### Impact Explanation
Because `current_session_id` is the primitive host applications (e.g., via the `ShopifyApp` gem or custom integrations) use to look up which merchant's stored `access_token` to attach to outgoing Admin/GraphQL API calls, an unprivileged internet user who can set/replay a cookie value with this name for the app's domain (e.g., across shops of a multi-tenant app deployment, or via any mechanism that lets them influence the cookie jar presented to the endpoint) can cause the application to resolve and use a *different* shop's session/access token. This is a cross-tenant access primitive: the value that is supposed to identify "this browser belongs to shop A's authenticated session" is not bound to any proof of shop A's identity at all — it is copied verbatim from client input, satisfying the "session id derived from unauthenticated bytes" bug class and constituting cross-tenant access to another merchant's credentials in the impact taxonomy.

### Likelihood Explanation
No secrets, access tokens, or privileged access are required — only knowledge of the fixed, publicly-known cookie name `shopify_app_session` (a constant in this open-source gem: `SessionCookie::SESSION_COOKIE_NAME`) and of the deterministic session-id format (`"{shop}_{user_id}"` / `"offline_{shop}"`), both of which are documented/public in this repository. Any client able to set an arbitrary cookie value for requests to the app (e.g., a non-embedded deployment, or an embedded app falling back to the cookie path) can trivially exercise this path exactly as designed by the gem's own API — no host-application misuse is required, since `current_session_id` is documented as the intended entry point for cookie-based session retrieval.

### Recommendation
Do not treat the raw cookie value as a trustworthy session identifier. Either (a) sign/MAC the cookie value with `Context.api_secret_key` when it is set in `validate_auth_callback`, and verify that MAC in `cookie_session_id` before returning the id, or (b) require the host framework's signed/encrypted cookie jar (e.g. Rails' `cookies.signed`/`cookies.encrypted`) explicitly in the documented usage, and validate that the resolved session id actually corresponds to a shop domain recognized via `Utils::ShopValidator` before it is used to fetch a stored access token.

### Proof of Concept
1. App A is embedded/non-embedded and stores sessions keyed by `session.id` as produced by `ShopifyAPI::Auth::Oauth.validate_auth_callback`, following the documented pattern (plain cookie, value = `session.id`). [2](#0-1) 
2. A merchant "victim-shop.myshopify.com" completes OAuth; the resulting offline session id is deterministically `offline_victim-shop.myshopify.com` (or `victim-shop.myshopify.com_{user_id}` for online sessions). [7](#0-6) 
3. An unprivileged attacker sets a `shopify_app_session` cookie with value `offline_victim-shop.myshopify.com` (or guesses/enumerates a user id) on their own request to the app.
4. The app calls `ShopifyAPI::Utils::SessionUtils.current_session_id(nil, cookies, false)`, which returns the attacker-supplied value unmodified via `cookie_session_id`. [8](#0-7) 
5. The host application looks up its session store using this id and retrieves victim-shop's `Session` object, including its real `access_token`, and uses it to serve the attacker's request — a cross-tenant credential compromise, without ever knowing `api_secret_key` or any access token in advance.

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

**File:** docs/usage/oauth.md (L253-263)
```markdown
    # Update cookies with the authorized access token from result
    cookies[auth_result[:cookie].name] = {
      expires: auth_result[:cookie].expires,
      secure: true,
      http_only: true,
      value: auth_result[:cookie].value
    }

    # Store the Session object if your app has a DB/file storage for session persistence
    # This session object could be retrieved later to make authenticated API requests to Shopify
    MyApp::SessionRepository.store_session(auth_result[:session])
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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-22)
```ruby
        sig { params(verifiable_query: VerifiableQuery).returns(T::Boolean) }
        def validate(verifiable_query)
          return false unless verifiable_query.hmac

          result = validate_signature(verifiable_query, Context.api_secret_key)
          if result || Context.old_api_secret_key.nil? || T.must(Context.old_api_secret_key).empty?
            result
          else
            validate_signature(verifiable_query, T.must(Context.old_api_secret_key))
          end
        end
```
