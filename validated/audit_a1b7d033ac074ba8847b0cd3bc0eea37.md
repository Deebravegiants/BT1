Confirmed: `Session.from` (for offline/store tokens) sets `id = "offline_#{shop}"` — a deterministic string derived entirely from the public shop domain, with no random or secret component. This is exactly the pattern the rules flag as "a session id derived from unauthenticated bytes." [1](#0-0) 

However, tracing the actual exploitability: this predictable `session.id` is only ever placed into the browser-facing `SessionCookie` for **non-embedded** apps, after `validate_auth_callback` has already completed a genuine OAuth code exchange with Shopify (using the HMAC-verified `auth_query.shop` and the app's real `client_secret`). For embedded apps, the cookie value is blanked out (`value: ""`) and this cookie path isn't used at all.### Title
Predictable, Unsigned Session Identifier Enables Cross-Tenant Session Hijacking - (lib/shopify_api/auth/session.rb)

### Summary
For non-embedded apps, `ShopifyAPI::Auth::Session.from` derives the session's `id` deterministically from public data — the shop's domain (and, for online tokens, the Shopify user id) — with no random or secret component. This value is placed verbatim into the browser-facing session cookie and is returned unmodified and unauthenticated by `ShopifyAPI::Utils::SessionUtils.current_session_id`/`cookie_session_id`, which the host app uses as the lookup key into its session store. Because the id is fully guessable from a shop's domain alone, an attacker can forge the cookie for a victim shop and have the gem return that shop's session id as if it were authenticated.

### Finding Description
`Session.from` builds the persistent session `id` purely from public identifiers: [1](#0-0) 

For non-embedded apps, `validate_auth_callback` copies this predictable `session.id` directly into the value of the `shopify_app_session` cookie sent to the browser: [2](#0-1) 

`SessionCookie` is a plain struct with no signature or MAC over its `value`: [3](#0-2) 

When the host app later resolves "who is making this request," it calls `SessionUtils.current_session_id`, which — for non-embedded apps, or for embedded apps that fall back to the cookie — returns the raw cookie value with zero validation that it was actually issued by this gem's own OAuth flow: [4](#0-3) [5](#0-4) 

The binding this is supposed to enforce is:
`session_id returned by SessionUtils.current_session_id == session_id genuinely issued to the shop that completed this app's OAuth flow`

Before the attack, only the shop that completed OAuth possesses cookie value `"offline_#{shop}"` (or `"#{shop}_#{user_id}"` for online tokens). After the attack, since that string is 100% derivable from the shop's public `.myshopify.com` domain (and the gem itself provides no HMAC/nonce/secret binding on the cookie), any party who knows a target shop's domain can present the identical cookie value in their own HTTP request to the host app. `current_session_id` returns that forged value unchanged, and — per this gem's own documented integration pattern (`MyApp::SessionRepository.store_session(auth_result[:session])`, looked up by `session.id`) — the host app resolves it to the victim shop's stored `Session`, including its Shopify access token.

### Impact Explanation
This breaks a tenant boundary using only a shop's public domain name — no `api_secret_key`, access token, or privileged account is required. If successfully exploited against a host app following this gem's documented storage/retrieval pattern, it results in cross-tenant session hijacking and exposure of another merchant's stored access token, which maps to the Critical impact category (cross-tenant access / theft of merchant access token).

### Likelihood Explanation
Exploitability depends on: (1) the app running in non-embedded mode (an explicitly supported, documented configuration in this gem, `docs/getting_started.md` "Cookie" section), and (2) the attacker knowing the victim shop's `.myshopify.com` domain, which is generally public/discoverable rather than secret. Given the gem generates the id and cookie value identically for every install, and applies no signing, the "secret" protecting the session boundary is effectively just the browser's cookie same-origin isolation — which does not stop a user from directly crafting/sending their own `Cookie` header value to the app's own domain. This is a moderate-likelihood, high-impact issue rooted entirely in the gem's own id/cookie generation code.

### Recommendation
Do not use a deterministic, guessable string (shop domain, user id) as the literal session cookie value. Either: (a) sign/HMAC the cookie value with `Context.api_secret_key` and verify it in `SessionUtils.cookie_session_id` before treating it as an authenticated session id, or (b) generate a cryptographically random, unguessable token (e.g., `SecureRandom.uuid`, similar to the existing `@id` fallback in `Session#initialize`) to use as the cookie value/session key, decoupled from the predictable `"offline_#{shop}"`/`"#{shop}_#{user_id}"` identifiers used for internal session storage keys.

### Proof of Concept
1. Attacker learns (or guesses) the victim's shop domain, e.g. `victim-shop.myshopify.com` (public information, visible on the storefront, in App Store listings, etc.).
2. Attacker computes the predictable offline session id per `Session.from`: `"offline_victim-shop.myshopify.com"`. [6](#0-5) 
3. Attacker sends a request to the vulnerable non-embedded host app with header `Cookie: shopify_app_session=offline_victim-shop.myshopify.com`.
4. The host app calls `ShopifyAPI::Utils::SessionUtils.current_session_id(nil, cookies, false)`, which returns `"offline_victim-shop.myshopify.com"` verbatim with no validation: [7](#0-6) 
5. The host app looks up its session store (as documented) using this id and returns the victim's stored `ShopifyAPI::Auth::Session`, including the victim's real Shopify access token, to the attacker's request.

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

**File:** lib/shopify_api/auth/oauth/session_cookie.rb (L7-14)
```ruby
      class SessionCookie < T::Struct
        extend T::Sig

        SESSION_COOKIE_NAME = "shopify_app_session"

        const :name, String, default: SESSION_COOKIE_NAME
        const :value, String
        const :expires, T.nilable(Time)
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
