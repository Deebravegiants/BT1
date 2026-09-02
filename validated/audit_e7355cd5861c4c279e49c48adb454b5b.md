### Title
Unvalidated `dest` claim from session token used as request host and credential destination in `TokenExchange.exchange_token` - (File: `lib/shopify_api/auth/token_exchange.rb`)

### Summary
`ShopifyAPI::Auth::TokenExchange.exchange_token` derives the destination host for the OAuth token-exchange HTTP request directly from the session token's `dest` JWT claim, without ever passing it through `Utils::ShopValidator.sanitize!`. Every sibling credential-issuing method in the same module and library (`migrate_to_expiring_token`, `ClientCredentials.client_credentials`, `RefreshToken.refresh_access_token`) explicitly sanitizes the caller-supplied `shop` against `ShopValidator::TRUSTED_SHOPIFY_DOMAINS` before using it to build the request host. `exchange_token` skips this step entirely.

### Finding Description
`Utils::ShopValidator.sanitize!` exists specifically to guarantee that a `shop` string, before being used to construct the host of a request carrying `client_id`/`client_secret`, resolves to one of the `TRUSTED_SHOPIFY_DOMAINS` (`shopify.com`, `myshopify.io`, `myshopify.com`, `spin.dev`, `shop.dev`, or the configured `myshopify_domain`): [1](#0-0) [2](#0-1) 

`ClientCredentials.client_credentials` and `RefreshToken.refresh_access_token` both call this sanitizer on the caller-supplied `shop` before creating the `Session` used to build the outbound request host: [3](#0-2) [4](#0-3) 

`TokenExchange.migrate_to_expiring_token` in the same file does the same: [5](#0-4) 

But `TokenExchange.exchange_token` takes `dest_shop` straight from the decoded JWT payload (`jwt_payload.shop`, i.e. the `dest` claim with `https://` stripped) and uses it unsanitized to build the `Session` whose `shop` attribute becomes the request host: [6](#0-5) [7](#0-6) 

`Clients::HttpClient#initialize` builds the outbound base URI directly from `session.shop` with no further validation: [8](#0-7) 

The request body sent to that host includes `client_id` and `client_secret` in plaintext: [9](#0-8) 

The identity binding broken (as an equality) is: `host that receives client_secret` should `== ShopValidator.sanitize!(shop)`, but in `exchange_token` it instead equals `dest_shop = jwt_payload.shop` (the raw, unvalidated `dest` claim), skipping the trusted-domain check that every other credential-issuing code path in this gem enforces.

### Impact Explanation
If the `dest` claim value can ever diverge from a `myshopify.com`/trusted domain (e.g., a malformed or maliciously influenced session token, or any future JWT source not strictly limited to Shopify's own issuance), the app's `client_secret` and `client_id` would be sent as an HTTP POST body to an attacker-influenced host — this is SSRF carrying the app's own OAuth credentials, matching the "High - SSRF with the app's credentials" impact category. This is a genuine gap relative to the rest of the codebase, since the same class of value (`shop`) is defense-in-depth validated everywhere else credentials are transmitted.

### Likelihood Explanation
Exploitability is constrained by the fact that `session_token` must pass `JwtPayload.new`'s signature verification, which requires the token to be HMAC-signed with `Context.api_secret_key` (or `old_api_secret_key`) — a secret only Shopify and the app itself should possess when issuing legitimate session tokens. Under normal operation, Shopify always populates `dest` with the shop's own genuine `myshopify.com` domain, so an unprivileged internet user cannot, on their own, produce a token with an arbitrary `dest` value without already controlling the app's secret. This significantly lowers likelihood versus a directly reachable unauthenticated primitive, but the code-level omission is a real, verifiable regression against this gem's own established pattern (every sibling method sanitizes `shop`), and is a legitimate defense-in-depth gap that a background engineer should close by applying `Utils::ShopValidator.sanitize!` to `dest_shop` consistently with `migrate_to_expiring_token`, `client_credentials`, and `refresh_access_token`.

### Recommendation
In `lib/shopify_api/auth/token_exchange.rb#exchange_token`, sanitize `dest_shop` with `Utils::ShopValidator.sanitize!(dest_shop)` (mirroring `migrate_to_expiring_token`) before constructing `shop_session` and before using it as `Session.from(shop: ...)`, so the host that receives `client_id`/`client_secret` is always constrained to `ShopValidator::TRUSTED_SHOPIFY_DOMAINS`.

### Proof of Concept
Not independently reproducible as a standalone unprivileged-attacker exploit in this codebase: it requires a session token whose `dest` claim is both HMAC-valid under `Context.api_secret_key` and set to a non-trusted domain — a precondition not achievable by an external, unauthenticated party without already possessing the app's `client_secret`. The finding is a verified code-level inconsistency/omission (missing `ShopValidator.sanitize!` call) rather than a demonstrated end-to-end exploit chain.

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

**File:** lib/shopify_api/utils/shop_validator.rb (L50-64)
```ruby
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

**File:** lib/shopify_api/auth/jwt_payload.rb (L47-50)
```ruby
      sig { returns(String) }
      def shop
        @dest.gsub("https://", "")
      end
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
