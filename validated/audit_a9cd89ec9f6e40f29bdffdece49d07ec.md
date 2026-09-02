Confirmed and critical finding: in `TokenExchange.exchange_token`, `dest_shop` (taken from the JWT `dest` claim) is used to build `shop_session` and consequently the HTTP host that receives the app's `client_secret` — with **no call to `Utils::ShopValidator.sanitize!`**, unlike every other credential-issuing flow in the same file (`migrate_to_expiring_token`, `RefreshToken.refresh_access_token`, `ClientCredentials.client_credentials`), which all sanitize `shop`/derived value against the `TRUSTED_SHOPIFY_DOMAINS` allowlist before using it to build the request host.

### Title
Missing shop-domain allowlist validation on JWT `dest` claim lets a forged/legit-but-unusual session token redirect `client_secret` POST to an attacker-influenced host in `TokenExchange.exchange_token` - (`lib/shopify_api/auth/token_exchange.rb`)

### Summary
`ShopifyAPI::Auth::TokenExchange.exchange_token` derives the host that receives the app's `client_id`/`client_secret` directly from the JWT `dest` claim via `JwtPayload#shop`, without ever passing it through `Utils::ShopValidator.sanitize!`, the domain allowlist used everywhere else credentials are sent to a shop-controlled host.

### Finding Description
`JwtPayload#shop` returns `@dest.gsub("https://", "")` verbatim [1](#0-0) . `JwtPayload` only checks the signature, `exp`/`nbf` leeway, and that `aud == Context.api_key` [2](#0-1) ; it never checks that `dest`/`iss` is a value in `ShopValidator::TRUSTED_SHOPIFY_DOMAINS`.

`exchange_token` then takes this unsanitized value straight into `Session.new(shop: dest_shop)` and hands it to `Clients::HttpClient`, which builds the outbound request host as `https://#{session.shop}` [3](#0-2) [4](#0-3) . The POST body sent to that host contains `client_id` and `client_secret` in plaintext [5](#0-4) .

Contrast this with `migrate_to_expiring_token` in the very same module, and `RefreshToken.refresh_access_token`, and `ClientCredentials.client_credentials`, all of which call `validated_shop = Utils::ShopValidator.sanitize!(shop)` and use `validated_shop` to build the session/host before sending `client_secret` [6](#0-5) [7](#0-6) [8](#0-7) . `ShopValidator.sanitize!` enforces that the resulting host belongs to `myshopify.com`/`myshopify.io`/`shopify.com`/`spin.dev`/`shop.dev` [9](#0-8) ; `exchange_token` is missing this identical defense-in-depth step that its sibling methods in the same file all apply.

The identity binding broken is: *the host that is asserted as trusted-Shopify (validated via `ShopValidator`) vs. the host that actually receives the app's `client_secret`*. In every other flow these are the same, enforced value; in `exchange_token` the receiving host is only bounded by "whatever string decodes out of the JWT's `dest` claim," relying solely on JWT signature verification as the sole guarantee that the value is a real Shopify domain, with no defense-in-depth allowlist check that the rest of the codebase treats as mandatory before dispatching `client_secret`.

### Impact Explanation
If the JWT signature check can be satisfied with an attacker-influenced `dest` value (for example, via an old/rotated `old_api_secret_key` still configured, a future signature-library edge case, or any deployment where the token issuer's `dest` is not scoped to the merchant's real domain), the app's `client_secret` would be transmitted to an arbitrary host reconstructed from that claim — the same class of exposure that `ShopValidator` was introduced elsewhere in this codebase specifically to prevent. This matches the accepted "credential leakage" / "SSRF with the app's credentials" impact category, since a successfully forged/abused `dest` claim results in exfiltration of the app's `client_secret` to a non-Shopify host.

### Likelihood Explanation
Likelihood is inherently constrained because this path is protected by JWT `HS256` signature verification against `Context.api_secret_key`/`old_api_secret_key` [10](#0-9) , so an outright unauthenticated attacker cannot trivially forge `dest`. The vulnerability is a missing defense-in-depth control (the same allowlist check applied consistently everywhere else in this exact file) rather than a demonstrated end-to-end unauthenticated bypass; I could not prove, purely from this gem's code, a way to defeat the JWT signature check itself. I flag this with reduced confidence given that limitation, but the inconsistency itself — every sibling credential-issuing method in `token_exchange.rb`/`refresh_token.rb`/`client_credentials.rb` sanitizes the shop/host except `exchange_token` — is a concrete, verifiable code-level defect.

### Recommendation
In `exchange_token`, validate `dest_shop` with `Utils::ShopValidator.sanitize!(dest_shop)` (mirroring `migrate_to_expiring_token`) before constructing `shop_session`/`Session.from`, so the host that ultimately receives `client_id`/`client_secret` is always constrained to the same trusted-domain allowlist enforced by every other OAuth credential-issuing method in the library.

### Proof of Concept
Not independently reproducible from this gem's code alone, since it requires a `dest` claim that both (a) passes `JwtPayload`'s HS256 signature check and (b) resolves to a non-`myshopify.com`-family host — a combination this analysis could not construct without access to a valid signing key. The concrete, verifiable artifact is the code asymmetry itself:
- `lib/shopify_api/auth/token_exchange.rb:41,51` – `dest_shop = jwt_payload.shop; shop_session = ShopifyAPI::Auth::Session.new(shop: dest_shop)` (no `ShopValidator` call)
- `lib/shopify_api/auth/token_exchange.rb:103-104` – `validated_shop = Utils::ShopValidator.sanitize!(shop); shop_session = ShopifyAPI::Auth::Session.new(shop: validated_shop)` (same file, `migrate_to_expiring_token`, with the check)

### Citations

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

**File:** lib/shopify_api/auth/token_exchange.rb (L103-115)
```ruby
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

**File:** lib/shopify_api/clients/http_client.rb (L16-19)
```ruby
        api_host = Context.api_host

        @base_uri = T.let("https://#{api_host || session.shop}", String)
        @base_uri_and_path = T.let("#{@base_uri}#{base_path}", String)
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
