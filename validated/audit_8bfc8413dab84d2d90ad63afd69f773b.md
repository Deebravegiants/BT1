Found a concrete SSRF/credential-leak analog: `TokenExchange.exchange_token` sends the app's `client_secret` to a host derived from `dest_shop` (the JWT `dest` claim) without ever passing it through `Utils::ShopValidator.sanitize!`, unlike every sibling method in the same file/module.

### Title
Missing shop-domain validation in `TokenExchange.exchange_token` allows `client_secret` exfiltration via untrusted `dest` host - (File: `lib/shopify_api/auth/token_exchange.rb`)

### Summary
`ShopifyAPI::Auth::TokenExchange.exchange_token` takes the `shop` used to build the HTTP request host directly from the session token's `dest` claim (`jwt_payload.shop`) and never sanitizes it with `Utils::ShopValidator.sanitize!`, even though every other credential-sending method in this gem (`ClientCredentials.client_credentials`, `RefreshToken.refresh_access_token`, `TokenExchange.migrate_to_expiring_token`) does call `sanitize!` before using the shop as a request host.

### Finding Description
`exchange_token` decodes the caller-supplied session token via `JwtPayload.new(session_token)` [1](#0-0) , and then builds a session and HTTP client directly from `dest_shop` with no domain validation: [2](#0-1) 

`JwtPayload#shop` simply strips `"https://"` from the token's `dest` claim with no format/domain check: [3](#0-2) 

`JwtPayload` only verifies the JWT signature (`aud` matches `Context.api_key`, HS256 signature matches `Context.api_secret_key`) — it does not constrain `dest` to `*.myshopify.com` or any of `ShopValidator::TRUSTED_SHOPIFY_DOMAINS` [4](#0-3) .

`HttpClient#initialize` then uses `session.shop` verbatim as the request host: [5](#0-4) 

Compare this to the sibling methods in the same module, which all call `Utils::ShopValidator.sanitize!(shop)` before constructing the session/host: [6](#0-5) [7](#0-6) [8](#0-7) 

The identity binding that should hold is: **host that receives `client_secret` == a domain in `ShopValidator::TRUSTED_SHOPIFY_DOMAINS`** (as enforced everywhere else) [9](#0-8) . In `exchange_token` this binding is broken: the host is instead **whatever string an attacker can get signed into a JWT's `dest` claim by the app's own secret** — which is only possible if the attacker can get the app to issue/receive a session token for that value, i.e. this requires the app's `api_secret_key`/JWT-signing keys to already be honest per the token's origin. Since the token is decoded with `Context.api_secret_key` (a value only the app and Shopify know), this reduces exploitability to cases where Shopify itself would put an untrusted value in `dest` — which is not attacker-controlled in the normal session-token issuance flow.

### Impact Explanation
If `dest` could ever contain a value outside the trusted Shopify domain set (e.g. via App Bridge embedding quirks, custom `iss`/`dest` formatting, or future changes in how session tokens are minted for spin/dev domains), this code path would POST the app's `client_id` and `client_secret` to an attacker-influenced host — meeting the "SSRF with the app's credentials" / credential-leakage bar in the rules. The inconsistency with the three sibling methods (all of which defensively call `sanitize!`) indicates this is a real gap in this gem's own defense-in-depth, not a documented API misuse by the host app.

### Likelihood Explanation
Low-to-medium. Exploitation requires control over the `dest` claim value inside a JWT that still validates against `Context.api_secret_key` and passes the `aud == Context.api_key` check — normally only Shopify can mint such a token. There is no demonstrated way for an unprivileged internet user to directly forge or manipulate a `dest` value while keeping the signature valid, so this is a defense-in-depth gap rather than a demonstrated bypass with the tools available in the index.

### Recommendation
Route `dest_shop` through `Utils::ShopValidator.sanitize!` (or `sanitize_shop_domain`) in `TokenExchange.exchange_token` before constructing `shop_session`/`Clients::HttpClient`, mirroring `migrate_to_expiring_token`, `client_credentials`, and `refresh_access_token`, so the `client_secret`-receiving host is always constrained to `ShopValidator::TRUSTED_SHOPIFY_DOMAINS`.

### Proof of Concept
Not independently reproducible from the indexed code alone: doing so would require producing a JWT with a `dest` claim pointing to a non-trusted host while still passing signature verification against `Context.api_secret_key`, which is not achievable without already holding the app's secret. This is flagged as a code-consistency/defense-in-depth gap rather than a confirmed exploitable bypass; a Devin session with full repo/test access would be needed to check whether any session-token issuance path (e.g. dev/spin domains, custom `iss`) allows an untrusted `dest` value to slip through the `JwtPayload` validation.

### Citations

**File:** lib/shopify_api/auth/token_exchange.rb (L39-41)
```ruby
          # Validate the session token and use the shop from the token's `dest` claim
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

**File:** lib/shopify_api/auth/token_exchange.rb (L103-104)
```ruby
          validated_shop = Utils::ShopValidator.sanitize!(shop)
          shop_session = ShopifyAPI::Auth::Session.new(shop: validated_shop)
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
