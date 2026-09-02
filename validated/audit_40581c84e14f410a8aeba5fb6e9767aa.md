### Title
`TokenExchange.exchange_token` sends the app's `client_secret` to the unsanitized JWT `dest` host, unlike its sibling OAuth methods - ([File: lib/shopify_api/auth/token_exchange.rb])

### Summary
`ShopifyAPI::Auth::TokenExchange.exchange_token` derives the request host for the `POST /admin/oauth/access_token` call (which carries the app's `client_id` and `client_secret`) directly from the session token's `dest` claim, without ever passing it through `Utils::ShopValidator.sanitize!`. Every other method in the OAuth surface that builds a request host from an externally-supplied `shop` value (`ClientCredentials.client_credentials`, `RefreshToken.refresh_access_token`, `TokenExchange.migrate_to_expiring_token`) explicitly calls `Utils::ShopValidator.sanitize!(shop)` first to constrain the destination host to `TRUSTED_SHOPIFY_DOMAINS`.

### Finding Description
`JwtPayload#shop` is computed as: [1](#0-0) 
which is just `@dest` with the scheme stripped, and `@dest` is taken verbatim from the decoded JWT payload with no domain-format validation: [2](#0-1) 

`exchange_token` then uses this value directly to build the session/host that receives the token-exchange request containing `client_id`/`client_secret`: [3](#0-2) 

Contrast this with `migrate_to_expiring_token` in the same file, `client_credentials`, and `refresh_access_token`, which all call `Utils::ShopValidator.sanitize!(shop)` before constructing the session used for the same `client_secret`-bearing request: [4](#0-3) [5](#0-4) [6](#0-5) 

`HttpClient#initialize` builds the outbound host straight from `session.shop` with no further checks: [7](#0-6) 

`ShopValidator.sanitize!` exists precisely to bind the destination host to `TRUSTED_SHOPIFY_DOMAINS` (`shopify.com`, `myshopify.io`, `myshopify.com`, `spin.dev`, `shop.dev`): [8](#0-7) 

The identity binding that is broken is: **the host that is cryptographically verified to accept the app's `client_secret` (via `ShopValidator.sanitize!` against `TRUSTED_SHOPIFY_DOMAINS`) ≠ the host actually used in `exchange_token`, which is the raw `dest` claim from the JWT.** JWT signature verification only proves `aud == Context.api_key` and integrity under `HS256` with the shared secret; it says nothing about whether the `dest` string is a well-formed `*.myshopify.com` (or other trusted) domain. The library accepts `dest` for any `iss` shape, including non-admin contexts (e.g. `iss` ending in `/checkouts` for checkout UI extension tokens is explicitly supported and tested), where `dest` values are not guaranteed to be `*.myshopify.com` admin hosts.

### Impact Explanation
If a `dest` value can point at a host outside the trusted Shopify domain set (e.g. a checkout-extension-context token whose `dest` is a merchant custom/checkout domain rather than an admin `*.myshopify.com` host, or any other issuer path this gem accepts), `exchange_token` will POST the app's `client_id` and `client_secret` to that host. This is a credential-leakage/SSRF-with-app-credentials risk: the app's `client_secret` is sent to a destination that was never validated to be a Shopify-controlled endpoint, whereas the library's own design intent (as shown by the sibling methods) is to always sanitize the destination host before sending `client_secret` there.

### Likelihood Explanation
Exploitation still requires a validly-signed session token (signed with the app's `api_secret_key`), so an attacker with no knowledge of the secret cannot mint an arbitrary `dest` from scratch. However, the vulnerability is a genuine code-level inconsistency, not a theoretical note: it is the one path among four structurally identical "build a host from `shop`, then send `client_secret`" call sites that omits the `ShopValidator.sanitize!` binding, and the JWT payload's `dest` is trusted for any accepted `iss` shape (admin, checkout, etc.) without host-format validation.

### Recommendation
In `lib/shopify_api/auth/token_exchange.rb`, sanitize `dest_shop` the same way the other three methods do before using it to build `shop_session`:
```ruby
dest_shop = Utils::ShopValidator.sanitize!(jwt_payload.shop)
```
This restores the binding between "host verified as trustworthy" and "host that receives `client_id`/`client_secret`", matching `client_credentials`, `refresh_access_token`, and `migrate_to_expiring_token`.

### Proof of Concept
1. Obtain (or have App Bridge issue) a valid session token whose `iss`/context is not the standard admin path and whose `dest` claim is a host outside `ShopValidator::TRUSTED_SHOPIFY_DOMAINS` (e.g. a checkout-extension-style token as already accepted by `JwtPayload`, see the `/checkouts` issuer test case).
2. Call `ShopifyAPI::Auth::TokenExchange.exchange_token(session_token: token, requested_token_type: ...)`.
3. Observe that `Clients::HttpClient` is constructed with `session.shop == dest_shop` unsanitized, and the resulting POST to `https://#{dest_shop}/admin/oauth/access_token` carries `client_id` and `client_secret` to that host — with no `ShopValidator.sanitize!` check ever having run, unlike the equivalent `client_credentials`/`refresh_access_token`/`migrate_to_expiring_token` code paths.

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
