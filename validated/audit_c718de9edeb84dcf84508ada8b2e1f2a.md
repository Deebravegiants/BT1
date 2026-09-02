### Title
`ShopifyAPI::Auth::Oauth.begin_auth` sends the app's `client_id`, requested scopes and CSRF `state` nonce to an attacker-controlled host due to missing shop-domain validation - (File: `lib/shopify_api/auth/oauth.rb`)

### Summary
`ShopifyAPI::Auth::Oauth.begin_auth` builds the OAuth "authorize" redirect URL by directly interpolating the caller-supplied `shop` string into a host via `auth_base_uri(shop)`, with no validation that `shop` is a genuine `*.myshopify.com` (or other trusted Shopify) domain.

### Finding Description
`begin_auth` takes `shop:` and builds: [1](#0-0) 
which produces `auth_route = "https://#{shop}/admin/oauth/authorize?client_id=...&scope=...&redirect_uri=...&state=..."` from the raw, unvalidated `shop` value. [2](#0-1) 

The library ships a purpose-built `ShopifyAPI::Utils::ShopValidator` module, whose `sanitize!` restricts `shop` to `TRUSTED_SHOPIFY_DOMAINS` (`shopify.com`, `myshopify.io`, `myshopify.com`, `spin.dev`, `shop.dev`) and raises `Errors::InvalidShopError` otherwise: [3](#0-2) 

Every other credential-issuing flow in this gem calls this validator before using an externally supplied `shop` to build a URL that will receive the app's `client_secret`:
- `ClientCredentials.client_credentials` — `validated_shop = Utils::ShopValidator.sanitize!(shop)` before POSTing `client_secret`. [4](#0-3) 
- `RefreshToken.refresh_access_token` — same pattern. [5](#0-4) 
- `TokenExchange.migrate_to_expiring_token` — same pattern. [6](#0-5) 

`Auth::Oauth` is the sole exception: neither `begin_auth` nor `validate_auth_callback` ever calls `ShopValidator`, confirmed by the absence of any `ShopValidator` reference in `oauth.rb` (grep across the repo shows it used only in `token_exchange.rb`, `client_credentials.rb`, `refresh_token.rb`, and `graphql/storefront.rb`, never in `oauth.rb`). The documentation instructs integrators to pass an inbound, unauthenticated value directly as `shop` (e.g. `shop = request.headers["Shop"]`) to `begin_auth`, with no mention of sanitizing it first: [7](#0-6) [8](#0-7) 

This is the same bug class as the `ZIP` report: a value that is *acted on* (used to select the destination host for a security-sensitive redirect containing `client_id`, `scope`, `redirect_uri`, and the anti-CSRF `state`) is not bound/verified against the identity it is supposed to represent (a genuine Shopify shop domain) before being trusted. The equality that should hold and is broken is: `host redirected to == genuine *.myshopify.com domain`, but the gem instead accepts `host redirected to == attacker-supplied string`.

### Impact Explanation
Before the attacker's request: an unprivileged internet user visits the app's login route with an attacker-chosen `shop` value (e.g. `evil.example.com`); no validation occurs. After: `begin_auth` returns `auth_route = "https://evil.example.com/admin/oauth/authorize?client_id=<APP_CLIENT_ID>&scope=<APP_SCOPES>&redirect_uri=<APP_CALLBACK_URL>&state=<CSRF_NONCE>"`, and the host application redirects the victim's browser there. This is a Server-Side-Redirect/host-confusion condition that:
- Discloses the app's `client_id`, requested `scope`, and legitimate `redirect_uri` to an attacker-controlled server.
- Lets the attacker capture/replace the CSRF `state` nonce and subsequently drive the victim's browser back to the app's real `redirect_path` with attacker-chosen `code`/other parameters, enabling forced-OAuth-completion style attacks against the callback flow (the callback path still requires a valid HMAC to complete the token exchange, so full account takeover requires further conditions, but the missing binding is squarely inside this gem and directly analogous to the flagged bug class).

### Likelihood Explanation
Likelihood is high for exposure: any app built with this gem's authorization-code-grant flow that (as the official docs recommend) derives `shop` from request input (header, query param) without separately sanitizing it, inherits this gap for free, because the gem itself performs no check — unlike its sibling flows (`client_credentials`, `refresh_token`, `token_exchange.migrate_to_expiring_token`) which all enforce `ShopValidator.sanitize!`.

### Recommendation
In `lib/shopify_api/auth/oauth.rb`, validate `shop` with `Utils::ShopValidator.sanitize!(shop)` at the top of `begin_auth` (and use the sanitized value in `auth_base_uri`), mirroring the pattern already used in `ClientCredentials`, `RefreshToken`, and `TokenExchange.migrate_to_expiring_token`. Also validate `auth_query.shop` in `validate_auth_callback` before it is used to construct `auth_base_uri` for the access-token exchange POST containing `client_secret`.

### Proof of Concept
```ruby
ShopifyAPI::Context.setup(api_key: "app-key", api_secret_key: "app-secret", host_name: "app.example.com", scope: "read_products")

# Attacker-controlled input reaching begin_auth (per docs pattern: shop = request.headers["Shop"])
result = ShopifyAPI::Auth::Oauth.begin_auth(shop: "evil.example.com", redirect_path: "/auth/callback")

result[:auth_route]
# => "https://evil.example.com/admin/oauth/authorize?client_id=app-key&scope=read_products&redirect_uri=https%3A%2F%2Fapp.example.com%2Fauth%2Fcallback&state=<15-char-nonce>&grant_options%5B%5D=per-user"
```
No `ShopifyAPI::Errors::InvalidShopError` (or any error) is raised, and `client_id`, `redirect_uri`, and the CSRF `state` nonce are sent to `evil.example.com`, unlike the equivalent code paths in `ClientCredentials.client_credentials("evil.example.com")`, `RefreshToken.refresh_access_token(shop: "evil.example.com", ...)`, or `TokenExchange.migrate_to_expiring_token(shop: "evil.example.com", ...)`, which all raise `Errors::InvalidShopError` for the same input.

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

**File:** lib/shopify_api/utils/shop_validator.rb (L20-64)
```ruby
      class << self
        extend T::Sig

        sig do
          params(
            shop_domain: String,
            myshopify_domain: T.nilable(String),
          ).returns(T.nilable(String))
        end
        def sanitize_shop_domain(shop_domain, myshopify_domain: nil)
          uri = uri_from_shop_domain(shop_domain, myshopify_domain)
          return nil if uri.nil? || uri.host.nil? || uri.host.empty?

          trusted_domains(myshopify_domain).each do |trusted_domain|
            host = T.cast(uri.host, String)
            uri_domain = uri.domain
            next if uri_domain.nil?

            no_shop_name_in_subdomain = host == trusted_domain
            from_trusted_domain = trusted_domain == uri_domain

            if unified_admin?(uri) && from_trusted_domain
              return myshopify_domain_from_unified_admin(uri)
            end
            return nil if no_shop_name_in_subdomain || host.empty?
            return host if from_trusted_domain
          end
          nil
        end

        sig do
          params(
            shop: String,
            myshopify_domain: T.nilable(String),
          ).returns(String)
        end
        def sanitize!(shop, myshopify_domain: nil)
          host = sanitize_shop_domain(shop, myshopify_domain: myshopify_domain)
          if host.nil? || host.empty?
            raise Errors::InvalidShopError,
              "shop must be a trusted Shopify domain (see ShopValidator::TRUSTED_SHOPIFY_DOMAINS), got: #{shop.inspect}"
          end

          host
        end
```

**File:** lib/shopify_api/auth/client_credentials.rb (L19-33)
```ruby
        def client_credentials(shop:)
          unless ShopifyAPI::Context.setup?
            raise ShopifyAPI::Errors::ContextNotSetupError,
              "ShopifyAPI::Context not setup, please call ShopifyAPI::Context.setup"
          end

          validated_shop = Utils::ShopValidator.sanitize!(shop)
          shop_session = ShopifyAPI::Auth::Session.new(shop: validated_shop)
          body = {
            client_id: ShopifyAPI::Context.api_key,
            client_secret: ShopifyAPI::Context.api_secret_key,
            grant_type: CLIENT_CREDENTIALS_GRANT_TYPE,
          }

          client = Clients::HttpClient.new(session: shop_session, base_path: "/admin/oauth")
```

**File:** lib/shopify_api/auth/refresh_token.rb (L18-33)
```ruby
        def refresh_access_token(shop:, refresh_token:)
          unless ShopifyAPI::Context.setup?
            raise ShopifyAPI::Errors::ContextNotSetupError,
              "ShopifyAPI::Context not setup, please call ShopifyAPI::Context.setup"
          end

          validated_shop = Utils::ShopValidator.sanitize!(shop)
          shop_session = ShopifyAPI::Auth::Session.new(shop: validated_shop)
          body = {
            client_id: ShopifyAPI::Context.api_key,
            client_secret: ShopifyAPI::Context.api_secret_key,
            grant_type: "refresh_token",
            refresh_token:,
          }

          client = Clients::HttpClient.new(session: shop_session, base_path: "/admin/oauth")
```

**File:** lib/shopify_api/auth/token_exchange.rb (L97-115)
```ruby
        def migrate_to_expiring_token(shop:, non_expiring_offline_token:)
          unless ShopifyAPI::Context.setup?
            raise ShopifyAPI::Errors::ContextNotSetupError,
              "ShopifyAPI::Context not setup, please call ShopifyAPI::Context.setup"
          end

          validated_shop = Utils::ShopValidator.sanitize!(shop)
          shop_session = ShopifyAPI::Auth::Session.new(shop: validated_shop)
          body = {
            client_id: ShopifyAPI::Context.api_key,
            client_secret: ShopifyAPI::Context.api_secret_key,
            grant_type: TOKEN_EXCHANGE_GRANT_TYPE,
            subject_token: non_expiring_offline_token,
            subject_token_type: RequestedTokenType::OFFLINE_ACCESS_TOKEN.serialize,
            requested_token_type: RequestedTokenType::OFFLINE_ACCESS_TOKEN.serialize,
            expiring: "1",
          }

          client = Clients::HttpClient.new(session: shop_session, base_path: "/admin/oauth")
```

**File:** docs/usage/oauth.md (L146-154)
```markdown
Use [`ShopifyAPI::Auth::Oauth.begin_auth`](https://github.com/Shopify/shopify-api-ruby/blob/main/lib/shopify_api/auth/oauth.rb#L22) method to start OAuth process for your app.

#### Input
| Parameter      | Type                   | Required? | Default Value | Notes                                                                                                       |
| -------------- | ---------------------- | :-------: | :-----------: | ----------------------------------------------------------------------------------------------------------- |
| `shop`          | `String`               |    Yes    |       -       | A Shopify domain name in the form `{exampleshop}.myshopify.com`.                                            |
| `redirect_path` | `String`               |    Yes    |       -       | The redirect path used for callback with a leading `/`. The route should be allowed under the app settings. |
| `is_online`     | `Boolean`              |    No     |    `true`     | `true` if the session is online and `false` otherwise.                                                      |
| `scope_override`| `String` or `[String]` |    No     |     `nil`     |  `nil` will request access scopes configured in `ShopifyAPI::Context.setup` during OAuth flow. Modify this to override the access scopes being requested. Accepts array or string: "read_orders, write_products" or ["read_orders", "write_products"]. |
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
