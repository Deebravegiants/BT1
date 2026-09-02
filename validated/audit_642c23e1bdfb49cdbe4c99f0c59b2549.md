Confirmed: `HttpClient#initialize` builds `@base_uri` directly from `session.shop` with no domain validation at that layer at all — [1](#0-0) , so any unsanitized `shop`/`dest` value passed into a `Session` flows straight into the URL that receives `client_secret` in the request body.

### Title
Missing domain validation on JWT `dest` claim allows SSRF with `client_secret` in `TokenExchange.exchange_token` - (File: `lib/shopify_api/auth/token_exchange.rb`)

### Summary
`TokenExchange.exchange_token` extracts the shop host from the session token's `dest` claim and uses it, unvalidated, to build the URL that the app's `client_id`/`client_secret` are POSTed to — unlike every sibling OAuth credential-exchange method in the same file and module, which all call `Utils::ShopValidator.sanitize!` before using the shop value.

### Finding Description
`JwtPayload#shop` simply strips the `https://` prefix from the `dest` claim and returns it as-is, with no check that the resulting host is a trusted Shopify domain: [2](#0-1) . The only validation performed on the payload is that `aud == Context.api_key` [3](#0-2) ; there is no check against `Utils::ShopValidator::TRUSTED_SHOPIFY_DOMAINS`.

`TokenExchange.exchange_token` takes this raw `dest_shop` and uses it directly to construct the `Session` used for the outbound HTTP request, without ever calling `Utils::ShopValidator.sanitize!`: [4](#0-3) .

Contrast this with the three sibling methods that perform the equivalent operation and explicitly sanitize the shop first:
- `ClientCredentials.client_credentials`: [5](#0-4) 
- `RefreshToken.refresh_access_token`: [6](#0-5) 
- `TokenExchange.migrate_to_expiring_token` (same file as the vulnerable method): [7](#0-6) 

`HttpClient#initialize` performs no domain restriction of its own — it builds `@base_uri` as `"https://#{api_host || session.shop}"` verbatim: [1](#0-0) . So whatever host value reaches `Session#shop` becomes the destination for the POST containing `client_id`/`client_secret`: [8](#0-7) .

This is the exact bug class from the report ("variables used but not initialized/validated before use") mapped onto this gem's identity boundary: **host validated (via `ShopValidator.sanitize!` in sibling flows) vs. host that actually receives the `client_secret`** — in `exchange_token` these are not the same code path, breaking that equality.

### Impact Explanation
If the `dest` claim of an otherwise validly-signed session token can carry a non-Shopify host (the JWT signature check only binds `aud` to the app; it does not constrain `dest` to `*.myshopify.com`/`myshopify.io`/`shopify.com`/`spin.dev`/`shop.dev`), `exchange_token` will POST the app's `client_id` and `client_secret` to that attacker-influenced host — SSRF with the app's credentials, i.e., credential exfiltration of the `client_secret` to a third party. This matches the High-severity "SSRF with the app's credentials" category in scope.

### Likelihood Explanation
Exploitability hinges entirely on whether an attacker can ever get a validly HS256-signed session token (signed with the shared `api_secret_key`) whose `dest` claim is not a genuine Shopify-issued domain. Session tokens are normally minted by Shopify itself for the actual embedded-app shop, so under Shopify's documented, well-behaved token-issuance flow this claim is not attacker-controlled. This library, however, provides no independent, defense-in-depth verification of `dest`/`shop` at the point where the credential-bearing request is built, unlike its sibling functions in the same module. This is a real and demonstrable inconsistency in the codebase's validation coverage, but I could not confirm from this gem's code alone a concrete mechanism by which an unprivileged internet user (without already controlling Shopify's session-token issuance or the app's secret) can inject an arbitrary `dest` value into a token that will pass HS256 verification. That confirmation would require exercising Shopify's session-token issuance service itself, which is outside this repository's index.

### Recommendation
In `TokenExchange.exchange_token`, validate `dest_shop` with `Utils::ShopValidator.sanitize!` (as `migrate_to_expiring_token`, `client_credentials`, and `refresh_access_token` already do) before constructing the `Session`/`HttpClient` that will transmit `client_id`/`client_secret`. Additionally, consider having `JwtPayload` itself enforce that `dest`/`iss` resolve to a domain in `Utils::ShopValidator::TRUSTED_SHOPIFY_DOMAINS` as a structural invariant of the class, rather than leaving it to each caller to remember.

### Proof of Concept
Not independently reproducible from this gem's code alone, since it depends on obtaining a validly HS256-signed session token whose `dest` claim is not a genuine Shopify domain — a precondition outside this repository's control. Conceptually:
1. Obtain (or construct, if `Context.old_api_secret_key`/secret rotation or another out-of-scope weakness ever allows it) a session token with `aud` equal to the target app's `api_key` and `dest` set to `https://attacker-controlled-host.example`.
2. Call `ShopifyAPI::Auth::TokenExchange.exchange_token(session_token: token, requested_token_type: ...)`.
3. Observe that `dest_shop` (`attacker-controlled-host.example`) is used unsanitized to build the `HttpClient` base URI, and the POST body containing `client_id`/`client_secret` is sent to `https://attacker-controlled-host.example/admin/oauth/access_token`.

### Citations

**File:** lib/shopify_api/clients/http_client.rb (L16-19)
```ruby
        api_host = Context.api_host

        @base_uri = T.let("https://#{api_host || session.shop}", String)
        @base_uri_and_path = T.let("#{@base_uri}#{base_path}", String)
```

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
