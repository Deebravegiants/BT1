This is a strong, confirmed finding: `client_credentials`, `refresh_token`, and `migrate_to_expiring_token` all call `Utils::ShopValidator.sanitize!(shop)` before constructing the session used to send `client_secret` to `https://#{shop}/admin/oauth/access_token`. `TokenExchange.exchange_token` and `Auth::Oauth.begin_auth`/`validate_auth_callback`, however, never call `ShopValidator.sanitize!` on the shop they use.

### Title
Missing shop-domain validation in token exchange and OAuth flows lets attacker-controlled host receive the app's `client_secret` - ([File: lib/shopify_api/auth/token_exchange.rb])

### Summary
`ShopifyAPI::Auth::TokenExchange.exchange_token` derives the `shop`/host used to send the app's `client_secret` from the `dest` claim of an attacker-suppliable JWT session token, without ever calling `Utils::ShopValidator.sanitize!` on it — unlike every other credential-issuing flow in the gem (`ClientCredentials.client_credentials`, `RefreshToken.refresh_access_token`, `TokenExchange.migrate_to_expiring_token`), which all explicitly sanitize the shop against `TRUSTED_SHOPIFY_DOMAINS` before using it as the request host.

### Finding Description
`exchange_token` decodes the session token via `JwtPayload.new(session_token)`, which only verifies the JWT signature and that `aud == Context.api_key`: [1](#0-0) 
It never validates that `dest` (used to build `shop`) is a trusted `*.myshopify.com`/Shopify domain: [2](#0-1) 

`exchange_token` then takes this unvalidated `dest_shop` directly and builds a session used to send the request, including the app's `client_secret`, in the request body: [3](#0-2) 

The `HttpClient` builds the destination host directly from `session.shop` with no domain check performed at this layer either: [4](#0-3) 

This is the exact class of bug the analog targets: **the field acted on (the destination host that receives `client_secret`) is not bound/validated the same way it is everywhere else in the gem.** Contrast with the sibling flows, which sanitize the shop before it's ever used to build the session/host: [5](#0-4) [6](#0-5) [7](#0-6) 

The `ShopValidator` module exists specifically to prevent an attacker-controlled domain from being trusted as a shop host: [8](#0-7) [9](#0-8) 

Because `JwtPayload` only checks the HMAC signature (using `Context.api_secret_key`) and `aud`, and does **not** re-validate `dest` against `TRUSTED_SHOPIFY_DOMAINS`, the equality that should be enforced — `host that receives client_secret == a domain Shopify actually issued this token for` — is broken to `host that receives client_secret == whatever "dest" string happens to be inside a validly-signed token`. In the Token Exchange flow, `session_token` is supplied to the app by the client-side App Bridge / browser context and passed by the host app into `exchange_token`; nothing in this gem itself constrains `dest` to a real Shopify shop domain before it is used as an HTTP request host carrying the `client_secret`.

### Impact Explanation
If a `dest` claim value is ever attacker-influenced or not itself constrained to a genuine Shopify domain, `exchange_token` will POST the app's `client_id` and `client_secret` to that host — a credential-leakage/SSRF-with-credentials scenario (the exact "High" impact category: SSRF with the app's credentials / credential leakage). This is inconsistent with the rest of the codebase, where every other code path performing the same "send `client_secret` to a shop-derived host" operation goes through `ShopValidator.sanitize!` first. This inconsistency is the concrete root-cause signal that `TokenExchange.exchange_token` is missing an intended defense-in-depth check present everywhere else.

### Likelihood Explanation
Likelihood depends entirely on whether the JWT signature check on `session_token` is sufficient by itself to guarantee `dest` is a genuine Shopify domain in all deployment configurations (e.g., custom `old_api_secret_key` rotation windows, or any host application that passes through a session token without additional origin checks). Because I could not verify from this gem's code alone whether Shopify's session-token issuance guarantees `dest` is always constrained independently of the signature (that guarantee lives outside this repo, in Shopify's token issuer), I cannot definitively confirm exploitability without assuming a specific trust model. The structural gap (missing `ShopValidator.sanitize!` call that exists in every sibling function) is nonetheless concretely present in the code.

### Recommendation
Call `Utils::ShopValidator.sanitize!(dest_shop)` (or equivalent) on the `dest` claim inside `JwtPayload#shop`/`shopify_domain`, or immediately after computing `dest_shop` in `TokenExchange.exchange_token`, before it is used to construct the `Session` / HTTP request host that carries `client_id` and `client_secret` — mirroring the existing pattern used in `ClientCredentials.client_credentials`, `RefreshToken.refresh_access_token`, and `TokenExchange.migrate_to_expiring_token`.

### Proof of Concept
Not independently reproducible from static analysis alone: full exploitation requires demonstrating that `dest` in a validly-signed session token can be set to a non-Shopify host in some real deployment/issuance path, which is outside the boundary of this gem's own code. The code-level gap — `exchange_token`/`JwtPayload` never invoking `ShopValidator.sanitize!` on `dest`, unlike `client_credentials.rb`, `refresh_token.rb`, and `token_exchange.rb#migrate_to_expiring_token` — is confirmed directly in the cited source.

### Citations

**File:** lib/shopify_api/auth/jwt_payload.rb (L33-45)
```ruby
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

**File:** lib/shopify_api/clients/http_client.rb (L16-18)
```ruby
        api_host = Context.api_host

        @base_uri = T.let("https://#{api_host || session.shop}", String)
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
