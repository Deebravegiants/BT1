### Title
Missing shop-domain sanitization in `TokenExchange.exchange_token` allows the app's `client_secret` to be sent to an unvalidated host derived from the JWT `dest` claim - (File: `lib/shopify_api/auth/token_exchange.rb`)

### Summary
`ShopifyAPI::Auth::TokenExchange.exchange_token` takes the `shop` value used to build the outbound `access_token` request host directly from the session token's (`Shopify Id Token`) `dest` claim, and never passes it through `Utils::ShopValidator`, the sanitization routine that every other credential-issuing flow in this gem (`ClientCredentials`, `RefreshToken`) explicitly applies before using a shop string as a request host that receives `client_secret`.

### Finding Description
`JwtPayload#shop` derives the host purely by string substitution on the raw `dest` claim, with no domain allow-listing: [1](#0-0) 

`TokenExchange.exchange_token` takes that unvalidated value (`dest_shop`) and uses it to build the `Session` whose `shop` becomes the request host, then posts a body containing `ShopifyAPI::Context.api_secret_key` to `"#{host}/admin/oauth/access_token"`: [2](#0-1) 

By contrast, the sibling grant flows that also transmit `client_secret` explicitly bind the shop value to a trusted Shopify domain via `Utils::ShopValidator.sanitize!` before it is used to construct the request host: [3](#0-2) [4](#0-3) 

`ShopValidator` exists precisely to enforce the equality "host authorized to receive `client_secret`" == "host in `ShopValidator::TRUSTED_SHOPIFY_DOMAINS` (or configured `myshopify_domain`)": [5](#0-4) [6](#0-5) 

`token_exchange.rb` breaks that equality: the host that ultimately receives the `client_secret` HTTP POST is bound only to "whatever string the JWT `dest` claim contains after a naive `gsub`", not to a verified Shopify domain. This mirrors the AAVE-portal analog structurally: a downstream, security-critical action (crediting the router / here, sending the app's secret) is driven by a value that passed one check (JWT signature integrity / swap success) but was never bound to the actual invariant that matters (the router must be trusted / the host must be a genuine Shopify domain).

### Impact Explanation
If the `dest` claim of a session token can ever contain a value outside the intended `*.myshopify.com` / trusted Shopify domain space (e.g., through a misconfigured issuer, a `spin.dev`/custom-domain edge case not covered by the JWT audience check, or any future relaxation of Shopify's session-token issuance), this code path will POST the app's `client_id` and `client_secret` directly to that attacker-influenced host — i.e., SSRF carrying the app's credentials, and outright leakage of `client_secret` to a non-Shopify server. This matches the "High - SSRF with the app's credentials" / potential "Critical - theft of the app's client_secret" impact tiers.

### Likelihood Explanation
Low-to-Moderate. Exploitation requires a validly-signed session token whose `dest` claim is not itself already constrained to a genuine Shopify domain by whichever Shopify subsystem issues it. Since the JWT is HS256-signed with `api_secret_key` (a secret shared only between Shopify and the app), an attacker without that secret cannot themselves forge an arbitrary `dest`. However, the code contains no independent, defense-in-depth check — exactly the class of check present in the two sibling flows — so any weakness or edge case upstream in Shopify's token issuance (embedded contexts, dev/spin environments, proxying, custom domains) is not caught here, unlike in `ClientCredentials`/`RefreshToken`.

### Recommendation
In `TokenExchange.exchange_token`, sanitize `dest_shop` through `Utils::ShopValidator.sanitize!` (consistent with `ClientCredentials.client_credentials` and `RefreshToken.refresh_access_token`) before constructing `shop_session`, raising `Errors::InvalidShopError` for any value that is not a trusted Shopify domain, so the host that receives `client_secret` is always provably bound to `ShopValidator::TRUSTED_SHOPIFY_DOMAINS` (or the configured `myshopify_domain`) regardless of what the JWT `dest` claim contains.

### Proof of Concept
1. Construct/obtain a session token whose `dest` claim is `"https://attacker-controlled-host.example"` instead of a `*.myshopify.com` domain (any path by which such a token becomes validly signed — e.g. a relaxed/mis-issued token from a non-standard Shopify environment — satisfies this precondition).
2. Call:
```ruby
ShopifyAPI::Auth::TokenExchange.exchange_token(
  session_token: token_with_malicious_dest,
  requested_token_type: ShopifyAPI::Auth::TokenExchange::RequestedTokenType::OFFLINE_ACCESS_TOKEN,
)
```
3. `dest_shop` becomes `"attacker-controlled-host.example"` with no `ShopValidator` check.
4. `Clients::HttpClient.new(session: shop_session, base_path: "/admin/oauth")` builds a request whose host is `attacker-controlled-host.example`, and `client.request(...)` POSTs `{ client_id, client_secret, grant_type, subject_token, ... }` to `https://attacker-controlled-host.example/admin/oauth/access_token`, leaking the app's `client_secret` and the raw session token to the attacker's server — contrast with `ClientCredentials.client_credentials(shop: "attacker-controlled-host.example")`, which raises `ShopifyAPI::Errors::InvalidShopError` at the `Utils::ShopValidator.sanitize!` call instead of sending the request.

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
