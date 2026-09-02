### Title
Non-embedded session lookup trusts a raw, unsigned, predictable cookie value as the authoritative session identifier - (File: `lib/shopify_api/utils/session_utils.rb`)

### Summary
`ShopifyAPI::Utils::SessionUtils.current_session_id`/`cookie_session_id` return the raw browser-supplied `shopify_app_session` cookie value verbatim as the session id used by the host application to look up a merchant's stored `Session` (and therefore its access token). This value is never cryptographically bound to the session it names: it carries no HMAC, no signature, nothing tying it to the OAuth flow that created it. Because the id format is deterministic and public (`offline_#{shop}` / `#{shop}_#{user_id}`), any party who can influence the cookie jar for the app's origin can present another tenant's session id and have the host app load that tenant's stored access token.

### Finding Description
For the embedded flow, the gem correctly derives the session id from a cryptographically verified artifact: `SessionUtils.session_id_from_shopify_id_token` decodes and HMAC-verifies the JWT via `Auth::JwtPayload.new(id_token)` before trusting the `shop`/`sub` claims that make up the id [1](#0-0) .

For the non-embedded (cookie) path, however, `current_session_id` and `cookie_session_id` simply read `cookies[Auth::Oauth::SessionCookie::SESSION_COOKIE_NAME]` and return it directly, with no verification step at all: [2](#0-1) [3](#0-2) 

The value that ends up in that cookie is `session.id`, set by `Oauth.validate_auth_callback` once OAuth completes: `SessionCookie.new(value: session.id, expires: ...)` [4](#0-3) . `session.id` itself is fully deterministic and derivable from public information — `"#{shop}_#{associated_user.id}"` for online sessions or `"offline_#{shop}"` for offline sessions — as built in `Session.from`: [5](#0-4) 

So the binding the host application relies on is:
`cookie_bytes_presented_by_browser == session_id_that_was_actually_issued_by_this_gem_after_OAuth`

But this gem never checks that equality — it only checks presence (`cookies[...]` non-nil) before handing the raw bytes back as the trusted id: [6](#0-5) . Since the id format is public/predictable and not signed, the cookie value is not proof that the browser ever completed OAuth for that shop — it is simply "unauthenticated bytes" that the host app's session-storage lookup (built directly on top of `current_session_id`) is documented to trust as-is, per this gem's own `getting_started.md` guidance to pass cookies straight into `current_session_id` for session retrieval [7](#0-6) .

### Impact Explanation
Any user of the multi-tenant host application (an "unprivileged" merchant/tenant of their own shop) can compute another shop's offline session id (`"offline_#{victim_shop}"`, where `victim_shop` is public, e.g. `victim-shop.myshopify.com`) and set that value in their own browser's `shopify_app_session` cookie for the app's domain. When the host app calls `SessionUtils.current_session_id` on the next request and uses the result to fetch a persisted `Session` (containing the victim shop's access token) from its session storage, it will serve the attacker the victim's session/access token — a cross-tenant access / session-fixation issue rooted entirely in this gem returning unverified cookie bytes as an authoritative identity claim, in contrast to the properly HMAC-verified JWT path used for embedded apps.

### Likelihood Explanation
Exploitation requires: (1) the target app runs non-embedded and relies on `SessionUtils.current_session_id`/cookie flow as documented, (2) the attacker can write/control the `shopify_app_session` cookie value sent to the app's origin (trivial for the attacker's own browser session, or via subdomain cookie tossing on shared-domain deployments), and (3) the id format is guessable, which it always is (`offline_#{shop}` where `shop` is a public myshopify.com domain). No secret credential is required. This is a realistic, low-effort attack against any app built following the gem's documented usage pattern.

### Recommendation
Do not treat the raw cookie value as a self-authenticating session id. Either (a) sign/HMAC the cookie value with `Context.api_secret_key` when it is set in `validate_auth_callback`, and verify that signature in `SessionUtils.cookie_session_id`/`current_session_id` before returning it, mirroring the verification already done for the JWT path in `JwtPayload`, or (b) use an unpredictable, per-session random token as the cookie value instead of the deterministic `shop`/`offline_#{shop}` id, with the mapping to the real session id kept server-side.

### Proof of Concept
1. Host app "AwesomeApp" is a non-embedded Shopify app using `shopify-api-ruby` and follows the documented pattern: pass `cookies` to `ShopifyAPI::Utils::SessionUtils.current_session_id(nil, cookies, false)` to fetch the offline `Session` from its session storage [6](#0-5) .
2. Victim shop `victim-shop.myshopify.com` has already completed OAuth; its offline session is stored under id `"offline_victim-shop.myshopify.com"` (per `Session.from` / `SessionUtils.offline_session_id`) [5](#0-4) [8](#0-7) .
3. Attacker, in their own browser (or via cookie injection into the app's origin), sets: `shopify_app_session=offline_victim-shop.myshopify.com`.
4. Attacker requests any AwesomeApp endpoint. AwesomeApp calls `current_session_id(nil, cookies, false)`, which returns `"offline_victim-shop.myshopify.com"` verbatim with zero verification [2](#0-1) .
5. AwesomeApp's session storage returns the victim's `Session` object, including its Shopify access token, to the attacker's request context.

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

**File:** lib/shopify_api/auth/session.rb (L107-118)
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

**File:** docs/getting_started.md (L47-53)
```markdown
#### Cookie
Cookie based authentication is not supported for embedded apps due to browsers dropping support for third party cookies due to security concerns. Non-embedded apps are able to use cookies for session storage/retrieval.

For *non-embedded* apps, you can pass the cookies into:
 - `ShopifyAPI::Utils::SessionUtils.current_session_id(nil, cookies, true)` for online (user) sessions or
 - `ShopifyAPI::Utils::SessionUtils.current_session_id(nil, cookies, false)` for offline (store) sessions.

```
