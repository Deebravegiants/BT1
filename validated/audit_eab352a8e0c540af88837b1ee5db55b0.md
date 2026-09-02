This confirms the analog: `docs/getting_started.md` explicitly documents `ShopifyAPI::Utils::SessionUtils.current_session_id(nil, cookies, true/false)` as the officially recommended mechanism for non-embedded apps to resolve a session from the `shopify_app_session` cookie [1](#0-0) , and the cookie's `value` is set directly to `session.id` by `ShopifyAPI::Auth::Oauth.validate_auth_callback` [2](#0-1) .

### Title
Non-embedded session cookie value is the deterministic, guessable session id itself, allowing session fixation/hijacking without completing OAuth - (File: `lib/shopify_api/auth/oauth.rb`, `lib/shopify_api/auth/session.rb`, `lib/shopify_api/utils/session_utils.rb`)

### Summary
For non-embedded apps, this gem sets the browser's `shopify_app_session` cookie value equal to the internal `Session#id`, which is deterministically derived from public data (the shop's domain, and for online sessions the numeric Shopify user id) rather than from a random, unguessable secret. The gem's own documented `SessionUtils.current_session_id`/`cookie_session_id` helper then uses that raw cookie value verbatim as the lookup key for the stored session/access token. This breaks the intended identity binding: *"cookie value" should equal "a secret proof that this browser completed OAuth for this shop"*, but instead *"cookie value" equals "a predictable string derivable from public information"*.

### Finding Description
`ShopifyAPI::Auth::Session.from` sets the session `id` deterministically:
```ruby
id = "#{shop}_#{associated_user.id}"   # online
id = "offline_#{shop}"                 # offline
``` [3](#0-2) 

`Oauth.validate_auth_callback`, for non-embedded apps, builds the browser cookie directly from this id, with no additional random/secret component:
```ruby
cookie = if Context.embedded?
  SessionCookie.new(value: "", expires: Time.now)
else
  SessionCookie.new(value: session.id, expires: session.expires ? session.expires : nil)
end
``` [2](#0-1) 

`SessionUtils.current_session_id` — the gem's documented API for non-embedded apps to resolve "who is calling" from cookies — simply echoes the raw cookie value back as the session id to use for lookup:
```ruby
def cookie_session_id(cookies)
  cookies[Auth::Oauth::SessionCookie::SESSION_COOKIE_NAME]
end
``` [4](#0-3) 

The documentation explicitly instructs consumers to pass raw request cookies into this method to resolve the active session for the request, for both online and offline sessions:
```
For *non-embedded* apps, you can pass the cookies into:
 - `ShopifyAPI::Utils::SessionUtils.current_session_id(nil, cookies, true)` for online (user) sessions or
 - `ShopifyAPI::Utils::SessionUtils.current_session_id(nil, cookies, false)` for offline (store) sessions.
``` [1](#0-0) 

Because the offline session id is exactly `"offline_#{shop}"`, and shop domains (`{store}.myshopify.com`) are public/discoverable (they appear in storefront URLs, marketing links, and are trivially enumerable), any unauthenticated internet user who knows or guesses a target's shop domain can set their own browser's `shopify_app_session` cookie to `offline_target-shop.myshopify.com` and, per the gem's own documented lookup flow, be resolved by the host application to the target shop's stored offline session — without ever presenting a secret or completing any part of the OAuth handshake. For online sessions, the id additionally depends on `associated_user.id`, which is a small sequential Shopify user id, making it brute-forceable as well.

This is the same root-cause pattern as the referenced report's math bug: an identity-binding value (there, the election timestamp; here, the session lookup key) is derived from a field that should be treated as opaque/secret-bound but is instead reconstructible from public, attacker-controllable/knowable inputs, so the equality the system relies on (`cookie value == proof of authenticated session`) can be forged as `cookie value == f(public shop name)`.

### Impact Explanation
This is a session fixation / cross-tenant session hijack: an unprivileged internet user can obtain access to another merchant's session context (and therefore the app's stored access token for that shop) purely by guessing/knowing the shop domain, without any credential, MITM, or privileged access. This matches the Critical impact category — cross-tenant access / authentication bypass — via a defect reachable entirely through this gem's own documented session/cookie API.

### Likelihood Explanation
Likelihood is high for offline sessions: shop domains are routinely public (visible in the merchant's storefront, marketing, or the `shop` field an app itself displays), so no guessing beyond attacker's chosen target is required — the attacker sets a single cookie value. For online sessions, only the numeric `associated_user.id` must be guessed, which is small-integer and enumerable.

### Recommendation
Never expose the internal deterministic `Session#id` as the client-facing cookie value. Instead, generate a separate, cryptographically random, unguessable session token bound server-side to the underlying `Session#id`/access token via a signed or server-held mapping (e.g., a random UUID stored in a session store keyed to the shop/session, or an HMAC-signed cookie whose payload includes an expiry and is verified before trusting the embedded shop/session id). `SessionUtils.cookie_session_id`/`current_session_id` should perform this verification rather than returning the raw cookie value.

### Proof of Concept
1. Attacker learns (or guesses) a target's shop domain, e.g. `victim-shop.myshopify.com` (publicly visible on the merchant's storefront).
2. Attacker sets their own browser cookie: `shopify_app_session=offline_victim-shop.myshopify.com`.
3. Attacker requests any page of the host app that (per this gem's documented pattern) calls:
   ```ruby
   ShopifyAPI::Utils::SessionUtils.current_session_id(nil, cookies, false)
   ```
4. This returns `"offline_victim-shop.myshopify.com"` verbatim [5](#0-4) , which the host app uses to look up the stored `Session`/access token for `victim-shop`, granting the attacker's browser the victim shop's authenticated context.

### Citations

**File:** docs/getting_started.md (L47-53)
```markdown
#### Cookie
Cookie based authentication is not supported for embedded apps due to browsers dropping support for third party cookies due to security concerns. Non-embedded apps are able to use cookies for session storage/retrieval.

For *non-embedded* apps, you can pass the cookies into:
 - `ShopifyAPI::Utils::SessionUtils.current_session_id(nil, cookies, true)` for online (user) sessions or
 - `ShopifyAPI::Utils::SessionUtils.current_session_id(nil, cookies, false)` for offline (store) sessions.

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
