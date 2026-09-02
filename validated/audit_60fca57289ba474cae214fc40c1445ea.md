### Title
Non-embedded session lookup trusts an unsigned, guessable session cookie value as the session identity - (File: `lib/shopify_api/utils/session_utils.rb`)

### Summary
`ShopifyAPI::Utils::SessionUtils.current_session_id`/`cookie_session_id` return the raw, unauthenticated `shopify_app_session` cookie value as the session-lookup key for non-embedded apps (and as a fallback for embedded apps), with no cryptographic binding to the shop or to Shopify at all. Because the library itself generates fully deterministic, guessable IDs for offline/online sessions (`"offline_#{shop}"`, `"#{shop}_#{user_id}"`), any client can set that cookie to a target shop's predictable ID and be looked up as that shop's authenticated session by any host application that follows the gem's documented pattern of calling `current_session_id`/`cookie_session_id` to fetch a stored `Session`.

### Finding Description
Two code paths derive a session id in `lib/shopify_api/utils/session_utils.rb`: [1](#0-0) 

- Embedded flow: `session_id_from_shopify_id_token` builds the id from a `JwtPayload`, which is cryptographically verified with `Context.api_secret_key` (`lib/shopify_api/auth/jwt_payload.rb`, `decode_token`). This path *is* bound to an authenticated identity.
- Non-embedded flow (and embedded fallback when no id token is present): `cookie_session_id(cookies)` simply returns `cookies[SESSION_COOKIE_NAME]` verbatim: [2](#0-1) [3](#0-2) 

The session id values the library itself produces during OAuth are deterministic and public-knowledge-derived, not random secrets: [4](#0-3) 

`Auth::Oauth.validate_auth_callback` sets this exact deterministic string as the cookie value for non-embedded apps: [5](#0-4) 

The `SessionCookie` struct carries no signature/MAC of its own — it is a plain value/expiry pair: [6](#0-5) 

The identity binding that should hold is: `session_id used to fetch the stored access-token session == an id that only the party who legitimately completed OAuth for that shop could produce`. Because `offline_#{shop}` requires no secret to construct — `shop` is the public `*.myshopify.com` domain — this equality is broken: any client can compute a target shop's offline session id and present it as a cookie value.

### Impact Explanation
If a host application follows the gem's documented, non-embedded OAuth flow and uses `SessionUtils.current_session_id`/`cookie_session_id` to key its session repository lookup, an attacker who knows (or guesses) a victim merchant's shop domain can set the `shopify_app_session` cookie to `offline_<victim-shop>.myshopify.com` and be treated by the host app as that shop's authenticated session — gaining access to the stored `Session` object and its `access_token`. This is cross-tenant session hijacking/fixation driven purely by unauthenticated, attacker-supplied bytes, consistent with the "Session fixation" High-impact category.

### Likelihood Explanation
Shop domains (`*.myshopify.com`) are not secrets — they are visible in store URLs, marketing, and app listings — so computing `offline_#{shop}` requires no privileged access. The only barrier is whether a specific host app treats this cookie value as sufficient proof of identity without additional binding (e.g., a signed/encrypted cookie framework feature), which the gem's own docs do not mandate; they only recommend `secure`/`http_only` flags, which do not stop an attacker's own browser from sending a chosen cookie value.

### Recommendation
- Do not use a deterministic, publicly-derivable string (`offline_#{shop}`, `#{shop}_#{user_id}`) as the sole session cookie value trusted for lookup.
- Sign/HMAC the session cookie value (e.g., MAC over the session id with `Context.api_secret_key`) and verify it in `cookie_session_id` before returning it, mirroring the CEI/signature pattern already used for the embedded JWT and OAuth-callback HMAC paths.
- Alternatively, use a high-entropy, unguessable session id (e.g., `SecureRandom.uuid`, as already used for `Session#id` in the default case) as the cookie value instead of the deterministic `offline_#{shop}` string, and document this requirement clearly for host apps.

### Proof of Concept
1. Host app (following the gem's documented non-embedded OAuth flow) stores sessions keyed by `ShopifyAPI::Utils::SessionUtils.current_session_id(...)`, i.e. the raw `shopify_app_session` cookie value, and uses that lookup to retrieve a `Session` with a real access token for API calls.
2. Merchant `victim-shop.myshopify.com` completes OAuth; the app's response sets `Set-Cookie: shopify_app_session=offline_victim-shop.myshopify.com`.
3. Attacker, in their own browser/HTTP client (no credentials, no access to the app's secret), sends a request to the host app with `Cookie: shopify_app_session=offline_victim-shop.myshopify.com`.
4. `SessionUtils.cookie_session_id` returns `"offline_victim-shop.myshopify.com"` unchanged; the host app looks this id up in its session store and returns the victim's stored `Session` (with the victim's real access token), and the attacker is now able to make API calls in the victim shop's context through the app.

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

**File:** lib/shopify_api/utils/session_utils.rb (L45-71)
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

**File:** lib/shopify_api/auth/oauth/session_cookie.rb (L7-25)
```ruby
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
