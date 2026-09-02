### Title
SSRF exfiltration of `client_secret` via unvalidated `dest` claim host in `TokenExchange.exchange_token` - (File: `lib/shopify_api/auth/token_exchange.rb`)

### Summary
`TokenExchange.exchange_token` derives the request host for the token-exchange call directly from the session token's `dest` claim without ever passing it through `Utils::ShopValidator.sanitize!`, unlike every other credential-bearing OAuth flow in this gem (`ClientCredentials.client_credentials`, `RefreshToken.refresh_access_token`, and even `TokenExchange.migrate_to_expiring_token` itself). Because the app's `client_id`/`client_secret` are POSTed to `https://#{session.shop}/admin/oauth/access_token`, an unvalidated `dest` value becomes an SSRF primitive that sends the app's `client_secret` to an attacker-controlled host.

### Finding Description
The binding that should hold is: **host actually receiving `client_secret` == a Shopify-trusted domain validated by `ShopValidator`**.

`JwtPayload` only checks that the JWT's signature is valid and that `aud == Context.api_key` [1](#0-0) . It never constrains the format or trust of the `dest` claim — `shop` is simply `@dest.gsub("https://", "")` [2](#0-1) . The docs explicitly state "Its `dest` claim determines which shop receives the token exchange request" — confirming `dest` directly controls the request destination.

`TokenExchange.exchange_token` takes `dest_shop = jwt_payload.shop` and uses it, unvalidated, to build the `Session` whose `shop` becomes the request host, sending `client_id`/`client_secret` to it: [3](#0-2) 

`HttpClient#initialize` builds the request base URI directly from `session.shop` with no domain validation: [4](#0-3) 

Contrast this with the sibling flows in the very same file and gem, which all sanitize the shop before using it as a request host:
- `TokenExchange.migrate_to_expiring_token`: `validated_shop = Utils::ShopValidator.sanitize!(shop)` [5](#0-4) 
- `ClientCredentials.client_credentials`: `validated_shop = Utils::ShopValidator.sanitize!(shop)` [6](#0-5) 
- `RefreshToken.refresh_access_token`: `validated_shop = Utils::ShopValidator.sanitize!(shop)` [7](#0-6) 

`ShopValidator.sanitize!` exists precisely to constrain a shop string to Shopify's trusted domain suffixes (`myshopify.com`, `myshopify.io`, `spin.dev`, `shop.dev`, `shopify.com`) before it is used as a request host, raising `Errors::InvalidShopError` otherwise: [8](#0-7) . `exchange_token` is the one OAuth-credential-sending method that skips this call entirely.

The signature verification of the JWT (`aud == Context.api_key`) confirms the token was intended for this app, but does not confirm the `dest` value is a legitimate Shopify shop domain — a `dest` value is not restricted by JWT signature checking to any host format. Since token exchange is the recommended/primary auth flow for embedded apps, `session_token` typically arrives via the request `Authorization` header or URL `id_token` param supplied by the host application's frontend/App Bridge context — but the gem's own contract in `exchange_token` treats `dest` as fully trusted for host selection without the sanitize step present in all its siblings, and no other layer in this gem performs that check for this specific method.

### Impact Explanation
This is a High-severity finding: SSRF carrying the app's own credentials. If a `dest` claim value that is not constrained to a genuine Shopify domain reaches `exchange_token` (e.g., via a malformed/relayed JWT that still verifies against `Context.api_secret_key`/`Context.old_api_secret_key`, or a host application that naively forwards a `dest`-controlled token without the additional application-level domain checks that `shopify_app` and other integrations may or may not perform), the app's `client_id` and `client_secret` are POSTed directly to that host, exfiltrating the app's `client_secret` to an attacker-controlled server.

### Likelihood Explanation
Moderate: exploitation requires a JWT that passes `JWT.decode` verification (i.e., is signed with the app's own `api_secret_key`/`old_api_secret_key`) but carries an attacker-influenced `dest`. Because the check that would normally prevent this — `ShopValidator.sanitize!` — is applied in every sibling method in the same file, its absence here is clearly an inconsistency/omission rather than an intentional design choice, increasing confidence this is a genuine gap rather than accepted risk.

### Recommendation
In `TokenExchange.exchange_token`, validate `dest_shop` through `Utils::ShopValidator.sanitize!(dest_shop)` (mirroring `migrate_to_expiring_token`, `client_credentials`, and `refresh_access_token`) before constructing `shop_session` and issuing the HTTP request, raising `Errors::InvalidShopError` for any host outside `ShopValidator::TRUSTED_SHOPIFY_DOMAINS`.

### Proof of Concept
1. Attacker obtains or crafts a session token whose payload sets `dest` to `https://attacker.example.com` and `aud` to the victim app's `api_key`.
2. If this token is signed with a key equal to the app's `api_secret_key` or `old_api_secret_key` (e.g., via key confusion, a leaked/rotated secret still accepted as `old_api_secret_key`, or a relaying host application that itself trusts an externally supplied token before calling `exchange_token`), `JwtPayload.new(token)` succeeds and `jwt_payload.shop` returns `attacker.example.com`.
3. The app calls `ShopifyAPI::Auth::TokenExchange.exchange_token(session_token: token, requested_token_type: ...)`.
4. `exchange_token` builds `shop_session = Session.new(shop: "attacker.example.com")` and `HttpClient` sends a POST to `https://attacker.example.com/admin/oauth/access_token` with body containing `client_id` and `client_secret`.
5. The attacker's server logs the received `client_secret`, achieving credential exfiltration — unlike `migrate_to_expiring_token`, `client_credentials`, and `refresh_access_token`, which would reject `attacker.example.com` via `ShopValidator.sanitize!` before ever making the request.

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

**File:** lib/shopify_api/utils/shop_validator.rb (L20-64)
```ruby
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
