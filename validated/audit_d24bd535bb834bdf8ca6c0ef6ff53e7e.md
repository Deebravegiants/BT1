### Title
Missing shop-domain validation on JWT `dest` claim allows SSRF with the app's `client_id`/`client_secret` in `TokenExchange.exchange_token` - (File: `lib/shopify_api/auth/token_exchange.rb`)

### Summary
`ShopifyAPI::Auth::TokenExchange.exchange_token` derives the host it POSTs the app's `client_id`/`client_secret` to directly from the unvalidated `dest` claim of a JWT, while every other credential-exchange helper in the same module/family (`client_credentials`, `refresh_token`, `migrate_to_expiring_token`) passes the caller-supplied `shop` through `Utils::ShopValidator.sanitize!` before using it to build the request host. `exchange_token` skips this check entirely.

### Finding Description
`ShopifyAPI::Auth::JwtPayload#initialize` decodes and verifies the JWT signature and checks only that `aud == Context.api_key`: [1](#0-0) 

It never validates that `iss`/`dest` are a legitimate Shopify domain (e.g. `*.myshopify.com`, `*.myshopify.io`, `admin.shopify.com`, etc.). `shop` is simply derived by stripping `https://` from `dest`: [2](#0-1) 

`TokenExchange.exchange_token` takes this unvalidated value and uses it, unmodified, as the `shop` of the session that determines the HTTP host the client talks to, and includes `client_id`/`client_secret` in the POST body sent to that host: [3](#0-2) 

Compare this with the sibling flows in the very same file and neighboring files, which explicitly bind/normalize the `shop` value to a trusted Shopify domain before it is used to build the request host that receives the same credentials: [4](#0-3) [5](#0-4) [6](#0-5) 

That validator (`Utils::ShopValidator.sanitize!`) exists specifically to restrict the destination host to `TRUSTED_SHOPIFY_DOMAINS`: [7](#0-6) 

The identity binding that is broken: **the host that receives `client_id`/`client_secret` (derived from the JWT `dest` claim) is not the same as "a validated, trusted Shopify domain"** — unlike `client_credentials`/`refresh_token`/`migrate_to_expiring_token`, where `sanitize!` enforces that equality before the credentialed request is dispatched.

### Impact Explanation
If `dest_shop` can ever contain an attacker-controlled hostname, `exchange_token` will make an HTTP POST containing the app's `client_id` and `client_secret` (plus the bearer session token) to that host — i.e., SSRF carrying the app's OAuth client credentials, which maps to the "High - SSRF with the app's credentials" bucket in scope.

### Likelihood Explanation
This is a defense-in-depth gap rather than a demonstrated end-to-end bypass reachable by a fully unprivileged internet user with this gem alone: in the standard token-exchange flow, the JWT consumed by `exchange_token` is a Shopify-issued session token (signed with the app's own `api_secret_key`, which `JwtPayload` verifies), and Shopify's token-minting service is what normally sets `dest` to the real embedding shop's domain — a value the end user's browser does not control directly. I could not find, purely from this gem's code, a way for an unprivileged party to supply an alternate, still-validly-signed token with an attacker-chosen `dest` without already controlling the app's secret or Shopify's token issuer. That means likelihood is lower than a straightforward remote bypass, and I cannot confirm a concrete exploit path strictly within this gem's boundary; I flag this primarily because it is an inconsistency against the codebase's own established defense (`ShopValidator.sanitize!`) for the exact same class of request (host that receives `client_secret`), and any code path that constructs or forwards such a JWT (e.g., a custom/host-app-side minting error, downgrade, or a future Shopify surface that lets the `dest` be less strictly bound) would turn this into full SSRF with credentials.

### Recommendation
In `ShopifyAPI::Auth::TokenExchange.exchange_token`, run `dest_shop` through `Utils::ShopValidator.sanitize!` (as already done in `migrate_to_expiring_token`, `client_credentials`, and `refresh_token`) before constructing `shop_session` / `Clients::HttpClient`, so the request host is always constrained to `ShopValidator::TRUSTED_SHOPIFY_DOMAINS` prior to sending `client_id`/`client_secret`.

### Proof of Concept
Not independently reproducible purely within this gem without a validly-signed JWT bearing an attacker-controlled `dest`; the gap is demonstrated by contrast of code paths:
1. `exchange_token` (`lib/shopify_api/auth/token_exchange.rb:39-51`) uses `jwt_payload.shop` directly as the request host with no domain check.
2. `migrate_to_expiring_token` (`lib/shopify_api/auth/token_exchange.rb:103-104`), `client_credentials.rb:25-26`, and `refresh_token.rb:24-25` all call `Utils::ShopValidator.sanitize!(shop)` first.
This inconsistency is the exploit-shaped gap; the actual attacker-reachability of an arbitrary `dest` claim in a validly-signed session token could not be fully verified from this gem's code alone.

### Citations

**File:** lib/shopify_api/auth/jwt_payload.rb (L33-45)
```ruby
        @iss = T.let(payload_hash["iss"], String)
        @dest = T.let(payload_hash["dest"], String)
        @aud = T.let(payload_hash["aud"], String)
        @sub = T.let(payload_hash["sub"], T.nilable(String))
        @exp = T.let(payload_hash["exp"], Integer)
        @nbf = T.let(payload_hash["nbf"], Integer)
        @iat = T.let(payload_hash["iat"], Integer)
        @jti = T.let(payload_hash["jti"], String)
        @sid = T.let(payload_hash["sid"], T.nilable(String))

        raise ShopifyAPI::Errors::InvalidJwtTokenError,
          "Session token had invalid API key" unless @aud == Context.api_key
      end
```

**File:** lib/shopify_api/auth/jwt_payload.rb (L47-51)
```ruby
      sig { returns(String) }
      def shop
        @dest.gsub("https://", "")
      end
      alias_method :shopify_domain, :shop
```

**File:** lib/shopify_api/auth/token_exchange.rb (L39-65)
```ruby
          # Validate the session token and use the shop from the token's `dest` claim
          jwt_payload = ShopifyAPI::Auth::JwtPayload.new(session_token)
          dest_shop = jwt_payload.shop

          if shop
            ShopifyAPI::Logger.deprecated(
              "The `shop` parameter for `exchange_token` is deprecated and will be removed in v17. " \
                "The shop is now always taken from the session token's `dest` claim.",
              "17.0.0",
            )
          end

          shop_session = ShopifyAPI::Auth::Session.new(shop: dest_shop)
          body = {
            client_id: ShopifyAPI::Context.api_key,
            client_secret: ShopifyAPI::Context.api_secret_key,
            grant_type: TOKEN_EXCHANGE_GRANT_TYPE,
            subject_token: session_token,
            subject_token_type: ID_TOKEN_TYPE,
            requested_token_type: requested_token_type.serialize,
          }

          if requested_token_type == RequestedTokenType::OFFLINE_ACCESS_TOKEN
            body.merge!({ expiring: ShopifyAPI::Context.expiring_offline_access_tokens ? 1 : 0 })
          end

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

**File:** lib/shopify_api/utils/shop_validator.rb (L6-64)
```ruby
module ShopifyAPI
  module Utils
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
