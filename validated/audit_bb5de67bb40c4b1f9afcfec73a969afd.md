Confirmed root cause: `ShopifyAPI::Auth::Oauth.validate_auth_callback` (`lib/shopify_api/auth/oauth.rb`) is the only credential-sending flow in this gem that never calls `Utils::ShopValidator.sanitize!` on the shop value before using it as the destination host for the `client_secret`-bearing token request. Every sibling flow (`ClientCredentials.client_credentials`, `RefreshToken.refresh_access_token`, `TokenExchange.migrate_to_expiring_token`) sanitizes the shop first.

### Title
OAuth callback sends `client_secret` to an unsanitized `shop` host, bypassing myshopify-domain binding - (File: lib/shopify_api/auth/oauth.rb)

### Summary
`validate_auth_callback` builds the access-token exchange request directly from `auth_query.shop` without ever passing it through `Utils::ShopValidator.sanitize!`, unlike every other credential-issuing flow in the gem.

### Finding Description
The equality this gem is supposed to enforce is: `host that received a valid HMAC signature == host that is authorized to receive the app's client_secret`. `HmacValidator.validate` confirms that `code/host/shop/state/timestamp` were signed together with `Context.api_secret_key` [1](#0-0) [2](#0-1) , but that check only proves the query bytes weren't tampered with — it says nothing about whether `shop` is an actual `*.myshopify.com` (or otherwise trusted) domain. `validate_auth_callback` then takes that raw, HMAC-verified-but-unsanitized `auth_query.shop` and uses it as-is to construct a `Session`/`HttpClient` that POSTs `client_id`, `client_secret`, and the authorization `code` to `https://#{shop}/admin/oauth/access_token`: [3](#0-2) .

Compare this with the gem's other three credential-issuing paths, which all call `Utils::ShopValidator.sanitize!(shop)` — which restricts the destination host to `TRUSTED_SHOPIFY_DOMAINS` (`shopify.com`, `myshopify.io`, `myshopify.com`, `spin.dev`, `shop.dev`) or an explicitly configured `myshopify_domain` — before building the session used to send the client_secret: [4](#0-3) [5](#0-4) [6](#0-5) . `ShopValidator.sanitize!` raises `Errors::InvalidShopError` unless the resulting host resolves to one of these trusted domains: [7](#0-6) .

`validate_auth_callback` is the only one of the four flows that skips this step, so the binding "HMAC-signed shop" == "trusted admin host" is never actually checked at the point where the `client_secret` leaves the app.

### Impact Explanation
If the `shop` value reaching `validate_auth_callback` can be influenced (e.g., an app that forwards a `shop` query parameter from the incoming HTTP request into `AuthQuery` and only relies on `validate_auth_callback`'s internal checks — which is exactly how the gem's own documentation describes wiring this method, receiving `shop` from `request` params, in `docs/usage/oauth.md`), the effective destination host for the `client_secret`-bearing POST request is not constrained to `*.myshopify.com`/trusted domains by the gem itself. This is exactly the SSRF-with-app-credentials class called out as High severity: the app's own `client_id`/`client_secret` are sent by the gem to a host that was never confirmed to be a legitimate Shopify domain.

### Likelihood Explanation
Medium. Exploitation requires that a value affecting `auth_query.shop` in the callback reach an attacker-influenced path and that the calling application does not perform its own equivalent sanitization before constructing `AuthQuery` — the HMAC does cover `shop`, so a fully independent attacker without knowledge of `api_secret_key` cannot arbitrarily rewrite `shop` in a still-valid callback. The vulnerability is a missing defense-in-depth check that the gem itself performs everywhere else in its own credential-exchange code paths, making this an internal inconsistency/gap rather than a fully attacker-controlled bypass in isolation.

### Recommendation
In `ShopifyAPI::Auth::Oauth.validate_auth_callback`, call `Utils::ShopValidator.sanitize!(auth_query.shop)` (mirroring `ClientCredentials`, `RefreshToken`, and `TokenExchange.migrate_to_expiring_token`) and use the sanitized/validated host — not the raw `auth_query.shop` — both for the `null_session`/`HttpClient` construction and for the resulting `Session.from(shop: ...)` call, so the same trusted-domain binding is enforced before any request carrying `client_secret` is issued.

### Proof of Concept
Not independently exploitable purely within this gem without an application that forwards unsanitized `shop` values into `AuthQuery`; conceptually:
1. App builds `AuthQuery` for the OAuth callback using a `shop` value taken from request input (as shown in `docs/usage/oauth.md`), assuming `validate_auth_callback` fully validates it.
2. `HmacValidator.validate` only confirms the bytes are unmodified relative to what was signed together — it never checks the shop is a real Shopify domain [8](#0-7) .
3. `validate_auth_callback` proceeds to POST `client_secret` to `https://#{auth_query.shop}/admin/oauth/access_token` with no `ShopValidator.sanitize!` check [9](#0-8) , unlike its sibling flows.

### Citations

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

**File:** lib/shopify_api/auth/oauth.rb (L60-94)
```ruby
        def validate_auth_callback(cookies:, auth_query:)
          unless Context.setup?
            raise Errors::ContextNotSetupError, "ShopifyAPI::Context not setup, please call ShopifyAPI::Context.setup"
          end
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
          rescue ShopifyAPI::Errors::HttpResponseError => e
            raise Errors::RequestAccessTokenError,
              "Cannot complete OAuth process. Received a #{e.code} error while requesting access token."
          end
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

**File:** lib/shopify_api/utils/shop_validator.rb (L8-64)
```ruby
    module ShopValidator
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
