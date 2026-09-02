## Title
Missing shop-domain validation in `TokenExchange.exchange_token` leaks `client_secret` to a host derived from an unvalidated JWT claim - (File: `lib/shopify_api/auth/token_exchange.rb`)

## Summary
`ShopifyAPI::Auth::TokenExchange.exchange_token` builds the HTTP request host that receives the app's `client_id`/`client_secret` directly from the `dest` claim of an unvalidated session-token JWT, whereas every sibling credential-exchange method in the same module (`client_credentials.rb`, `refresh_token.rb`, `token_exchange.rb#migrate_to_expiring_token`) passes the `shop` value through `Utils::ShopValidator.sanitize!` before using it to build the request host.

## Finding Description
`JwtPayload#shop` simply strips `"https://"` from the token's `dest` claim with no allow-listing: [1](#0-0) 

`TokenExchange.exchange_token` takes that unchecked value and uses it verbatim to build the `Session` whose `shop` attribute becomes the request host: [2](#0-1) 

`Clients::HttpClient#initialize` derives `@base_uri` directly from `session.shop` (falling back only if `Context.api_host` is unset), with no domain check inside the HTTP client either: [3](#0-2) 

Consequently, the POST body containing `client_id` and `client_secret` (`ShopifyAPI::Context.api_secret_key`) is sent to `https://#{dest_shop}/admin/oauth/access_token`: [4](#0-3) 

This is exactly the pattern the rest of the same module deliberately guards against. `client_credentials.rb` and `refresh_token.rb` both call `Utils::ShopValidator.sanitize!(shop)` before constructing the session/host that will receive `client_secret`: [5](#0-4) [6](#0-5) 

`token_exchange.rb`'s own sibling method `migrate_to_expiring_token` does the same: [7](#0-6) 

`ShopValidator.sanitize!` restricts the resulting host to a small allow-list of trusted Shopify domains (`shopify.com`, `myshopify.io`, `myshopify.com`, `spin.dev`, `shop.dev`) or an app-configured custom domain: [8](#0-7) 

`exchange_token` alone skips this step, so the equality the gem is meant to enforce — *host that receives `client_secret` == a domain in `ShopValidator::TRUSTED_SHOPIFY_DOMAINS`* — is broken specifically for the token-exchange code path, which is the flow the gem recommends for embedded apps performing session-token → access-token exchange. `JwtPayload` only verifies the signature and `aud`; it never checks that `dest`/`iss` correspond to a trusted Shopify domain shape, so nothing else in the call chain re-establishes the binding that `ShopValidator` provides elsewhere in the same module.

## Impact Explanation
If a session token whose `dest` claim is not constrained to a `myshopify.com`-style domain can reach `exchange_token` (e.g., a token issued for a different embed surface/context that shares the same signing key/audience but is not an admin-embedded app session, or any other case where `dest` is not host-restricted), the app's `client_secret` and `client_id` are transmitted directly to that attacker-influenceable host. This matches the specified High-severity impact class "SSRF with the app's credentials, ... credential leakage" since the request carries the app's own OAuth credentials to a host chosen from unvalidated data.

## Likelihood Explanation
Exploitability depends on whether an unprivileged actor can obtain a validly HS256-signed token (correct `aud`) whose `dest` is not itself constrained to the merchant's real `myshopify.com` domain, before the caller invokes `exchange_token`. The library's own defense-in-depth pattern (every other method in this same file validates `shop` with `ShopValidator.sanitize!`) shows the maintainers intended this constraint to be applied universally; its absence here is a code-path inconsistency rather than a defense that was consciously omitted, making it a genuine gap rather than an intentional design choice.

## Recommendation
In `exchange_token`, validate `dest_shop` with `Utils::ShopValidator.sanitize!(dest_shop)` (mirroring `migrate_to_expiring_token`, `client_credentials`, and `refresh_token`) before constructing `shop_session`/`Clients::HttpClient`, so the request host is always constrained to `ShopValidator::TRUSTED_SHOPIFY_DOMAINS` (or the configured `myshopify_domain`) prior to sending `client_id`/`client_secret`.

## Proof of Concept
1. Craft/obtain a session token JWT signed with the app's `api_secret_key`, `aud` equal to `Context.api_key`, and `dest` set to a non-`myshopify.com` value the attacker controls, e.g. `dest: "https://attacker.example"`.
2. Call `ShopifyAPI::Auth::TokenExchange.exchange_token(session_token: token, requested_token_type: OFFLINE_ACCESS_TOKEN)`.
3. Observe (via network trace / stub) that `Clients::HttpClient` sends a POST to `https://attacker.example/admin/oauth/access_token` with body containing `client_id` and `client_secret`, per: [4](#0-3) 
   whereas the same call in `client_credentials.rb`/`refresh_token.rb` would have raised `Errors::InvalidShopError` for the same non-trusted `shop` value: [9](#0-8)

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

**File:** lib/shopify_api/clients/http_client.rb (L11-19)
```ruby
      sig { params(base_path: String, session: T.nilable(Auth::Session)).void }
      def initialize(base_path:, session: nil)
        session ||= Context.active_session
        raise Errors::NoActiveSessionError, "No passed or active session" unless session

        api_host = Context.api_host

        @base_uri = T.let("https://#{api_host || session.shop}", String)
        @base_uri_and_path = T.let("#{@base_uri}#{base_path}", String)
```

**File:** lib/shopify_api/auth/client_credentials.rb (L25-33)
```ruby
          validated_shop = Utils::ShopValidator.sanitize!(shop)
          shop_session = ShopifyAPI::Auth::Session.new(shop: validated_shop)
          body = {
            client_id: ShopifyAPI::Context.api_key,
            client_secret: ShopifyAPI::Context.api_secret_key,
            grant_type: CLIENT_CREDENTIALS_GRANT_TYPE,
          }

          client = Clients::HttpClient.new(session: shop_session, base_path: "/admin/oauth")
```

**File:** lib/shopify_api/auth/refresh_token.rb (L24-33)
```ruby
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
