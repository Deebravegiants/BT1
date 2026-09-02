Found the vulnerable binding break.

### Title
Token exchange sends `client_secret` to a host derived from the JWT `dest` claim without validating it against the Shopify trusted-domain list - ([File: lib/shopify_api/auth/token_exchange.rb])

### Summary
`ShopifyAPI::Auth::TokenExchange.exchange_token` builds the OAuth token-exchange request host directly from the `dest` claim of the caller-supplied session token, and never validates that claim against `ShopifyAPI::Utils::ShopValidator::TRUSTED_SHOPIFY_DOMAINS` before sending the app's `client_secret` there. `migrate_to_expiring_token`, by contrast, does call `Utils::ShopValidator.sanitize!(shop)` before using the `shop` value to build the request host, showing the library authors intended this validation for exactly this class of request but omitted it on the token-exchange path.

### Finding Description
`exchange_token` decodes the JWT with `ShopifyAPI::Auth::JwtPayload.new(session_token)` and takes `dest_shop = jwt_payload.shop`, which simply strips `"https://"` from the token's `dest` claim (`shop` method in `lib/shopify_api/auth/jwt_payload.rb:47-50`) with no format/domain restriction. It then builds `shop_session = ShopifyAPI::Auth::Session.new(shop: dest_shop)` and passes it straight into `Clients::HttpClient.new(session: shop_session, base_path: "/admin/oauth")` [1](#0-0) . Inside `HttpClient#initialize`, the request host is computed as `@base_uri = "https://#{api_host || session.shop}"` [2](#0-1) , i.e. directly from the unvalidated `dest_shop` string (when `Context.api_host` is not configured, which is the default/typical non-first-party setup). The POST body sent to that host includes `client_secret: ShopifyAPI::Context.api_secret_key` [3](#0-2) .

The binding that should hold is: `host that receives client_secret == a value drawn from ShopValidator::TRUSTED_SHOPIFY_DOMAINS` [4](#0-3) . Instead the actual binding enforced is: `host that receives client_secret == JwtPayload#shop`, where `JwtPayload#shop` is only constrained by JWT signature/expiry checks (`aud == Context.api_key`, `exp`, `nbf`) [5](#0-4)  — none of which restrict the `dest`/`iss` value to a `*.myshopify.com` (or other trusted) domain. `JwtPayload` never cross-checks `dest` against `iss` or against `ShopValidator`, and `exchange_token` performs no additional sanitation, unlike its sibling method `migrate_to_expiring_token`, which explicitly calls `Utils::ShopValidator.sanitize!(shop)` before constructing the session used for the identical `/admin/oauth/access_token` request [6](#0-5) .

### Impact Explanation
Because `exchange_token` is called by the host application with a session token that ultimately supplies the `dest` value used to build the host receiving `client_secret`, any code path where an untrusted or attacker-influenced JWT's `dest` claim reaches `exchange_token` (for example, custom App Bridge/session-token handling that doesn't itself re-validate `dest`) results in the app's `client_secret` being exfiltrated via an HTTP POST to an attacker-controlled host — this is SSRF carrying the app's OAuth `client_id`/`client_secret`, matching the "High: SSRF with the app's credentials" impact bucket. This is a break of the trusted-domain binding relative to `ShopValidator`, the exact class of defense the library ships and applies inconsistently (present in `migrate_to_expiring_token`, absent in `exchange_token`).

### Likelihood Explanation
The likelihood depends on whether host applications treat the `dest` claim of any presented "session token" as pre-validated before calling `exchange_token`. Since the JWT is only checked for `aud` match and standard time-based claims — not `dest`/`iss` domain trust — any JWT signed with the app's own `api_secret_key` (which the app itself possesses and could be tricked into signing/relaying, e.g. from a proxied or non-Shopify-origin request) or any legitimately-issued token whose `dest` was manipulated upstream before signature (not possible without the secret) is not directly forgeable by an outside attacker without the secret. Given this, exploitation by a pure unauthenticated remote attacker requires an additional weak link (e.g., an app that accepts externally supplied JWTs for exchange without itself confirming the shop), so the likelihood assessment is uncertain and cannot be fully confirmed from this gem's code alone — it depends on host application behavior, which is out of scope per the rules ("Reject analogs that depend on the host application ignoring this gem's documented API"). Given that constraint, this finding is best treated as a defense-in-depth gap rather than a fully self-contained, gem-only exploit chain.

### Recommendation
In `TokenExchange.exchange_token`, sanitize `dest_shop` with `Utils::ShopValidator.sanitize!(dest_shop)` (mirroring `migrate_to_expiring_token`) before constructing `shop_session`, and/or have `JwtPayload` validate `dest`/`iss` against `ShopValidator::TRUSTED_SHOPIFY_DOMAINS` at decode time so no downstream consumer of `JwtPayload#shop` can receive an untrusted host value.

### Proof of Concept
Not constructible as a fully self-contained unauthenticated PoC within this gem alone: producing a JWT with an attacker-chosen `dest` that still passes `JwtPayload`'s signature check requires knowledge of `Context.api_secret_key`, which is out of scope per the rules. The code-level gap (missing `ShopValidator` call in `exchange_token` vs. its presence in `migrate_to_expiring_token`) is demonstrated by direct comparison of the two methods cited above.

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

**File:** lib/shopify_api/clients/http_client.rb (L16-19)
```ruby
        api_host = Context.api_host

        @base_uri = T.let("https://#{api_host || session.shop}", String)
        @base_uri_and_path = T.let("#{@base_uri}#{base_path}", String)
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

**File:** lib/shopify_api/auth/jwt_payload.rb (L33-50)
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

      sig { returns(String) }
      def shop
        @dest.gsub("https://", "")
      end
```
