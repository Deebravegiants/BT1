### Title
Predictable, Unsigned Session ID Used as Session Cookie Enables Cross-Tenant Session Hijacking - (File: `lib/shopify_api/auth/oauth.rb`, `lib/shopify_api/auth/session.rb`, `lib/shopify_api/utils/session_utils.rb`)

### Summary
For the non-embedded (cookie-based) OAuth flow, `ShopifyAPI::Auth::Oauth.validate_auth_callback` sets the session cookie's value to the plain `Session#id`, and that ID is a deterministic string (`"#{shop}_#{associated_user_id}"` or `"offline_#{shop}"`) rather than a random, unguessable token. `ShopifyAPI::Utils::SessionUtils.cookie_session_id` later hands this raw, unauthenticated cookie value straight back to the host app as the session lookup key, with no signature or binding check. Because the identifier is guessable from public information (the shop's `myshopify.com` domain, and often enumerable user IDs), an attacker can forge this cookie value themselves and, if the host app resolves sessions by this ID (the documented usage pattern), be handed another merchant's stored session — including its real access token.

### Finding Description
The binding that should hold is:

`session_cookie_value (attacker-controlled bytes) == cryptographically-unguessable_session_identifier`

but the gem instead produces:

`session_cookie_value == f(shop, associated_user_id)` (deterministic, no secret involved)

Trace of the root cause:

1. `Session.from` computes the session `id` deterministically from public/guessable inputs: [1](#0-0) 

For online sessions the ID is `"#{shop}_#{associated_user.id}"`; for offline sessions it is `"offline_#{shop}"`. Neither `shop` nor a merchant's `associated_user.id` is a secret — the shop domain is the store's own public `myshopify.com` domain, and Shopify user IDs are small sequential integers that are easy to enumerate/guess.

2. `Oauth.validate_auth_callback` uses this deterministic `session.id` directly as the value stored in the browser cookie for non-embedded apps: [2](#0-1) 

3. `SessionUtils.cookie_session_id` and `current_session_id` take that cookie value and return it verbatim as "the" session identifier for the app to use, without any cryptographic check that it was actually issued by the server to this browser: [3](#0-2) [4](#0-3) 

4. The documentation confirms the intended usage: the app is expected to persist the `Session` object keyed by `session.id`, and to look sessions up later by an identifier derived from the request/cookie: [5](#0-4) [6](#0-5) 

Since the identifier that gates access to a stored `Session` (containing the real `access_token`) is fully computable by anyone who knows a target shop's domain (and, for online sessions, the associated user's numeric ID), an unprivileged attacker can construct the exact same string and present it as their own session cookie. There is no HMAC, signature, or server-side secret binding the cookie value to the browser/user that originally completed OAuth — unlike the `AuthQuery`/webhook flows, which are protected by `Utils::HmacValidator` (`lib/shopify_api/utils/hmac_validator.rb`), the cookie-derived session ID undergoes no such verification.

This is the same class of bug as the ApeCoin report's "split pair" issue: an identity/ownership binding that the protocol assumes is exclusive (BAYC owner ⇔ recipient of unstaked APE) actually is not exclusive/unguessable, and a second party can supply the missing piece cheaply to redirect value/access intended for someone else. Here, the assumed binding "possession of this cookie value ⇔ having completed OAuth for that shop/user" fails because the value itself is a public function of public/guessable inputs, not a secret proof of that event.

### Impact Explanation
If a host application follows the gem's documented pattern (store `Session` keyed by `session.id`, and resolve the current session from the cookie value returned by `SessionUtils`), an attacker who knows or guesses a victim shop's domain can retrieve that shop's persisted `Session`, including its live `access_token`. This is cross-tenant access to another merchant's data and credentials, satisfying the Critical impact bar ("cross-tenant access", "theft ... of a merchant access token").

### Likelihood Explanation
The shop domain is not secret (it's the store's own `*.myshopify.com` address, frequently visible in URLs, app listings, and support requests), and for online sessions the associated user ID is a small, easily enumerable integer. No XSS, MITM, or credential theft is required — the attacker only needs to control the cookie value sent in their own request, which is trivial (e.g. via browser dev tools or a raw HTTP client), regardless of `HttpOnly`/`Secure` flags, since those flags only prevent script-based reads, not the attacker setting a cookie value in requests they themselves send.

### Recommendation
Do not use a deterministic, publicly-derivable string as the sole session cookie value/lookup key. Generate a cryptographically random session token (e.g., `SecureRandom.uuid`/`SecureRandom.hex`) to store in the cookie, and keep the deterministic `shop_userid`/`offline_shop` string purely as an internal storage key that is never trusted as coming from the client. Alternatively, sign/HMAC the cookie value (similar to `Utils::HmacValidator`) so that `SessionUtils` can verify the value actually originated from the server before treating it as a trusted session identifier.

### Proof of Concept
1. Note (or guess) a target shop's domain, e.g. `victim-shop.myshopify.com`, which is public information.
2. Compute the deterministic offline session ID the gem would have generated after that shop completed OAuth: `"offline_victim-shop.myshopify.com"` (per `lib/shopify_api/auth/session.rb:116`).
3. Send a request to the vulnerable host app with the `SESSION_COOKIE_NAME` cookie set to that forged value.
4. `SessionUtils.current_session_id` / `cookie_session_id` returns the forged value unchanged (`lib/shopify_api/utils/session_utils.rb:68-71`) and the host app's `SessionRepository` (built per the gem's documented pattern) looks up and returns the victim shop's real, persisted `Session`, including its `access_token`.
5. The attacker's subsequent API calls execute against the victim shop using the victim's access token.

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

**File:** docs/usage/oauth.md (L21-25)
```markdown
## Session Persistence
Session persistence is deprecated from the `ShopifyAPI` library gem since [version 12.3.0](https://github.com/Shopify/shopify-api-ruby/blob/main/CHANGELOG.md#version-1230). The responsibility of session storage typically is fulfilled by the web framework middleware.
This API library's focus is on making requests and facilitate session creation.

⚠️ If you're not using the [ShopifyApp](https://github.com/Shopify/shopify_app) gem, you may use ShopifyAPI to perform OAuth to create sessions, but you must implement your own session storage method to persist the session information to be used in authenticated API calls.
```

**File:** docs/usage/oauth.md (L230-237)
```markdown
##### Example
Your app should call `validate_auth_callback` to construct the `Session` object and cookie that will be used later for authenticated API requests.

1. Call `validate_auth_callback` to construct `Session` and `SessionCookie`.
2. Update browser cookies with the new value for the session.
3. Store the `Session` object to be used later when [making authenticated API calls](#using-oauth-session-to-make-authenticated-api-calls).
   - See [Make a GraphQL API call](https://github.com/Shopify/shopify-api-ruby/blob/main/docs/usage/graphql.md), or
   [Make a REST API call](https://github.com/Shopify/shopify-api-ruby/blob/main/docs/usage/rest.md) for examples on how to use the result `Session` object.
```
