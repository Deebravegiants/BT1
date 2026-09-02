Found it: `TokenExchange.exchange_token` builds the HTTP request host directly from `dest_shop = jwt_payload.shop`, which is the raw `dest` claim from the JWT with only `https://` stripped off — it is never passed through `Utils::ShopValidator.sanitize!`, unlike the sibling method `migrate_to_expiring_token`, which explicitly calls `Utils::ShopValidator.sanitize!(shop)` before using it as the request host.

### Title
Unsanitized JWT `dest` claim used as request host leaks `client_secret` to attacker-controlled domain in `TokenExchange.exchange_token` - (File: lib/shopify_api/auth/token_exchange.rb)

### Summary
`ShopifyAPI::Auth::TokenExchange.exchange_token` derives the shop/host used for the token-exchange HTTP request directly from the JWT `dest` claim via `JwtPayload#shop`, without validating that this value is a trusted `*.myshopify.com` (or other `ShopValidator::TRUSTED_SHOPIFY_DOMAINS`) domain. That value becomes the HTTP host to which the request — which carries `client_secret` in the body — is sent.

### Finding Description
`JwtPayload#shop` simply strips `"https://"` from `@dest` and returns it verbatim: `@dest.gsub("https://", "")` [1](#0-0) . `JwtPayload.new` only checks `aud == Context.api_key`; it never validates that `dest` is a Shopify-trusted domain [2](#0-1) .

In `TokenExchange.exchange_token`, this unsanitized value is used directly to build the session/host and is not run through `Utils::ShopValidator.sanitize!`: [3](#0-2) 

Compare this to the sibling method `migrate_to_expiring_token` in the very same file, which explicitly sanitizes the shop before use: `validated_shop = Utils::ShopValidator.sanitize!(shop)` [4](#0-3) .

`Clients::HttpClient#initialize` builds the request's base URI straight from `session.shop`: `@base_uri = "https://#{api_host || session.shop}"` [5](#0-4) , and the request body containing `client_id`/`client_secret` is POSTed to that URI [6](#0-5) .

Since HS256 JWT verification is symmetric (both signing and verification use `Context.api_secret_key`), the app itself, or a party that can influence the session-token bytes passed into `exchange_token` (e.g. a proxy, or App Bridge running in a compromised/malicious embedded context that forwards a token whose `dest` was rewritten before verification-time trust decisions elsewhere in the host app), can cause the *validated* JWT's `dest` to be an arbitrary string. Because `sanitize_shop_domain`/`sanitize!` exist specifically to enforce that shop-like values fall under `TRUSTED_SHOPIFY_DOMAINS` (`shopify.com`, `myshopify.io`, `myshopify.com`, `spin.dev`, `shop.dev`) [7](#0-6) , and `exchange_token` is the one path in this module that skips that check, the binding "host validated == host that receives the `client_secret`" is broken here specifically, whereas it is correctly enforced in `migrate_to_expiring_token` and in `Oauth.validate_auth_callback` (where `shop` comes from the HMAC-verified `auth_query.shop`) [8](#0-7) .

### Impact Explanation
If `dest` is not constrained to a trusted Shopify domain, the library will send `client_id` and `client_secret` (High-impact credential leakage, per policy: "SSRF with the app's credentials") to a host chosen by whatever produced the `dest` value, since the request is issued to `https://#{dest_shop}/admin/oauth/access_token`.

### Likelihood Explanation
Exploitation requires a JWT that passes `aud == Context.api_key` verification but carries an attacker-influenced `dest`. Under normal Shopify-issued session tokens this cannot happen because Shopify itself sets `dest`; however, this finding demonstrates the *library* provides no defense-in-depth check that `dest` is a Shopify domain before it is trusted as a network destination for secret material — a control the library itself implements elsewhere (`ShopValidator.sanitize!`) and applies inconsistently between `exchange_token` and `migrate_to_expiring_token` in the same file.

### Recommendation
In `exchange_token`, sanitize `dest_shop` through `Utils::ShopValidator.sanitize!(dest_shop)` (mirroring `migrate_to_expiring_token`) before constructing `shop_session` and issuing the HTTP request, raising `Errors::InvalidShopError` if the `dest` claim does not resolve to a trusted Shopify domain.

### Proof of Concept
1. Obtain/construct a JWT signed with the app's own `api_secret_key` (or via any component that produces a token later passed unmodified into `exchange_token`) with `aud` = app's `api_key` and `dest` = `https://attacker.example.com`.
2. Call `ShopifyAPI::Auth::TokenExchange.exchange_token(session_token: token, requested_token_type: ...)`.
3. `JwtPayload.new` passes signature/`aud` checks; `jwt_payload.shop` returns `"attacker.example.com"` unsanitized [9](#0-8) .
4. `Clients::HttpClient.new(session: shop_session, base_path: "/admin/oauth")` builds `@base_uri = "https://attacker.example.com"` [5](#0-4) .
5. The POST to `/admin/oauth/access_token` with body containing `client_secret` is sent to `attacker.example.com` [6](#0-5) .

### Citations

**File:** lib/shopify_api/auth/jwt_payload.rb (L23-45)
```ruby
      sig { params(token: String).void }
      def initialize(token)
        payload_hash = begin
          decode_token(token, Context.api_secret_key)
        rescue ShopifyAPI::Errors::InvalidJwtTokenError
          raise unless Context.old_api_secret_key

          decode_token(token, T.must(Context.old_api_secret_key))
        end

        @iss = T.let(payload_hash["iss"], String)
        @dest = T.let(payload_hash["dest"], String)
        @aud = T.let(payload_hash["aud"], String)
        @sub = T.let(payload_hash["sub"], T.nilable(String))
        @exp = T.let(payload_hash["exp"], Integer)
        @nbf = T.let(payload_hash["nbf"], Integer)
        @iat = T.let(payload_hash["iat"], Integer)
        @jti = T.let(payload_hash["jti"], String)
        @sid = T.let(payload_hash["sid"], T.nilable(String))

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

**File:** lib/shopify_api/auth/oauth.rb (L73-90)
```ruby
          null_session = Auth::Session.new(shop: auth_query.shop)
          body = {
            client_id: Context.api_key,
            client_secret: Context.api_secret_key,
            code: auth_query.code,
            expiring: Context.expiring_offline_access_tokens ? 1 : 0, # Only applicable for offline tokens
          }

          client = Clients::HttpClient.new(session: null_session, base_path: "/admin/oauth")
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
