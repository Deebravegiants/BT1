### Title
Unvalidated `dest` claim used to route the app's `client_secret` in `TokenExchange.exchange_token` - ([File: lib/shopify_api/auth/token_exchange.rb])

### Summary
`ShopifyAPI::Auth::TokenExchange.exchange_token` derives the request host for the Shopify OAuth token endpoint directly from the JWT `dest` claim (`jwt_payload.shop`) without ever passing it through `Utils::ShopValidator.sanitize!`, unlike every sibling method in the same module/class family (`client_credentials`, `refresh_token.refresh_access_token`, `TokenExchange.migrate_to_expiring_token`) that all validate the `shop` string before using it to build the request host that receives `client_id`/`client_secret`.

### Finding Description
`ShopifyAPI::Auth::JwtPayload#shop` derives the shop host with a naive string substitution rather than strict domain parsing/allow-listing: [1](#0-0) 

`TokenExchange.exchange_token` takes this value (`dest_shop = jwt_payload.shop`) and uses it, unvalidated, to build the `Auth::Session` whose `shop` attribute becomes the `HttpClient`'s request host, in the same call that attaches the app's `client_id`/`client_secret` to the POST body: [2](#0-1) 

`Clients::HttpClient#initialize` builds the outgoing request's base URI directly from `session.shop` with no further validation: [3](#0-2) 

By contrast, every other credential-exchange entry point in this gem explicitly runs the shop string through `Utils::ShopValidator.sanitize!` — which restricts the host to `myshopify.com`/`myshopify.io`/`spin.dev`/`shop.dev`/`shopify.com` domains — before it is allowed to become the destination host for a request carrying the `client_secret`: [4](#0-3) [5](#0-4) [6](#0-5) 

`Utils::ShopValidator` exists precisely to close this class of gap (its own test suite is titled around "rejects attacker controlled domain"): [7](#0-6) [8](#0-7) 

The identity binding broken here is: `host validated by ShopValidator (used by every sibling grant-type method) ≠ host that receives client_secret in exchange_token`. `exchange_token` is the sole exception where the destination host for the app's `client_secret` is accepted as-is from the token's `dest` claim, gated only by JWT signature verification (`aud == Context.api_key`), not by an independent domain allow-list. `JwtPayload` does not cross-validate `dest` against `iss`, or apply `ShopValidator`, so nothing in the decode path constrains `dest` to a genuine Shopify domain shape beyond stripping the literal substring `"https://"`.

### Impact Explanation
If `dest` is ever attacker-influenced (e.g., a malformed/relayed session token, or any code path that manages to get a token past `JwtPayload`'s signature check with a non-Shopify `dest`), `exchange_token` will silently POST the app's `client_id` and `client_secret` to an attacker-controlled host — an SSRF that exfiltrates the app's `client_secret`, satisfying the High-impact criterion "SSRF with the app's credentials". This is a strictly weaker guarantee than every other credential-bearing method in the file, which is the concrete, provable root-cause defect in this gem's own code (missing call to `Utils::ShopValidator.sanitize!`), independent of how `dest` ends up attacker-influenced in a given deployment.

### Likelihood Explanation
Likelihood is Low-to-Moderate: under normal operation the JWT's HS256 signature (verified against `Context.api_secret_key`) constrains `dest` to values Shopify actually signed, so a fully unauthenticated attacker with no additional foothold cannot forge an arbitrary `dest`. However, the missing validation removes a defense-in-depth layer that this same codebase applies consistently everywhere else that a `shop` string is turned into a credential-bearing request host, making `exchange_token` the single inconsistent, unguarded path.

### Recommendation
In `lib/shopify_api/auth/token_exchange.rb`, validate `dest_shop` through `Utils::ShopValidator.sanitize!` (as done in `client_credentials`, `refresh_token`, and `migrate_to_expiring_token`) before constructing `shop_session`/`HttpClient`, so the host that ultimately receives `client_id`/`client_secret` is provably constrained to a trusted Shopify domain, matching the guarantees already enforced elsewhere in the library.

### Proof of Concept
Not independently reproducible with a fully unprivileged, credential-less request against a stock deployment, because exploitation requires a validly-signed JWT whose `dest` claim is attacker-controlled — which is normally impossible without the app's `api_secret_key`. The finding is a provable code-level root-cause inconsistency (absence of `Utils::ShopValidator.sanitize!` in `exchange_token` versus its presence in `client_credentials`, `refresh_token`, and `migrate_to_expiring_token`), cited above; I could not construct a concrete unauthenticated exploit chain within this gem's own code that forges a `dest` value without already possessing the secret, so full end-to-end exploitability is unconfirmed.

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

**File:** lib/shopify_api/auth/token_exchange.rb (L103-115)
```ruby
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

**File:** lib/shopify_api/auth/client_credentials.rb (L25-33)
```ruby
          validated_shop = Utils::ShopValidator.sanitize!(shop)
          shop_session = ShopifyAPI::Auth::Session.new(shop: validated_shop)
          body = {
            client_id: ShopifyAPI::Context.api_key,
            client_secret: ShopifyAPI::Context.api_secret_key,
            grant_type: CLIENT_CREDENTIALS_GRANT_TYPE,
          }

          client = Clients::HttpClient.new(session: shop_session, base_path: "/admin/oauth")
```

**File:** lib/shopify_api/auth/refresh_token.rb (L24-33)
```ruby
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

**File:** lib/shopify_api/utils/shop_validator.rb (L8-18)
```ruby
    module ShopValidator
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
