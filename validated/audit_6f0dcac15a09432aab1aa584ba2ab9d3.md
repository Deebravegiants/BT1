## Title
`TokenExchange.exchange_token` builds the token-exchange host from an unvalidated JWT `dest` claim, sending the app's `client_secret` to attacker-influenced hosts — ([File: lib/shopify_api/auth/token_exchange.rb])

### Summary
`ShopifyAPI::Auth::TokenExchange.exchange_token` derives the shop host used to send the app's `client_id`/`client_secret` (via `Clients::HttpClient`) directly from the JWT `dest` claim (`jwt_payload.shop`), **without ever routing it through `Utils::ShopValidator.sanitize!`**, unlike every sibling method in the same file (`migrate_to_expiring_token`) and in `client_credentials.rb`, which both call `Utils::ShopValidator.sanitize!(shop)` before constructing the session/host.

### Finding Description
The binding that should hold is: **the host that receives the `client_secret` == a value verified to be a genuine `*.myshopify.com`/trusted Shopify domain**.

- `JwtPayload#shop` simply returns `@dest.gsub("https://", "")` (`lib/shopify_api/auth/jwt_payload.rb:47-50`) with no domain-format restriction — `dest` is only checked for JWT signature/`aud`, not that it resolves to a `myshopify.com`/trusted host.
- `TokenExchange.exchange_token` (`lib/shopify_api/auth/token_exchange.rb:40-51`) takes `dest_shop = jwt_payload.shop` and immediately does `shop_session = ShopifyAPI::Auth::Session.new(shop: dest_shop)`, then `Clients::HttpClient.new(session: shop_session, base_path: "/admin/oauth")`.
- `HttpClient#initialize` (`lib/shopify_api/clients/http_client.rb:16-19`) builds `@base_uri = "https://#{api_host || session.shop}"` directly from `session.shop` — no sanitization occurs here either.
- The request body sent to that host includes `client_secret: ShopifyAPI::Context.api_secret_key` (`lib/shopify_api/auth/token_exchange.rb:52-59`).

Contrast this with the two other flows in the same module: `migrate_to_expiring_token` explicitly calls `validated_shop = Utils::ShopValidator.sanitize!(shop)` (`lib/shopify_api/auth/token_exchange.rb:103`) before building the session, and `ClientCredentials.client_credentials` does the same (`lib/shopify_api/auth/client_credentials.rb:25`). `exchange_token` is the outlier that skips this check while still using its "shop" value to build the destination host for the credential-bearing POST.

While the `aud` claim of the JWT is verified against `Context.api_key`, the `dest`/`iss` claims themselves are **not constrained to end in `myshopify.com` or any Shopify-trusted suffix** anywhere in `JwtPayload`. Since the token is HS256-signed with `Context.api_secret_key`, an attacker without that secret cannot forge a token from scratch — but this still leaves a documented API-shape mismatch: the maintainers evidently consider `shop` values needing sanitization before being used to construct a request host (as shown by the two sibling flows), yet `exchange_token`, the newest and now-canonical OAuth flow (recommended by `docs/usage/oauth.md`), omits it. If `dest` is ever attacker-influenceable (e.g., an app embedding a modified/relayed token, or a future change that decodes `dest` before verifying issuer format), the app's `client_secret` would be sent to a host chosen by that field.

### Impact Explanation
If reachable, this results in exfiltration of the app's `client_secret` to a non-Shopify host (SSRF carrying the app's credential) — a High-severity outcome per the taxonomy (SSRF with the app's credentials / credential leakage). This maps directly to the report's bug class: "a JWT claim trusted without being bound" — here, `dest`/`shop` is trusted as a routable host without being bound to the `myshopify.com`/trusted-domain constraint enforced by `ShopValidator` elsewhere in the same file.

### Likelihood Explanation
Under the gem's designed trust model (JWT signature requires possession of `api_secret_key`), directly forging `dest` is not possible for an unprivileged internet user, so today's exploitability is constrained. However, this is flagged because the gem's own internal contract (evidenced by `client_credentials.rb` and `migrate_to_expiring_token`) treats raw `shop`/`dest`-derived values as requiring sanitization before being used as a request host, and `exchange_token` — the primary, documented, and recommended token-exchange path — silently violates that contract. This inconsistency is a real defect in the identity-binding chain (host used for credential POST vs. host validated as trusted), even though full exploitation would additionally require an unverified or relayed token acceptance path in the host application.

### Recommendation
Add `validated_shop = Utils::ShopValidator.sanitize!(dest_shop)` in `TokenExchange.exchange_token`, mirroring `migrate_to_expiring_token` and `ClientCredentials.client_credentials`, and use `validated_shop` for both `shop_session` construction and `Session.from(shop: ...)`. Additionally, consider enforcing the `myshopify.com`/trusted-domain shape check for `dest`/`iss` inside `JwtPayload` itself so no consumer of the JWT can bypass this invariant.

### Proof of Concept
Not independently reproducible against this gem in isolation, because `JwtPayload` requires a token signed with `Context.api_secret_key`, which an external attacker does not possess; conceptually, the gap is demonstrated by comparing the code paths:

```ruby
# lib/shopify_api/auth/token_exchange.rb:40-51 (NOT sanitized)
jwt_payload = ShopifyAPI::Auth::JwtPayload.new(session_token)
dest_shop = jwt_payload.shop                      # <-- from JWT `dest`, no domain-shape check
shop_session = ShopifyAPI::Auth::Session.new(shop: dest_shop)
client = Clients::HttpClient.new(session: shop_session, base_path: "/admin/oauth")
# body includes Context.api_secret_key -> POSTed to "https://#{dest_shop}/admin/oauth/access_token"

# lib/shopify_api/auth/token_exchange.rb:103 (sanitized, contrast)
validated_shop = Utils::ShopValidator.sanitize!(shop)
shop_session = ShopifyAPI::Auth::Session.new(shop: validated_shop)
``` [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4)

### Citations

**File:** lib/shopify_api/auth/token_exchange.rb (L40-59)
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

**File:** lib/shopify_api/auth/jwt_payload.rb (L33-50)
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

      sig { returns(String) }
      def shop
        @dest.gsub("https://", "")
      end
```
