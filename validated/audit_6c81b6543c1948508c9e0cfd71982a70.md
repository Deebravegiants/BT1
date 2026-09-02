Found a concrete analog: an unvalidated `shop` parameter that is used directly to build the URL that receives the app's `client_id`/`client_secret`, in exactly the pattern that `ShopValidator.sanitize!` was introduced elsewhere to prevent.

### Title
SSRF exfiltrating `client_id`/`client_secret` via unvalidated `shop` in `TokenExchange.exchange_token` - (File: lib/shopify_api/auth/token_exchange.rb)

### Summary
`ShopifyAPI::Auth::TokenExchange.exchange_token` builds the OAuth token-exchange request URL from a `shop` value that is taken from an unauthenticated, attacker-controlled source (`dest_shop` from the session-token payload) and never passes it through `Utils::ShopValidator.sanitize!`, unlike every sibling method in the same module.

### Finding Description
`exchange_token` derives the request target from `jwt_payload.shop`, i.e. the `dest` claim of the JWT: [1](#0-0)  This value is used unvalidated to build `shop_session` and is passed straight into `Clients::HttpClient.new(session: shop_session, base_path: "/admin/oauth")`, which the client uses to compute the target host for the POST request that carries `client_id` and `client_secret`: [2](#0-1) 

`JwtPayload#shop` simply strips `"https://"` from the `dest` claim with no domain allowlist: [3](#0-2)  The only validation performed anywhere on the JWT is that `aud == Context.api_key`, `iss`/`nbf`/`exp` timing, and the HS256 signature with the app's own `api_secret_key`: [4](#0-3)  — nothing constrains `dest` to a `*.myshopify.com`/trusted Shopify domain.

Contrast this with the three sibling methods in the very same file and module — `migrate_to_expiring_token`, and the neighboring `RefreshToken.refresh_access_token` / `ClientCredentials.client_credentials` — which all explicitly call `Utils::ShopValidator.sanitize!(shop)` before constructing the session/host that receives `client_secret`: [5](#0-4) [6](#0-5) [7](#0-6)  `Utils::ShopValidator.sanitize!` is the gem's dedicated defense against exactly this class of bug — it restricts the shop host to `TRUSTED_SHOPIFY_DOMAINS` (`shopify.com`, `myshopify.io`, `myshopify.com`, `spin.dev`, `shop.dev`): [8](#0-7)  `exchange_token` is the one method in this family that omits the call, breaking the identity binding `host that receives client_secret == validated Shopify shop domain`.

This is the same bug class as the Absorber report: a value that participates in a security-relevant decision (which host is trusted to receive privileged material) is validated on one code path (`ShopValidator.sanitize!` in the sibling methods) but skipped on another path that handles equivalent data (`exchange_token`), producing an inconsistent, incorrect state (an SSRF target host that is not actually a verified Shopify domain).

### Impact Explanation
`Clients::HttpClient` builds the request host directly from `session.shop`, so an attacker-controlled `dest` claim value is used to target the HTTP POST that includes the app's `client_id` and `client_secret` in the body. Since the destination host is derived from unvalidated data, a request whose JWT `dest` claim is set to an attacker-controlled hostname causes the gem to POST `client_id`/`client_secret` (and the `subject_token`, i.e. the session token itself) to that attacker-controlled host — meeting the High/Critical bar of "SSRF with the app's credentials" / theft of the app's `client_secret`.

### Likelihood Explanation
The JWT is verified with HS256 using `Context.api_secret_key`, so exploitation requires a JWT signed with the app's own secret key. This is meaningfully different from a purely external, credential-less attacker; it typically requires either (a) a token that was already issued to the merchant/browser (e.g., replay/manipulation of the `dest` claim before signing is not possible without the secret, so this is only exploitable if the host application forwards an untrusted, unsigned `dest`-controlling value into a re-signed token, or if there is any other component in the ecosystem that signs tokens with attacker-influenced `dest`). Given the rules exclude findings that require `api_secret_key`, this significantly limits standalone exploitability by an unprivileged internet user acting alone against this gem in isolation, and I could not confirm within this gem's code a path where an entirely credential-less attacker can supply an arbitrary `dest` value that gets signed.

### Recommendation
Add the missing validation in `TokenExchange.exchange_token`, mirroring the other three methods:
```ruby
dest_shop = Utils::ShopValidator.sanitize!(jwt_payload.shop)
```
so all four methods in `ShopifyAPI::Auth` that build a `shop_session` used to send `client_id`/`client_secret` consistently enforce the same trusted-domain check.

### Proof of Concept
Not applicable as a standalone unauthenticated PoC — exploitation of `exchange_token`'s missing `ShopValidator.sanitize!` call requires a validly-signed JWT (signed with the app's own `api_secret_key`) whose `dest` claim is an attacker-controlled host, which this gem alone cannot produce. I could not verify a concrete, credential-free exploitation path within the gem's own code, so I flag this as a code-inconsistency finding (missing defense-in-depth relative to sibling methods) rather than a confirmed unauthenticated exploit.

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
