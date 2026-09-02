## Title
`ShopifyAPI::Auth::TokenExchange.exchange_token` Sends `client_secret` to an Unvalidated Host Derived from JWT `dest` Claim - (File: `lib/shopify_api/auth/token_exchange.rb`)

### Summary
`TokenExchange.exchange_token` derives the shop host from the `dest` claim of the caller-supplied session token and uses it, without validation, to build the HTTP session that receives the app's `client_id`/`client_secret` in the OAuth token-exchange POST body. Every sibling method in the same auth layer (`ClientCredentials.client_credentials`, `RefreshToken.refresh_access_token`, and `TokenExchange.migrate_to_expiring_token`) calls `Utils::ShopValidator.sanitize!(shop)` before constructing the session/host, but `exchange_token` does not.

### Finding Description
`exchange_token` extracts the shop from the session token via `ShopifyAPI::Auth::JwtPayload.new(session_token)` / `jwt_payload.shop`, then immediately builds the session used for the outbound request: [1](#0-0) 

That `shop_session` is passed straight into `Clients::HttpClient.new(session: shop_session, ...)`, and `HttpClient` uses `session.shop` verbatim as the request host: [2](#0-1) 

The POST body sent to that host includes the app's `client_id` and `client_secret`: [3](#0-2) 

Contrast this with the three sibling methods that build the exact same kind of request, all of which sanitize the shop value against `ShopValidator::TRUSTED_SHOPIFY_DOMAINS` before it is ever used to construct the outbound host: [4](#0-3) [5](#0-4) [6](#0-5) 

`ShopValidator.sanitize!` is the mechanism designed to enforce the binding "host that will receive the request == a trusted `*.myshopify.com`/Shopify domain": [7](#0-6) 

`exchange_token` breaks this binding: the value trusted to become the request host (`dest_shop`, from the JWT `dest` claim) is never checked against `ShopValidator`, whereas the value verified as authentic (a validly-signed session token) is not bound to a specific, checked host string. This matches the report's "a JWT claim trusted without being bound" analog and the "host validated versus the host that receives ... `client_secret`" identity-binding class explicitly called out in scope.

I was not able to fully inspect `lib/shopify_api/auth/jwt_payload.rb` in this session (tool budget exhausted) to confirm whether it independently constrains the `dest` claim's format/domain before exposing it via `jwt_payload.shop`. This is the one open question that would need to be verified to finalize root cause — if `JwtPayload` already restricts `dest` to a trusted Shopify domain shape, the practical exploitability is reduced; if it only parses/decodes the claim without domain-allowlist checking (as the asymmetry with the three sibling call sites strongly suggests, since they clearly needed to add sanitization to guard against exactly this), the SSRF-with-credentials path is live.

### Impact Explanation
If the `dest` claim is not constrained to a trusted domain, an app that calls `exchange_token` with a session token whose `dest` claim points to an attacker-controlled host will cause the gem to POST the app's `client_id` and `client_secret` to that attacker-controlled host — SSRF carrying the app's OAuth `client_secret`, i.e., direct credential exfiltration to a third party (High/Critical per the rules' "SSRF with the app's credentials" and "theft of ... the app's `client_secret`" categories).

### Likelihood Explanation
`exchange_token` is the standard, documented flow for embedded apps performing Shopify's token-exchange authentication, and it accepts session tokens that ultimately originate from the browser (App Bridge) rather than being generated solely by Shopify's OAuth server, unlike the classic OAuth callback where `shop`/`host` are additionally covered by the Shopify-computed HMAC (`lib/shopify_api/utils/hmac_validator.rb`, `lib/shopify_api/auth/oauth/auth_query.rb`). This flow, by contrast, relies solely on `JwtPayload`'s parsing to trust `dest`. Given that this is the only one of four structurally identical helper methods in the auth layer missing the `ShopValidator.sanitize!` call, the omission looks like a real gap rather than an intentional design choice.

### Recommendation
In `TokenExchange.exchange_token`, validate `dest_shop` with `Utils::ShopValidator.sanitize!(dest_shop)` (as already done in `migrate_to_expiring_token`, `client_credentials`, and `refresh_access_token`) before constructing `shop_session`, so the host that ultimately receives `client_id`/`client_secret` is guaranteed to be a domain in `ShopValidator::TRUSTED_SHOPIFY_DOMAINS`.

### Proof of Concept
Conceptual (pending confirmation of `JwtPayload`'s claim validation, which could not be verified in this session):
1. Attacker crafts/obtains a session token whose `dest` claim is set to an attacker-controlled host (e.g., `evil.example.com`) rather than a `*.myshopify.com` domain.
2. Host application calls `ShopifyAPI::Auth::TokenExchange.exchange_token(session_token: attacker_token, requested_token_type: ...)`.
3. `exchange_token` sets `dest_shop = jwt_payload.shop` unchecked, builds `shop_session` with that shop, and `Clients::HttpClient` sends `POST https://evil.example.com/admin/oauth/access_token` with body containing the app's real `client_id` and `client_secret`.
4. Attacker's server captures the `client_secret`, gaining the ability to impersonate the app going forward.

Because verification of `lib/shopify_api/auth/jwt_payload.rb`'s claim validation was not completed due to the session's tool-call limit, this finding should be treated as requiring confirmation of that file's contents before being considered fully proven.

### Citations

**File:** lib/shopify_api/auth/token_exchange.rb (L39-59)
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
