This confirms a clear pattern break: every other credential-exchange flow (`ClientCredentials#client_credentials`, `RefreshToken#refresh_access_token`, `TokenExchange#migrate_to_expiring_token`) explicitly calls `Utils::ShopValidator.sanitize!(shop)` before using the caller-supplied `shop` string to build the host that receives `client_secret`. `ShopifyAPI::Auth::Oauth.begin_auth` and `ShopifyAPI::Auth::Oauth.validate_auth_callback` — the classic OAuth entry points — never call `ShopValidator` at all.

### Title
OAuth flow builds authorize/token-exchange host from unsanitized `shop`, unlike every sibling flow - (File: `lib/shopify_api/auth/oauth.rb`)

### Summary
`ShopifyAPI::Auth::Oauth.begin_auth` takes a caller-supplied `shop:` value and uses it, unsanitized, to build the URL the merchant's browser is redirected to for OAuth authorization. Every other credential-issuing flow in this gem (`ClientCredentials`, `RefreshToken`, `TokenExchange#migrate_to_expiring_token`) validates the equivalent `shop` argument with `Utils::ShopValidator.sanitize!` before it is used to construct the host that will receive the app's `client_id`/`client_secret`. `oauth.rb` skips this step entirely.

### Finding Description
`begin_auth` builds the redirect target directly from the caller's `shop` argument: [1](#0-0) 
`auth_base_uri` uses this value verbatim as the hostname: [2](#0-1) 
No call to `Utils::ShopValidator.sanitize!` exists anywhere in `oauth.rb`, confirmed by the whole-repo search that only found `ShopValidator` usage in `token_exchange.rb`, `client_credentials.rb`, and `refresh_token.rb`. In contrast, those three flows explicitly bind `shop` to a trusted Shopify domain before it can influence any outbound request: [3](#0-2) [4](#0-3) [5](#0-4) 
`validate_auth_callback` similarly builds `null_session` straight from `auth_query.shop` (which does travel through `Utils::HmacValidator.validate`, so it is at least bound to the callback's HMAC) and never re-validates it against `ShopValidator.TRUSTED_SHOPIFY_DOMAINS`: [6](#0-5) 
`ShopValidator.sanitize!` is the gem's documented mechanism for binding a shop string to `TRUSTED_SHOPIFY_DOMAINS` (`shopify.com`, `myshopify.io`, `myshopify.com`, `spin.dev`, `shop.dev`) before it is trusted as a network destination: [7](#0-6) 

The equality this breaks: `shop` used to build the destination host for the OAuth flow == `shop` validated as a trusted Shopify domain. The identity binding that every other flow enforces (`validated_shop = Utils::ShopValidator.sanitize!(shop)`) is absent in `begin_auth`.

### Impact Explanation
When a host application passes a request-controlled `shop` parameter straight to `begin_auth` — the exact usage pattern this method's keyword signature (`shop:`) invites, mirroring how `ClientCredentials.client_credentials(shop:)` and `RefreshToken.refresh_access_token(shop:)` are used with unsanitized input in the same codebase — an attacker can supply an arbitrary hostname (e.g. `evil.example.com`). `auth_base_uri` returns `https://evil.example.com/admin`, so `begin_auth`'s returned `auth_route` sends the merchant's browser, embedding the app's `client_id`, the crafted `redirect_uri`, and a real session `state`/nonce cookie value, to an attacker-controlled host. This is a forced-OAuth/host-confusion condition (open redirect carrying app OAuth parameters and a valid state cookie), which corresponds to the "High — SSRF with the app's credentials, session fixation or forced OAuth completion" category, since the state nonce and cookie set for the flow can be driven toward an attacker's chosen authorize endpoint.

### Likelihood Explanation
This is directly reachable if a host application forwards a request-supplied shop identifier into `begin_auth` without its own separate sanitization — a realistic integration pattern given that the sibling methods in this same gem (`ClientCredentials`, `RefreshToken`) accept the same kind of parameter and are documented to require the caller supply a shop domain. Because the gem validates `shop` in three of its four OAuth-adjacent entry points but not in the primary `begin_auth`/`validate_auth_callback` pair, the omission is an internal inconsistency rather than a documented, expected caller responsibility.

### Recommendation
Call `Utils::ShopValidator.sanitize!(shop)` in `begin_auth` before constructing `auth_base_uri`, and similarly sanitize/validate `auth_query.shop` in `validate_auth_callback` before it is used to build `null_session` and the token-exchange host, bringing `oauth.rb` in line with `client_credentials.rb`, `refresh_token.rb`, and `token_exchange.rb`.

### Proof of Concept
```ruby
ShopifyAPI::Context.setup(api_key: "key", api_secret_key: "secret", host: "https://app.example.com", ...)

result = ShopifyAPI::Auth::Oauth.begin_auth(
  shop: "evil.example.com", # attacker-controlled input forwarded by host app
  redirect_path: "/auth/callback",
)
result[:auth_route]
# => "https://evil.example.com/admin/oauth/authorize?client_id=key&scope=...&redirect_uri=https://app.example.com/auth/callback&state=<nonce>"
```
The merchant's browser (with the freshly issued state cookie) is redirected to a host the attacker controls, with no domain validation performed by the gem.

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

**File:** lib/shopify_api/auth/oauth.rb (L60-79)
```ruby
        def validate_auth_callback(cookies:, auth_query:)
          unless Context.setup?
            raise Errors::ContextNotSetupError, "ShopifyAPI::Context not setup, please call ShopifyAPI::Context.setup"
          end
          raise Errors::InvalidOauthError, "Invalid OAuth callback." unless Utils::HmacValidator.validate(auth_query)
          raise Errors::UnsupportedOauthError, "Cannot perform OAuth for private apps." if Context.private?

          state = cookies[SessionCookie::SESSION_COOKIE_NAME]
          raise Errors::NoSessionCookieError unless state

          raise Errors::InvalidOauthError,
            "Invalid state in OAuth callback." unless state == auth_query.state

          null_session = Auth::Session.new(shop: auth_query.shop)
          body = {
            client_id: Context.api_key,
            client_secret: Context.api_secret_key,
            code: auth_query.code,
            expiring: Context.expiring_offline_access_tokens ? 1 : 0, # Only applicable for offline tokens
          }
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

**File:** lib/shopify_api/utils/shop_validator.rb (L9-64)
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
