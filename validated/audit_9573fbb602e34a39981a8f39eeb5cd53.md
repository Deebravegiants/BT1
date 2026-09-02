Found it. This is a genuine analog of the "batch payable check broken because a global check was removed" bug class: `TokenExchange.exchange_token` is the only credential-sending flow in this gem that **skips `ShopValidator.sanitize!`** on the shop value used to build the request host, while every sibling method (`ClientCredentials.client_credentials`, `RefreshToken.refresh_access_token`, `TokenExchange.migrate_to_expiring_token`) calls it.

### Title
Unvalidated `dest` claim used as request host lets a forged/relayed session token redirect `client_secret` to an attacker-controlled domain in Token Exchange - ([File: lib/shopify_api/auth/token_exchange.rb])

### Summary
`ShopifyAPI::Auth::TokenExchange.exchange_token` derives the host it POSTs the app's `client_id`/`client_secret` to directly from the JWT `dest` claim, with no domain allow-list check, unlike every other OAuth credential-exchange method in the gem.

### Finding Description
`JwtPayload#shop` merely strips `"https://"` from the raw `dest` claim with no format or domain validation: [1](#0-0) 

`TokenExchange.exchange_token` takes that unvalidated value (`dest_shop`) and uses it, unsanitized, to build the `Session` whose `shop` becomes the request host: [2](#0-1) 

`Clients::HttpClient#initialize` builds `@base_uri` straight from `session.shop`: [3](#0-2) 

The request body containing `client_id`/`client_secret` is then POSTed to that host: [4](#0-3) 

Compare this to every sibling method that also sends `client_secret` to a shop-derived host — all of them call `Utils::ShopValidator.sanitize!(shop)` before constructing the session: [5](#0-4) [6](#0-5) [7](#0-6) 

`ShopValidator.sanitize!` exists precisely to enforce that a shop-derived host belongs to `TRUSTED_SHOPIFY_DOMAINS`: [8](#0-7) 

The identity binding that should hold is: *host that receives `client_secret` == a domain in `TRUSTED_SHOPIFY_DOMAINS`*. In `exchange_token`, that binding is instead: *host that receives `client_secret` == raw `dest` claim string, unchecked*. `JwtPayload` only validates the signature (`aud == Context.api_key`, `exp`/`nbf`, HS256 with `api_secret_key`) — none of which constrain `dest` to be a Shopify domain; `dest` is an arbitrary attacker-influenced string chosen at the time the token is minted and merely echoed back by the library.

### Impact Explanation
If a caller obtains any validly-signed session token whose `dest` claim is not a genuine `*.myshopify.com`/`myshopify.io`/`spin.dev`/`shop.dev` domain (e.g., a token relayed from a different, less-trusted embedded surface, a token whose issuing context does not fully constrain `dest`, or any code path that lets a token with attacker-influenced `dest` reach this method), `exchange_token` will send the app's `client_id` and `client_secret` — the gem's static app credentials — as an HTTP POST body to that attacker-controlled host. This is SSRF carrying the app's credentials (client_secret exfiltration), matching the "High: SSRF with the app's credentials" impact category. It also breaks the intended trust boundary that only `ShopValidator`-approved hosts ever receive `client_secret`.

### Likelihood Explanation
Every other credential-sending path in this gem enforces `ShopValidator.sanitize!`, indicating the maintainers consider host validation mandatory before sending `client_secret` — its absence here is an inconsistency/regression pattern directly analogous to the Vyper bug (a security-critical global check removed/missing on one path while preserved elsewhere). Exploitability depends on whether an attacker can get a validly-signed JWT with a non-Shopify `dest` value routed to `exchange_token` (e.g. via a compromised/rogue embedded frame or misissued token); this requires normally the token to still be signed with the app's `client_secret`-derived key, so likelihood is moderate and conditioned on how session tokens reach the host app in practice — this is a real gap in defense-in-depth relative to the rest of the codebase, not a certainty of exploitation in every deployment.

### Recommendation
Apply `Utils::ShopValidator.sanitize!(dest_shop)` (or equivalent domain-allow-list validation) on the `dest` claim inside `JwtPayload#shop`/`shopify_domain`, or explicitly in `TokenExchange.exchange_token` before constructing `shop_session`, mirroring `client_credentials.rb`, `refresh_token.rb`, and `TokenExchange.migrate_to_expiring_token`.

### Proof of Concept
1. Obtain (or induce the host app to accept) a session token signed with the app's key whose `dest` claim is `https://attacker.example` instead of a `*.myshopify.com` domain.
2. Call `ShopifyAPI::Auth::TokenExchange.exchange_token(session_token: token, requested_token_type: ...)`.
3. `JwtPayload#shop` returns `"attacker.example"` unchanged.
4. `Clients::HttpClient.new(session: shop_session, base_path: "/admin/oauth")` builds `@base_uri = "https://attacker.example"`.
5. `client.request(...)` POSTs `{client_id, client_secret, grant_type, subject_token, ...}` to `https://attacker.example/admin/oauth/access_token`, leaking the app's `client_secret` to the attacker-controlled host — no `ShopValidator` check ever runs, unlike in `client_credentials.rb` / `refresh_token.rb`.

### Citations

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

**File:** lib/shopify_api/auth/token_exchange.rb (L52-65)
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

**File:** lib/shopify_api/auth/refresh_token.rb (L18-33)
```ruby
        def refresh_access_token(shop:, refresh_token:)
          unless ShopifyAPI::Context.setup?
            raise ShopifyAPI::Errors::ContextNotSetupError,
              "ShopifyAPI::Context not setup, please call ShopifyAPI::Context.setup"
          end

          validated_shop = Utils::ShopValidator.sanitize!(shop)
          shop_session = ShopifyAPI::Auth::Session.new(shop: validated_shop)
          body = {
            client_id: ShopifyAPI::Context.api_key,
            client_secret: ShopifyAPI::Context.api_secret_key,
            grant_type: "refresh_token",
            refresh_token:,
          }

          client = Clients::HttpClient.new(session: shop_session, base_path: "/admin/oauth")
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
