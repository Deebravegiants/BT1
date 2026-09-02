Found a genuine finding: `TokenExchange.exchange_token` in `lib/shopify_api/auth/token_exchange.rb` sends the app's `client_secret` to a host derived from the JWT's `dest` claim without running it through `Utils::ShopValidator.sanitize!`, unlike every other credential-issuing flow in the same file/module.

### Title
`client_secret` sent to an unvalidated host derived from JWT `dest` claim in token exchange - (File: `lib/shopify_api/auth/token_exchange.rb`)

### Summary
`TokenExchange.exchange_token` builds the HTTP client used to POST the app's `client_secret` from `dest_shop = jwt_payload.shop`, which is taken directly from the JWT `dest` claim without ever calling `Utils::ShopValidator.sanitize!`. Every sibling method that builds a similar credential-bearing request (`ClientCredentials.client_credentials`, `RefreshToken.refresh_access_token`, `TokenExchange.migrate_to_expiring_token`) explicitly calls `Utils::ShopValidator.sanitize!(shop)` before constructing the session/host used for the request. `exchange_token` is the outlier.

### Finding Description
`JwtPayload#shop` simply strips the scheme from the raw `dest` claim: [1](#0-0) . Verification of the token only checks the signature (HS256 with `Context.api_secret_key`/`old_api_secret_key`) and that `aud == Context.api_key`: [2](#0-1) . Nothing constrains `dest` to a `*.myshopify.com`/`*.myshopify.io`/`*.spin.dev`/`*.shop.dev` value, and no domain-shape check is applied downstream in `token_exchange.rb`.

`exchange_token` then does: [3](#0-2) 

The resulting `Clients::HttpClient` derives its request host from `shop_session.shop` (i.e., `dest_shop`), and the request body includes `client_secret: ShopifyAPI::Context.api_secret_key`. In contrast, `ClientCredentials.client_credentials` [4](#0-3) , `RefreshToken.refresh_access_token` [5](#0-4) , and `TokenExchange.migrate_to_expiring_token` [6](#0-5)  all route the `shop` value through `Utils::ShopValidator.sanitize!`, which is designed specifically to reject non-Shopify/attacker-controlled hosts and confusable domains such as `myshopify.com.evil.com` or a leading userinfo like `shop.myshopify.com@evil.com` [7](#0-6) .

This is exactly the class of bug the rules flag: a value (`dest`) is "trusted without being bound" to the domain-shape restriction the library enforces everywhere else before it is used to route a credential-bearing (`client_secret`) HTTP request.

### Impact Explanation
If the app's own token-exchange code path is reachable with an id_token whose `dest` claim is not shape-validated, an attacker who can influence the `dest` value of a token that still verifies under the app's secret (e.g. via a signing-key mixup, JWKS confusion, or any scenario where the equality `HMAC-verified issuer == myshopify.com-shaped host` doesn't hold) could redirect the outbound `client_secret`-bearing request to a non-Shopify host — an SSRF that exfiltrates the app's `client_secret`. This maps to the "High: SSRF with the app's credentials" impact class in scope.

### Likelihood Explanation
Exploitation requires a session token that passes HMAC verification but carries an attacker-influenced `dest`. Under normal operation, only Shopify (holding the shared secret) issues valid session tokens, so this is not exploitable by a generic unprivileged caller without an additional token-issuance weakness. This bounds likelihood to low/theoretical given current code, but it is a real missing-defense-in-depth: the library enforces `ShopValidator.sanitize!` everywhere else a `shop` value reaches a credential request except here, so any future relaxation of JWT verification (e.g., key rotation edge cases, misconfigured `old_api_secret_key`, or JWKS-based verification changes) would immediately become exploitable without further code review because the missing check is silent.

### Recommendation
In `TokenExchange.exchange_token`, pass `dest_shop` through `Utils::ShopValidator.sanitize!` (as already done in `migrate_to_expiring_token`, `client_credentials`, and `refresh_access_token`) before constructing `shop_session`/`Clients::HttpClient`, and raise `Errors::InvalidShopError` on mismatch.

### Proof of Concept
Not independently reproducible with unprivileged access alone (requires a validly-signed JWT with a non-Shopify-shaped `dest`, which normally requires the app's `api_secret_key`). The finding is a code-structure inconsistency/missing-binding, demonstrated by comparing:
- `token_exchange.rb` line 41 (`dest_shop = jwt_payload.shop`, no sanitize) vs.
- `token_exchange.rb` line 103 (`validated_shop = Utils::ShopValidator.sanitize!(shop)` in the sibling method), and
- `jwt_payload.rb` lines 47-50 confirming `shop` has no domain-shape constraint. [8](#0-7) [9](#0-8) [10](#0-9)

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

**File:** lib/shopify_api/utils/shop_validator.rb (L20-48)
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
```
