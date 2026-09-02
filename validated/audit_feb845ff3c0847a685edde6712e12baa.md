### Title
`TokenExchange.exchange_token` sends the app's `client_secret` to a host derived from an unvalidated JWT `dest` claim - (File: `lib/shopify_api/auth/token_exchange.rb`)

### Summary
`ShopifyAPI::Auth::TokenExchange.exchange_token` builds the request host that receives the app's `client_secret` and the merchant's session token directly from the JWT `dest` claim, without passing it through `Utils::ShopValidator.sanitize!` — the same validation every sibling OAuth-credential-exchange method (`client_credentials`, `refresh_token.refresh_access_token`, and `TokenExchange.migrate_to_expiring_token`) performs on their `shop` input before using it to build the request host.

### Finding Description
`JwtPayload#shop` only strips a literal `"https://"` prefix from the `dest` claim; it performs no host/domain validation: [1](#0-0) 

`exchange_token` takes this unvalidated value (`dest_shop`) and uses it, unsanitized, to build the `Session` whose `shop` becomes the request host for the token-exchange HTTP call that carries `client_id`/`client_secret`/`subject_token`: [2](#0-1) 

`HttpClient#initialize` builds the outbound request base URI directly from `session.shop`: [3](#0-2) 

Contrast this with every other credential-exchange method in the same file/module, which explicitly calls `Utils::ShopValidator.sanitize!(shop)` — raising `Errors::InvalidShopError` unless the host resolves to a trusted Shopify domain (`shopify.com`, `myshopify.io`, `myshopify.com`, `spin.dev`, `shop.dev`) — before constructing the session used for the outbound request:
- `migrate_to_expiring_token`: [4](#0-3) 
- `ClientCredentials.client_credentials`: [5](#0-4) 
- `RefreshToken.refresh_access_token`: [6](#0-5) 

`ShopValidator.sanitize_shop_domain`/`sanitize!` is the gem's designated mechanism for binding an arbitrary "shop" string to a trusted Shopify domain: [7](#0-6) 

The identity binding that should hold is: `host that receives client_secret == ShopValidator.sanitize!(claimed shop)`. In `exchange_token` this instead reduces to `host that receives client_secret == dest.gsub("https://", "")`, i.e. the request destination is bound only to whatever string Shopify's token issuer places in the `dest` claim, with no allowlist check against `ShopValidator::TRUSTED_SHOPIFY_DOMAINS` inside this gem.

### Impact Explanation
If `dest` can ever contain a value outside the trusted Shopify domain set (the gem's own test fixtures show `dest` formats varying across contexts — admin sessions use `"https://shop/admin"`-derived hosts, checkout UI extension tokens use bare hostnames without an `https://` prefix at all, e.g. `dest: "test-shop.myshopify.io"`), `exchange_token` would send the app's `client_id`, `client_secret`, and the raw session token (`subject_token`) to that host — an SSRF carrying the app's credentials, matching the "SSRF with the app's credentials" High-impact category. This is strictly weaker/inconsistent versus the other three sibling flows, which explicitly reject any `shop` value that doesn't resolve to a trusted domain.

### Likelihood Explanation
Exploitability is bounded by the fact that the JWT is HMAC-verified against `Context.api_secret_key` (or `old_api_secret_key`) in `JwtPayload#initialize`, so only a party holding that shared secret — normally only Shopify's own token issuer — can produce a token that passes validation: [8](#0-7)  This means a fully unprivileged internet user cannot forge the `dest` claim outright. The residual risk is a defense-in-depth gap: this method is the only OAuth-credential-exchange path in the module that omits the `ShopValidator` allowlist check that its three siblings apply, so it relies entirely on Shopify's token issuer never producing a `dest` outside the trusted set, rather than on this gem's own code enforcing that invariant. Given this dependency on Shopify's server-side guarantees, the direct, gem-only exploit path is not conclusively demonstrable from this codebase alone.

### Recommendation
In `TokenExchange.exchange_token`, validate `dest_shop` through `Utils::ShopValidator.sanitize!(dest_shop)` (mirroring `migrate_to_expiring_token`, `ClientCredentials.client_credentials`, and `RefreshToken.refresh_access_token`) before constructing `shop_session`, so the request host is always bound to an allow-listed trusted Shopify domain rather than trusting the raw `dest` claim string.

### Proof of Concept
Not independently reproducible from this gem alone: exploitation requires a validly HMAC-signed session token whose `dest` claim resolves (after stripping `"https://"`) to a non-trusted host, which requires either possession of `api_secret_key`/`old_api_secret_key` or a Shopify-issued token with an out-of-allowlist `dest` — neither of which is demonstrable purely through this gem's code. The code-level inconsistency (missing `ShopValidator.sanitize!` call unique to `exchange_token` versus its three sibling methods) is directly verifiable via the file/line citations above.

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

**File:** lib/shopify_api/auth/token_exchange.rb (L103-104)
```ruby
          validated_shop = Utils::ShopValidator.sanitize!(shop)
          shop_session = ShopifyAPI::Auth::Session.new(shop: validated_shop)
```

**File:** lib/shopify_api/clients/http_client.rb (L16-19)
```ruby
        api_host = Context.api_host

        @base_uri = T.let("https://#{api_host || session.shop}", String)
        @base_uri_and_path = T.let("#{@base_uri}#{base_path}", String)
```

**File:** lib/shopify_api/auth/client_credentials.rb (L25-26)
```ruby
          validated_shop = Utils::ShopValidator.sanitize!(shop)
          shop_session = ShopifyAPI::Auth::Session.new(shop: validated_shop)
```

**File:** lib/shopify_api/auth/refresh_token.rb (L24-25)
```ruby
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
