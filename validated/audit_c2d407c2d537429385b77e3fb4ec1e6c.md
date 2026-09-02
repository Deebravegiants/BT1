This confirms the key finding: `Clients::HttpClient#initialize` builds `@base_uri = "https://#{api_host || session.shop}"` directly from `session.shop` [1](#0-0) , and `TokenExchange.exchange_token` builds that `session.shop` from `jwt_payload.shop` (the JWT `dest` claim) without ever passing it through `Utils::ShopValidator.sanitize!`, unlike every sibling OAuth flow in the same file/module.

### Title
Missing domain validation of session-token `dest` claim before it is used as the OAuth token-exchange host, exfiltrating `client_secret` to an unverified host - (File: `lib/shopify_api/auth/token_exchange.rb`)

### Summary
`TokenExchange.exchange_token` derives the host it sends the app's `client_id`/`client_secret` to directly from the JWT `dest` claim, bypassing the `ShopValidator.sanitize!` check that every other OAuth-grant method in this gem performs on shop input.

### Finding Description
`JwtPayload#shop` returns `@dest.gsub("https://", "")` [2](#0-1) , a value that is verified only for a valid signature/`aud`, not for being a trusted `myshopify.com`/`myshopify.io`/`spin.dev`/`shop.dev` domain — that trusted-domain check is what `ShopValidator` enforces separately [3](#0-2) .

`TokenExchange.exchange_token` takes this unvalidated value as `dest_shop`, wraps it directly in a `Session`, and hands it to `Clients::HttpClient`: [4](#0-3) 

By contrast, every other grant flow in the very same file/module validates the shop before using it as a request host:
- `TokenExchange.migrate_to_expiring_token` calls `Utils::ShopValidator.sanitize!(shop)` [5](#0-4) 
- `ClientCredentials.client_credentials` calls `Utils::ShopValidator.sanitize!(shop)` [6](#0-5) 
- `RefreshToken.refresh_access_token` calls `Utils::ShopValidator.sanitize!(shop)` [7](#0-6) 

`Clients::HttpClient#initialize` then builds the request base URI straight from `session.shop`, with no additional domain check: `@base_uri = "https://#{api_host || session.shop}"` [1](#0-0) . The POST body sent to that host includes `client_id` and the app's `client_secret` in plaintext [8](#0-7) .

The identity binding that should hold is: **host that receives the `client_secret` == a domain independently verified to be a genuine Shopify shop domain**. Because the token-exchange path skips `ShopValidator.sanitize!`, this binding is broken — the host is taken as-is from `dest` after only a literal `"https://"` string-strip, with no scheme/domain allow-listing (e.g., a `dest` of `"http://evil.example"` would not even match the `"https://"` substring and would pass through unchanged).

### Impact Explanation
If a `dest` claim value can ever resolve to an attacker-influenced/non-myshopify host (e.g., through App Bridge session tokens sourced from non-`/admin` issuers, spoofed embed contexts, or any future JWT source this method is fed with), the gem will POST the app's `client_id` and `client_secret` — its highest-value credential — to that host. This matches the report's SSRF/credential-exfiltration class: an outbound, server-initiated HTTP request whose destination is attacker-influenced rather than allow-listed, here carrying the app's OAuth client secret instead of just probing ports.

### Likelihood Explanation
Exploitability depends entirely on whether an attacker can get `JwtPayload.new` to accept and return a `dest` claim pointing off the myshopify family while still satisfying `JwtPayload`'s own checks (valid signature under `api_secret_key`/`old_api_secret_key`, matching `aud`) [9](#0-8) . `JwtPayload` performs no `iss`/`dest` domain restriction itself, so trust in `dest` rests solely on "this token was minted by Shopify," which is the deprecated rationale used to remove the old `validate_shop` check per the changelog [10](#0-9) . This is an internal inconsistency in the codebase (three sibling methods still validate, this one doesn't) rather than a proven remotely-forgeable input; I could not find a code path in this repo that lets an unprivileged internet user supply an arbitrary `dest` into a signature-valid token, so full exploitability could not be confirmed from static analysis alone.

### Recommendation
In `TokenExchange.exchange_token`, apply `Utils::ShopValidator.sanitize!` (or an equivalent allow-list check against `ShopValidator::TRUSTED_SHOPIFY_DOMAINS`) to `dest_shop` before constructing `shop_session`/`Clients::HttpClient`, matching the pattern already used in `migrate_to_expiring_token`, `ClientCredentials.client_credentials`, and `RefreshToken.refresh_access_token`.

### Proof of Concept
Not fully constructible from this gem alone: exploitation requires producing a JWT that both (a) verifies against `Context.api_secret_key`/`old_api_secret_key` and matches `aud`, and (b) carries a `dest` claim outside the myshopify domain family. Conceptually:
1. Obtain/derive a session token whose `dest` claim is `https://attacker.example` yet still passes `JWT.decode(token, api_secret_key, true, algorithm: "HS256")` and `aud == Context.api_key`.
2. Call `ShopifyAPI::Auth::TokenExchange.exchange_token(session_token: token, requested_token_type: ...)`.
3. Observe that `Clients::HttpClient` POSTs `client_id`/`client_secret` to `https://attacker.example/admin/oauth/access_token` [1](#0-0) [11](#0-10) , unlike the sibling `sanitize!`-guarded flows which would raise `Errors::InvalidShopError` for the same input.

### Citations

**File:** lib/shopify_api/clients/http_client.rb (L16-19)
```ruby
        api_host = Context.api_host

        @base_uri = T.let("https://#{api_host || session.shop}", String)
        @base_uri_and_path = T.let("#{@base_uri}#{base_path}", String)
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

**File:** CHANGELOG.md (L220-221)
```markdown
- [#935](https://github.com/Shopify/shopify-api-ruby/pull/935) Fix issue [#931](https://github.com/Shopify/shopify-api-ruby/pull/931), weight of variant should be float
- [#944](https://github.com/Shopify/shopify-api-ruby/pull/944) Deprecated the `validate_shop` method from the JWT class since we can trust the token payload, since it comes from Shopify.
```
