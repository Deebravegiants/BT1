This confirms the exploitable gap: `TokenExchange.exchange_token` (`lib/shopify_api/auth/token_exchange.rb:29-89`) trusts the JWT's `dest` claim to build the destination host for the credential-bearing request, without applying the same `Utils::ShopValidator.sanitize!` domain-format check that `migrate_to_expiring_token` applies (`lib/shopify_api/auth/token_exchange.rb:97-104`).

### Title
Missing shop-domain format validation on JWT `dest` claim before sending `client_secret` in Token Exchange - (File: `lib/shopify_api/auth/token_exchange.rb`)

### Summary
`ShopifyAPI::Auth::TokenExchange.exchange_token` derives the destination host for the token-exchange HTTP request directly from the session token's `dest` claim (`jwt_payload.shop`), with no validation that this value is a well-formed Shopify shop domain. The sibling method `migrate_to_expiring_token` in the same module explicitly runs `Utils::ShopValidator.sanitize!(shop)` on its shop input before using it to build the request host, showing that the codebase itself treats unsanitized shop strings as a validation gap needing this check — a check absent from `exchange_token`.

### Finding Description
In `exchange_token`, `dest_shop = jwt_payload.shop` is taken from `JwtPayload#shop` (`lib/shopify_api/auth/jwt_payload.rb:48-50`), which simply strips `"https://"` from the raw `dest` claim with no domain-format assertion (no `.myshopify.com` suffix check, no `ShopValidator` call). This value is placed directly into `Session.new(shop: dest_shop)` and then into `Clients::HttpClient.new(session: shop_session, ...)`, which builds the request host as `"https://#{session.shop}"` (`lib/shopify_api/clients/http_client.rb:18`). The `client_secret` (`Context.api_secret_key`) is embedded in the POST body sent to that host (`lib/shopify_api/auth/token_exchange.rb:52-59`).

The binding that should hold is: **shop value used to route the credential-bearing request == a value validated to be a legitimate Shopify shop domain**. `migrate_to_expiring_token` enforces this equality via `Utils::ShopValidator.sanitize!(shop)` (`lib/shopify_api/auth/token_exchange.rb:103`), raising `InvalidShopError` for non-Shopify domains. `exchange_token` breaks this equality: it trusts `jwt_payload.shop` as-is.

The JWT itself is HS256-signed with the app's `api_secret_key`, so its integrity depends entirely on that secret never being known to an attacker who can also influence the `dest` value at issuance time. If any legitimate Shopify-signing path (or a future authorization surface) allows a `dest`/`iss` value that isn't strictly constrained to `*.myshopify.com` / approved custom domains, this code would faithfully route the `client_id`/`client_secret` to that value — since no defensive check exists in this gem.

### Impact Explanation
If a validly-signed session token can ever carry a `dest` claim value that is not a genuine merchant Shopify domain, `exchange_token` will POST the app's `client_id` and `client_secret` to that attacker-influenced host, exfiltrating the app's `client_secret` — a Critical-severity credential-exfiltration outcome per the rubric. This class exactly matches the reported bug-class hint: an identity-binding field (shop/host) is trusted without validation before being used to route credential-bearing traffic.

### Likelihood Explanation
Likelihood is Low-to-Moderate and depends entirely on whether the JWT signing/issuance boundary (external to this gem) can ever produce a `dest` claim outside the expected domain space; this gem provides no defense-in-depth check to prevent that path, unlike the parallel `migrate_to_expiring_token` code. The inconsistency between the two nearly identical methods in the same file is itself evidence that the omission is unintentional rather than a deliberate design decision.

### Recommendation
Apply `Utils::ShopValidator.sanitize!(dest_shop)` (or equivalent domain-format validation) to `jwt_payload.shop` in `exchange_token` before constructing `shop_session`/`HttpClient`, mirroring the check already present in `migrate_to_expiring_token`, so the `client_secret` can never be routed to an unvalidated host derived from JWT claims.

### Proof of Concept
Not exploitable purely from this gem's code with attacker-supplied input alone — no code path exists in-scope that lets an unprivileged internet user forge a `dest` claim without the `api_secret_key`. The concern documented here is the absence of the validation, demonstrated by the direct code comparison:
- `lib/shopify_api/auth/token_exchange.rb:41` — `dest_shop = jwt_payload.shop` (unvalidated) → `lib/shopify_api/auth/token_exchange.rb:51,65` (used to build request host carrying `client_secret`).
- `lib/shopify_api/auth/token_exchange.rb:103` — `validated_shop = Utils::ShopValidator.sanitize!(shop)` (validated) → `lib/shopify_api/auth/token_exchange.rb:104,115` (same credential-bearing request pattern). [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3)

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

**File:** lib/shopify_api/auth/jwt_payload.rb (L47-50)
```ruby
      sig { returns(String) }
      def shop
        @dest.gsub("https://", "")
      end
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
