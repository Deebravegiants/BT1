### Title
Session identifier for non-embedded apps is an unauthenticated, deterministic value that is trusted as a proof of authentication - ([File: lib/shopify_api/auth/oauth.rb], [File: lib/shopify_api/utils/session_utils.rb])

### Summary
For non-embedded (and non-App-Bridge-JWT) OAuth flows, this gem sets a `session.id` cookie value that is a deterministic string derived only from public information (`offline_#{shop}` or `#{shop}_#{associated_user_id}`), and later hands this raw, unsigned cookie value straight back to the calling app as the "session id" via `ShopifyAPI::Utils::SessionUtils.current_session_id`. No HMAC, signature, or secret protects this value.

### Finding Description
When `validate_auth_callback` completes OAuth for a non-embedded app, the cookie value that is meant to identify the session is set to the session's `id`: [1](#0-0) 

That `id` is not a random secret; for offline sessions it is always `"offline_#{shop}"`, and for online sessions it is `"#{shop}_#{associated_user.id}"` — both fully derivable from public information (the shop's `myshopify.com` domain, and in the online case a user id that is often also easy to enumerate): [2](#0-1) 

Later, when the app wants to identify "the current session" for a request, the gem's own utility reads this value directly out of the cookie header with no verification whatsoever that it was actually issued by the server for this browser/user: [3](#0-2) [4](#0-3) 

Compare this to the embedded/JWT path, where the "session id" is derived from a value (`payload.sub`) that is cryptographically bound inside a Shopify-signed JWT (`JwtPayload`), so it cannot be forged without the shared secret. The cookie-derived path has no equivalent binding — `cookie_session_id` simply echoes back whatever bytes the client sent in the `shopify_app_session` cookie.

This is the "session id derived from unauthenticated bytes" pattern: the gem's documented contract is that the app should treat the value returned by `current_session_id`/`cookie_session_id` as a trustworthy key to fetch a stored `Session` (with a live access token) from the app's session repository. But nothing ties that returned id to proof that the requester actually completed OAuth as that shop/user — the id is guessable and self-consistent, so an attacker can fabricate it outright.

### Impact Explanation
Because `offline_#{shop}` (and the online variant) are the only two ID formats the gem ever generates, and `shop` is simply the merchant's `*.myshopify.com` domain (public, often guessable/enumerable), an attacker who merely knows or guesses a target shop's domain can set the cookie `shopify_app_session=offline_targetshop.myshopify.com` on their own request to the app. If the app follows the gem's documented pattern (`SessionRepository.retrieve_session_for_shop`/`by_id` keyed on `current_session_id`), the attacker's request resolves to the victim shop's stored `Session`, which contains the real Admin API access token for that tenant. This is a cross-tenant authentication bypass: no credential, cookie theft, or secret is required — only knowledge of the shop's domain name, which this gem's own docs (`docs/usage/oauth.md`) show being passed around in plaintext query/header parameters (`shop = request.headers["Shop"]`). This satisfies the Critical impact bar of cross-tenant access / authentication bypass.

### Likelihood Explanation
High. No secret material, brute-forcing, or race condition is required — only the target's `myshopify.com` domain, which app installation flows and public storefront URLs routinely expose. The vulnerable code path (`validate_auth_callback` cookie assignment plus `SessionUtils.current_session_id`/`cookie_session_id`) is the officially documented mechanism for non-embedded session identification in this gem, so any app that follows the docs as written inherits the flaw — it is not the result of the host app deviating from documented usage.

### Recommendation
Do not use a deterministic, publicly-derivable value as the session cookie/session-id. Instead:
- Generate a cryptographically random, unguessable session identifier (e.g., `SecureRandom.uuid`, already available and used elsewhere in the codebase) and store the mapping `random_id -> Session` internally, or
- Sign/HMAC the cookie value (similar to `HmacValidator`) so that `cookie_session_id` can verify integrity/authenticity before returning it, rejecting any cookie value that doesn't carry a valid signature produced with `Context.api_secret_key`.
- At minimum, document prominently that `session.id`/`cookie_session_id` must never be used directly as a trusted session lookup key without an additional binding (e.g., signed cookie) — but the safer fix is in the gem itself, since it currently manufactures and hands back the exact deterministic ID that becomes the attack payload.

### Proof of Concept
1. App using this gem completes OAuth for `victim-shop.myshopify.com` (a normal legitimate install). Per `Oauth.validate_auth_callback`, the app sets cookie `shopify_app_session = "offline_victim-shop.myshopify.com"` in the victim merchant's browser and stores a `Session` with that same `id` and the real access token in its session repository (per the documented pattern in `docs/usage/oauth.md`).
2. Attacker, without any access to the victim's browser or cookies, sends their own HTTP request to the app with header `Cookie: shopify_app_session=offline_victim-shop.myshopify.com`.
3. The app calls `ShopifyAPI::Utils::SessionUtils.current_session_id(nil, request.cookies, false)`, which returns `"offline_victim-shop.myshopify.com"` straight from the attacker-supplied cookie value: [5](#0-4) 
4. The app looks up `SessionRepository.retrieve_session_by_id("offline_victim-shop.myshopify.com")`, retrieves the victim's real `Session` (with the live Admin API access token), and proceeds to serve the attacker's request as if it were an authenticated request from `victim-shop`.
5. No secret, cookie theft, or brute force was needed — only the ability to compute `"offline_#{shop}"` for a known shop domain.

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

**File:** lib/shopify_api/auth/session.rb (L107-140)
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

          if access_token_response.refresh_token_expires_in
            refresh_token_expires = Time.now + access_token_response.refresh_token_expires_in.to_i
          end

          new(
            id: id,
            shop: shop,
            access_token: access_token_response.access_token,
            scope: access_token_response.scope,
            is_online: is_online,
            associated_user_scope: associated_user_scope,
            associated_user: associated_user,
            expires: expires,
            shopify_session_id: access_token_response.session,
            refresh_token: access_token_response.refresh_token,
            refresh_token_expires: refresh_token_expires,
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

**File:** lib/shopify_api/utils/session_utils.rb (L68-71)
```ruby
        sig { params(cookies: T::Hash[String, String]).returns(T.nilable(String)) }
        def cookie_session_id(cookies)
          cookies[Auth::Oauth::SessionCookie::SESSION_COOKIE_NAME]
        end
```
