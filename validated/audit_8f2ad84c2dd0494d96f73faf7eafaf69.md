Confirmed: `ShopValidator.sanitize!` is applied in `client_credentials.rb`, `refresh_token.rb`, `clients/graphql/storefront.rb`, and in `token_exchange.rb`'s `migrate_to_expiring_token`, but **not** in `token_exchange.rb`'s `exchange_token`, nor in `oauth.rb`'s `begin_auth`/`validate_auth_callback` (both use the raw `shop`/`auth_query.shop` directly to build the `Session` that becomes the HTTP request host).

### Title
Unvalidated shop domain from session-token `dest` claim used as OAuth token-exchange request host - (File: lib/shopify_api/auth/token_exchange.rb)

### Summary
`ShopifyAPI::Auth::TokenExchange.exchange_token` derives the destination shop directly from the JWT `dest` claim and uses it, unsanitized, as the host that receives the app's `client_secret` and the user's session token in the OAuth token-exchange POST body.

### Finding Description
`exchange_token` decodes the caller-supplied session token with `ShopifyAPI::Auth::JwtPayload.new(session_token)` and takes `dest_shop = jwt_payload.shop`, which is simply `@dest.gsub("https://", "")` with no further validation of the domain shape or trust boundary [1](#0-0) . That `dest_shop` is placed into a new `Session` and passed to `Clients::HttpClient`, whose `initialize` sets `@base_uri = "https://#{api_host || session.shop}"` — i.e., `session.shop` becomes the actual network destination for the request [2](#0-1) . The request body sent to that host includes `client_id`, `client_secret`, and the raw `subject_token` (the session token) [3](#0-2) .

Elsewhere in the very same file, `migrate_to_expiring_token` performs `validated_shop = Utils::ShopValidator.sanitize!(shop)` before building the equivalent session/host used to send `client_secret` [4](#0-3) , and `ShopValidator.sanitize!` explicitly restricts hosts to `TRUSTED_SHOPIFY_DOMAINS` (`shopify.com`, `myshopify.io`, `myshopify.com`, `spin.dev`, `shop.dev`) or a configured `myshopify_domain` [5](#0-4) . `exchange_token` has no equivalent check on `dest_shop` — the binding "host that receives `client_secret`" == "host validated against `ShopValidator`" holds in `migrate_to_expiring_token` but does not hold in `exchange_token`.

The `JwtPayload` itself confirms `dest` is not constrained to a myshopify domain: the test fixtures show `dest` values ranging from `https://test-shop.myshopify.io` to bare `test-shop.myshopify.io` for checkout/extension-issued tokens (`iss` ending in `/checkouts`) [6](#0-5) , and no cross-check exists between `iss` and `dest`, nor any domain-suffix validation in `JwtPayload#initialize` beyond the HMAC signature and `aud == Context.api_key` check [7](#0-6) .

### Impact Explanation
If a `dest` value that is not a genuine `*.myshopify.com`-family host reaches `exchange_token` (e.g., via a custom/legacy domain that later lapses and is re-pointed by an attacker, or any code path that mints/relays a session token with an unexpected `dest`), the app's `client_secret` and the merchant's session token are transmitted to that host via `Clients::HttpClient`, which builds the URL purely from `session.shop` with no allow-list check [2](#0-1) . That satisfies the Critical bar: exfiltration of the app's `client_secret` and theft of the subject/session token, sent outbound with attacker-influenced destination.

### Likelihood Explanation
Exploitation requires a validly-HMAC-signed session token whose `dest` is not a trusted Shopify domain to reach `exchange_token`. Since the JWT is HMAC-signed with `Context.api_secret_key` [8](#0-7) , only Shopify can normally mint one, and I could not confirm from this gem's code alone that Shopify ever issues tokens with a `dest` outside the trusted set (this would need verification against Shopify's session-token issuance behavior for custom domains/checkout extensibility, which is outside this gem). The code-level fact I can prove is the inconsistency: the same file enforces `ShopValidator.sanitize!` on one token-exchange path but not the other, which is a concrete, provable gap in defense-in-depth even if the practical trigger condition needs external confirmation.

### Recommendation
Apply `Utils::ShopValidator.sanitize!(dest_shop)` (or equivalent, with the configured `myshopify_domain`) to the `dest` claim in `TokenExchange.exchange_token` before constructing `shop_session`, mirroring the check already done in `migrate_to_expiring_token`. Consider centralizing this validation inside `JwtPayload#shop` so all consumers (`SessionUtils`, `TokenExchange`, host apps) get it uniformly.

### Proof of Concept
1. Obtain (or otherwise cause the library to receive) a session token whose `dest` claim is a non-myshopify host `H`, correctly HMAC-signed with the app's `api_secret_key` and with `aud` matching `Context.api_key`.
2. Call `ShopifyAPI::Auth::TokenExchange.exchange_token(session_token: token, requested_token_type: ...)`.
3. `dest_shop = jwt_payload.shop` resolves to `H` unchanged [9](#0-8) .
4. `Clients::HttpClient.new(session: shop_session, base_path: "/admin/oauth")` builds `@base_uri = "https://H"` [2](#0-1) .
5. The POST to `https://H/admin/oauth/access_token` carries `client_id`, `client_secret`, and `subject_token` in the body [10](#0-9) , exposing the app's `client_secret` and the session token to host `H`.

**Caveat:** I could not verify, using only this gem's code, whether Shopify's real session-token issuance ever produces a `dest` value outside `ShopValidator::TRUSTED_SHOPIFY_DOMAINS` for a legitimately-obtained token — that would require Shopify platform-side documentation/behavior not present in this repository. The provable root cause is the missing `ShopValidator` check in `exchange_token` relative to the sibling method `migrate_to_expiring_token` in the same file.

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

**File:** lib/shopify_api/auth/jwt_payload.rb (L76-81)
```ruby
      sig { params(token: String, api_secret_key: String).returns(T::Hash[String, T.untyped]) }
      def decode_token(token, api_secret_key)
        JWT.decode(token, api_secret_key, true, leeway: JWT_LEEWAY, algorithm: "HS256")[0]
      rescue JWT::DecodeError => err
        raise ShopifyAPI::Errors::InvalidJwtTokenError, "Error decoding session token: #{err.message}"
      end
```

**File:** lib/shopify_api/clients/http_client.rb (L16-19)
```ruby
        api_host = Context.api_host

        @base_uri = T.let("https://#{api_host || session.shop}", String)
        @base_uri_and_path = T.let("#{@base_uri}#{base_path}", String)
```

**File:** lib/shopify_api/auth/token_exchange.rb (L40-65)
```ruby
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

**File:** test/auth/jwt_payload_test.rb (L23-32)
```ruby
        @checkout_ui_extension_jwt_payload = {
          iss: "https://test-shop.myshopify.io/checkouts",
          dest: "test-shop.myshopify.io",
          aud: ShopifyAPI::Context.api_key,
          sub: "gid://shopify/Customer/123456789",
          exp: (Time.now + 10).to_i,
          nbf: 1234,
          iat: 1234,
          jti: "4321",
        }
```
