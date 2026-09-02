### Title
Unvalidated `shop` parameter in `Oauth.begin_auth` allows forced OAuth completion / session fixation to an attacker-chosen shop - (File: `lib/shopify_api/auth/oauth.rb`)

### Summary
`ShopifyAPI::Auth::Oauth.begin_auth` builds the OAuth "authorize" redirect target directly from the caller-supplied `shop:` argument with no format validation, unlike every other flow in this gem that accepts a `shop` string (`RefreshToken`, `ClientCredentials`, `TokenExchange.migrate_to_expiring_token`), which all call `Utils::ShopValidator.sanitize!` before using it. Because the authorize destination is attacker-controllable, an attacker can make the app redirect a victim to an OAuth authorize page of the attacker's choosing while the app has already bound a `state` nonce to the victim's browser cookie. `validate_auth_callback` only checks that the returning `state` equals the cookie value and that the whole callback payload has a valid HMAC — it never re-checks that the `shop` completing the callback is the same `shop` the flow was started for.

### Finding Description
`begin_auth` in [1](#0-0)  takes `shop:` as-is and passes it into `auth_base_uri(shop)`: [2](#0-1) 

There is no call to `Utils::ShopValidator.sanitize!` here, even though that helper exists specifically to restrict shop values to `TRUSTED_SHOPIFY_DOMAINS` and is already used in the sibling flows: [3](#0-2) [4](#0-3) [5](#0-4) [6](#0-5) 

The docs for `begin_auth` describe `shop` as a value the host application collects from the merchant/installer to start OAuth, i.e. it originates from an unauthenticated internet user hitting the app's "login" route. Because it is not validated as a genuine `*.myshopify.com` domain, an attacker can pass any hostname, causing the app to redirect the victim's browser to `https://<attacker-host>/admin/oauth/authorize?client_id=...&redirect_uri=<real-app-callback>&state=<nonce>&...`. The `state` cookie set for the victim's browser is: [7](#0-6) 

The attacker's server (masquerading as the OAuth authorization endpoint for the attacker-chosen "shop") can read this `state` value straight out of the query string it receives, then redirect the still-cookied victim browser to the real app's own callback URL, substituting a `code`/`shop`/`hmac`/`timestamp` set that the attacker legitimately obtained from Shopify for a *real* shop they control (e.g. their own dev/partner store). The app's callback handler only verifies: [8](#0-7) 

Both checks pass: the HMAC is valid because it was genuinely produced by Shopify for the attacker's own shop, and `state` matches because the attacker relayed the exact value bound to the victim's cookie. `validate_auth_callback` then proceeds to build a `Session` keyed to `auth_query.shop` — the attacker's shop — and stores/sets a cookie for it: [9](#0-8) 

Nothing in this method compares `auth_query.shop` against the `shop` that `begin_auth` was originally invoked with, so the binding "shop the flow was started for" == "shop the flow completes for" is never enforced.

### Impact Explanation
This lets an unprivileged attacker force a victim's browser (and any host-app session/cookie state built on top of the returned `Session`/`SessionCookie`) to become associated with a shop of the attacker's choosing rather than the shop the merchant actually intended to install/connect — a session-fixation / forced-OAuth-completion outcome, explicitly one of the accepted High-impact categories for this scan. Depending on how the host application wires `SessionRepository.store_session` and subsequent authorization checks, this can lead the victim to unknowingly interact with, or have their in-app identity bound to, an attacker-controlled shop/tenant.

### Likelihood Explanation
The attacker only needs: (1) the ability to send the victim a crafted link to the app's own OAuth-start route with a `shop` query parameter under their control (a very common, documented entry point for merchant-initiated installs), and (2) a real Shopify store of their own to legitimately generate a valid `code`/`hmac` pair. No access token, `client_secret`, or privileged credential is required from the app being attacked — the app's `client_secret` is never sent to the attacker's server (it is only POSTed by `validate_auth_callback` to the HMAC-verified `auth_query.shop`, which in this scenario is the attacker's own genuine `myshopify.com` domain). The gap is purely the missing shop-format validation at `begin_auth` time and the missing shop-continuity check at callback time.

### Recommendation
- Validate `shop:` in `Oauth.begin_auth` with `Utils::ShopValidator.sanitize!` (the same helper already used by `RefreshToken`, `ClientCredentials`, and `TokenExchange.migrate_to_expiring_token`) before constructing `auth_route`, rejecting non-`myshopify.com`-family hosts.
- In `Oauth.validate_auth_callback`, additionally bind the `state`/session cookie to the specific `shop` the flow was started for (e.g., store the shop alongside the nonce in the cookie/session and assert `auth_query.shop` matches it), so a callback for a different (even legitimately signed) shop cannot be substituted.

### Proof of Concept
1. Victim clicks attacker's link: `https://realapp.example.com/login?shop=attacker-fake.example.com`.
2. `begin_auth(shop: "attacker-fake.example.com", ...)` sets a `state` cookie on the victim's browser and redirects to `https://attacker-fake.example.com/admin/oauth/authorize?client_id=...&redirect_uri=https://realapp.example.com/callback&state=NONCE123`.
3. Attacker's server (running at `attacker-fake.example.com`) reads `state=NONCE123` from the request, then 302-redirects the victim's browser to `https://realapp.example.com/callback?shop=attacker-real-shop.myshopify.com&code=VALID_CODE&timestamp=...&state=NONCE123&hmac=VALID_HMAC`, where `code`/`hmac` were obtained by the attacker performing a genuine OAuth authorize flow for their own real store beforehand.
4. `validate_auth_callback` checks `Utils::HmacValidator.validate(auth_query)` (passes, real Shopify-signed values) and `state == auth_query.state` (passes, victim's cookie carries `NONCE123`), then creates/stores a `Session` for `attacker-real-shop.myshopify.com` and sets the resulting session cookie in the victim's browser — completing OAuth for a shop the victim never chose.

### Citations

**File:** lib/shopify_api/auth/oauth.rb (L22-52)
```ruby
        def begin_auth(shop:, redirect_path:, is_online: true, scope_override: nil)
          scope = if scope_override.nil?
            ShopifyAPI::Context.scope
          elsif scope_override.is_a?(ShopifyAPI::Auth::AuthScopes)
            scope_override
          else
            ShopifyAPI::Auth::AuthScopes.new(scope_override)
          end

          unless Context.setup?
            raise Errors::ContextNotSetupError, "ShopifyAPI::Context not setup, please call ShopifyAPI::Context.setup"
          end
          raise Errors::UnsupportedOauthError, "Cannot perform OAuth for private apps." if Context.private?

          state = SecureRandom.alphanumeric(NONCE_LENGTH)

          cookie = SessionCookie.new(value: state, expires: Time.now + 60)

          query = {
            client_id: ShopifyAPI::Context.api_key,
            scope: scope.to_s,
            redirect_uri: "#{ShopifyAPI::Context.host}#{redirect_path}",
            state: state,
            "grant_options[]": is_online ? "per-user" : "",
          }

          query_string = URI.encode_www_form(query)
          auth_route = auth_base_uri(shop) + "/oauth/authorize?#{query_string}"

          { auth_route: auth_route, cookie: cookie }
        end
```

**File:** lib/shopify_api/auth/oauth.rb (L64-71)
```ruby
          raise Errors::InvalidOauthError, "Invalid OAuth callback." unless Utils::HmacValidator.validate(auth_query)
          raise Errors::UnsupportedOauthError, "Cannot perform OAuth for private apps." if Context.private?

          state = cookies[SessionCookie::SESSION_COOKIE_NAME]
          raise Errors::NoSessionCookieError unless state

          raise Errors::InvalidOauthError,
            "Invalid state in OAuth callback." unless state == auth_query.state
```

**File:** lib/shopify_api/auth/oauth.rb (L96-110)
```ruby
          session_params = T.cast(response.body, T::Hash[String, T.untyped]).to_h
          session = Session.from(shop: auth_query.shop,
            access_token_response: Oauth::AccessTokenResponse.from_hash(session_params))

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

**File:** lib/shopify_api/auth/oauth.rb (L117-120)
```ruby
        sig { params(shop: String).returns(String) }
        def auth_base_uri(shop)
          return "https://#{shop}/admin" unless defined?(DevServer) && shop.include?(".my.shop.dev")

```

**File:** lib/shopify_api/auth/refresh_token.rb (L18-25)
```ruby
        def refresh_access_token(shop:, refresh_token:)
          unless ShopifyAPI::Context.setup?
            raise ShopifyAPI::Errors::ContextNotSetupError,
              "ShopifyAPI::Context not setup, please call ShopifyAPI::Context.setup"
          end

          validated_shop = Utils::ShopValidator.sanitize!(shop)
          shop_session = ShopifyAPI::Auth::Session.new(shop: validated_shop)
```

**File:** lib/shopify_api/auth/client_credentials.rb (L19-26)
```ruby
        def client_credentials(shop:)
          unless ShopifyAPI::Context.setup?
            raise ShopifyAPI::Errors::ContextNotSetupError,
              "ShopifyAPI::Context not setup, please call ShopifyAPI::Context.setup"
          end

          validated_shop = Utils::ShopValidator.sanitize!(shop)
          shop_session = ShopifyAPI::Auth::Session.new(shop: validated_shop)
```

**File:** lib/shopify_api/auth/token_exchange.rb (L97-104)
```ruby
        def migrate_to_expiring_token(shop:, non_expiring_offline_token:)
          unless ShopifyAPI::Context.setup?
            raise ShopifyAPI::Errors::ContextNotSetupError,
              "ShopifyAPI::Context not setup, please call ShopifyAPI::Context.setup"
          end

          validated_shop = Utils::ShopValidator.sanitize!(shop)
          shop_session = ShopifyAPI::Auth::Session.new(shop: validated_shop)
```

**File:** lib/shopify_api/utils/shop_validator.rb (L9-18)
```ruby
      TRUSTED_SHOPIFY_DOMAINS = T.let(
        [
          "shopify.com",
          "myshopify.io",
          "myshopify.com",
          "spin.dev",
          "shop.dev",
        ].freeze,
        T::Array[String],
      )
```
