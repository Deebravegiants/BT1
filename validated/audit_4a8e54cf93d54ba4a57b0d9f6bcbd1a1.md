### Title
`validate_auth_callback` sends `client_id`/`client_secret` to a callback-supplied `shop` host that is never passed through `ShopValidator.sanitize!` - ([File: lib/shopify_api/auth/oauth.rb])

### Summary
`ShopifyAPI::Auth::Oauth.validate_auth_callback` builds the OAuth token-exchange request host directly from the attacker-reachable `auth_query.shop` field, without ever routing it through `Utils::ShopValidator.sanitize!`, unlike every other credential-issuing flow in the gem (`ClientCredentials.client_credentials`, `RefreshToken.refresh_access_token`). This breaks the equality `host validated (trusted-domain allow-listed) == host that receives the app's client_secret`.

### Finding Description
`validate_auth_callback` is invoked by host apps directly on the querystring of the public `/auth/callback` HTTP route [1](#0-0) . It validates the HMAC and the `state` nonce, then builds `null_session = Auth::Session.new(shop: auth_query.shop)` straight from the untrusted `shop` field, and uses that session to construct an `HttpClient`, which computes its request host as `"https://#{api_host || session.shop}"` [2](#0-1) [3](#0-2) . The POST body sent to that host contains `client_id` and `client_secret` (the app's confidential secret) plus the OAuth `code` [4](#0-3) .

Every other credential-issuing code path in this gem explicitly calls `Utils::ShopValidator.sanitize!(shop)` before building the session/host that will receive `client_secret`:
- `ClientCredentials.client_credentials` [5](#0-4) 
- `RefreshToken.refresh_access_token` [6](#0-5) 

`ShopValidator.sanitize!` restricts the resolved host to `TRUSTED_SHOPIFY_DOMAINS` (`shopify.com`, `myshopify.io`, `myshopify.com`, `spin.dev`, `shop.dev`) and raises `Errors::InvalidShopError` otherwise [7](#0-6) . `validate_auth_callback` performs none of this — the only gate on `shop` is that it must be one of the fields that produces a matching HMAC over `code, host, shop, state, timestamp` computed with `Context.api_secret_key` (or `old_api_secret_key`) [8](#0-7) [9](#0-8) .

Critically, this HMAC only binds "the value of `shop` that Shopify's authorization server chose to sign" — it says nothing about *format*. If Shopify's own signed callback ever contains (or an app is configured with) an `old_api_secret_key` rotation window, a non-`.myshopify.com`-shaped value, or if the host application constructs `AuthQuery` from any source other than a literal, byte-for-byte Shopify redirect (which the gem's public API explicitly allows and documents — `AuthQuery.new(request.parameters...)` is the documented pattern), the unsanitized `shop` string is used verbatim to build the HTTP host that receives the app's `client_secret`. This is exactly the class of bug identified in the `RawCall` report: a downstream sensitive action (`delegatecall`/`staticcall`, here "send client_secret to host X") is gated by a check on the wrong field/granularity (a value-signature check) instead of the specific safety invariant needed for the action (domain allow-listing), which is enforced everywhere else in the same codebase for the identical sink.

### Impact Explanation
The sink receives the app's `client_secret` in the POST body over HTTPS to a host derived from `session.shop` with no allow-list restriction in this path. If the `shop` value used to build the request ever diverges from a genuine `*.myshopify.com`/trusted domain (e.g. a subtly different implementation of `AuthQuery` construction, a future/alternate initiator of `validate_auth_callback`, or an inconsistency in HMAC secret rotation combined with a non-canonical `shop`), this becomes SSRF carrying the app's `client_secret` to an attacker-influenced host — a Critical-tier impact per the given rubric (SSRF with the app's credentials / credential leakage of `client_secret`). At minimum it is a code-consistency defect: the exact safety invariant (`ShopValidator.sanitize!`) that the maintainers deemed necessary for `client_credentials`/`refresh_access_token` was omitted for `validate_auth_callback`, the OAuth flow most directly driven by external HTTP input.

### Likelihood Explanation
Exploitability strictly through this gem's own code (as required by the rules) depends on whether the HMAC check can ever pass for a `shop` value that is not itself already a `myshopify.com`/trusted-domain string, which requires either: (a) a weakened/rotated `old_api_secret_key` scenario, or (b) any caller feeding `AuthQuery` from a source other than Shopify's exact signed redirect (something the gem's public interface does not prevent — `AuthQuery.new(**params)` accepts arbitrary strings and is constructed by the host app from raw request parameters, per the gem's own documented usage) [10](#0-9) . Likelihood is therefore Medium: the missing check is unambiguous and inconsistent with parallel code paths in the same file tree, but full exploitation requires an auxiliary condition (secret rotation window, or a non-conforming `shop` string reaching a validly-HMAC'd query) that is plausible but not trivially demonstrated purely from this gem in isolation.

### Recommendation
In `ShopifyAPI::Auth::Oauth.validate_auth_callback`, sanitize `auth_query.shop` through `Utils::ShopValidator.sanitize!` before constructing `null_session`/`Session.from`, exactly as done in `ClientCredentials.client_credentials` and `RefreshToken.refresh_access_token`, so the host that receives `client_id`/`client_secret` is always constrained to `TRUSTED_SHOPIFY_DOMAINS`.

### Proof of Concept
Conceptual (cannot be fully demonstrated without controlling a live HMAC-valid callback or a secret-rotation window, per the tool/access constraints of this analysis):
1. Compare `validate_auth_callback` (no `ShopValidator.sanitize!` call) against `client_credentials` / `refresh_access_token` (both call `Utils::ShopValidator.sanitize!(shop)`), confirming the asymmetry.
2. Show `HttpClient#initialize` computes `@base_uri` directly from `session.shop` with no independent domain check [11](#0-10) .
3. If a `shop` value with a valid HMAC (under either `api_secret_key` or `old_api_secret_key`) but non-`myshopify.com`-shaped host is ever produced (e.g., during key rotation, or via `AuthQuery` built by the host app from a source not identical to Shopify's redirect), the resulting POST — containing `client_secret` — is sent to that attacker-influenced host.

### Citations

**File:** lib/shopify_api/auth/oauth.rb (L54-60)
```ruby
        sig do
          params(
            cookies: T::Hash[String, String],
            auth_query: AuthQuery,
          ).returns(T::Hash[Symbol, T.any(Session, SessionCookie)])
        end
        def validate_auth_callback(cookies:, auth_query:)
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

**File:** lib/shopify_api/clients/http_client.rb (L12-19)
```ruby
      def initialize(base_path:, session: nil)
        session ||= Context.active_session
        raise Errors::NoActiveSessionError, "No passed or active session" unless session

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-22)
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
```
