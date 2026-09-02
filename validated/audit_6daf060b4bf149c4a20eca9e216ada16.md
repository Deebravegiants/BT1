### Title
Non-embedded OAuth session cookie stores a predictable, shop-derived session ID that is used directly as the session-lookup key without any cryptographic binding - (File: `lib/shopify_api/auth/oauth.rb`, `lib/shopify_api/auth/session.rb`, `lib/shopify_api/utils/session_utils.rb`)

### Summary
For non-embedded apps, `ShopifyAPI::Auth::Oauth.validate_auth_callback` sets the browser session cookie's value to the raw `Session#id`, and `SessionUtils.current_session_id` later trusts that same raw cookie value verbatim as the key used to fetch the stored session/access-token. The offline session ID is deterministically derived as `"offline_#{shop}"` from the (public) shop domain, with no HMAC, signature, or other secret binding it to a completed OAuth flow.

### Finding Description
`Session.from` computes the session identifier purely from public information: [1](#0-0) 

For offline sessions this is `"offline_#{shop}"`; for online sessions it is `"#{shop}_#{associated_user.id}"` — both values an unprivileged internet user can trivially construct once they know (or guess) the target merchant's `*.myshopify.com` domain, which is not secret.

`validate_auth_callback` then puts this exact, unsigned value into the cookie that is handed back to the caller to be set in the browser: [2](#0-1) 

The documented integration pattern shows this cookie being set as a plain (non-signed) cookie: [3](#0-2) 

On subsequent requests, the cookie is read back and used **directly** as the session-lookup key with no re-validation: [4](#0-3) 

and it feeds `current_session_id`, which is the identifier host applications use to retrieve the stored `Session` (including its `access_token`) from their session storage: [5](#0-4) 

The identity binding that should hold is:
`session_id presented by the client == session_id only obtainable by completing the HMAC-validated OAuth callback (`Utils::HmacValidator.validate(auth_query)` in `lib/shopify_api/auth/oauth.rb:64`)`.

That equality does not hold here: the offline session id is a pure function of a public string (the shop domain) with no secret material, so any unprivileged party can compute it without ever passing HMAC validation or possessing a `client_secret`. The gem performs no additional check (e.g., re-signing the cookie, or binding it to a nonce established during `begin_auth`) before this value is used as the trust anchor for session retrieval by `SessionUtils`.

### Impact Explanation
This is a session-fixation / forced-session-adoption class of issue explicitly listed as in-scope (“session fixation or forced OAuth completion”): an attacker who knows a merchant's shop domain can pre-set (or induce the victim/app to use) the value `"offline_#{shop}"` as their own session cookie. If the host application's session storage already contains a real session for that ID (created once during the legitimate merchant's install), the attacker's browser will be handed the merchant's stored `access_token` by the application logic that trusts `SessionUtils.current_session_id`'s output, resulting in cross-tenant access to another shop's authenticated session — without ever completing HMAC-validated OAuth or possessing any secret.

### Likelihood Explanation
The shop domain is not secret (often visible in URLs, app listings, or via enumeration of `*.myshopify.com`), and the derivation formula (`"offline_#{shop}"` / `"#{shop}_#{user_id}"`) is public in this gem's source. The only mitigating factor is the host application's own cookie-jar implementation (e.g., Rails' `cookies.signed`) — but this gem's own code and documented example do not require or enforce that, and the value that must be protected (the session id) is generated and consumed entirely within this gem's `Session`, `Oauth`, and `SessionUtils` classes.

### Recommendation
Do not use a shop-derived, guessable value as the bearer session identifier stored in a client-visible cookie. Instead:
- Bind the browser-stored session cookie value to a high-entropy, unpredictable secret (e.g., a random session token) rather than `Session#id` itself, and store the mapping from that secret to the underlying `Session` server-side.
- If `Session#id` must remain deterministic for storage-key purposes, sign/HMAC the value placed in the cookie (similar to the existing `Utils::HmacValidator` pattern already used for the OAuth callback) and verify that signature in `SessionUtils.cookie_session_id` before trusting it.
- Explicitly document that host applications must use tamper-proof (signed/encrypted) cookies for `ShopifyAPI::Auth::Oauth::SessionCookie`, and consider enforcing this by exposing a signed-cookie helper from the gem itself instead of a plain `SessionCookie` value/expiry pair.

### Proof of Concept
1. Attacker learns the target merchant's shop domain, `target-shop.myshopify.com` (public/discoverable).
2. Attacker computes the offline session id exactly as `Session.from` would: `"offline_target-shop.myshopify.com"` (`lib/shopify_api/auth/session.rb:116`).
3. Attacker sets this value as their own `shopify_app_session` cookie (per the documented pattern in `docs/usage/oauth.md:188-193`, which uses a plain, unsigned cookie) and visits the app.
4. The app calls `SessionUtils.current_session_id(nil, cookies, false)` → `cookie_session_id(cookies)` (`lib/shopify_api/utils/session_utils.rb:35,69-71`), which returns the attacker-supplied value unchanged.
5. The host application looks up its session storage using this id and, if the real merchant previously completed OAuth (so a session already exists under that same predictable key), returns that `Session` object — including its `access_token` — to the attacker's request context, with no HMAC/JWT/signature check ever performed on the impersonated id.

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

**File:** docs/usage/oauth.md (L181-199)
```markdown
  def login
    shop = request.headers["Shop"]

    # Builds the authorization URL route to redirect the user to
    auth_response = ShopifyAPI::Auth::Oauth.begin_auth(shop: domain, redirect_path: "/auth/callback")

    # Store the authorization cookie
    cookies[auth_response[:cookie].name] = {
      expires: auth_response[:cookie].expires,
      secure: true,
      http_only: true,
      value: auth_response[:cookie].value
    }

    # Redirect the user to "auth_response[:auth_route]" to allow user to grant the app permission
    # This will lead the user to the Shopify Authorization page
    head 307
    response.set_header("Location", auth_response[:auth_route])
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
