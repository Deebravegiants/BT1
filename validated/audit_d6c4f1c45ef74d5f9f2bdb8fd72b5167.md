### Title
Missing `ShopValidator` sanitization of JWT `dest` claim before sending `client_secret` in `Auth::TokenExchange.exchange_token` - (File: `lib/shopify_api/auth/token_exchange.rb`)

### Summary
`ShopifyAPI::Auth::TokenExchange.exchange_token` takes the `shop` value straight from the session token's `dest` claim and uses it, unvalidated, to build the host that receives the app's `client_id`/`client_secret` during the token-exchange POST. Every other credentialed flow in the gem (`ClientCredentials.client_credentials`, `TokenExchange.migrate_to_expiring_token`) runs the shop value through `Utils::ShopValidator.sanitize!` before using it the same way. `exchange_token` is the one path that skips this check.

### Finding Description
The identity binding that should hold is:
`shop value used to authenticate the JWT (verified `dest` claim)` == `shop value allow-listed by ShopValidator as a trusted Shopify host` == `host that receives the app's client_secret`.

In `exchange_token`, the third equality is never checked: [1](#0-0) 

`dest_shop = jwt_payload.shop` is derived purely from the JWT's `dest` claim, with `jwt_payload.shop` simply doing `@dest.gsub("https://", "")`: [2](#0-1) 

That un-sanitized string becomes `shop_session.shop`, and `Clients::HttpClient` uses `session.shop` directly to build the base URI that the credentialed request (containing `client_id` and `client_secret` in the JSON body) is sent to: [3](#0-2) 

Compare this with the sibling `client_credentials` and `migrate_to_expiring_token` flows, which both call `Utils::ShopValidator.sanitize!(shop)` — restricting the destination host to `TRUSTED_SHOPIFY_DOMAINS` (`shopify.com`, `myshopify.com`, `myshopify.io`, `spin.dev`, `shop.dev`) — before constructing the session used for the exact same credentialed HTTP request: [4](#0-3) [5](#0-4) [6](#0-5) 

`JwtPayload` does verify the JWT signature against `Context.api_secret_key` and checks the `aud` claim matches `Context.api_key`, so the token itself cannot be forged without the app's secret: [7](#0-6) 

However, signature validity only proves the token was minted by Shopify for this app — it says nothing about whether the `dest` value inside is restricted to a `*.myshopify.com`/`*.shopify.com` style host. `exchange_token` trusts that field as the SSRF destination for the `client_secret` with no allow-list check, unlike its sibling methods.

### Impact Explanation
If the `dest` claim value can ever diverge from a `TRUSTED_SHOPIFY_DOMAINS`-conformant host (e.g., through non-standard installation flows, dev/spin domains, or any Shopify-side edge case that embeds a different host string in `dest`), `exchange_token` will POST the app's `client_id` and `client_secret` to that host. That is a credential-exfiltration / SSRF-with-app-credentials primitive — the exact class of "host validated (JWT signature) versus host that receives the `client_secret`" identity-binding break called out in scope. This is High/Critical impact per the accepted-impact list (SSRF with the app's credentials / theft of the app's `client_secret`).

### Likelihood Explanation
Likelihood is moderate and conditional: exploitation requires a legitimately Shopify-signed session token whose `dest` claim is not a value covered by `ShopValidator::TRUSTED_SHOPIFY_DOMAINS`. The gem's own maintainers evidently consider this scenario plausible enough to defend against it in `ClientCredentials` and `migrate_to_expiring_token` (both explicitly call `sanitize!`), but the newer, now-canonical `exchange_token` path (which the library recommends and deprecates the manual `shop:` argument for) was not updated to apply the same allow-list check. This is an inconsistency between code paths handling the identical “send `client_secret` to `session.shop`” operation, not a theoretical worry — one path enforces the invariant, the other does not, for the exact same effective operation.

### Recommendation
In `ShopifyAPI::Auth::TokenExchange.exchange_token`, sanitize `dest_shop` through `Utils::ShopValidator.sanitize!` (mirroring `migrate_to_expiring_token` and `client_credentials`) before constructing `shop_session` and issuing the token-exchange HTTP request, e.g.:
```ruby
dest_shop = Utils::ShopValidator.sanitize!(jwt_payload.shop)
shop_session = ShopifyAPI::Auth::Session.new(shop: dest_shop)
```
This ensures the host that ultimately receives `client_id`/`client_secret` is always restricted to the same trusted-domain allow-list enforced elsewhere in the gem.

### Proof of Concept
1. Obtain (or cause to be minted) a validly Shopify-signed session token (`id_token`) whose `dest` claim is a host string not present in `Utils::ShopValidator::TRUSTED_SHOPIFY_DOMAINS`.
2. Call `ShopifyAPI::Auth::TokenExchange.exchange_token(session_token: id_token, requested_token_type: ...)`.
3. `jwt_payload.shop` returns the unsanitized `dest` value; `Clients::HttpClient.new(session: shop_session, base_path: "/admin/oauth")` builds `@base_uri = "https://#{session.shop}"` and POSTs a JSON body containing `client_id` and `client_secret` to `https://{dest}/admin/oauth/access_token`, exfiltrating the app's credentials to that host — with no `ShopValidator` check ever performed, unlike the equivalent `client_credentials`/`migrate_to_expiring_token` code paths.

### Citations

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

**File:** lib/shopify_api/auth/jwt_payload.rb (L47-50)
```ruby
      sig { returns(String) }
      def shop
        @dest.gsub("https://", "")
      end
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
