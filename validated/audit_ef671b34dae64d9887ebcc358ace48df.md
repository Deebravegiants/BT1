### Title
Session ID trusted directly from unauthenticated cookie bytes bypasses the cryptographic binding used elsewhere - (File: lib/shopify_api/utils/session_utils.rb)

### Summary
The reported Cally bug is a class of "identity binding" failure: a value (`tokenType`) that is trusted by one code path is never cross-checked against the value that another path actually needs to be true (the real token type), so the two get out of sync and the contract acts on unverified state. The same class of bug appears in this gem's session-resolution logic: for the *online JWT* path, the session id is derived only from claims inside a cryptographically verified `JwtPayload` (checked against `Context.api_secret_key`), but for the *cookie fallback* path the exact same "session id" is derived by simply reading the raw `Cookie` header value with no cryptographic check at all.

### Finding Description
`ShopifyAPI::Utils::SessionUtils.current_session_id` has two branches: [1](#0-0) 

When a `shopify_id_token` is present, the session id is computed from `Auth::JwtPayload.new(id_token)`, whose constructor verifies the JWT signature with `Context.api_secret_key` and validates `aud == Context.api_key`: [2](#0-1) 

But when no id token is supplied (or the app is not embedded), the code falls back to: [3](#0-2) 

`cookie_session_id` returns `cookies[SESSION_COOKIE_NAME]` verbatim — there is no HMAC, no signature, and no re-derivation check against anything the app previously authenticated. The value stored in that cookie is itself just `session.id`, produced in the OAuth callback as a predictable, non-secret string: [4](#0-3) 

Session ids are built with a fixed, guessable format: [5](#0-4) 

i.e. `"#{shop}_#{user_id}"` for online sessions or `"offline_#{shop}"` for offline sessions — both fully derivable from a shop's public `myshopify.com` domain name. Because `cookie_session_id` performs no integrity check, the identity binding that should hold —

`session_id_returned_by_gem == session_id_that_was_actually_established_via_verified_OAuth`

— collapses to

`session_id_returned_by_gem == raw_bytes_the_client_sent_in_the_Cookie_header`

This is exactly the "session id derived from unauthenticated bytes" analog: the gem's own code accepts client-supplied bytes as an authoritative tenant/session key in one path while enforcing full cryptographic verification in the sibling path for the same logical value.

### Impact Explanation
`current_session_id`'s return value is the documented mechanism by which a host application looks up the `Session` object (containing the merchant's access token) from its session storage. If an unprivileged internet user can set/guess the offline session id for a *target* shop (`"offline_<shop>.myshopify.com"` requires no secret, just the public shop domain) and place it in the cookie the gem reads, the gem will hand back that id as "the current session," letting the calling app fetch and act with another merchant's stored access token — a cross-tenant access / authentication bypass, achieved without possessing `api_secret_key`, any access token, or `client_secret`. This satisfies the Critical impact bar (cross-tenant access, theft/misuse of merchant access token) defined in the rules.

### Likelihood Explanation
Exploitability depends on whether the surrounding cookie is delivered/stored with additional protection (e.g., signed/encrypted cookie jar) by the host framework, which the gem itself does not enforce, mandate, or verify. Within the gem's own boundaries, nothing prevents `cookie_session_id` from returning attacker-controlled bytes; the predictable id format compounds the risk since no secret material is needed to construct a valid-looking target id. This makes the likelihood dependent on integration but the root cause — an unauthenticated trust boundary the online JWT path deliberately avoids — is squarely inside this gem's code.

### Recommendation
Do not treat the raw cookie value as a trustworthy, unauthenticated-bytes-derived session key. At minimum, sign/HMAC the session cookie value (mirroring the JWT verification already used for the embedded path) using `Context.api_secret_key`, and verify that signature in `SessionUtils.cookie_session_id` before returning it as the resolved session id, so that the same binding guarantee enforced for the JWT path (`aud == api_key`, signature verified) also holds for the cookie fallback path.

### Proof of Concept
1. App is non-embedded (or embedded without JWT), so `current_session_id` takes the cookie branch: [6](#0-5) 
2. Attacker knows (or guesses) a target shop's myshopify domain, e.g. `victim-shop.myshopify.com`.
3. Attacker sets their own browser's `SESSION_COOKIE_NAME` cookie value to `offline_victim-shop.myshopify.com` (the exact deterministic format produced by `offline_session_id`): [7](#0-6) 
4. `cookie_session_id` returns this attacker-chosen string unchanged, with zero cryptographic verification: [3](#0-2) 
5. The host application uses this id to load the `Session` (and its access token) for `victim-shop` from its session storage and performs Shopify API calls on the attacker's behalf using the victim merchant's access token — a cross-tenant access bypass rooted entirely in the gem's unauthenticated trust of the cookie bytes.

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
