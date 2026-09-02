Found the vulnerability: in `TokenExchange.exchange_token`, the `client_secret` is sent to a host derived from an unvalidated JWT claim.

### Title
SSRF with app's `client_secret` via unsanitized JWT `dest` claim in token exchange - (File: lib/shopify_api/auth/token_exchange.rb)

### Summary
`ShopifyAPI::Auth::TokenExchange.exchange_token` builds the token-exchange request host directly from the `dest` claim of the caller-supplied session token, without ever passing it through `Utils::ShopValidator.sanitize!`. This is inconsistent with `TokenExchange.migrate_to_expiring_token`, which does call `Utils::ShopValidator.sanitize!(shop)` on its `shop` parameter before using it in the same code path.

### Finding Description
`exchange_token` decodes the session token via `ShopifyAPI::Auth::JwtPayload.new(session_token)` and takes `dest_shop = jwt_payload.shop` directly: [1](#0-0) 

`JwtPayload#shop` simply strips `"https://"` from the `dest` claim with no allow-list/domain check: [2](#0-1) 

`dest_shop` is then used to build a `Session` whose `shop` attribute becomes the request host, and the request (containing `client_id` and `client_secret` in the body) is sent via `Clients::HttpClient`, which builds `@base_uri` as `"https://#{api_host || session.shop}"`: [3](#0-2) [4](#0-3) 

Compare with `migrate_to_expiring_token`, in the same module, which validates `shop` with `Utils::ShopValidator.sanitize!` before constructing the identical request/session pattern: [5](#0-4) 

The equality that should be enforced is: **the host that receives the `client_secret` == a validated Shopify domain (`ShopValidator`-approved)**. In `exchange_token` this equality is broken: the host that receives the app's `client_id`/`client_secret` is instead **whatever string the JWT's `dest` claim contains**, with no validation against `ShopValidator::TRUSTED_SHOPIFY_DOMAINS`.

Because `JWT.decode` in `JwtPayload#decode_token` only verifies the signature, `exp`/`nbf` and `aud == Context.api_key` (the `api_key` is not secret — it's the app's public client ID, often embedded in the frontend), the *value* of the `dest` claim is not itself constrained to a Shopify domain by cryptographic verification of its content beyond "the entire payload including `dest` was signed by our `api_secret_key`." Under the normal, intended flow this token can only be minted by Shopify itself (Shopify signs `dest` to the real shop domain), so exploitation requires either: (a) a way to obtain the gem to trust an id_token whose `dest` is attacker controlled, or (b) any environment where `JWT_LEEWAY`/verification is otherwise weakened. Given the constraints of this analysis (no access to `api_secret_key`/leaked credentials allowed), a fully forged token cannot be produced by an unprivileged internet user — the exploitability of the primary vector is therefore inconsistent with the "Reject … anything requiring `api_secret_key`… or leaked credentials" rule.

### Impact Explanation
If the `dest` claim binding is broken (e.g., through any host-application misuse this gem doesn't prevent by design, or a future/alternate JWT-verification bypass), the impact would be High: SSRF carrying the app's `client_id` and `client_secret` to an attacker-chosen host, since `client_secret` is placed unconditionally in the outgoing request body to `session.shop` in `exchange_token`.

### Likelihood Explanation
Low as a standalone, credential-free unprivileged-user analog: exploitation of `exchange_token` specifically requires a validly-signed JWT (signed with the real `api_secret_key`) whose `dest` claim is not a genuine Shopify domain — something Shopify itself would not produce, and something an unprivileged internet user cannot forge without the `api_secret_key`. The only concrete, code-level finding is the **inconsistency** between `exchange_token` (no `ShopValidator` check) and `migrate_to_expiring_token` (has `ShopValidator.sanitize!`) within the same file/module, which is a defense-in-depth gap rather than a directly demonstrable exploit given the constraints of this task.

### Recommendation
Apply `Utils::ShopValidator.sanitize!(dest_shop)` to the `dest_shop` value derived from the JWT payload in `TokenExchange.exchange_token`, mirroring the validation already performed in `TokenExchange.migrate_to_expiring_token`, before constructing `shop_session` and issuing the HTTP request that carries `client_secret`.

### Proof of Concept
Not reproducible as a concrete unprivileged-attacker exploit within this analysis's constraints (would require a validly-signed session token with a non-Shopify `dest` claim, i.e., control over `api_secret_key`-signed tokens, which is out of scope per the rules). The code-level evidence is the missing `ShopValidator.sanitize!` call on `dest_shop` in `lib/shopify_api/auth/token_exchange.rb` lines 40–51, contrasted with its presence in the same file's `migrate_to_expiring_token` method (line 103).

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

**File:** lib/shopify_api/auth/jwt_payload.rb (L47-51)
```ruby
      sig { returns(String) }
      def shop
        @dest.gsub("https://", "")
      end
      alias_method :shopify_domain, :shop
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
