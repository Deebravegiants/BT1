### Title
Inconsistent shop-domain validation in `TokenExchange.exchange_token` allows `client_secret` to be routed to a host not covered by the trusted-domain allowlist - (File: `lib/shopify_api/auth/token_exchange.rb`)

### Summary
The gem has multiple sibling OAuth-flow methods (`ClientCredentials.client_credentials`, `RefreshToken.refresh_access_token`, `TokenExchange.migrate_to_expiring_token`) that all call `Utils::ShopValidator.sanitize!(shop)` before using the shop value to build the HTTP client that transmits the app's `client_secret`. `TokenExchange.exchange_token`, which performs the same kind of request (POST `client_secret` to `https://#{shop}/admin/oauth/access_token`), is implemented separately and skips this validation step entirely, taking the shop value straight from the JWT payload instead.

### Finding Description
`ClientCredentials.client_credentials`, `RefreshToken.refresh_access_token`, and `TokenExchange.migrate_to_expiring_token` each do: [1](#0-0) [2](#0-1) [3](#0-2) 

i.e. `validated_shop = Utils::ShopValidator.sanitize!(shop)` — enforcing that the destination host is a `*.myshopify.com`/`myshopify.io`/`spin.dev`/`shop.dev` domain (or a configured `myshopify_domain`) — before building `ShopifyAPI::Auth::Session.new(shop: validated_shop)` and passing it to `Clients::HttpClient`, which derives the request's base URI directly from `session.shop`: [4](#0-3) 

`TokenExchange.exchange_token`, however, takes the shop straight from the (unvalidated for domain shape) `dest` claim of the JWT payload and uses it unchanged to build the session/base URI that receives `client_secret`: [5](#0-4) [6](#0-5) 

`JwtPayload` only checks `aud == Context.api_key`; it never validates that `dest`/`iss` is a trusted Shopify-owned host: [7](#0-6) 

This breaks the identity binding: "the shop that is trusted to receive `client_secret`" (equality enforced by `ShopValidator::TRUSTED_SHOPIFY_DOMAINS` in three sibling methods) is not equal to "the shop actually used to build the HTTP client base URI" in `exchange_token` (raw `dest` claim, unchecked against the allowlist). This is the same class of defect as the ERC20 report: near-duplicate logic implemented inconsistently, where one copy carries a security check the other lacks, undermining maintainability and creating a latent gap in the shop-domain trust boundary.

### Impact Explanation
If `dest`/`iss` in a validly-HS256-signed session token were ever anything other than a genuine `*.myshopify.com`-style host (e.g., due to a future Shopify format change, custom infra, or reuse of `old_api_secret_key`/`api_secret_key` across environments), `exchange_token` would build an HTTP request to that host and place the app's `client_secret` in the POST body with no allowlist check — matching the report's High-impact class ("SSRF with the app's credentials"). All three sibling methods in the same module/file already treat this as a security-relevant check worth enforcing, underscoring that its absence here is unintentional inconsistency rather than a deliberate design choice.

### Likelihood Explanation
Exploitability is bounded by the fact that `dest` is inside a JWT that must carry a valid HS256 signature over `Context.api_secret_key` (or `old_api_secret_key`), so an external attacker without the app secret cannot forge an arbitrary `dest`. This limits the practical likelihood today, but the missing defense-in-depth check is a genuine, reachable inconsistency in code that already treats this exact validation as necessary in three other call sites performing the identical operation (sending `client_secret` to a shop-derived host).

### Recommendation
Apply `Utils::ShopValidator.sanitize!` (or equivalent) to `jwt_payload.shop`/`dest` before constructing `shop_session` in `TokenExchange.exchange_token`, exactly as done in `client_credentials`, `refresh_access_token`, and `migrate_to_expiring_token`, so all methods that route `client_secret` to a shop-derived host share the same trusted-domain check.

### Proof of Concept
Not applicable as a working exploit — under current Shopify token-issuance guarantees, a validly-signed session token's `dest` claim cannot be attacker-controlled without possession of `api_secret_key`. This finding documents a code-consistency/defense-in-depth gap rather than a demonstrated bypass: [8](#0-7)

### Citations

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

**File:** lib/shopify_api/auth/token_exchange.rb (L65-65)
```ruby
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

**File:** lib/shopify_api/auth/jwt_payload.rb (L43-51)
```ruby
        raise ShopifyAPI::Errors::InvalidJwtTokenError,
          "Session token had invalid API key" unless @aud == Context.api_key
      end

      sig { returns(String) }
      def shop
        @dest.gsub("https://", "")
      end
      alias_method :shopify_domain, :shop
```
