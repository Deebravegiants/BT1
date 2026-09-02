Confirmed: `HttpClient#initialize` builds the outbound request host directly from `session.shop` (`@base_uri = "https://#{api_host || session.shop}"`) [1](#0-0) , and this is exactly the host that receives the `client_id`/`client_secret` in the token-exchange body [2](#0-1) .

### Title
Unvalidated `dest` claim from session-token JWT used as SSRF/credential-exfiltration destination in `TokenExchange.exchange_token` - (File: lib/shopify_api/auth/token_exchange.rb)

### Summary
`TokenExchange.exchange_token` decodes the caller-supplied `session_token`, extracts the shop directly from the JWT's `dest` claim, and uses it *unsanitized* as the destination host to which it POSTs the app's `client_id` and `client_secret` for the OAuth token-exchange request.

### Finding Description
`exchange_token` builds the shop entirely from `jwt_payload.shop`, which is just `dest.gsub("https://", "")` with no further validation: [3](#0-2) [4](#0-3) . This value is passed straight into `Session.new(shop: dest_shop)` and then into `Clients::HttpClient.new(session: shop_session, base_path: "/admin/oauth")`, which sets `@base_uri = "https://#{session.shop}"` and sends the POST containing `client_id`/`client_secret` there [1](#0-0) .

Compare this to the sibling method `migrate_to_expiring_token`, which validates the shop with `Utils::ShopValidator.sanitize!(shop)` before constructing the session/host [5](#0-4) , and `ShopValidator` itself enforces an allow-list of trusted Shopify domains (`myshopify.com`, `myshopify.io`, `shopify.com`, `spin.dev`, `shop.dev`) [6](#0-5) . `exchange_token` has no equivalent call — the identity binding "host that receives the `client_secret`" ≟ "a Shopify-owned domain validated by `ShopValidator`" is broken: it is only bound to "whatever string appears in the JWT `dest` claim," not to a merchant/shop identity constrained to Shopify's domain space.

`JwtPayload#initialize` only verifies the HS256 signature against `Context.api_secret_key`/`old_api_secret_key` and checks `aud == Context.api_key`; it never validates that `dest`/`iss` are restricted to Shopify's trusted domains [7](#0-6) .

### Impact Explanation
Because the app's `client_secret` and `client_id` are sent to a host derived solely from the JWT `dest` claim without domain allow-listing, if an attacker can influence or supply a `session_token` (id_token) accepted by the app's `exchange_token` call — e.g., via an app's endpoint that forwards the `id_token` query param/Authorization header verbatim from an untrusted request — a token with a signature the app will still accept (via `old_api_secret_key` fallback windows, or any future weakening of validation) and an attacker-controlled `dest` value could cause the library to make an SSRF request carrying the app's `client_id`/`client_secret` to an attacker-controlled host. This matches the report's bug class (a value used in a security-critical operation without validating it stays within the expected trust domain) mapped onto this gem's "host that receives the app's `client_secret`" binding, and falls under the in-scope "High - SSRF with the app's credentials" impact category.

### Likelihood Explanation
Exploitation requires the attacker to get a validly-signed JWT accepted by `JwtPayload` (signature checked against `api_secret_key`/`old_api_secret_key`) with a non-Shopify `dest` claim. Under normal operation Shopify itself signs these tokens with a legitimate `dest`, so this is not trivially exploitable by a pure network attacker without any credential — but the missing allow-list check is a real gap: it means the library places no independent guarantee on the destination host, relying entirely on JWT signature validation as the only safeguard, unlike the parallel `migrate_to_expiring_token` path which double-checks with `ShopValidator`. This is a defense-in-depth gap rather than a directly-demonstrated bypass with only unprivileged internet access, given current information.

### Recommendation
In `TokenExchange.exchange_token`, validate `dest_shop` through `Utils::ShopValidator.sanitize!` (as already done in `migrate_to_expiring_token`) before constructing `shop_session`/`HttpClient`, ensuring the token-exchange request (and the embedded `client_secret`) can only ever be sent to a domain in `ShopValidator::TRUSTED_SHOPIFY_DOMAINS`.

### Proof of Concept
1. Obtain a `session_token` whose signature validates against the app's configured `api_secret_key` (or `old_api_secret_key`) but whose `dest` claim is set to an attacker-controlled host (e.g. `https://attacker.example`).
2. Call `ShopifyAPI::Auth::TokenExchange.exchange_token(session_token: token, requested_token_type: ...)`.
3. `JwtPayload.new` accepts the token (only checks signature + `aud`) [8](#0-7) ; `dest_shop` becomes `attacker.example`.
4. `HttpClient` builds `@base_uri = "https://attacker.example"` [1](#0-0)  and POSTs the JSON body containing `client_id`/`client_secret` to `https://attacker.example/admin/oauth/access_token` [9](#0-8) , exfiltrating the app's credentials to the attacker's server.

### Citations

**File:** lib/shopify_api/clients/http_client.rb (L16-19)
```ruby
        api_host = Context.api_host

        @base_uri = T.let("https://#{api_host || session.shop}", String)
        @base_uri_and_path = T.let("#{@base_uri}#{base_path}", String)
```

**File:** lib/shopify_api/auth/token_exchange.rb (L39-74)
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
            client.request(
              Clients::HttpRequest.new(
                http_method: :post,
                path: "access_token",
                body: body,
                body_type: "application/json",
              ),
            )
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

**File:** lib/shopify_api/auth/jwt_payload.rb (L23-51)
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
