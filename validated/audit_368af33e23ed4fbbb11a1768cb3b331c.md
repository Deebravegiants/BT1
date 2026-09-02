### Title
Session ID for non-embedded apps is a deterministic, guessable value (`offline_{shop}` / `{shop}_{user_id}`) used directly as a bearer session cookie - ([File: lib/shopify_api/auth/session.rb])

### Summary
For non-embedded apps, the gem sets the browser session cookie to the raw value of `Session#id`, and later trusts whatever value arrives in that cookie as the lookup key for the stored session/access token, with no cryptographic binding between the cookie and any secret. Because `Session#id` is generated deterministically from public data (the shop's `myshopify.com` domain, and for online sessions the merchant's numeric staff user id), an attacker who simply knows a shop's domain can construct the exact cookie value used to identify that shop's stored session/access token.

### Finding Description
When completing OAuth for a non-embedded app, `ShopifyAPI::Auth::Oauth.validate_auth_callback` builds the session via `Session.from`, and then sets the cookie value to the session's `id`: [1](#0-0) 

`Session.from` derives that `id` purely from the shop domain (and, for online tokens, the associated user's numeric id) — no random or secret component is used: [2](#0-1) 

Specifically:
- Offline sessions: `id = "offline_#{shop}"` — fully determined by the public shop domain.
- Online sessions: `id = "#{shop}_#{associated_user.id}"` — determined by the shop domain plus the merchant staff user's numeric id, which is not a secret.

Later, when the host app calls back into the gem to resolve the current session from the browser's cookie, the gem does no verification of the cookie value at all — it echoes it back verbatim: [3](#0-2) [4](#0-3) 

The library's own documentation confirms this is the intended, documented flow: the `Session` object (keyed by this predictable `id`) is what host apps are told to persist and later retrieve using `SessionUtils.current_session_id`/`cookie_session_id`: [5](#0-4) 

The identity binding that is broken here is: **session id (the bearer-like value trusted to select a stored access-token session) == unauthenticated, attacker-derivable bytes (shop domain / user id)**, rather than a random secret bound to the actual authenticated browser flow. Nothing in `Session`, `SessionCookie`, or `SessionUtils` HMACs, signs, or otherwise binds the cookie value to the OAuth state/nonce that was actually verified during the callback (`Utils::HmacValidator.validate(auth_query)` only guards the *initial* callback, not subsequent session lookups).

### Impact Explanation
Because the cookie value is not a secret, an unauthenticated attacker who only knows (or guesses) a target shop's `.myshopify.com` domain can set `Cookie: shopify_app_session=offline_{shop}` (or, with a guessable/enumerable staff user id, `{shop}_{user_id}`) on a direct HTTP request to the host application. If the host follows the gem's documented pattern (store/retrieve `Session` by `id`, as shown in `docs/getting_started.md` and `BREAKING_CHANGES_FOR_V16.md`'s reference implementation), this results in the host resolving and using the victim merchant's stored access token to serve the attacker's request — i.e., cross-tenant access and effective theft/misuse of the merchant's access token, without the attacker ever completing OAuth or possessing any secret.

### Likelihood Explanation
Shop domains are effectively public (visible in storefront URLs, app listing installs, etc.), and offline session ids require only the shop domain — no other secret. This makes the offline-session case trivially exploitable by any unprivileged internet user against apps built on this gem's documented non-embedded cookie flow.

### Recommendation
Do not use a deterministic, publicly-derivable string as the bearer session cookie value. Generate a cryptographically random session identifier (e.g., `SecureRandom.uuid`/`SecureRandom.hex`) for the cookie itself, and keep the deterministic `shop`/`user`-derived id purely as an internal lookup key that is never exposed to the browser unsigned. Alternatively, HMAC-sign the cookie value (bound to a per-install secret) so that `SessionUtils.cookie_session_id` can validate authenticity before trusting it as a lookup key.

### Proof of Concept
1. App completes OAuth (offline, non-embedded) for `victim-shop.myshopify.com`; per `lib/shopify_api/auth/session.rb` L107-140 and `lib/shopify_api/auth/oauth.rb` L100-112, the session cookie set in the victim's browser is `shopify_app_session=offline_victim-shop.myshopify.com`.
2. Attacker, without ever visiting the app or completing OAuth, sends a request to the host app with header `Cookie: shopify_app_session=offline_victim-shop.myshopify.com`.
3. Host app calls `ShopifyAPI::Utils::SessionUtils.current_session_id(nil, cookies, false)`, which returns the cookie value unmodified (`lib/shopify_api/utils/session_utils.rb` L19-37, L68-71).
4. Host app looks up the stored `Session` by that id (per the gem's documented pattern) and finds the victim's session/access token, then performs an authenticated Shopify Admin API call on the attacker's behalf using the victim's access token.

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

**File:** docs/getting_started.md (L47-52)
```markdown
#### Cookie
Cookie based authentication is not supported for embedded apps due to browsers dropping support for third party cookies due to security concerns. Non-embedded apps are able to use cookies for session storage/retrieval.

For *non-embedded* apps, you can pass the cookies into:
 - `ShopifyAPI::Utils::SessionUtils.current_session_id(nil, cookies, true)` for online (user) sessions or
 - `ShopifyAPI::Utils::SessionUtils.current_session_id(nil, cookies, false)` for offline (store) sessions.
```
