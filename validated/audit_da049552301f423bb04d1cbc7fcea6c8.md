### Title
SSRF with the app's `client_id`/`client_secret` via unvalidated JWT `dest` claim in `TokenExchange.exchange_token` - (File: lib/shopify_api/auth/token_exchange.rb)

### Summary
`ShopifyAPI::Auth::TokenExchange.exchange_token` builds an outbound HTTP request carrying the app's `client_id` and `client_secret` to a host derived directly from the `dest` claim of an attacker-suppliable session token, without ever passing that value through `Utils::ShopValidator.sanitize!`. Every sibling method in the same file and module family (`migrate_to_expiring_token`, `ClientCredentials.client_credentials`, `RefreshToken.refresh_access_token`) explicitly validates the `shop`/host value with `ShopValidator.sanitize!` before using it to construct the outbound request host, but `exchange_token` does not apply the same check to the value it extracts from the JWT.

### Finding Description
`JwtPayload#initialize` verifies the JWT signature and the `aud` claim against `Context.api_key` [1](#0-0) , but performs **no validation of the `dest`/`iss` claim's format or domain** — `shop` is derived by a naive string substitution: `@dest.gsub("https://", "")` [2](#0-1) .

In `exchange_token`, this unsanitized value is used directly to build the session and thus the outbound request host:
```
jwt_payload = ShopifyAPI::Auth::JwtPayload.new(session_token)
dest_shop = jwt_payload.shop
...
shop_session = ShopifyAPI::Auth::Session.new(shop: dest_shop)
...
client = Clients::HttpClient.new(session: shop_session, base_path: "/admin/oauth")
``` [3](#0-2) 

`HttpClient#initialize` sets `@base_uri = "https://#{api_host || session.shop}"` and sends the POST body — including `client_id` and `client_secret` — to that host [4](#0-3) , [5](#0-4) .

By contrast, the other three OAuth grant helpers in the same trust boundary all sanitize the shop before using it as the request host:
- `migrate_to_expiring_token`: `validated_shop = Utils::ShopValidator.sanitize!(shop)` [6](#0-5) 
- `ClientCredentials.client_credentials`: `validated_shop = Utils::ShopValidator.sanitize!(shop)` [7](#0-6) 
- `RefreshToken.refresh_access_token`: `validated_shop = Utils::ShopValidator.sanitize!(shop)` [8](#0-7) 

`ShopValidator.sanitize!` exists specifically to enforce that a host belongs to a trusted Shopify domain (`myshopify.com`, `myshopify.io`, `spin.dev`, `shop.dev`, `shopify.com`) before it is used as a network destination [9](#0-8) . `exchange_token` is the one path in this family that skips this check, breaking the intended identity binding: **the host that is validated as a legitimate Shopify domain ≠ the host that actually receives the app's `client_secret`**.

The `session_token` parameter to `exchange_token` is not necessarily something only Shopify can produce and control the content of from the calling app's perspective — the JWT signature check only proves the token was signed with `api_secret_key`; it does not constrain what string is put in `dest`. Since `dest` is attacker/embedding-context-supplied content that Shopify's front end places into the token and forwards through the host application to this library call, and this library performs no domain allow-listing on it (unlike the parallel `shop` parameters elsewhere), a malformed or non-Shopify `dest` value flows unchecked into the outbound request host.

### Impact Explanation
If a `dest` value that is not a genuine Shopify domain reaches `exchange_token` (e.g., due to any downstream token issuance path or host-application defect that does not itself constrain `dest`/`aud` sufficiently to a real store), the library will POST `client_id` and `client_secret` in cleartext, over HTTPS, to an arbitrary attacker-controlled host — this is SSRF carrying the app's OAuth client credentials, which matches the "High" impact criteria (SSRF with the app's credentials / credential leakage) and could lead directly to `client_secret` exfiltration (Critical) if realized.

### Likelihood Explanation
Medium-low. Exploitability depends on whether an attacker can influence the `dest` claim of a JWT that still passes signature and `aud` verification in `JwtPayload`, which in the standard Shopify-issued session-token flow is controlled by Shopify itself. However, the inconsistency is a genuine defense-in-depth gap in this gem: every other analogous grant type is defended with `ShopValidator.sanitize!`, and `exchange_token` alone is not, so any future scenario that widens control over `session_token` (custom token issuance, non-Shopify token providers, host misconfiguration) turns into immediate SSRF+credential leakage with no compensating control inside this library.

### Recommendation
Apply the same treatment as the sibling methods: call `Utils::ShopValidator.sanitize!(dest_shop)` on the value extracted from the JWT's `dest` claim in `TokenExchange.exchange_token` before constructing `shop_session`, ensuring the outbound host used to transmit `client_id`/`client_secret` is provably a trusted Shopify domain, consistent with `migrate_to_expiring_token`, `client_credentials`, and `refresh_access_token`.

### Proof of Concept
1. Construct (or obtain) a session token whose payload has `dest` set to a non-Shopify, attacker-controlled value (e.g. `https://attacker.example.com`) but which otherwise satisfies `JwtPayload`'s checks (valid HS256 signature with the app's secret is required for full exploitation in the strict Shopify-issued-token model; the described flaw is that no additional host-domain restriction is applied regardless).
2. Call:
```ruby
ShopifyAPI::Auth::TokenExchange.exchange_token(
  session_token: crafted_jwt,
  requested_token_type: ShopifyAPI::Auth::TokenExchange::RequestedTokenType::OFFLINE_ACCESS_TOKEN
)
```
3. Observe (via `lib/shopify_api/auth/token_exchange.rb:40-65` and `lib/shopify_api/clients/http_client.rb:16-19`) that the library builds `https://attacker.example.com/admin/oauth/access_token` and POSTs a JSON body containing `client_id` and `client_secret` to it — with no `ShopValidator.sanitize!` check ever applied to `dest_shop`, unlike the parallel code paths in `client_credentials.rb`, `refresh_token.rb`, and `migrate_to_expiring_token` in the same file.

### Citations

**File:** lib/shopify_api/auth/jwt_payload.rb (L47-51)
```ruby
      sig { returns(String) }
      def shop
        @dest.gsub("https://", "")
      end
      alias_method :shopify_domain, :shop
```

**File:** lib/shopify_api/auth/jwt_payload.rb (L76-81)
```ruby
      sig { params(token: String, api_secret_key: String).returns(T::Hash[String, T.untyped]) }
      def decode_token(token, api_secret_key)
        JWT.decode(token, api_secret_key, true, leeway: JWT_LEEWAY, algorithm: "HS256")[0]
      rescue JWT::DecodeError => err
        raise ShopifyAPI::Errors::InvalidJwtTokenError, "Error decoding session token: #{err.message}"
      end
```

**File:** lib/shopify_api/auth/token_exchange.rb (L40-65)
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
