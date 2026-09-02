Found a concrete break in the identity binding for token exchange: `TokenExchange.exchange_token` is the only OAuth flow that constructs the destination host for a `client_secret`-bearing request from the `dest` claim **without** running it through `Utils::ShopValidator.sanitize!`, unlike every sibling method (`client_credentials`, `refresh_access_token`, `migrate_to_expiring_token`) which all explicitly call `Utils::ShopValidator.sanitize!(shop)` before building the session/host used for the token request.

### Title
Unsanitized JWT `dest` claim used as OAuth token-exchange host, unlike all sibling token endpoints - (File: lib/shopify_api/auth/token_exchange.rb)

### Summary
`ShopifyAPI::Auth::TokenExchange.exchange_token` derives the shop/host that receives the app's `client_secret` directly from the session token's `dest` claim, bypassing `Utils::ShopValidator.sanitize!` that every other credential-bearing flow in this gem enforces.

### Finding Description
`exchange_token` decodes the caller-supplied `session_token` via `ShopifyAPI::Auth::JwtPayload.new(session_token)` and takes `dest_shop = jwt_payload.shop` [1](#0-0) . `JwtPayload#shop` merely strips `"https://"` from the raw `dest` claim with no domain allow-listing [2](#0-1) . That value is used unsanitized to build `shop_session = ShopifyAPI::Auth::Session.new(shop: dest_shop)`, which `Clients::HttpClient` turns directly into the request's `base_uri` host: `"https://#{api_host || session.shop}"` [3](#0-2) . The POST body sent to that host contains `client_secret: ShopifyAPI::Context.api_secret_key` [4](#0-3) .

Every other method that performs the same kind of `client_secret`-bearing request enforces the identity binding `validated_shop == ShopValidator.sanitize!(shop)` before using it to build the host:
- `client_credentials` [5](#0-4) 
- `refresh_access_token` [6](#0-5) 
- `migrate_to_expiring_token` [7](#0-6) 

`exchange_token` is the sole exception; it neither validates `dest_shop` against `ShopValidator::TRUSTED_SHOPIFY_DOMAINS` nor otherwise constrains it before using it as an HTTP host for a credential-bearing request.

Note: because `JwtPayload.new` requires the token to verify with `Context.api_secret_key` (or `old_api_secret_key`) via `JWT.decode(..., true, algorithm: "HS256")` [8](#0-7) , an attacker without the app's secret cannot forge an arbitrary `dest` value in a token that will pass this check. The missing `ShopValidator` call is therefore a defense-in-depth gap that deviates from this gem's own established pattern for every analogous call site, rather than a bypassable signature check.

### Impact Explanation
If reached, this would be SSRF carrying the app's `client_secret` to an attacker-chosen host (the `dest` value inside a validly-signed session token) — matching the report's "High" SSRF-with-credentials category, since the destination host is not constrained the way it is in every sibling method in this file.

### Likelihood Explanation
Low likelihood in practice: reaching this code path with an attacker-controlled `dest` requires a session token that already verifies against `Context.api_secret_key`, which an unprivileged internet user does not possess. This is a structural inconsistency versus a directly exploitable-by-outsider bug, unlike the strict rules' credential-boundary requirement.

### Recommendation
Apply the same `Utils::ShopValidator.sanitize!` call to `dest_shop` in `exchange_token` before constructing `shop_session`, matching `client_credentials`, `refresh_access_token`, and `migrate_to_expiring_token`, so the destination host for any `client_secret`-bearing request is always constrained to `ShopValidator::TRUSTED_SHOPIFY_DOMAINS`.

### Proof of Concept
Not independently exploitable by an unauthenticated party under the stated scope constraints: producing a `session_token` with a malicious `dest` value that still passes `JwtPayload`'s HMAC verification requires knowledge of `Context.api_secret_key`, which is explicitly out of scope per the rules ("anything requiring `api_secret_key`... a leaked credential"). No PoC that stays within an unprivileged-internet-user threat model was found.

### Citations

**File:** lib/shopify_api/auth/token_exchange.rb (L39-41)
```ruby
          # Validate the session token and use the shop from the token's `dest` claim
          jwt_payload = ShopifyAPI::Auth::JwtPayload.new(session_token)
          dest_shop = jwt_payload.shop
```

**File:** lib/shopify_api/auth/token_exchange.rb (L52-59)
```ruby
          body = {
            client_id: ShopifyAPI::Context.api_key,
            client_secret: ShopifyAPI::Context.api_secret_key,
            grant_type: TOKEN_EXCHANGE_GRANT_TYPE,
            subject_token: session_token,
            subject_token_type: ID_TOKEN_TYPE,
            requested_token_type: requested_token_type.serialize,
          }
```

**File:** lib/shopify_api/auth/token_exchange.rb (L103-104)
```ruby
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

**File:** lib/shopify_api/auth/jwt_payload.rb (L76-81)
```ruby
      sig { params(token: String, api_secret_key: String).returns(T::Hash[String, T.untyped]) }
      def decode_token(token, api_secret_key)
        JWT.decode(token, api_secret_key, true, leeway: JWT_LEEWAY, algorithm: "HS256")[0]
      rescue JWT::DecodeError => err
        raise ShopifyAPI::Errors::InvalidJwtTokenError, "Error decoding session token: #{err.message}"
      end
```

**File:** lib/shopify_api/clients/http_client.rb (L16-19)
```ruby
        api_host = Context.api_host

        @base_uri = T.let("https://#{api_host || session.shop}", String)
        @base_uri_and_path = T.let("#{@base_uri}#{base_path}", String)
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
