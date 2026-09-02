### Title
Unvalidated JWT `dest` claim used to build the OAuth token-exchange request host, bypassing the trusted-domain check applied to every other credential-bearing endpoint - (File: `lib/shopify_api/auth/token_exchange.rb`, `lib/shopify_api/auth/jwt_payload.rb`)

### Summary
`TokenExchange.exchange_token` derives the request host that receives the app's `client_secret` directly from the JWT `dest` claim (`jwt_payload.shop`), with no call to `Utils::ShopValidator.sanitize!`. Every other credential-bearing flow in the gem (`ClientCredentials.client_credentials`, `RefreshToken.refresh_access_token`, `TokenExchange.migrate_to_expiring_token`) explicitly sanitizes the `shop` value through `ShopValidator.sanitize!` before using it to build the request host. `exchange_token` is the one path that skips this check.

### Finding Description
`JwtPayload#shop` is computed as:
```ruby
def shop
  @dest.gsub("https://", "")
end
``` [1](#0-0) 
This simply strips a scheme prefix; it does not validate that the resulting string is a trusted `*.myshopify.com` / `myshopify.io` / `spin.dev` / `shop.dev` host, unlike `Utils::ShopValidator.sanitize!`, which enforces that constraint [2](#0-1) .

`exchange_token` then binds this unvalidated value directly to the host that will receive the app's `client_id`/`client_secret`:
```ruby
jwt_payload = ShopifyAPI::Auth::JwtPayload.new(session_token)
dest_shop = jwt_payload.shop
...
shop_session = ShopifyAPI::Auth::Session.new(shop: dest_shop)
body = { client_id: ..., client_secret: ShopifyAPI::Context.api_secret_key, ... }
client = Clients::HttpClient.new(session: shop_session, base_path: "/admin/oauth")
``` [3](#0-2) 

Compare this to the sibling methods in the same file and module, which sanitize `shop` before it is bound to the credential-bearing session/host:
```ruby
validated_shop = Utils::ShopValidator.sanitize!(shop)
shop_session = ShopifyAPI::Auth::Session.new(shop: validated_shop)
``` [4](#0-3) [5](#0-4) [6](#0-5) 

The identity binding that should hold is: `host that receives client_secret == a Shopify-trusted domain (ShopValidator-validated)`. In `exchange_token` this becomes: `host that receives client_secret == raw JWT "dest" claim value, unchecked`. The `JwtPayload` constructor only validates the `aud` claim against `Context.api_key` [7](#0-6) ; it never validates `dest`/`iss` against `ShopValidator::TRUSTED_SHOPIFY_DOMAINS`.

### Impact Explanation
If any code path allows an app to obtain, decode, or otherwise handle a well-formed but non-Shopify-signed/tampered `session_token` before calling `exchange_token` (e.g., a host application that decodes/re-serializes the token, or any future/alternate signing-key configuration), the resulting host is trusted implicitly and the app's `client_id`/`client_secret` and the `subject_token` are POSTed to whatever host `dest` names, unlike every other flow in this module which enforces `ShopValidator.sanitize!`. This is a credential-exfiltration / SSRF-with-credentials risk class consistent with the "host validated versus host that receives client_secret" analog called for in scope, and is inconsistent with the rest of the module's defensive posture.

### Likelihood Explanation
Under the normal, fully-trusted flow (App Bridge session token verified purely via HS256 with the correct `api_secret_key`), an attacker cannot forge `dest` without already possessing `api_secret_key`, which is explicitly out of scope. This limits the practically demonstrable likelihood without secret compromise. The finding is best framed as a defense-in-depth/consistency gap: `exchange_token` is the only client_secret-sending routine in the gem that omits the `ShopValidator.sanitize!` step present in `client_credentials`, `refresh_access_token`, and `migrate_to_expiring_token`, and the code comment ("Validate the session token and use the shop from the token's `dest` claim") implies validation is expected but the domain-trust check is not actually performed.

### Recommendation
In `TokenExchange.exchange_token`, sanitize `dest_shop` through `Utils::ShopValidator.sanitize!` before constructing `shop_session`, exactly as done in `client_credentials`, `refresh_access_token`, and `migrate_to_expiring_token`:
```ruby
dest_shop = Utils::ShopValidator.sanitize!(jwt_payload.shop)
```
This ensures the host that receives `client_secret` is always constrained to `ShopValidator::TRUSTED_SHOPIFY_DOMAINS`, matching the invariant enforced everywhere else credentials are sent.

### Proof of Concept
1. `JwtPayload.shop` returns the raw `dest` claim value with only the `"https://"` prefix stripped, with no domain trust check [1](#0-0) .
2. `TokenExchange.exchange_token` uses this value unchecked as `dest_shop`, builds `Auth::Session.new(shop: dest_shop)`, and issues an HTTP POST containing `client_id`/`client_secret` to a host derived from `dest_shop` [3](#0-2) .
3. Contrast with `ClientCredentials.client_credentials` [4](#0-3)  and `RefreshToken.refresh_access_token` [5](#0-4) , both of which call `Utils::ShopValidator.sanitize!(shop)` before it is bound to the credential-sending session — the check that is absent in `exchange_token`.

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

**File:** lib/shopify_api/auth/token_exchange.rb (L103-104)
```ruby
          validated_shop = Utils::ShopValidator.sanitize!(shop)
          shop_session = ShopifyAPI::Auth::Session.new(shop: validated_shop)
```

**File:** lib/shopify_api/auth/client_credentials.rb (L25-26)
```ruby
          validated_shop = Utils::ShopValidator.sanitize!(shop)
          shop_session = ShopifyAPI::Auth::Session.new(shop: validated_shop)
```

**File:** lib/shopify_api/auth/refresh_token.rb (L24-25)
```ruby
          validated_shop = Utils::ShopValidator.sanitize!(shop)
          shop_session = ShopifyAPI::Auth::Session.new(shop: validated_shop)
```
