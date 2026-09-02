## Finding

### Title
Predictable, unsigned session-cookie identifier enables cross-tenant session takeover in non-embedded OAuth flow - (File: `lib/shopify_api/auth/oauth.rb`)

### Summary
For non-embedded apps, `ShopifyAPI::Auth::Oauth.validate_auth_callback` sets the browser session cookie's value to the raw `Session#id`, which is deterministically derived from the public shop domain (and, for online sessions, the associated user id) rather than from a secret or HMAC-bound value. `ShopifyAPI::Utils::SessionUtils.cookie_session_id`/`current_session_id` then hands this raw, unverified cookie value straight back to the host application as the authoritative "session id" to use for session-store lookup, with no cryptographic binding proving the browser ever completed OAuth for that shop.

### Finding Description
In the non-embedded branch of `validate_auth_callback`, the cookie value is set to `session.id`: [1](#0-0) 

That id is computed deterministically in `Session.from`: [2](#0-1) 

For offline sessions the id is simply `"offline_#{shop}"`, and for online sessions it's `"#{shop}_#{associated_user.id}"` — both derivable from public/guessable data (the shop's `.myshopify.com` domain, and a small/enumerable numeric user id), with no HMAC, signature, or nonce.

On subsequent requests, the gem's own helper extracts this cookie value and returns it *as the session id to use for lookup*, performing no verification whatsoever: [3](#0-2) [4](#0-3) 

This is precisely the documented API contract (`docs/getting_started.md` instructs non-embedded apps to pass raw cookies into `current_session_id`, and `docs/usage/oauth.md` shows storing/retrieving `Session` objects keyed by this id/shop). The equality the library implicitly relies on is:

`cookie_value (attacker-settable, unauthenticated bytes) == session_id (used as the key to retrieve the shop's access_token from the host's session store)`

Unlike the embedded/JWT path — where `session_id_from_shopify_id_token` derives the id only from a claim inside a JWT verified against `Context.api_secret_key` (`lib/shopify_api/auth/jwt_payload.rb`, lines 76-81) — the non-embedded cookie path has no equivalent secret binding. Anyone who knows or guesses a target shop's domain can set `shopify_app_session=offline_target-shop.myshopify.com` in their own browser and have the host application treat them as that shop, because the library-provided lookup key is exactly reproducible from public information.

### Impact Explanation
An unprivileged internet user who knows (or guesses) a victim merchant's `*.myshopify.com` domain can, without ever completing OAuth or possessing any secret, set the `shopify_app_session` cookie themselves and cause `ShopifyAPI::Utils::SessionUtils.current_session_id` to return the victim's exact session id. If the host app follows the gem's documented pattern of using this id to retrieve the stored `Session` (and its `access_token`), the attacker obtains cross-tenant access to another merchant's Admin API data using the merchant's real access token — matching the "Critical - cross-tenant access / theft of a merchant access token" and "High - session fixation" categories.

### Likelihood Explanation
Likelihood is high for non-embedded integrations that follow the gem's documented cookie usage: the attacker needs no credentials, no network position, and no social engineering — only the target's shop domain, which is frequently public (store front URL, app-install redirect, marketing material) or straightforward to enumerate for small shop-name spaces.

### Recommendation
Do not use `Session#id` (or any value derivable purely from the shop domain/user id) as the session cookie's value. Instead, generate a cryptographically random, unguessable session identifier at OAuth completion, store the mapping `random_id -> Session` server-side, and set that random id as the cookie value returned to the browser, so that `cookie_session_id`/`current_session_id` can no longer be trivially forged by any client that knows a shop's domain.

### Proof of Concept
1. Victim shop `victim-shop.myshopify.com` completes non-embedded OAuth; the app sets cookie `shopify_app_session=offline_victim-shop.myshopify.com` (per `lib/shopify_api/auth/oauth.rb:106-109`) and stores the `Session` (with `access_token`) keyed by that same id.
2. Attacker, who only knows the shop domain, opens the target app in their own browser and manually sets the cookie `shopify_app_session=offline_victim-shop.myshopify.com`.
3. On any subsequent request, the app calls `ShopifyAPI::Utils::SessionUtils.current_session_id(nil, cookies, false)`, which returns `"offline_victim-shop.myshopify.com"` verbatim (`lib/shopify_api/utils/session_utils.rb:19-37,68-71`) with no cryptographic check.
4. The host app looks up the `Session` by that id (as documented) and uses the victim's real `access_token` to serve the attacker's request — granting the attacker cross-tenant access to the victim's store data.

### Citations

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
