This confirms the vulnerability: `HttpClient#initialize` builds `@base_uri = "https://#{api_host || session.shop}"` [1](#0-0)  and the OAuth `access_token` request body carries `client_secret: Context.api_secret_key` [2](#0-1) , so whatever string becomes `session.shop` is exactly where the app's `client_secret` gets sent.

### Title
Missing shop-domain sanitization in `TokenExchange.exchange_token` allows the JWT `dest` claim to control where `client_secret` is sent - (File: `lib/shopify_api/auth/token_exchange.rb`)

### Summary
`TokenExchange.exchange_token` and its sibling `TokenExchange.migrate_to_expiring_token` both build an offline/online-token request whose body includes the app's `client_secret` and whose HTTP target host is taken from a `ShopifyAPI::Auth::Session#shop` value. `migrate_to_expiring_token` correctly runs the caller-supplied `shop` through `Utils::ShopValidator.sanitize!`, which restricts the value to `TRUSTED_SHOPIFY_DOMAINS` (`shopify.com`, `myshopify.io`, `myshopify.com`, `spin.dev`, `shop.dev`, or the configured `myshopify_domain`) before it is ever used as a host [3](#0-2) [4](#0-3) . `exchange_token`, however, takes `dest_shop` straight from `JwtPayload#shop` (the JWT's `dest` claim with `https://` stripped) and never passes it through `ShopValidator` before using it to build the session and the HTTP client [5](#0-4) [6](#0-5) .

### Finding Description
`JwtPayload#initialize` verifies the JWT signature against `Context.api_secret_key` and checks only that `aud == Context.api_key` [7](#0-6) . It performs no validation that `dest` is a real `*.myshopify.com` (or otherwise trusted) domain — that check exists only in `Utils::ShopValidator`, and `exchange_token` is the one caller in this module that skips it. The identity binding that should hold is:

`host contacted for /admin/oauth/access_token (carrying client_secret)` == `a ShopValidator-trusted Shopify domain`

In `exchange_token`, this becomes instead:

`host contacted for /admin/oauth/access_token (carrying client_secret)` == `raw jwt_payload.shop string (unsanitized "dest" claim)`

`dest_shop` flows unsanitized into `Auth::Session.new(shop: dest_shop)` → `Clients::HttpClient.new(session: shop_session, ...)`, whose `@base_uri` is built directly from `session.shop` [8](#0-7) [1](#0-0) . The POST body sent to that host includes `client_secret: ShopifyAPI::Context.api_secret_key` in plaintext [2](#0-1) .

This exactly matches the report's duplicate-code hazard: two structurally identical functions (`exchange_token` vs `migrate_to_expiring_token`) implement the "validate shop before using it as an HTTP host" check, but the copy was not kept consistent — one has the guard, the other lost it (replaced by a deprecation notice for the `shop:` kwarg while the trusted-shop check on the value actually used, `dest_shop`, was never added).

### Impact Explanation
If a hosting application passes attacker-controllable input into `dest` before signing, or if any code path allows an unsanitized/forwarded session token whose `dest` claim is not a genuine Shopify domain to reach `exchange_token`, the gem will issue an HTTPS request containing the app's `client_secret` to a host derived entirely from that string — an SSRF-with-credentials that leaks the app's `client_secret` to an attacker-influenced host. This matches the High-severity class "SSRF with the app's credentials" / credential leakage explicitly in scope.

### Likelihood Explanation
Exploitability depends entirely on whether the JWT signature check is the only gate — since decoding requires knowledge of `Context.api_secret_key`, a token cannot be forged without that secret. This significantly limits the standalone exploitability compared to the primary token-exchange trust bypass; the deeper risk is the missing defense-in-depth check present in the sibling function, not a directly demonstrable exploit purely from this gem's code without the host application first accepting an untrusted token or an already-compromised secret.

### Recommendation
Route `dest_shop` through `Utils::ShopValidator.sanitize!` (or `sanitize_shop_domain`) before constructing `shop_session` in `exchange_token`, exactly as `migrate_to_expiring_token` and `client_credentials`/`refresh_token` already do, so all four sibling OAuth-flow methods enforce the same trusted-domain check on any string that becomes an HTTP host carrying `client_secret`.

### Proof of Concept
Not independently demonstrable within this gem alone: exploitation requires a session token whose `dest` claim is not a genuine Shopify domain yet still verifies against `Context.api_secret_key` (e.g., via a compromised/rotated secret, or a host application that forwards session tokens from an unauthenticated source into `exchange_token`). Given the JWT signature gate, this is reported as a code-consistency/defense-in-depth gap rather than a directly provable exploit chain from this gem's code in isolation.

### Citations

**File:** lib/shopify_api/clients/http_client.rb (L16-19)
```ruby
        api_host = Context.api_host

        @base_uri = T.let("https://#{api_host || session.shop}", String)
        @base_uri_and_path = T.let("#{@base_uri}#{base_path}", String)
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

**File:** lib/shopify_api/auth/token_exchange.rb (L103-104)
```ruby
          validated_shop = Utils::ShopValidator.sanitize!(shop)
          shop_session = ShopifyAPI::Auth::Session.new(shop: validated_shop)
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

**File:** lib/shopify_api/auth/jwt_payload.rb (L33-44)
```ruby
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
```

**File:** lib/shopify_api/auth/jwt_payload.rb (L47-50)
```ruby
      sig { returns(String) }
      def shop
        @dest.gsub("https://", "")
      end
```
