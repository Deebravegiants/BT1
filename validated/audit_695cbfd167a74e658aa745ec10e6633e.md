### Title
Missing `dest` domain validation in `TokenExchange.exchange_token` sends `client_secret` to an unvalidated host - ([File: lib/shopify_api/auth/token_exchange.rb])

### Summary
`ShopifyAPI::Auth::TokenExchange.exchange_token` derives the shop host it sends the app's `client_secret` to directly from the unvalidated `dest` claim of the caller-supplied session token, whereas every sibling credential-exchange method in the same module (and package) runs the shop value through `Utils::ShopValidator.sanitize!` (an allowlist check against `TRUSTED_SHOPIFY_DOMAINS`) before using it to build the outbound request host.

### Finding Description
`JwtPayload#shop` simply strips the scheme from the `dest` claim with no domain allowlisting: [1](#0-0) 

`TokenExchange.exchange_token` takes that unvalidated value (`dest_shop`) and uses it to construct the `Session` that `Clients::HttpClient` uses to build the request host, then puts the app's `client_secret` in the POST body sent to that host: [2](#0-1) 

`Clients::HttpClient#initialize` builds `@base_uri` directly from `session.shop` with no further validation: [3](#0-2) 

Contrast this with every other method in the same file/module that performs the identical "exchange credentials for a token" pattern — `client_credentials`, `refresh_access_token`, and `migrate_to_expiring_token` — all of which explicitly call `Utils::ShopValidator.sanitize!(shop)` before constructing the session used to send `client_secret`: [4](#0-3) [5](#0-4) [6](#0-5) 

The identity binding that should hold is: *the host that receives the app's `client_secret` == a host in `Utils::ShopValidator::TRUSTED_SHOPIFY_DOMAINS`*. In `exchange_token`, this binding is broken — the equality is never checked. The `dest` claim is a JWT field that is trusted (used to select the destination host for a secret-bearing request) without being bound to the same allowlist enforced everywhere else in the module. Note that `JwtPayload` does verify the token's HMAC signature, `exp`/`nbf`, and `aud`, so this is not a forgeable-signature bug; it is a missing defense-in-depth/domain-binding check that the rest of the codebase treats as mandatory for exactly this class of operation (sending `client_secret` to a shop-derived host).

### Impact Explanation
If `dest` is ever not a genuine Shopify-controlled myshopify/admin domain (e.g., due to any Shopify-side session-token issuance edge case, an app's own custom code path, a spin/dev configuration mismatch, or a future change in how the value is populated), `exchange_token` will POST the app's `client_id` and `client_secret` to that host with no allowlist check. That squarely matches the "SSRF with the app's credentials" high-severity category. The severity is high specifically because this is the one exchange path in the module that is missing the check that its three siblings enforce, i.e., a broken equality between "validated shop host" and "host receiving client_secret."

### Likelihood Explanation
Likelihood is moderated by the fact that `dest` is inside a signature-verified JWT, so a fully unprivileged internet attacker with no valid session token cannot exploit this directly today. However, this is a real, demonstrable code defect: it is the only one of four structurally identical "exchange for token" flows in this file that omits `Utils::ShopValidator.sanitize!`, so any relaxation of `dest` trustworthiness (now or in future Shopify token issuance behavior, or reuse of `exchange_token` with attacker-supplied tokens in a misconfigured host app) turns directly into secret exfiltration/SSRF with no code-level backstop, unlike the sibling flows.

### Recommendation
In `lib/shopify_api/auth/token_exchange.rb#exchange_token`, validate `dest_shop` the same way the other methods validate `shop`:
```ruby
dest_shop = Utils::ShopValidator.sanitize!(jwt_payload.shop)
```
before constructing `shop_session` and issuing the request, so the host that receives `client_secret` is always bound to `Utils::ShopValidator::TRUSTED_SHOPIFY_DOMAINS`, consistent with `client_credentials`, `refresh_access_token`, and `migrate_to_expiring_token`.

### Proof of Concept
1. Compare the four token/credential exchange entry points in the package:
   - `ClientCredentials.client_credentials` → calls `Utils::ShopValidator.sanitize!(shop)` [7](#0-6) 
   - `RefreshToken.refresh_access_token` → calls `Utils::ShopValidator.sanitize!(shop)` [8](#0-7) 
   - `TokenExchange.migrate_to_expiring_token` → calls `Utils::ShopValidator.sanitize!(shop)` [9](#0-8) 
   - `TokenExchange.exchange_token` → uses `jwt_payload.shop` (i.e., raw `dest` claim) with **no** call to `Utils::ShopValidator.sanitize!` [10](#0-9) 
2. `JwtPayload#shop` performs no domain check, only a scheme strip: [1](#0-0) 
3. `HttpClient` uses `session.shop` verbatim to build `@base_uri`, then `TokenExchange.exchange_token` POSTs a body containing `client_secret` to `"#{@base_uri}/admin/oauth/access_token"`: [3](#0-2) [11](#0-10) 

This demonstrates the code-level absence of the same domain-allowlist binding that the other three sibling secret-exchange flows enforce, confirmed by direct file comparison; I was not able to further verify (given tool limits) whether any current Shopify session-token issuance path can actually produce a `dest` value outside the trusted domain set, which is the remaining open question for full exploitability confirmation.

### Citations

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

**File:** lib/shopify_api/auth/refresh_token.rb (L18-25)
```ruby
        def refresh_access_token(shop:, refresh_token:)
          unless ShopifyAPI::Context.setup?
            raise ShopifyAPI::Errors::ContextNotSetupError,
              "ShopifyAPI::Context not setup, please call ShopifyAPI::Context.setup"
          end

          validated_shop = Utils::ShopValidator.sanitize!(shop)
          shop_session = ShopifyAPI::Auth::Session.new(shop: validated_shop)
```
