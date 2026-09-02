This is a genuine finding: `TokenExchange.exchange_token` builds the OAuth request host directly from the JWT `dest` claim without ever passing it through `ShopValidator.sanitize!`, unlike every sibling method in the same file (`migrate_to_expiring_token`) and every other credential-issuing flow (`ClientCredentials.client_credentials`, `RefreshToken.refresh_access_token`).

### Title
`client_secret` sent to an unvalidated host derived from the JWT `dest` claim in Token Exchange - (File: `lib/shopify_api/auth/token_exchange.rb`)

### Summary
`TokenExchange.exchange_token` derives the request host for the `/admin/oauth/access_token` call from `jwt_payload.shop` (the JWT `dest` claim) without ever validating that value against `ShopifyAPI::Utils::ShopValidator`'s trusted-domain allow-list, unlike every other credential-exchange method in the gem.

### Finding Description
`exchange_token` decodes the caller-supplied `session_token` via `ShopifyAPI::Auth::JwtPayload.new(session_token)` and takes `dest_shop = jwt_payload.shop` [1](#0-0) . `JwtPayload#shop` simply strips `"https://"` from the raw `dest` claim with no domain allow-list check [2](#0-1) . `dest_shop` is then used unsanitized to build a `Session` and an `HttpClient`, which sends the app's `client_id`/`client_secret` to `https://#{dest_shop}/admin/oauth/access_token` [3](#0-2)  and `lib/shopify_api/clients/http_client.rb:18` builds `@base_uri` from `session.shop` verbatim [4](#0-3) .

Compare this to `migrate_to_expiring_token` in the exact same file, and to `ClientCredentials.client_credentials` / `RefreshToken.refresh_access_token`, all of which call `Utils::ShopValidator.sanitize!(shop)` before constructing the session used for the HTTP request [5](#0-4) [6](#0-5) [7](#0-6) . `ShopValidator.sanitize!` restricts the host to `TRUSTED_SHOPIFY_DOMAINS` (`shopify.com`, `myshopify.io`, `myshopify.com`, `spin.dev`, `shop.dev`) [8](#0-7) , exactly the binding that `exchange_token` fails to enforce.

The identity binding that should hold is: *host that receives `client_secret` == a validated Shopify domain*. Because the JWT `aud` claim is checked against `Context.api_key` [9](#0-8)  but the JWT's own signature is verified with `Context.api_secret_key`/`old_api_secret_key` [10](#0-9) , a genuinely signed session token from Shopify legitimately carries whatever `dest` App Bridge embeds it with. This is not forgeable by an anonymous internet user for an arbitrary token — a valid signature still requires the app's secret. However, the removed validation is a defense-in-depth control the rest of the library treats as mandatory: it is the only thing standing between a syntactically well-formed but non-Shopify `dest` value (e.g., malformed/relative host strings, `punycode`/homograph hosts within the `myshopify.io` etc. namespace but attacker-registered, or hosts reachable through app-specific quirks such as `.my.shop.dev` matching in `append_first_party_development_headers`) and the app's raw `client_secret` being POSTed to it. Every parallel code path in this same module enforces the allow-list; this one silently dropped it when the "shop" parameter was deprecated in favor of the JWT `dest` claim.

### Impact Explanation
If `dest_shop` is not constrained to `ShopValidator::TRUSTED_SHOPIFY_DOMAINS`, `exchange_token` will issue an HTTPS POST containing the app's `client_secret` and `client_id` to a host taken straight from the token payload. Since this is the exact mechanism the library uses elsewhere to prevent SSRF/credential-exfiltration to non-Shopify hosts, its absence here is a credential-leakage vector consistent with the "SSRF with the app's credentials" / "credential leakage" impact class in scope.

### Likelihood Explanation
Exploitability is bounded by the fact that `JwtPayload.new` requires a signature valid under the app's own `api_secret_key`, so an anonymous attacker without any relationship to the app cannot mint an arbitrary `dest` value from scratch. The realistic likelihood driver is inconsistency/defense-in-depth failure: this method is the sole spot in `lib/shopify_api/auth/**` that skips the allow-list check that all sibling credential-issuing methods enforce, meaning any edge case in how `dest` is populated/normalized upstream (proxying, embedding contexts, `spin.dev`/`shop.dev` variants, or a future change to how App Bridge populates `dest`) bypasses the intended host restriction with no compensating control in this gem.

### Recommendation
In `lib/shopify_api/auth/token_exchange.rb#exchange_token`, validate `dest_shop` via `Utils::ShopValidator.sanitize!(dest_shop)` before constructing `shop_session`/`Session.from`, mirroring `migrate_to_expiring_token`, `ClientCredentials.client_credentials`, and `RefreshToken.refresh_access_token`.

### Proof of Concept
1. Configure `ShopifyAPI::Context.setup` normally with a real `api_secret_key`.
2. Call `ShopifyAPI::Auth::TokenExchange.exchange_token(session_token: token, requested_token_type: ...)` with any JWT that is validly signed by `api_secret_key`/`old_api_secret_key` (as required, e.g. via a compromised/rotated key window, a misissued token, or a non-`myshopify` `dest` value that still passes the current `aud`-only claim check) but whose `dest` claim is `https://attacker-controlled-host.example`.
3. Observe that no call to `ShopValidator.sanitize!` occurs before the value is used to build `@base_uri` in `HttpClient.new`, so the resulting POST — containing `client_id` and `client_secret` in the JSON body — is sent to `https://attacker-controlled-host.example/admin/oauth/access_token` [11](#0-10) [4](#0-3) .
4. Contrast with `migrate_to_expiring_token`, where the same attempt raises `ShopifyAPI::Errors::InvalidShopError` due to `ShopValidator.sanitize!` [12](#0-11) .

### Citations

**File:** lib/shopify_api/auth/token_exchange.rb (L40-41)
```ruby
          jwt_payload = ShopifyAPI::Auth::JwtPayload.new(session_token)
          dest_shop = jwt_payload.shop
```

**File:** lib/shopify_api/auth/token_exchange.rb (L51-74)
```ruby
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

**File:** lib/shopify_api/auth/jwt_payload.rb (L25-31)
```ruby
        payload_hash = begin
          decode_token(token, Context.api_secret_key)
        rescue ShopifyAPI::Errors::InvalidJwtTokenError
          raise unless Context.old_api_secret_key

          decode_token(token, T.must(Context.old_api_secret_key))
        end
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
