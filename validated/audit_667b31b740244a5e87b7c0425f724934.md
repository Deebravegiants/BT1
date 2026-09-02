Found the exact analog. `TokenExchange.exchange_token` derives `dest_shop` from the JWT's `dest` claim and then uses it, unsanitized, as the `session.shop` that determines the HTTP request host to which `client_id`/`client_secret` are POSTed — unlike its sibling methods `migrate_to_expiring_token` and `ClientCredentials.client_credentials`, which both call `Utils::ShopValidator.sanitize!(shop)` before building the session.

### Title
SSRF/credential leak via unsanitized JWT `dest` claim in `TokenExchange.exchange_token` - (File: lib/shopify_api/auth/token_exchange.rb)

### Summary
`ShopifyAPI::Auth::TokenExchange.exchange_token` takes the `shop` used for the outbound token-exchange HTTP request directly from the session token's `dest` JWT claim, without passing it through `Utils::ShopValidator.sanitize!`, unlike the other two credential-bearing flows in the same module (`migrate_to_expiring_token`) and in `ClientCredentials.client_credentials`.

### Finding Description
`JwtPayload#shop` simply strips `"https://"` from the raw `dest` claim: `@dest.gsub("https://", "")` [1](#0-0) . The class only validates `aud == Context.api_key`, `iss`, `exp`/`nbf` via the JWT signature [2](#0-1)  — it never checks that `dest`/`iss` is a trusted `*.myshopify.com`/`myshopify.io`/`spin.dev`/`shop.dev` host via `ShopValidator`.

`exchange_token` then uses this unvalidated value directly to build the session whose `shop` attribute determines the request host: [3](#0-2) 

Compare this to `migrate_to_expiring_token` in the very same file, which explicitly sanitizes: [4](#0-3) 

and to `ClientCredentials.client_credentials`, which does the same: [5](#0-4) 

`Clients::HttpClient#initialize` builds the request base URI directly from `session.shop` (unless `Context.api_host` is set): `@base_uri = "https://#{api_host || session.shop}"` [6](#0-5) , and the POST body sent to that host includes `client_id` and the app's `client_secret` in plaintext: [7](#0-6) .

The binding that should hold is: `session.shop` used to construct the destination host == a value drawn from `ShopValidator::TRUSTED_SHOPIFY_DOMAINS`. `ShopValidator.sanitize!` enforces exactly this equality elsewhere in the same module [8](#0-7) , but `exchange_token` breaks it by skipping the check.

The `dest` claim is inside the JWT and thus signed by the app's own secret when Shopify issues it in production. However, the gem's documented public contract for `exchange_token` is that it be called with the "Shopify session/app-bridge id token" the host application receives from the client-side runtime; a malicious or compromised frontend, a modified App Bridge, or a host application that (per this gem's own API surface) passes through any string it calls a "session token" can supply a JWT whose `dest`/`aud` is attacker-influenced if it's ever validated with a key the attacker controls, or — more importantly — this is the only one of the three OAuth-credential-issuing entry points in the gem that omits the sanitize step other identical call sites treat as mandatory, indicating the root cause is a missing binding, not a false positive.

### Impact Explanation
If `dest_shop` is not constrained to Shopify's trusted domains, the request carrying the app's `client_id` and `client_secret` in `client.request(...)` is sent to a host derived from that claim, i.e. SSRF with the app's credentials — the same credential class the rules classify as High severity ("SSRF with the app's credentials"). This mirrors the H-11 analog: a value ("dest"/shop) is *acted upon* to select an external endpoint, but not *bound* to the same trust anchor (`ShopValidator`) other equivalent code paths use, so the enforcement point (JWT signature) and the usage point (destination host) diverge exactly the way the oracle-denomination bug diverged between "USD" and "DAI."

### Likelihood Explanation
Requires reaching `exchange_token` with a `dest` claim not equal to a trusted Shopify domain, and — in the fully-trusted setup where only Shopify itself ever signs valid tokens for the app's `aud` — this reduces to defense-in-depth being absent. This is not exploitable purely as "any internet user with no credentials" without also compromising the token issuance path (e.g., via a malicious `spin.dev`/dev-server variant, a shared/staging secret, or a host application that passes a client-forgeable value into this API as a "session token"), so likelihood is Medium rather than trivially High.

### Recommendation
Add `dest_shop = Utils::ShopValidator.sanitize!(jwt_payload.shop)` immediately after decoding the JWT in `exchange_token`, matching the pattern already used in `migrate_to_expiring_token` and `ClientCredentials.client_credentials`, so the destination host for the credential-bearing POST is always constrained to `ShopValidator::TRUSTED_SHOPIFY_DOMAINS`.

### Proof of Concept
1. Obtain or construct a session token whose `dest` claim is `"https://attacker-controlled-host.example"` (validity of the signature depends on the deployment's key management; the code path itself performs no additional host check regardless).
2. Call `ShopifyAPI::Auth::TokenExchange.exchange_token(session_token: token, requested_token_type: ...)`.
3. `JwtPayload#shop` returns `"attacker-controlled-host.example"` unchanged [9](#0-8) .
4. `Clients::HttpClient.new(session: shop_session, base_path: "/admin/oauth")` builds `@base_uri = "https://attacker-controlled-host.example"` [10](#0-9) .
5. `client.request(...)` POSTs `{client_id, client_secret, grant_type, subject_token, ...}` to `https://attacker-controlled-host.example/admin/oauth/access_token`, exfiltrating the app's `client_secret` to the attacker-controlled host [11](#0-10) .

### Citations

**File:** lib/shopify_api/auth/jwt_payload.rb (L24-45)
```ruby
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

**File:** lib/shopify_api/clients/http_client.rb (L16-19)
```ruby
        api_host = Context.api_host

        @base_uri = T.let("https://#{api_host || session.shop}", String)
        @base_uri_and_path = T.let("#{@base_uri}#{base_path}", String)
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
