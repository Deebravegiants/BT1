Confirmed: `Oauth.begin_auth` at [1](#0-0)  and `auth_base_uri` at [2](#0-1)  use the caller-supplied `shop` directly with no `ShopValidator.sanitize!` call, unlike `ClientCredentials.client_credentials` [3](#0-2) , `RefreshToken.refresh_access_token` [4](#0-3) , and `TokenExchange` methods which all call `Utils::ShopValidator.sanitize!(shop)` before using the shop value. This confirms the analog.

### Title
Missing shop-domain validation in `Oauth.begin_auth` enables forced OAuth redirection to attacker-controlled hosts - (File: lib/shopify_api/auth/oauth.rb)

### Summary
`ShopifyAPI::Auth::Oauth.begin_auth` builds the Shopify authorization redirect URL directly from the caller-supplied `shop` parameter without validating that it is a real, trusted `myshopify.com`/`myshopify.io`/`spin.dev`/`shop.dev` domain. Every other OAuth-adjacent entry point in the gem (`ClientCredentials.client_credentials`, `RefreshToken.refresh_access_token`, `TokenExchange.exchange_token`/`migrate_to_expiring_token`) enforces this via `ShopifyAPI::Utils::ShopValidator.sanitize!`, but `begin_auth` (and `validate_auth_callback`'s use of `auth_query.shop` for building the `null_session`/redirect host) does not.

### Finding Description
The identity binding that should hold is: **the "shop" a host application redirects the browser to equals a shop domain that is actually part of the trusted Shopify domain set** (`ShopValidator::TRUSTED_SHOPIFY_DOMAINS`). This is exactly the binding `ShopValidator.sanitize!` was introduced to enforce, and is applied consistently in `client_credentials.rb`, `refresh_token.rb`, and `token_exchange.rb`: [3](#0-2) 

`begin_auth`, however, takes the `shop:` keyword argument (which in nearly every real-world app comes from an unauthenticated request parameter, e.g. `request.headers["Shop"]` as shown in the gem's own documentation) and passes it straight into `auth_base_uri(shop)`: [1](#0-0) [2](#0-1) 

`auth_base_uri` simply interpolates `shop` into `"https://#{shop}/admin"` with no domain allow-list check, unlike `ShopValidator.sanitize_shop_domain`, which validates the host against `TRUSTED_SHOPIFY_DOMAINS` [5](#0-4) .

Because of this, an unprivileged internet user can supply an arbitrary string as `shop` (e.g. `attacker.example`) to a host application built on top of this gem's documented `begin_auth` API, causing the gem to construct and return an `auth_route` pointing at `https://attacker.example/admin/oauth/authorize?...` together with a `state` nonce cookie that the host application sets on the victim's browser via the returned `SessionCookie`.

### Impact Explanation
This maps to the "session fixation or forced OAuth completion" High-impact category. The victim's browser is redirected off Shopify's real infrastructure to an attacker-controlled host, while a CSRF-protection `state` cookie tied to the app is planted in the victim's browser session. The attacker's server, now knowing the `state` value it caused to be issued, can host a convincing OAuth consent-screen phish or otherwise stage a forced-completion attack against the app's callback route, since the only thing standing between "attacker knows the correct `state`" and a completed install is out of this gem's control (the app's own callback handling), but the gem itself is the component that failed to stop the redirect to a non-Shopify host in the first place — precisely the gap `ShopValidator` exists to close everywhere else in the same file's sibling modules.

### Likelihood Explanation
Reaching this requires only that a host application invoke `begin_auth(shop:, redirect_path:)` with a shop value taken from an unauthenticated source — which is the exact integration pattern shown in this gem's own `docs/usage/oauth.md` example (`shop = request.headers["Shop"]`) [6](#0-5) . No credentials, tokens, or special access are needed by the attacker; they only need to control the `shop` value passed to a documented public entry point of this library.

### Recommendation
Call `Utils::ShopValidator.sanitize!(shop)` (or `sanitize_shop_domain`) at the top of `Oauth.begin_auth`, mirroring `ClientCredentials.client_credentials`, `RefreshToken.refresh_access_token`, and `TokenExchange`, and use the sanitized/validated shop value when constructing `auth_base_uri`. Consider applying the same validation to `auth_query.shop` inside `validate_auth_callback` before it is used to build the `null_session` and subsequent access-token request host.

### Proof of Concept
1. Host app (following the gem's documented pattern) calls:
   ```ruby
   ShopifyAPI::Auth::Oauth.begin_auth(shop: params[:shop], redirect_path: "/auth/callback")
   ```
2. Attacker sends a victim a link to the app's login route with `?shop=attacker.example`.
3. `begin_auth` returns:
   ```ruby
   { auth_route: "https://attacker.example/admin/oauth/authorize?client_id=...&scope=...&redirect_uri=...&state=<nonce>&grant_options%5B%5D=per-user",
     cookie: #<SessionCookie value: <nonce>, ...> }
   ```
4. The host app 307-redirects the victim's browser to `attacker.example` (not Shopify) and sets the `state` cookie, as shown in the gem's own documented controller example [6](#0-5) , with no domain check having been performed by the library.

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

**File:** lib/shopify_api/auth/oauth.rb (L117-128)
```ruby
        sig { params(shop: String).returns(String) }
        def auth_base_uri(shop)
          return "https://#{shop}/admin" unless defined?(DevServer) && shop.include?(".my.shop.dev")

          # For first-party apps in development only, we leverage DevServer to build the admin base URI
          admin_web = T.unsafe(Object.const_get("DevServer")) # rubocop:disable Sorbet/ConstantsFromStrings
            .new("admin-web")
          admin_host = admin_web.host!(nonstandard_host_prefix: "admin")
          shop_name = shop.split(".").first

          "https://#{admin_host}/store/#{shop_name}"
        end
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

**File:** lib/shopify_api/utils/shop_validator.rb (L8-18)
```ruby
    module ShopValidator
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
