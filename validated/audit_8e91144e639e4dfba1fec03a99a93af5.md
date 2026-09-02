### Title
`exchange_token` sends the app's `client_secret` to a host derived from an unvalidated JWT `dest` claim - ([File: lib/shopify_api/auth/token_exchange.rb])

### Summary
`ShopifyAPI::Auth::TokenExchange.exchange_token` derives the destination host for the OAuth token-exchange POST (which carries `client_secret`) directly from the session token's `dest` claim, via `JwtPayload#shop`, without ever passing it through `Utils::ShopValidator.sanitize!`. Every sibling credential-exchange flow in the same file/module (`migrate_to_expiring_token`, and `ClientCredentials.client_credentials`, `RefreshToken.refresh_access_token`) explicitly calls `Utils::ShopValidator.sanitize!(shop)` before constructing the session used to build the HTTP client's base URI. `exchange_token` is the one path that skips this check.

### Finding Description
`JwtPayload#shop` is computed as `@dest.gsub("https://", "")` [1](#0-0)  with no restriction on what domain `dest` may contain beyond signature/`aud`/`exp` checks [2](#0-1) .

In `exchange_token`, this unsanitized value is used as-is to build the `Session` that determines the request host: [3](#0-2) 

`Clients::HttpClient#initialize` builds the request base URI directly from `session.shop` with no domain allow-list check: `@base_uri = "https://#{api_host || session.shop}"` [4](#0-3) . The request body posted to that host includes `client_secret: ShopifyAPI::Context.api_secret_key` [5](#0-4) .

This is a direct structural analog to the "unvalidated Chainlink data" bug class: a value (`dest`/`shop`) is consumed to determine a security-sensitive action (which host receives the `client_secret`) without the same validation that is applied to the equivalent value everywhere else in the same module. Compare with `migrate_to_expiring_token`, `client_credentials`, and `refresh_access_token`, which all call `Utils::ShopValidator.sanitize!(shop)` [6](#0-5) [7](#0-6) [8](#0-7)  before building the exact same kind of session/HTTP client. `ShopValidator` exists specifically to enforce the binding "host receiving the token == a domain in `TRUSTED_SHOPIFY_DOMAINS`" [9](#0-8) , and `exchange_token` breaks that binding for the one flow that both accepts external, less-trusted input (a session token that in practice is passed through from the frontend/host app) and always transmits the `client_secret`.

### Impact Explanation
If the `dest` claim can, through any path, end up containing a non-Shopify host (e.g., a proxied/relayed or otherwise irregular session token whose `dest` was not constrained to a `myshopify.com`/`myshopify.io`/`spin.dev`/`shop.dev` domain, unlike every other credential-issuing entry point in this gem which enforces that constraint), `exchange_token` will POST the application's `client_secret` and the raw `subject_token` to that host — an SSRF-with-credentials condition carrying the app's `client_id`/`client_secret`, matching the "SSRF with the app's credentials" High-impact category.

### Likelihood Explanation
Likelihood is constrained by the fact that a validly-signed JWT normally originates from Shopify's own token-issuance and is bound by `aud == Context.api_key`, so under strict Shopify-only issuance the `dest` value is expected to always be a legitimate shop domain. The bug is that this gem does not itself enforce/verify that expectation the way it does in the three sibling methods — it relies entirely on the issuer's behavior rather than validating the claim itself, which is inconsistent within the same module and is the exact class of gap being reported (trusting upstream data without local validation).

### Recommendation
Apply the same treatment as the other three credential-exchange functions: pass `dest_shop` through `Utils::ShopValidator.sanitize!` (or reject the token) before constructing `shop_session` in `exchange_token`, so that the host receiving `client_secret` is always constrained to `ShopValidator::TRUSTED_SHOPIFY_DOMAINS`.

### Proof of Concept
1. Obtain/construct a session token whose `dest` claim is not confined by this library to a Shopify domain (the only enforced constraints are HS256 signature validity and `aud == Context.api_key`; `dest` is used verbatim except for stripping the `https://` prefix).
2. Call `ShopifyAPI::Auth::TokenExchange.exchange_token(session_token: token, requested_token_type: ...)`.
3. Observe that `Session.new(shop: dest_shop)` is built directly from the unsanitized claim [10](#0-9) , and `HttpClient` issues `POST https://#{dest_shop}/admin/oauth/access_token` with `client_secret` in the body [4](#0-3) , unlike `migrate_to_expiring_token`/`client_credentials`/`refresh_access_token`, which would reject an untrusted `shop` via `ShopValidator.sanitize!` before reaching this point.

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

**File:** lib/shopify_api/auth/token_exchange.rb (L103-104)
```ruby
          validated_shop = Utils::ShopValidator.sanitize!(shop)
          shop_session = ShopifyAPI::Auth::Session.new(shop: validated_shop)
```

**File:** lib/shopify_api/clients/http_client.rb (L16-19)
```ruby
        api_host = Context.api_host

        @base_uri = T.let("https://#{api_host || session.shop}", String)
        @base_uri_and_path = T.let("#{@base_uri}#{base_path}", String)
```

**File:** lib/shopify_api/auth/client_credentials.rb (L25-26)
```ruby
          validated_shop = Utils::ShopValidator.sanitize!(shop)
          shop_session = ShopifyAPI::Auth::Session.new(shop: validated_shop)
```

**File:** lib/shopify_api/auth/refresh_token.rb (L24-25)
```ruby
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
