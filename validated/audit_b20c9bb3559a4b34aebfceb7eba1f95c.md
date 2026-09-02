### Title
Unvalidated `dest` Claim in Token Exchange Allows `client_secret` Delivery to a Non-Shopify Host - (File: `lib/shopify_api/auth/token_exchange.rb`)

### Summary
`TokenExchange.exchange_token` derives the destination host for the OAuth token-exchange HTTP request directly from the JWT session token's `dest` claim without passing it through `Utils::ShopValidator.sanitize!`, unlike every other credential-issuing flow in this gem (`ClientCredentials`, `RefreshToken`).

### Finding Description
`JwtPayload#shop` simply strips the `https://` prefix from the `dest` claim and returns it verbatim: [1](#0-0) . `TokenExchange.exchange_token` takes this value as `dest_shop` and uses it, unvalidated, to build the session that determines the request host: [2](#0-1) . That session is passed to `Clients::HttpClient`, which sets `@base_uri = "https://#{api_host || session.shop}"` — i.e., `session.shop` (the unsanitized `dest`) becomes the literal request host whenever `Context.api_host` is not configured: [3](#0-2) . The request body sent to that host includes `client_secret` in plaintext: [4](#0-3) .

Contrast this with `ClientCredentials.client_credentials` and `RefreshToken.refresh_access_token`, which both call `Utils::ShopValidator.sanitize!(shop)` before constructing the session that determines the request host: [5](#0-4) , [6](#0-5) . `ShopValidator.sanitize!` enforces that the host resolves to one of a fixed set of trusted Shopify domains (`shopify.com`, `myshopify.io`, `myshopify.com`, `spin.dev`, `shop.dev`) and rejects anything else: [7](#0-6) , [8](#0-7) . `TokenExchange` skips this check entirely — this is the identity binding that is broken: the "host that receives the `client_secret`" should equal "a validated trusted Shopify domain," but here it is instead bound only to "whatever string is present in the JWT `dest` claim."

This binding gap matters because `JwtPayload` validates only that the token is a syntactically/cryptographically well-formed HS256 JWT signed with `Context.api_secret_key` and that `aud == Context.api_key`: [9](#0-8) . It performs no validation of the `dest`/`iss` claim's domain against the trusted-domain allowlist that `ShopValidator` enforces elsewhere in this same file's sibling flows. There is no length, charset, scheme, or domain-suffix check on `dest` in `JwtPayload` itself.

### Impact Explanation
If a session token can be produced with an attacker-controlled `dest` value (e.g., via a compromised/malicious embedded-app iframe context, a proxy or host application defect that forwards a modified token, or any code path that is less strict than App Bridge's official token issuance), `exchange_token` will send the app's `client_id`/`client_secret` and `subject_token` (the raw session token) to that attacker-controlled host as part of the token-exchange POST body. This is credential exfiltration of the app's `client_secret` and constitutes SSRF carrying the app's credentials to a host chosen from unvalidated JWT payload content — matching the "High: SSRF with the app's credentials" / "credential leakage" impact class.

### Likelihood Explanation
Exploitation requires the caller to supply (or the environment to produce) a session token whose `dest` claim is not a legitimate Shopify domain while still passing the signature/`aud` checks. Because the token must be signed with `Context.api_secret_key` (a secret the app itself controls), the primary realistic trigger is not a remote attacker forging a token from scratch, but a broken invariant the gem itself fails to enforce as defense-in-depth — the same invariant it *does* enforce in `ClientCredentials` and `RefreshToken`. This asymmetry is the core defect: the gem's own design intends `dest`/shop values to be validated against trusted domains before being used as request hosts, and `TokenExchange` is the one flow where that step is missing.

### Recommendation
In `lib/shopify_api/auth/token_exchange.rb`, sanitize `dest_shop` through `Utils::ShopValidator.sanitize!` (as done in `ClientCredentials` and `RefreshToken`) before constructing `shop_session` and issuing the request, so the token-exchange request host is always bound to a validated, trusted Shopify domain rather than raw JWT payload content.

### Proof of Concept
1. Obtain or construct a session token whose `dest` claim is `https://attacker.example.com` but which is otherwise correctly HS256-signed with the app's `api_secret_key` and has `aud == Context.api_key` (e.g., via any code path that builds a session token outside of official App Bridge issuance, or a host-app bug that lets a value flow into this field).
2. Call `ShopifyAPI::Auth::TokenExchange.exchange_token(session_token: forged_token, requested_token_type: ...)`.
3. `JwtPayload.new(session_token).shop` returns `"attacker.example.com"` unchanged: [1](#0-0) .
4. `Clients::HttpClient.new(session: shop_session, ...)` builds `@base_uri = "https://attacker.example.com"`: [3](#0-2) .
5. The POST to `/admin/oauth/access_token` — containing `client_id` and `client_secret` — is sent to `attacker.example.com` instead of a Shopify-controlled host: [10](#0-9) .

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

**File:** lib/shopify_api/auth/token_exchange.rb (L52-74)
```ruby
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

**File:** lib/shopify_api/utils/shop_validator.rb (L56-64)
```ruby
        def sanitize!(shop, myshopify_domain: nil)
          host = sanitize_shop_domain(shop, myshopify_domain: myshopify_domain)
          if host.nil? || host.empty?
            raise Errors::InvalidShopError,
              "shop must be a trusted Shopify domain (see ShopValidator::TRUSTED_SHOPIFY_DOMAINS), got: #{shop.inspect}"
          end

          host
        end
```
