### Title
Token Exchange sends the app's `client_secret` to an unvalidated host derived from the JWT `dest` claim - ([File: lib/shopify_api/auth/token_exchange.rb])

### Summary
`ShopifyAPI::Auth::TokenExchange.exchange_token` derives the shop hostname it will contact directly from the session token's `dest` claim, without ever passing it through `Utils::ShopValidator`. That unvalidated hostname becomes the HTTPS host that receives an HTTP POST containing the app's `client_id` and `client_secret`. The sibling method `migrate_to_expiring_token`, in the very same file, does apply `Utils::ShopValidator.sanitize!` to its shop input before using it the same way — showing the library authors recognize this value needs validation, but the `dest`-derived path was left unchecked.

### Finding Description
`JwtPayload#shop` only strips a literal prefix from the `dest` claim, it performs no domain validation: [1](#0-0) 

`JwtPayload.new` verifies the token's signature and checks only `aud == Context.api_key`; it never checks that `iss`/`dest` are consistent with each other or that they match a trusted Shopify domain pattern: [2](#0-1) 

`TokenExchange.exchange_token` takes that raw value (`dest_shop`) and uses it, unsanitized, to build the `Session` that determines the request host, then puts the app's `client_id`/`client_secret` in the POST body sent to that host: [3](#0-2) 

Contrast this with `migrate_to_expiring_token` in the same module, which explicitly runs the shop string through `Utils::ShopValidator.sanitize!` — restricting the host to `TRUSTED_SHOPIFY_DOMAINS` (`shopify.com`, `myshopify.io`, `myshopify.com`, `spin.dev`, `shop.dev`) — before doing the identical "POST client_secret to this host" operation: [4](#0-3) [5](#0-4) 

`HttpClient` builds the request URL directly from `session.shop` with no further validation: [6](#0-5) 

The equality that should hold is: **host whose signature/authenticity was verified (JWT `aud`/HMAC check) == host that ultimately receives the app's `client_secret`**. Because the code only validates `aud` (which host issued/consumed the token key) and never constrains `dest` to a Shopify-owned domain, that equality is not enforced on the `exchange_token` path, whereas it is enforced on the `migrate_to_expiring_token` path in the same class.

### Impact Explanation
If the `dest` claim of a validly-signed session token can ever contain a value outside the Shopify-owned domain set (e.g., because the host application forwards a token whose `dest` was not strictly constrained, or because trust in `dest` is otherwise weaker than trust in an explicit shop parameter — exactly the class of gap `ShopValidator` was introduced to close for other callers), `exchange_token` will silently perform an HTTPS POST containing the app's `client_id` and `client_secret` to that host. That is credential exfiltration of the app's OAuth client secret (SSRF carrying the app's credentials), which can subsequently be used to complete OAuth/token-exchange flows as the app for any shop.

### Likelihood Explanation
Exploitation requires an attacker to obtain a session token that passes `JwtPayload`'s signature check (i.e., it is HS256-signed with the real `api_secret_key`) but whose `dest` value is not a genuine Shopify domain. In the normal, correctly-functioning Shopify session-token issuance flow this is difficult, since `dest` is set by Shopify's own token-minting process. However, the code contains no independent, library-side enforcement of this invariant — it relies entirely on upstream token issuance being correct, with no defense-in-depth check that `dest` matches `TRUSTED_SHOPIFY_DOMAINS` the way `ShopValidator.sanitize!` enforces for the `migrate_to_expiring_token` path. This inconsistency between two nearly-identical code paths in the same file is a concrete root-cause gap, even though full weaponization depends on factors (token-issuance behavior for custom/dev domains, `spin.dev`/`shop.dev` handling, etc.) that are outside this gem and not fully verifiable from the library alone.

### Recommendation
Route the `dest`-derived shop value through `Utils::ShopValidator.sanitize!` (as already done in `migrate_to_expiring_token`) before constructing the `Session`/`HttpClient` used to send the access-token/token-exchange request, and additionally cross-validate that `iss` and `dest` refer to the same host so the "host that was authenticated" and the "host that receives the client_secret" are provably the same value.

### Proof of Concept
1. Obtain (or otherwise cause the host application to pass in) a session token that is HS256-signed with the app's real `api_secret_key` but whose `dest` claim is `"https://attacker.example.com"` instead of a `*.myshopify.com`/trusted domain.
2. Call:
```ruby
ShopifyAPI::Auth::TokenExchange.exchange_token(
  session_token: crafted_token,
  requested_token_type: ShopifyAPI::Auth::TokenExchange::RequestedTokenType::OFFLINE_ACCESS_TOKEN,
)
```
3. `jwt_payload.shop` returns `"attacker.example.com"` unmodified [1](#0-0) ; `Session.new(shop: dest_shop)` and `Clients::HttpClient.new(session: shop_session, ...)` then build `@base_uri = "https://attacker.example.com"` [6](#0-5) , and the library POSTs `{client_id, client_secret, ...}` to `https://attacker.example.com/admin/oauth/access_token` [7](#0-6) , leaking the app's `client_secret` to the attacker-controlled host.

### Citations

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

**File:** lib/shopify_api/clients/http_client.rb (L16-19)
```ruby
        api_host = Context.api_host

        @base_uri = T.let("https://#{api_host || session.shop}", String)
        @base_uri_and_path = T.let("#{@base_uri}#{base_path}", String)
```
