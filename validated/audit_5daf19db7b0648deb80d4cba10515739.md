### Title
Missing shop-domain validation in `TokenExchange.exchange_token` sends `client_secret` to an unvalidated host derived from the JWT `dest` claim - (File: `lib/shopify_api/auth/token_exchange.rb`)

### Summary
`ShopifyAPI::Auth::TokenExchange.exchange_token` derives the target host for the OAuth token-exchange HTTP request directly from the session token's `dest` claim (`jwt_payload.shop`), and never passes that value through `Utils::ShopValidator.sanitize!`, unlike every sibling credential-exchange method in the same module and its neighbours.

### Finding Description
`JwtPayload#shop` returns `@dest.gsub("https://", "")` with no allow-list check [1](#0-0) . `TokenExchange.exchange_token` takes this value as `dest_shop`, builds a `Session` from it, and uses it as the host that receives the request containing `client_id`/`client_secret` in the POST body: [2](#0-1) 

Contrast this with the sibling method in the very same file, `migrate_to_expiring_token`, and with `RefreshToken.refresh_access_token` and `ClientCredentials.client_credentials`, all of which call `Utils::ShopValidator.sanitize!(shop)` before constructing the session/host that will receive `client_secret`: [3](#0-2) [4](#0-3) [5](#0-4) 

`Utils::ShopValidator.sanitize!` exists precisely to guarantee that any string used to build a request host is a member of `TRUSTED_SHOPIFY_DOMAINS` (`shopify.com`, `myshopify.io`, `myshopify.com`, `spin.dev`, `shop.dev`), rejecting look-alike or attacker-controlled domains [6](#0-5) . This is the same class of bug described in the analog report: a check ("sanitize the domain that will receive the app's secret") that is correctly applied to some call sites but silently omitted for a sibling path (`exchange_token`), exactly like `only_owner` being dropped when it follows `when_paused`.

`exchange_token` is the primary, documented flow for embedded apps to convert a session token into an access token, and it is the one path in this module that skips host sanitization before sending `client_id`/`client_secret` to `https://#{dest_shop}/admin/oauth/access_token` via `Clients::HttpClient`.

### Impact Explanation
If the value bound into `dest_shop` is ever attacker-influenceable — e.g. through JWT key confusion/rotation edge cases (`old_api_secret_key` fallback verification path in `JwtPayload#initialize`), a mis-issued or malformed token that still passes `JWT.decode`, or any future code path that constructs `JwtPayload`/`dest` from less-trusted input — the missing `ShopValidator.sanitize!` call means this is the one place in the module where nothing stops the app's `client_id` and `client_secret` from being POSTed to an arbitrary attacker-chosen host. That is SSRF carrying the app's OAuth client credentials, which can lead to credential theft, matching the High/Critical impact classes defined for this analysis (SSRF with the app's credentials / theft of `client_secret`).

### Likelihood Explanation
Likelihood is moderate-to-low in the current codebase because `JwtPayload.new` requires a valid HS256 signature over `api_secret_key` (or `old_api_secret_key`) before `dest` is trusted at all, so a fully unauthenticated attacker cannot forge an arbitrary `dest`. However, the structural gap — a security check present in three sibling functions but absent in the one function that is the primary/most-used entry point — is a concrete, provable inconsistency in the code as written, independent of whether a bypass of JWT verification currently exists. Any future change that weakens the guarantee that `dest` originates solely from a genuine Shopify-signed token (e.g. broader `old_api_secret_key` acceptance windows, additional token issuers, or checkout/extension token types) would immediately turn this into a directly exploitable SSRF/credential-exfiltration path with no additional code changes needed on the vulnerable side.

### Recommendation
Add `validated_shop = Utils::ShopValidator.sanitize!(dest_shop)` in `TokenExchange.exchange_token` immediately after computing `dest_shop = jwt_payload.shop`, and use `validated_shop` for both the `Session` construction and the final `Session.from(shop: ...)` call, mirroring the pattern already used in `migrate_to_expiring_token`, `refresh_access_token`, and `client_credentials`.

### Proof of Concept
Not applicable as a standalone unauthenticated PoC: exploitation requires a code path (current or future) where `JwtPayload#shop`/`dest` is not strictly bound to a Shopify-issued, `api_secret_key`-signed token. The finding is a structural/code-consistency defect (missing `ShopValidator.sanitize!` call) proven by direct comparison of `exchange_token` against its sibling functions in the same file and module, all cited above.

### Citations

**File:** lib/shopify_api/auth/jwt_payload.rb (L47-50)
```ruby
      sig { returns(String) }
      def shop
        @dest.gsub("https://", "")
      end
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

**File:** lib/shopify_api/utils/shop_validator.rb (L6-18)
```ruby
module ShopifyAPI
  module Utils
    module ShopValidator
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
