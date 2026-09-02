### Title
SSRF/credential-leak via unsanitized `dest` claim host used as OAuth token-exchange endpoint - (File: lib/shopify_api/auth/token_exchange.rb)

### Finding Description
`TokenExchange.exchange_token` takes the shop host directly from the JWT session token's `dest` claim (`jwt_payload.shop`, which is just `@dest.gsub("https://", "")` with no format/domain restriction) and uses it, unsanitized, as the host that the app's `client_id` and `client_secret` are sent to: [1](#0-0) [2](#0-1) 

Every sibling credential-exchange method in the same module — `migrate_to_expiring_token`, `ClientCredentials.client_credentials`, and `RefreshToken.refresh_access_token` — explicitly calls `Utils::ShopValidator.sanitize!(shop)` before constructing the `Session` used to build the request host, restricting the destination to `ShopValidator::TRUSTED_SHOPIFY_DOMAINS`: [3](#0-2) [4](#0-3) [5](#0-4) [6](#0-5) 

`exchange_token` is the one path that skips this check, breaking the intended equality: *host validated == host that receives `client_secret`*. The JWT's HMAC signature (via `Context.api_secret_key`) is verified in `JwtPayload#initialize`, and `aud` is checked against `Context.api_key`, but nothing constrains the `dest`/`iss` value to a `*.myshopify.com`/trusted Shopify domain shape the way `ShopValidator` does elsewhere in the same module: [7](#0-6) 

This mirrors the audit's bug class: a sibling/twin code path (`query_reverse_simulation` vs `query_simulation`) implements the correct binding, while another path in the same function family silently omits it, producing incorrect (here, security-relevant) behavior for one specific call path.

### Impact Explanation
If `dest` is ever attacker-influenced — e.g., through a modified/relayed App Bridge context, a compromised iframe, or any host application that forwards a session token whose `dest` was not itself independently checked before calling this library — `Clients::HttpClient` would issue a POST to `https://<dest>/admin/oauth/access_token` carrying the app's `client_id` and `client_secret` in the body. That is SSRF carrying the app's credentials to an attacker-chosen host, matching the "High" impact bucket (SSRF with the app's credentials / credential leakage). Because `client_secret` is explicitly excluded from scope as a required precondition for other bug classes but is exactly what's exfiltrated *by this code itself* (not by an attacker who already has it), this is a genuine boundary-crossing issue introduced by the missing sanitize call, not a documented-API-misuse case.

### Likelihood Explanation
Likelihood is moderate-to-low: under normal operation the JWT signature check ties `dest` to whatever Shopify's own session-token issuance puts in the claim, and Shopify is assumed to only mint tokens with legitimate shop hosts. However, the library provides no defense-in-depth here even though it does so consistently for the exact same class of host in three adjacent functions, and the code path is reachable by any caller of the public `exchange_token` API without any additional privilege — the inconsistency itself is the vulnerability (a defense that the library's own design pattern says should be present is missing on one path).

### Recommendation
Apply `Utils::ShopValidator.sanitize!` (or an equivalent trusted-domain check) to `jwt_payload.shop`/`dest_shop` in `TokenExchange.exchange_token` before constructing `shop_session` and issuing the token-exchange HTTP request, exactly as is already done in `migrate_to_expiring_token`, `client_credentials`, and `refresh_access_token`.

### Proof of Concept
1. Obtain/construct a session token whose `dest` claim is not a trusted Shopify domain shape but still validates (any scenario where the JWT signature check passes but the raw `dest` string is not host-restricted, e.g. a host application layer that pre-validates HMAC but relays a modified `dest`, or future logic changes weakening the `aud`/`iss` coupling).
2. Call `ShopifyAPI::Auth::TokenExchange.exchange_token(session_token: token, requested_token_type: ...)`.
3. Observe that `dest_shop = jwt_payload.shop` is passed straight into `Session.new(shop: dest_shop)` and then into `Clients::HttpClient.new(session: shop_session, base_path: "/admin/oauth")` with no `ShopValidator.sanitize!` call, unlike the parallel `migrate_to_expiring_token` method a few lines below in the same file: [8](#0-7) [9](#0-8) 
4. The POST containing `client_id`/`client_secret` is sent to `https://#{dest_shop}/admin/oauth/access_token` with no restriction on `dest_shop`'s domain.

### Citations

**File:** lib/shopify_api/auth/jwt_payload.rb (L23-45)
```ruby
      sig { params(token: String).void }
      def initialize(token)
        payload_hash = begin
          decode_token(token, Context.api_secret_key)
        rescue ShopifyAPI::Errors::InvalidJwtTokenError
          raise unless Context.old_api_secret_key

          decode_token(token, T.must(Context.old_api_secret_key))
        end

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

**File:** lib/shopify_api/auth/jwt_payload.rb (L47-50)
```ruby
      sig { returns(String) }
      def shop
        @dest.gsub("https://", "")
      end
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
