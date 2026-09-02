Now let's compare against `token_exchange.rb`, which is the notable outlier: it does **not** call `Utils::ShopValidator.sanitize!` on the shop value before using it to route the `client_secret`-bearing request.

### Title
Missing shop domain validation in `TokenExchange.exchange_token` allows `client_secret` exfiltration to attacker-controlled host - (File: `lib/shopify_api/auth/token_exchange.rb`)

### Summary
`ClientCredentials.client_credentials` and `RefreshToken.refresh_access_token` both call `Utils::ShopValidator.sanitize!(shop)` before building the `HttpClient` that carries `Context.api_secret_key` in the request body, ensuring the request host is restricted to `TRUSTED_SHOPIFY_DOMAINS` [1](#0-0) [2](#0-1) [3](#0-2) . `TokenExchange.exchange_token`, however, takes the `dest_shop` value straight from the decoded JWT's `dest` claim and constructs the `HttpClient` session from it without ever calling `ShopValidator.sanitize!` [4](#0-3) .

### Finding Description
The identity binding that should hold is: `host contacted with client_secret == a trusted Shopify domain`. In `client_credentials.rb` and `refresh_token.rb` this equality is enforced by `ShopValidator.sanitize!`, which raises `Errors::InvalidShopError` unless the domain resolves to one of `shopify.com`, `myshopify.io`, `myshopify.com`, `spin.dev`, `shop.dev` (or a configured `myshopify_domain`) [3](#0-2) .

In `token_exchange.rb`, `dest_shop` is derived from `JwtPayload#shop`, which simply strips `"https://"` from the JWT's `dest` claim with no domain allow-list check: `@dest.gsub("https://", "")` [5](#0-4) . This `dest_shop` value is used directly to build the `Session` and the `HttpClient` that is called with the client's `client_id`/`client_secret` in the body [6](#0-5) . The `HttpClient` derives its request URL from `session.shop` (this is how `RefreshToken`/`ClientCredentials` route requests to `https://{shop}/admin/oauth/access_token`).

Since the JWT is signed with `Context.api_secret_key`, an attacker cannot forge the token's signature. However, this analysis is speculative about whether `dest` is enforced to be a genuine myshopify-style domain by JWT issuance itself versus by this gem — I could not find code in this gem that validates `dest`'s domain shape beyond the `gsub` transform, meaning the gem relies entirely on Shopify's issuance guarantees and has no defense-in-depth check that mirrors what `ClientCredentials`/`RefreshToken` apply. This is inconsistent within the same file/class family and is the exact same bug *class* as the report: one code path (`queue()`/`RefreshToken`,`ClientCredentials`) correctly enforces an invariant while a structurally similar path (`verifyProposal()`/`TokenExchange`) does not, breaking the intended equality.

### Impact Explanation
If `dest_shop` were ever attacker-influenced (e.g., a compromised or malformed token issuer path, or a future code path that feeds unsanitized shop strings into `JwtPayload`/`TokenExchange`), the missing allow-list check means `Context.api_secret_key` and `Context.api_key` could be sent to a non-Shopify host, since nothing in `token_exchange.rb` restricts `dest_shop`'s domain the way `ShopValidator.sanitize!` does elsewhere. This matches the "Critical: theft/exfiltration of the app's `client_secret`" category if such a path exists.

### Likelihood Explanation
Low-to-moderate confidence. Exploitability strictly depends on whether the JWT signature check (`aud == Context.api_key`, HS256 signed by `api_secret_key`) fully constrains `dest` to a legitimate Shopify-issued value in all deployments. I did not find any place in this gem where `dest` is independently validated as myshopify-domain-shaped, which is the same class of "checked-in-one-path-but-not-another" inconsistency as the report, but I could not construct an end-to-end scenario using only this gem's code where an unprivileged, unauthenticated attacker supplies a forged/unsigned `dest` value, because the JWT signature check would reject it before `dest` is read out unless the attacker already holds a validly-signed token (which requires knowledge of `api_secret_key`, out of scope per the rules).

### Recommendation
For defense-in-depth and consistency with `ClientCredentials`/`RefreshToken`, validate `dest_shop` with `Utils::ShopValidator.sanitize!` in `TokenExchange.exchange_token` before using it to construct the `HttpClient` session, matching the pattern already used in the sibling OAuth flows.

### Proof of Concept
Not constructible with unprivileged, unauthenticated access using only this gem's code: exploitation would require presenting `TokenExchange.exchange_token` with a validly HS256-signed JWT (signed with the app's own `api_secret_key`) whose `dest` claim is a non-Shopify host, which requires already possessing the app's secret — a capability excluded by the rules (no `api_secret_key`, no leaked credentials). No proof-of-concept satisfying the unprivileged-internet-user constraint could be constructed.

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

**File:** lib/shopify_api/auth/token_exchange.rb (L40-74)
```ruby
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

**File:** lib/shopify_api/auth/jwt_payload.rb (L47-51)
```ruby
      sig { returns(String) }
      def shop
        @dest.gsub("https://", "")
      end
      alias_method :shopify_domain, :shop
```
