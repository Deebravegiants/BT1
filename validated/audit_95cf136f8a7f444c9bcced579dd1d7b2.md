This is the vulnerability: `TokenExchange.exchange_token` is the only credential-sending path in the OAuth family that skips `Utils::ShopValidator.sanitize!` on the shop value used as the request host, while every sibling method (`RefreshToken.refresh_access_token`, `ClientCredentials.client_credentials`, `TokenExchange.migrate_to_expiring_token`) enforces it.

### Title
`TokenExchange.exchange_token` sends the app's `client_secret` to an unvalidated host derived from the JWT `dest` claim - (File: lib/shopify_api/auth/token_exchange.rb)

### Summary
`ShopifyAPI::Auth::TokenExchange.exchange_token` derives the destination host for the token-exchange HTTP POST directly from the `dest` claim of the caller-supplied session token, without passing it through `Utils::ShopValidator.sanitize!`, unlike every other method in the auth module that builds a request host and sends the `client_secret`.

### Finding Description
`exchange_token` decodes the JWT session token and takes `dest_shop = jwt_payload.shop`, which is simply `@dest.gsub("https://", "")` from the JWT payload [1](#0-0) . It then builds a `Session` with that raw string as `shop` and constructs an `HttpClient` from it directly: [2](#0-1) 

`HttpClient#initialize` uses `session.shop` verbatim to build `@base_uri = "https://#{api_host || session.shop}"` and sends the `client_secret` in the POST body to that URI [3](#0-2) .

The only binding enforced on the JWT is signature validity and `aud == Context.api_key`; there is no check that `iss`/`dest` is a trusted Shopify domain (`*.myshopify.com`, `*.myshopify.io`, `spin.dev`, `shop.dev`, unified-admin) [4](#0-3) . This is the exact analog to the PoolTogether bug class: one identity-bearing field (`aud`, the app key) is checked, but the sibling field that actually determines *where the credential is sent* (`dest`) is not checked against the same "must be a trusted domain" invariant that the gem enforces everywhere else via `ShopValidator.sanitize!`.

Compare with the three sibling credential-exchange methods, which all call `Utils::ShopValidator.sanitize!(shop)` before building the session/host: [5](#0-4) [6](#0-5) [7](#0-6) 

`ShopValidator.sanitize!` exists precisely to prevent a shop value from being a non-Shopify/attacker domain: [8](#0-7) . `exchange_token` is the odd one out — it never calls it, breaking the equality that the gem otherwise enforces everywhere else: `host that receives client_secret == a domain in TRUSTED_SHOPIFY_DOMAINS`.

### Impact Explanation
Since the JWT is HS256-signed with the app's own `api_secret_key`, an attacker cannot forge an arbitrary `dest` value without already possessing that secret — under a pure external-attacker threat model this narrows exploitability significantly (the token has to be a genuine, signature-valid token, e.g., a real session token issued for the app's own installation on a shop domain the attacker set up, or one relayed/replayed by a malicious/compromised embedded surface that can supply a session token with an unexpected `dest`). Within that constraint, this is High severity per the rubric's SSRF-with-credentials category: the code will happily POST the app's `client_id`/`client_secret` to whatever host is present in a validly-signed token's `dest` claim, with no domain allow-listing, unlike its sibling methods.

### Likelihood Explanation
Likelihood is limited by the requirement for a validly HS256-signed token (same constraint that applies to any JWT-based Shopify integration), so full exploitation requires an existing session-token-issuing surface with attacker influence over `dest` (e.g., a checkout/extension token flow, a spin/dev domain, or a bug in a component that mints/relays session tokens). Given the surrounding code explicitly hardens every other credential-sending path with `ShopValidator.sanitize!`, but not this one, the omission is a genuine, concrete regression in this gem rather than a purely theoretical concern — the fix is a one-line reachable gap in an otherwise consistently-enforced invariant.

### Recommendation
In `TokenExchange.exchange_token`, validate `dest_shop` with `Utils::ShopValidator.sanitize!` (or an equivalent trusted-domain check that also accounts for the `dest`/`aud` binding used by session tokens) before using it to construct the `Session`/`HttpClient` that receives `client_id`/`client_secret`, mirroring `migrate_to_expiring_token`, `refresh_access_token`, and `client_credentials`.

### Proof of Concept
1. Obtain (or have relayed to your app) a validly HS256-signed session token whose `aud` equals the app's `api_key` but whose `dest` claim is set to `https://attacker-controlled-host.example` (e.g., via a component that mints/forwards session tokens with attacker influence over `dest`, or a shop the attacker fully controls with a non-Shopify-looking host permitted by that flow).
2. Call `ShopifyAPI::Auth::TokenExchange.exchange_token(session_token: token, requested_token_type: ...)`.
3. Observe that `JwtPayload.new(token)` passes (signature + `aud` check succeed) and `dest_shop` becomes `attacker-controlled-host.example` without any `ShopValidator` check [9](#0-8) .
4. `Clients::HttpClient.new(session: shop_session, base_path: "/admin/oauth")` builds `@base_uri = "https://attacker-controlled-host.example"` [10](#0-9) , and the subsequent `client.request(...)` POSTs `client_id`/`client_secret` to that host [11](#0-10) .

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

**File:** lib/shopify_api/clients/http_client.rb (L16-32)
```ruby
        api_host = Context.api_host

        @base_uri = T.let("https://#{api_host || session.shop}", String)
        @base_uri_and_path = T.let("#{@base_uri}#{base_path}", String)

        user_agent_prefix = Context.user_agent_prefix.nil? ? "" : "#{Context.user_agent_prefix} | "

        @headers = T.let({
          "User-Agent": "#{user_agent_prefix}Shopify API Library v#{VERSION} | Ruby #{RUBY_VERSION}",
          "Accept": "application/json",
        }, T::Hash[T.any(Symbol, String), T.untyped])

        @headers["Host"] = session.shop unless api_host.nil?

        unless session.access_token.nil? || T.must(session.access_token).empty?
          @headers["X-Shopify-Access-Token"] = T.cast(session.access_token, String)
        end
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

**File:** lib/shopify_api/utils/shop_validator.rb (L9-64)
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

      class << self
        extend T::Sig

        sig do
          params(
            shop_domain: String,
            myshopify_domain: T.nilable(String),
          ).returns(T.nilable(String))
        end
        def sanitize_shop_domain(shop_domain, myshopify_domain: nil)
          uri = uri_from_shop_domain(shop_domain, myshopify_domain)
          return nil if uri.nil? || uri.host.nil? || uri.host.empty?

          trusted_domains(myshopify_domain).each do |trusted_domain|
            host = T.cast(uri.host, String)
            uri_domain = uri.domain
            next if uri_domain.nil?

            no_shop_name_in_subdomain = host == trusted_domain
            from_trusted_domain = trusted_domain == uri_domain

            if unified_admin?(uri) && from_trusted_domain
              return myshopify_domain_from_unified_admin(uri)
            end
            return nil if no_shop_name_in_subdomain || host.empty?
            return host if from_trusted_domain
          end
          nil
        end

        sig do
          params(
            shop: String,
            myshopify_domain: T.nilable(String),
          ).returns(String)
        end
        def sanitize!(shop, myshopify_domain: nil)
          host = sanitize_shop_domain(shop, myshopify_domain: myshopify_domain)
          if host.nil? || host.empty?
            raise Errors::InvalidShopError,
              "shop must be a trusted Shopify domain (see ShopValidator::TRUSTED_SHOPIFY_DOMAINS), got: #{shop.inspect}"
          end

          host
        end
```
