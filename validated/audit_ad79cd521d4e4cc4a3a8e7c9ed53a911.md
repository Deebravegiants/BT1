### Title
Session cookie value is a predictable, unsigned session identifier, enabling session fixation and cross-tenant session hijacking - (File: `lib/shopify_api/auth/oauth/session_cookie.rb`, `lib/shopify_api/auth/oauth.rb`, `lib/shopify_api/utils/session_utils.rb`)

### Summary
For non-embedded apps, this gem sets the `shopify_app_session` cookie to the raw, unsigned `session.id` value, and later trusts whatever value a client presents in that cookie as the session lookup key. Offline session ids are computed deterministically as `"offline_#{shop}"` from the public shop domain, and online session ids as `"#{shop}_#{associated_user.id}"`. Because neither the cookie nor the id itself carries any HMAC/signature tying it to a completed OAuth exchange, an attacker who merely knows (or guesses) a target shop's domain can construct the exact session id string and present it as their own cookie value, without ever completing OAuth for that shop.

### Finding Description
In `ShopifyAPI::Auth::Oauth.validate_auth_callback`, after HMAC-validating the OAuth query and exchanging the code for an access token, the gem builds the response cookie directly from the session id: [1](#0-0) 

`SessionCookie` itself is a plain struct holding only `name`, `value`, `expires` — no signature or MAC field exists to bind `value` to anything: [2](#0-1) 

The session id placed in that cookie is fully deterministic and derivable from public information (the shop's `myshopify.com` domain, and for online sessions the staff user id): [3](#0-2) 

On subsequent requests, `SessionUtils.current_session_id` retrieves this identifier straight from the incoming cookie header with no cryptographic verification at all — it is returned verbatim and used by the host application as the key to fetch the stored `Session` (and its access token): [4](#0-3) [5](#0-4) 

This breaks the identity binding: `client-presented session id == id of a shop that legitimately completed OAuth` is verified only by string equality against a guessable, unsigned value — never by proof that the presenter actually completed the HMAC-validated OAuth callback (`Utils::HmacValidator.validate(auth_query)` in `oauth.rb` line 64 only protects the *authorization callback*, not the cookie that is issued afterward and reused on every later request).

### Impact Explanation
This is a session fixation / cross-tenant impersonation primitive scoped to Critical (cross-tenant access): any unprivileged internet user who knows a target merchant's `*.myshopify.com` domain (always public) can compute `"offline_#{shop}"` and set it as their `shopify_app_session` cookie value. If the host application's session store (which is exactly what this gem's `SessionUtils.current_session_id` is designed to feed) returns the real stored `Session` object for that id, the attacker's browser is now treated as an authenticated request for the victim's shop and its offline access token is used on the attacker's behalf — a direct cross-tenant access / token misuse condition, entirely due to this gem issuing and trusting an unsigned, predictable identifier as the sole session-binding artifact.

### Likelihood Explanation
Medium-High: exploitation requires no secret material — only the target's public shop domain (or, for online sessions, an easily enumerable small staff-user id, often exposed in the merchant admin UI). The attack surface is the gem's own documented non-embedded cookie/session mechanism (`docs/usage/oauth.md` references the same `SessionCookie` flow), so any app built with the standard non-embedded flow this gem provides is affected unless the host wraps the cookie in its own signing layer — something the gem does not do or document as mandatory.

### Recommendation
Do not use the raw, deterministic `session.id` as the cookie value. Instead, sign the cookie contents (e.g., HMAC the session id with `Context.api_secret_key`, or use a cryptographically random opaque token that is separately mapped to the session id server-side) so that possessing/guessing the shop domain or user id is insufficient to produce a valid cookie value. Reject cookies whose signature does not verify before using their value as a session lookup key in `SessionUtils.cookie_session_id`.

### Proof of Concept
1. Merchant installs the app in non-embedded mode; the gem returns `SessionCookie.new(value: "offline_victim-shop.myshopify.com", ...)` as shown in `oauth.rb` lines 106-109.
2. Attacker (unrelated, unauthenticated user) learns `victim-shop.myshopify.com` is a customer of the app (public knowledge, e.g. via the shop's storefront).
3. Attacker sends a request to the app with `Cookie: shopify_app_session=offline_victim-shop.myshopify.com`.
4. The app calls `ShopifyAPI::Utils::SessionUtils.current_session_id(nil, cookies, false)`, which returns `cookie_session_id(cookies)` verbatim — line `lib/shopify_api/utils/session_utils.rb:68-71` — with no signature check.
5. The host app looks up the stored `Session` for that id and uses its access token on the attacker's request, granting the attacker the victim shop's authenticated context.

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

**File:** lib/shopify_api/auth/session.rb (L107-120)
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
