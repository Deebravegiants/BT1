Found a concrete analog: in `ShopifyAPI::Auth::TokenExchange.exchange_token`, the shop used to build the base URI that receives the app's `client_secret` (`session.shop` in `HttpClient#initialize`) is derived directly from the unvalidated JWT `dest` claim (`JwtPayload#shop`, simple `gsub("https://", "")`), unlike every other flow in this file (`migrate_to_expiring_token`, `RefreshToken.refresh_access_token`, `ClientCredentials.client_credentials`) which all pass the shop through `Utils::ShopValidator.sanitize!` before it is used to build the outbound request host.

### Title
Unsanitized JWT `dest` claim used as request host for `client_secret` in Token Exchange - (File: lib/shopify_api/auth/token_exchange.rb)

### Summary
`TokenExchange.exchange_token` builds the outbound `HttpClient` host from `jwt_payload.shop`, which is just `dest.gsub("https://", "")` with no domain allow-listing, while the sibling flows in the same module and file (`migrate_to_expiring_token`) and other auth flows (`RefreshToken.refresh_access_token`, `ClientCredentials.client_credentials`) all call `Utils::ShopValidator.sanitize!` on the shop before using it as the request host.

### Finding Description
`JwtPayload#shop` is computed as `@dest.gsub("https://", "")` [1](#0-0) . The JWT's signature is verified with `Context.api_secret_key`/`old_api_secret_key`, and the only cross-field check performed is `aud == Context.api_key` [2](#0-1) . There is no check that `dest`/`iss` is a trusted Shopify domain (`myshopify.com`, `myshopify.io`, `spin.dev`, `shop.dev`, unified `admin.shopify.com`, etc.) as is done elsewhere via `Utils::ShopValidator` [3](#0-2) .

`exchange_token` takes this unvalidated `dest_shop` value and uses it directly to build a `Session`, which is then passed into `Clients::HttpClient.new(session: shop_session, ...)` together with a request body containing `client_id` and `client_secret` [4](#0-3) . `HttpClient#initialize` uses `session.shop` verbatim to construct `@base_uri` (`"https://#{api_host || session.shop}"`) that the HTTP request — including the `client_secret` in its POST body — is sent to [5](#0-4) .

Contrast this with the pattern used everywhere else that builds a request carrying `client_secret`: `ClientCredentials.client_credentials` sanitizes `shop` via `Utils::ShopValidator.sanitize!(shop)` before constructing the session/host [6](#0-5) ; `RefreshToken.refresh_access_token` does the same [7](#0-6) ; and even `TokenExchange.migrate_to_expiring_token` in the very same file sanitizes `shop` [8](#0-7) . `exchange_token` is the outlier that skips this validation and relies purely on the JWT's `dest` claim, trusting that Shopify (the token issuer) never issues a `dest` outside the myshopify domain space, and trusting that the signature check plus `aud` check is a substitute for host allow-listing.

The identity-binding equality being broken (or at least not enforced defense-in-depth) is: *the host the `client_secret` is sent to* should equal *a value validated against `Utils::ShopValidator`'s trusted-domain set*, exactly as is enforced in every sibling method in this module. Here it instead equals *whatever string the `dest` claim contains after a `https://` strip*, with no domain restriction.

### Impact Explanation
If this binding is ever violated (e.g., a future change to token issuance, a bug allowing `dest` to be attacker-influenced, or if this code path is reused with a token from a less trusted source), the consequence is SSRF carrying the app's `client_secret` and `client_id` to an arbitrary host — a direct violation of the Critical/High bar (SSRF with the app's credentials). Today, exploitability depends entirely on trusting that Shopify signs tokens with only legitimate `dest` values; the code itself provides no independent enforcement of that trust, unlike its sibling methods.

### Likelihood Explanation
Low-to-moderate under current conditions, since JWT signature verification (`JWT.decode` with `HS256` and `api_secret_key`) is a real barrier [9](#0-8) , but the missing defense-in-depth check is a real gap relative to the codebase's own established pattern (used in 3 of 4 sibling flows), making this a genuine inconsistency and latent risk rather than a currently fully proven remote exploit without the secret.

### Recommendation
Apply `Utils::ShopValidator.sanitize!` (or equivalent) to `dest_shop` in `TokenExchange.exchange_token` before constructing `shop_session`, mirroring `migrate_to_expiring_token`, `RefreshToken.refresh_access_token`, and `ClientCredentials.client_credentials`, so the host that receives `client_secret` is always constrained to `Utils::ShopValidator::TRUSTED_SHOPIFY_DOMAINS`.

### Proof of Concept
Conceptual: any code path that can produce a validly-signed JWT (per `Context.api_secret_key`) with a `dest` claim outside the myshopify domain set (e.g., `dest: "https://attacker.example"`) will cause `exchange_token` to POST `client_id`/`client_secret` to `https://attacker.example/admin/oauth/access_token`, since neither `JwtPayload` nor `exchange_token` restricts `dest` to trusted domains, unlike `migrate_to_expiring_token` in the same file which sanitizes its `shop` argument first [10](#0-9) .

### Citations

**File:** lib/shopify_api/auth/jwt_payload.rb (L43-45)
```ruby
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

**File:** lib/shopify_api/auth/jwt_payload.rb (L76-81)
```ruby
      sig { params(token: String, api_secret_key: String).returns(T::Hash[String, T.untyped]) }
      def decode_token(token, api_secret_key)
        JWT.decode(token, api_secret_key, true, leeway: JWT_LEEWAY, algorithm: "HS256")[0]
      rescue JWT::DecodeError => err
        raise ShopifyAPI::Errors::InvalidJwtTokenError, "Error decoding session token: #{err.message}"
      end
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

**File:** lib/shopify_api/clients/http_client.rb (L11-19)
```ruby
      sig { params(base_path: String, session: T.nilable(Auth::Session)).void }
      def initialize(base_path:, session: nil)
        session ||= Context.active_session
        raise Errors::NoActiveSessionError, "No passed or active session" unless session

        api_host = Context.api_host

        @base_uri = T.let("https://#{api_host || session.shop}", String)
        @base_uri_and_path = T.let("#{@base_uri}#{base_path}", String)
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
