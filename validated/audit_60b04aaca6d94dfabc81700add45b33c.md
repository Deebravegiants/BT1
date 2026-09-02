This is the key finding: `exchange_token` in `TokenExchange` derives `dest_shop` from the JWT payload's `dest` claim and passes it **directly** to `ShopifyAPI::Auth::Session.new(shop: dest_shop)` without ever routing it through `ShopValidator.sanitize!`, unlike its sibling method `migrate_to_expiring_token`, which explicitly calls `Utils::ShopValidator.sanitize!(shop)` before building the session.

### Title
Unsanitized `dest` claim from session token used as OAuth token-exchange host - (File: `lib/shopify_api/auth/token_exchange.rb`)

### Summary
`TokenExchange.exchange_token` takes the `dest` claim straight out of the caller-supplied session token (`JwtPayload#shop`, i.e. `dest.gsub("https://", "")`) and uses it, unchecked, as the hostname for the HTTP request that carries the app's `client_id`/`client_secret` to `https://#{dest_shop}/admin/oauth/access_token` [1](#0-0) . Unlike `migrate_to_expiring_token`, which calls `Utils::ShopValidator.sanitize!(shop)` before building the session and host [2](#0-1) , `exchange_token` never validates `dest_shop` against `ShopValidator::TRUSTED_SHOPIFY_DOMAINS` [3](#0-2) .

### Finding Description
`JwtPayload#shop` only strips the `https://` prefix from the `dest` claim — it performs no domain allow-listing [4](#0-3) . `JwtPayload.new` verifies the JWT signature against `Context.api_secret_key` (or the old secret) and checks only that `aud == Context.api_key`; it never validates that `dest`/`iss` belong to a Shopify-owned domain [5](#0-4) . `TokenExchange.exchange_token` then builds `shop_session = Session.new(shop: dest_shop)` and issues the token-exchange POST (containing `client_id` and `client_secret`) to a `Clients::HttpClient` scoped to that session's host [6](#0-5) .

The identity binding that should hold is: *the host that receives the app's `client_secret` == a Shopify-trusted domain*. Because the `dest` claim is not run through `ShopValidator.sanitize!`, this equality is never enforced for the token-exchange path, even though the sibling `migrate_to_expiring_token` method enforces exactly this check for the same kind of request.

### Impact Explanation
If a session token can be produced (or replayed) with a `dest` claim pointing to something other than a genuine `*.myshopify.com`/trusted domain — e.g. via a malformed/legacy `dest` value, an embedding context that doesn't strictly control the token issuer, or any future relaxation of the JWT/`aud` check — the resulting HTTP request sends the app's `client_id` and `client_secret` to a non-Shopify host chosen by the value of `dest`. This is SSRF carrying the app's credentials, i.e. credential exfiltration of the `client_secret` to an attacker-controlled host, which matches the "High" impact bucket (SSRF with the app's credentials / credential leakage).

### Likelihood Explanation
Exploitation normally requires a validly-signed session token, which in turn requires knowledge of `api_secret_key` — this reduces likelihood under the stated scope. However, the code path is asymmetric with its sibling method that already treats the shop value as untrusted enough to require `ShopValidator.sanitize!`; this inconsistency indicates the token-exchange path was not held to the same trust boundary and is a latent SSRF/credential-leak vector should the `dest` claim ever be less strictly bound (e.g. non-`HS256` tokens, wrong-secret rejection bypassed, or shared/leaked secrets across environments).

### Recommendation
Apply `Utils::ShopValidator.sanitize!` (or equivalent allow-list check against `ShopValidator::TRUSTED_SHOPIFY_DOMAINS`) to `dest_shop` in `TokenExchange.exchange_token` before constructing `shop_session`/`client`, mirroring the existing check in `migrate_to_expiring_token`.

### Proof of Concept
1. Obtain/produce a session token whose `dest` claim is `"attacker.example"` (requires it be signed with the configured `api_secret_key`, or exploit any future path where the signature/`aud` check is weakened).
2. Call `ShopifyAPI::Auth::TokenExchange.exchange_token(session_token: token, requested_token_type: ...)`.
3. Observe `Session.new(shop: "attacker.example")` is created and the HTTP client issues a POST containing `client_id` and `client_secret` to `https://attacker.example/admin/oauth/access_token`, versus `migrate_to_expiring_token`, which would raise `ShopifyAPI::Errors::InvalidShopError` for the same input [7](#0-6) .

### Citations

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

**File:** lib/shopify_api/auth/jwt_payload.rb (L24-45)
```ruby
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

**File:** test/utils/shop_validator_test.rb (L38-42)
```ruby
      def test_rejects_attacker_controlled_domain
        assert_raises(ShopifyAPI::Errors::InvalidShopError) do
          ShopifyAPI::Utils::ShopValidator.sanitize!("attacker.example")
        end
      end
```
