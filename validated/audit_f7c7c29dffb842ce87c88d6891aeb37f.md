### Title
`client_secret` sent to an unvalidated host derived from the JWT `dest` claim - (File: `lib/shopify_api/auth/token_exchange.rb`)

### Summary
`ShopifyAPI::Auth::TokenExchange.exchange_token` builds the host that receives the app's `client_secret` directly from the session token's `dest` claim, without validating that claim against `ShopifyAPI::Utils::ShopValidator`'s trusted-domain allowlist, and without cross-checking it against the token's `iss` claim.

### Finding Description
`JwtPayload#shop` returns `@dest.gsub("https://", "")` with no further checks: [1](#0-0)  The class validates `aud == Context.api_key` [2](#0-1)  but never checks that `dest` is a trusted Shopify domain, nor that it matches the `iss` claim's host — the two fields that should identify the same shop.

`TokenExchange.exchange_token` then uses this unsanitized value directly: [3](#0-2) 
The resulting `shop_session` (built from `dest_shop`) is passed to `Clients::HttpClient`, which builds the destination host from `session.shop`, and the request body contains `client_id` and `client_secret` — the app's confidential secret: [4](#0-3) 

Contrast this with the sibling method `migrate_to_expiring_token` in the same module, which explicitly sanitizes the shop before use: [5](#0-4)  `exchange_token` omits this call entirely, an inconsistency that mirrors the reported bug class ("value trusted in one path but not another," or here, "host validated in one code path but not the one that actually receives the credential").

The equality this breaks: `host-that-receives(client_secret) == verified-issuer-of-token`. The gem instead enforces only `dest == parsed-from-JWT-payload`, with no comparison to `iss` and no membership check against `ShopValidator::TRUSTED_SHOPIFY_DOMAINS` (myshopify.com, shopify.com, spin.dev, shop.dev, myshopify.io) as is done for the OAuth `shop` parameter elsewhere: [6](#0-5) 

### Impact Explanation
If the JWT signature check can be satisfied (bound to `Context.api_secret_key`/`old_api_secret_key`) but `dest` is not independently constrained to a legitimate Shopify domain, the gem will POST the app's `client_id`/`client_secret` (its own OAuth credential) to whatever host is embedded in `dest`. This is the SSRF-with-app-credentials pattern called out in scope: the request carries the app's `client_secret` to a host chosen from unvalidated token data, rather than to a verified Shopify domain.

### Likelihood Explanation
Exploitation still requires producing a JWT that passes the HS256 signature check against the app's `api_secret_key`. Under the stated in-scope rules (no access to `api_secret_key`), I could not fully verify that an unprivileged internet user can supply a `dest` value independent from the value Shopify itself sets when issuing genuine session tokens — Shopify's own token issuance likely keeps `iss`/`dest` consistent and pointed at the real shop. I was unable to find, within this gem's code, any place that constrains what value `dest` may take relative to `iss`, which is the actual root-cause gap; but without evidence of an attacker-controlled JWT-issuance path in this gem itself, this remains a defense-in-depth gap rather than a demonstrated, fully independent exploit chain.

### Recommendation
In `ShopifyAPI::Auth::JwtPayload`, validate that `dest` (after stripping scheme) matches the shop encoded in `iss`, and pass `dest`/`shop` through `Utils::ShopValidator.sanitize!` before it is used anywhere a network request or credential-bearing session is built — matching the behavior already present in `TokenExchange.migrate_to_expiring_token`.

### Proof of Concept
Not producible without a validly-signed JWT whose `dest` differs from `iss`, which requires either the app's `api_secret_key` or an alternate issuance path not present in this gem — out of scope per the rules. The code-level gap (missing `iss`/`dest` cross-check and missing `ShopValidator.sanitize!` call in `exchange_token`) is demonstrated by the cited lines above.

### Citations

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

**File:** lib/shopify_api/auth/token_exchange.rb (L103-104)
```ruby
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
