### Title
Session shop domain used to route OAuth token-exchange requests without trust validation - (File: lib/shopify_api/auth/token_exchange.rb)

### Summary
`ShopifyAPI::Auth::TokenExchange.exchange_token` derives the shop domain solely from the JWT `dest` claim and uses it—unsanitized—to build the `HttpClient` that posts the app's `client_id`/`client_secret` to `https://#{dest_shop}/admin/oauth/access_token`, unlike the sibling method `migrate_to_expiring_token`, which calls `Utils::ShopValidator.sanitize!` before using an equivalent shop value.

### Finding Description
In `exchange_token`, the shop used to target the token endpoint is taken directly from `JwtPayload#shop` (which strips `"https://"` from the `dest` claim) with no call to `Utils::ShopValidator.sanitize!`/`sanitize_shop_domain`: [1](#0-0) 
That value is passed straight into `Session.new(shop: dest_shop)` and then into `Clients::HttpClient.new(session: shop_session, ...)`, whose constructor builds the request base URI directly from `session.shop`: [2](#0-1) 
Compare this to `migrate_to_expiring_token` in the same file, which validates the shop with `Utils::ShopValidator.sanitize!(shop)` before constructing the session used for the identical `/admin/oauth/access_token` request: [3](#0-2) 
`JwtPayload` itself only checks that `aud == Context.api_key`; it performs no validation that `iss`/`dest` is a trusted `*.myshopify.com` (or other `ShopValidator::TRUSTED_SHOPIFY_DOMAINS`) domain: [4](#0-3) 

The identity binding that should hold is: *the host that receives `client_id`/`client_secret` during token exchange == a domain in `ShopValidator::TRUSTED_SHOPIFY_DOMAINS`*. In `exchange_token` this equality is never checked—only `aud` is checked, not the destination host used for the outbound POST.

### Impact Explanation
Because the signature check binds the payload only to `Context.api_secret_key` and `aud`, the `dest` field is not independently constrained to a Shopify-controlled domain by this gem. If any code path in the surrounding application (or a future/alternate JWT source) supplies a token satisfying signature/`aud` requirements but with an attacker-influenced `dest`, `exchange_token` will send the app's `client_id` and `client_secret_key` to that attacker-chosen host — this is SSRF carrying the app's credentials, matching the "High - SSRF with the app's credentials... or credential leakage" impact category. The inconsistency with `migrate_to_expiring_token` (which does perform `ShopValidator.sanitize!`) indicates this is a missing check rather than an intentional design decision.

### Likelihood Explanation
Exploitability strictly requires a validly-signed JWT (signed with `Context.api_secret_key` or `old_api_secret_key`) whose `dest` claim is attacker-influenced but which still passes `JwtPayload`'s only content check (`aud == Context.api_key`). Because the signature check binds `Context.api_secret_key`, an unprivileged internet user without access to that secret cannot forge such a token today, which limits the likelihood under the stated in-scope threat model. However, this is a code-level correctness gap distinct from key compromise: the gem has no host-domain check at all for this value, whereas an equivalent value in `migrate_to_expiring_token` is explicitly validated, showing this is the omission the codebase itself intends to guard against.

### Recommendation
Call `Utils::ShopValidator.sanitize!(dest_shop)` (or `sanitize_shop_domain`) on the value derived from `jwt_payload.shop` in `TokenExchange.exchange_token` before constructing `shop_session`/`HttpClient`, mirroring the check already present in `migrate_to_expiring_token`. Additionally, consider having `JwtPayload` validate that `dest`/`iss` resolve to a domain in `ShopValidator::TRUSTED_SHOPIFY_DOMAINS` as part of token construction, so any consumer of `JwtPayload#shop` receives an already-validated value.

### Proof of Concept
Not concretely demonstrable within this gem's own boundary using only unprivileged-internet-user capabilities: exploitation requires a JWT that passes signature verification against `Context.api_secret_key`/`old_api_secret_key`, which an external attacker without the secret cannot produce. The finding is a genuine missing-validation defect (asymmetry with `migrate_to_expiring_token`) but does not currently constitute a provable analog that crosses a credential/tenant boundary without already assuming a compromised or non-standard-issued JWT.

### Citations

**File:** lib/shopify_api/auth/token_exchange.rb (L39-51)
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

**File:** lib/shopify_api/clients/http_client.rb (L11-19)
```ruby
      sig { params(base_path: String, session: T.nilable(Auth::Session)).void }
      def initialize(base_path:, session: nil)
        session ||= Context.active_session
        raise Errors::NoActiveSessionError, "No passed or active session" unless session

        api_host = Context.api_host

        @base_uri = T.let("https://#{api_host || session.shop}", String)
        @base_uri_and_path = T.let("#{@base_uri}#{base_path}", String)
```

**File:** lib/shopify_api/auth/jwt_payload.rb (L33-45)
```ruby
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
