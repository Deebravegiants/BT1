### Title
`ShopifyAPI::Auth::Oauth.begin_auth` builds the authorization redirect from an unvalidated `shop` parameter, enabling forced OAuth completion / state-nonce leakage - ([File: lib/shopify_api/auth/oauth.rb])

### Summary
`ShopifyAPI::Auth::Oauth.begin_auth` accepts a caller-supplied `shop:` string and uses it, unvalidated, to build the host that the user's browser is redirected to for authorization, along with the app's `client_id`, requested `scope`, `redirect_uri`, and the CSRF `state` nonce. Unlike every other flow in this gem that builds an OAuth-related request from a shop string, `begin_auth` never calls `Utils::ShopValidator.sanitize!` to confirm the shop is a genuine `*.myshopify.com` (or otherwise trusted) domain before using it.

### Finding Description
The gem ships `Utils::ShopValidator.sanitize!` specifically to bind an untrusted "shop" input to Shopify's trusted domain set (`myshopify.com`, `shopify.com`, `myshopify.io`, `spin.dev`, `shop.dev`) before it's used to construct any URL: [1](#0-0) [2](#0-1) 

This validator is consistently applied everywhere else a caller-supplied `shop` value is turned into a request host that will carry the app's `client_secret`: `ClientCredentials.client_credentials` [3](#0-2)  and `RefreshToken.refresh_access_token` [4](#0-3)  both call `Utils::ShopValidator.sanitize!(shop)` before building the `Clients::HttpClient` session/base host.

`Oauth.begin_auth`, however, takes the `shop` argument directly and passes it straight into `auth_base_uri(shop)` with no sanitization: [5](#0-4)  and [6](#0-5) 

The resulting `auth_route` — containing `client_id`, `scope`, `redirect_uri`, and the freshly generated CSRF `state` nonce — is returned to the caller specifically to redirect the user's browser to it. The docs' own reference implementation sources `shop` straight from an incoming HTTP header (`request.headers["Shop"]`) with no validation before calling `begin_auth`: [7](#0-6) 

The security-relevant identity binding that breaks here is: *the shop the browser is redirected to* ≠ *a shop actually verified/authenticated as belonging to Shopify's trusted domain set*. `begin_auth` never enforces this equality, while `ClientCredentials`/`RefreshToken` do.

### Impact Explanation
An unprivileged attacker who can influence the `shop` value passed into `begin_auth` (e.g., via a header/query param on the app's own login route, exactly as shown in this gem's documented usage) can redirect a victim's browser to an attacker-controlled host instead of `*.myshopify.com`. This leaks the app's `client_id`, requested `scope`, `redirect_uri`, and — critically — the CSRF `state` nonce (also stored in the victim's session cookie) to the attacker's server. The attacker can then complete an OAuth flow of their own choosing (e.g., authorize the app against an attacker-owned shop) and redirect the victim back to the legitimate `redirect_path` with a matching `state`, causing `validate_auth_callback` to succeed and bind the victim's browser session to a session/access token for the attacker's shop — a forced OAuth completion / session-fixation-style attack, matching the in-scope "High" impact category.

### Likelihood Explanation
Reachable purely through the app's own login endpoint if it forwards a user-controlled shop value (as this gem's own documentation example does) into `begin_auth` without independent validation — no credentials, tokens, or privileged access are required. Likelihood is tempered by the fact that a well-implemented host application may itself validate `shop` before calling `begin_auth`, but the gem provides no such protection internally, unlike its sibling flows (`ClientCredentials`, `RefreshToken`) which do.

### Recommendation
Call `Utils::ShopValidator.sanitize!(shop)` (or `sanitize_shop_domain`) inside `Oauth.begin_auth` before deriving `auth_base_uri(shop)`, mirroring the pattern already used in `ClientCredentials.client_credentials` and `RefreshToken.refresh_access_token`, so that only a domain from `ShopValidator::TRUSTED_SHOPIFY_DOMAINS` can ever receive the CSRF `state`, `client_id`, and redirect parameters.

### Proof of Concept
1. App's login route builds the shop from an unauthenticated request value, per the gem's documented pattern: `shop = request.headers["Shop"]`.
2. Attacker sends the victim to the app's login route with `Shop: attacker.example.com`.
3. `ShopifyAPI::Auth::Oauth.begin_auth(shop: "attacker.example.com", redirect_path: "/auth/callback")` executes `auth_base_uri("attacker.example.com")` → `"https://attacker.example.com/admin"`, with no call to `ShopValidator`, producing `auth_route = "https://attacker.example.com/admin/oauth/authorize?client_id=...&scope=...&redirect_uri=https://app.com/auth/callback&state=<nonce>&grant_options[]=per-user"`. See [8](#0-7) 
4. The app sets the `state` cookie and 307-redirects the victim's browser to `auth_route`, sending `client_id`, `scope`, `redirect_uri`, and `state` to the attacker-controlled server.
5. Attacker uses the captured `state`/`redirect_uri` to complete a legitimate Shopify OAuth authorization against an attacker-owned shop and redirects the victim back to `redirect_path` with a matching `state` and valid `hmac` (computed by real Shopify for the attacker's shop), causing `validate_auth_callback` to succeed and establish a session tied to the attacker's shop in the victim's browser context.

### Citations

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

**File:** lib/shopify_api/utils/shop_validator.rb (L56-64)
```ruby
        def sanitize!(shop, myshopify_domain: nil)
          host = sanitize_shop_domain(shop, myshopify_domain: myshopify_domain)
          if host.nil? || host.empty?
            raise Errors::InvalidShopError,
              "shop must be a trusted Shopify domain (see ShopValidator::TRUSTED_SHOPIFY_DOMAINS), got: #{shop.inspect}"
          end

          host
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
