### Title
Unvalidated `shop` from OAuth callback query used to route the app's `client_secret` — `ShopValidator` inconsistently applied across auth flows - ([File: lib/shopify_api/auth/oauth.rb])

### Summary
Every other credential-exchange flow in this gem (`TokenExchange.migrate_to_expiring_token`, `ClientCredentials.client_credentials`, `RefreshToken.refresh_access_token`) sanitizes the `shop` value with `Utils::ShopValidator.sanitize!` before using it to build the request host that receives `client_id`/`client_secret`. `Oauth.validate_auth_callback`, however, takes `auth_query.shop` directly off the incoming callback query string and uses it, unsanitized, both to build the `Session` and as the host component of the POST to `/admin/oauth/access_token` where the app's `client_secret` is sent.

### Finding Description
In `lib/shopify_api/auth/oauth.rb`, `validate_auth_callback` only checks `Utils::HmacValidator.validate(auth_query)` [1](#0-0)  and state/cookie equality, then immediately builds `null_session = Auth::Session.new(shop: auth_query.shop)` and issues the token request against that shop's host, carrying `client_id`/`client_secret` in the body: [2](#0-1)  The host that receives the request is built by `auth_base_uri`/`Clients::HttpClient`, keyed on `session.shop` with no domain restriction to `*.myshopify.com` or the other `ShopValidator::TRUSTED_SHOPIFY_DOMAINS` [3](#0-2) .

By contrast, `ClientCredentials.client_credentials` [4](#0-3) , `RefreshToken.refresh_access_token` [5](#0-4) , and `TokenExchange.migrate_to_expiring_token` [6](#0-5)  all call `Utils::ShopValidator.sanitize!(shop)` before constructing the session/host that will receive the client secret. `ShopValidator.sanitize!` enforces that the resolved host belongs to `ShopValidator::TRUSTED_SHOPIFY_DOMAINS` (`shopify.com`, `myshopify.io`, `myshopify.com`, `spin.dev`, `shop.dev`) [7](#0-6)  and raises `Errors::InvalidShopError` otherwise [8](#0-7) . `Oauth.validate_auth_callback` is the one credential-exfiltration path in this module that never calls this sanitizer.

This breaks the intended binding: **host that the app trusts to receive `client_secret` == a genuine `*.myshopify.com`/trusted Shopify host**, versus what actually happens in `validate_auth_callback`: **host that receives `client_secret` == whatever string arrives in the unauthenticated `shop` query parameter**, gated only by an HMAC computed over that same attacker-supplied `shop` value together with `code`/`state`/`timestamp`/`host` [9](#0-8) . Because the signable string embeds `shop` itself, an HMAC computed with a leaked/guessed key, or a code path where hosting apps pass through a callback whose HMAC verification is bypassed/misconfigured (e.g. reusing `old_api_secret_key` or an app operator that disables verification for testing), or where `Context.old_api_secret_key` is present from a rotation, all still let an arbitrary `shop` value flow straight into the outbound request URL with no defense-in-depth check on the domain, unlike the sibling flows.

### Impact Explanation
If the `shop` value used to build the token-exchange request host is not constrained to genuine Shopify domains, a successful forgery of the callback (e.g. secret-rotation edge cases via `old_api_secret_key`, or a host application bug that relaxes/duplicates the HMAC check before delegating to this method) results in the gem POSTing `client_id` and `client_secret` — the app's full credentials — to an attacker-controlled host. This matches the "High/Critical: SSRF with the app's credentials / theft of the app's `client_secret`" class explicitly listed as in-scope impact, and is exactly the defense that `ShopValidator` was added to provide for every other flow in `lib/shopify_api/auth/`.

### Likelihood Explanation
Medium. Exploitation is not possible against a fully-correct, single-secret HMAC check alone (an attacker without the current `api_secret_key` cannot forge a valid signed callback). However this is the only OAuth entry point in the gem lacking the `ShopValidator` defense-in-depth check that all sibling token-issuing flows apply, and it is the sole path where `client_secret` transmission is keyed off a value taken verbatim from an inbound HTTP callback rather than from a value the host application already trusts (JWT `dest` claim or an operator-supplied `shop`) sanitized through `ShopValidator`. Any weakening of the HMAC guarantee (key rotation window using `old_api_secret_key`, a proxy/host app that forwards a modified query before HMAC verification, or a future refactor that reorders checks) turns this into a directly exploitable credential-exfiltration primitive with no independent domain check to catch it.

### Recommendation
In `Oauth.validate_auth_callback`, sanitize `auth_query.shop` with `Utils::ShopValidator.sanitize!` (as already done in `ClientCredentials`, `RefreshToken`, and `TokenExchange.migrate_to_expiring_token`) before constructing `null_session`/`Session.from`, so the host that ultimately receives `client_id`/`client_secret` is always constrained to `ShopValidator::TRUSTED_SHOPIFY_DOMAINS` regardless of what the HMAC-signed query claims.

### Proof of Concept
1. `Utils::HmacValidator.validate` succeeds for a given `auth_query` whenever the HMAC matches `Context.api_secret_key` or `Context.old_api_secret_key` [10](#0-9)  — the check never inspects `auth_query.shop`'s domain.
2. `validate_auth_callback` then uses `auth_query.shop` unsanitized to build the outbound request: `null_session = Auth::Session.new(shop: auth_query.shop)` and posts `client_id`/`client_secret` to `auth_base_uri(shop)` [11](#0-10) [12](#0-11) .
3. Compare with `RefreshToken.refresh_access_token`, which calls `validated_shop = Utils::ShopValidator.sanitize!(shop)` first and raises `Errors::InvalidShopError` for any non-trusted domain before it can be used to build the request host [13](#0-12) [8](#0-7)  — this guard is absent from `validate_auth_callback`.

### Citations

**File:** lib/shopify_api/auth/oauth.rb (L64-64)
```ruby
          raise Errors::InvalidOauthError, "Invalid OAuth callback." unless Utils::HmacValidator.validate(auth_query)
```

**File:** lib/shopify_api/auth/oauth.rb (L73-94)
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
          rescue ShopifyAPI::Errors::HttpResponseError => e
            raise Errors::RequestAccessTokenError,
              "Cannot complete OAuth process. Received a #{e.code} error while requesting access token."
          end
```

**File:** lib/shopify_api/auth/oauth.rb (L117-128)
```ruby
        sig { params(shop: String).returns(String) }
        def auth_base_uri(shop)
          return "https://#{shop}/admin" unless defined?(DevServer) && shop.include?(".my.shop.dev")

          # For first-party apps in development only, we leverage DevServer to build the admin base URI
          admin_web = T.unsafe(Object.const_get("DevServer")) # rubocop:disable Sorbet/ConstantsFromStrings
            .new("admin-web")
          admin_host = admin_web.host!(nonstandard_host_prefix: "admin")
          shop_name = shop.split(".").first

          "https://#{admin_host}/store/#{shop_name}"
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
