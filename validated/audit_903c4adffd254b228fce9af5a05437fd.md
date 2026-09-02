This is exactly the confirmed bug class. `ShopValidator.sanitize!` exists and is used by `TokenExchange`, `ClientCredentials`, `RefreshToken`, and `Clients::Graphql::Storefront` to constrain the shop domain to trusted Shopify suffixes before it's used to construct request hosts. `Auth::Oauth.validate_auth_callback` never calls it.

### Title
Unvalidated `shop` parameter in OAuth authorization-code callback allows `client_secret` and authorization `code` to be sent to an attacker-controlled host - (File: `lib/shopify_api/auth/oauth.rb`)

### Summary
`ShopifyAPI::Auth::Oauth.validate_auth_callback` builds the access-token exchange request host directly from the caller-supplied `auth_query.shop` value via `auth_base_uri(shop)`, without ever validating that `shop` is a genuine `*.myshopify.com`/trusted Shopify domain using `Utils::ShopValidator.sanitize!`, unlike every other credential-bearing flow in this gem.

### Finding Description
`validate_auth_callback` only checks the HMAC over the query params and that the `state` cookie matches [1](#0-0) , then immediately uses the unvalidated `shop` to build a `null_session` and derive the OAuth host: `auth_base_uri(shop)` returns `"https://#{shop}/admin"` for any non-`.my.shop.dev` value [2](#0-1) . That host is then used as `base_path` for `Clients::HttpClient`, and the POST body containing `client_id`, `client_secret`, and `code` is sent to it [3](#0-2) .

By contrast, the gem has a dedicated `Utils::ShopValidator.sanitize!` that restricts shop values to a fixed set of trusted Shopify suffixes (`myshopify.com`, `myshopify.io`, `spin.dev`, `shop.dev`, `shopify.com`) and rejects attacker-controlled domains, e.g. `attacker.example`, `evil.com`, `myshopify.com.evil.com`, `shop.myshopify.com@evil.com` [4](#0-3) [5](#0-4) . This validator is applied in `TokenExchange`, `ClientCredentials`, `RefreshToken`, and `Clients::Graphql::Storefront`, but the authorization-code OAuth callback path (`oauth.rb`) is the outlier that never calls it.

Note that `shop` is part of the HMAC-signed string (`AuthQuery#to_signable_string` includes `shop`) [6](#0-5) , so the HMAC check does bind `shop` to the *value the app's own secret signed*. This means a pure external attacker who does not already know `api_secret_key` cannot forge a brand-new query with a malicious `shop`. However, HMAC coverage of a field is not the same as *content validation* of that field: nothing stops `shop` from being a syntactically valid but non-Shopify host, and the missing check means the identity binding the report describes — "the field acted on is not independently validated for its trust domain, only for tamper-evidence" — is broken. The exact class of exploitation depends on whether an app operator/host allows arbitrary `shop` input to reach `validate_auth_callback` before HMAC verification design assumptions hold (e.g., some host frameworks call this with request parameters that include a `shop` sourced from elsewhere, or reuse cached queries). Given the constraints of this review (no host-app code, no leaked secret), I cannot construct a complete attacker-only proof that bypasses the HMAC binding itself.

### Impact Explanation
If reachable without a valid HMAC-signed `shop` (e.g., via a code path that reuses/relaxes the callback validation, or a host integration that passes through an unauthenticated `shop`), this results in the app's `client_secret` and the OAuth authorization `code` being transmitted to an attacker-controlled host — SSRF carrying the app's credentials, matching the High-severity criteria in scope.

### Likelihood Explanation
Low-to-moderate as a standalone, credential-less exploit against this gem alone: the `shop` field is HMAC-bound in the intended call path, so a pure unprivileged internet user cannot alone force a different `shop` through `validate_auth_callback` without also controlling a valid HMAC (which requires the secret). The residual risk is the absence of defense-in-depth validation that every sibling flow (`TokenExchange`, `ClientCredentials`, `RefreshToken`) already applies.

### Recommendation
Call `ShopifyAPI::Utils::ShopValidator.sanitize!(auth_query.shop, myshopify_domain: ...)` in `validate_auth_callback` before using `shop` to build `auth_base_uri` or the `null_session`, mirroring the pattern already used in `lib/shopify_api/auth/token_exchange.rb`, `lib/shopify_api/auth/client_credentials.rb`, and `lib/shopify_api/auth/refresh_token.rb`.

### Proof of Concept
1. `Utils::ShopValidator::TRUSTED_SHOPIFY_DOMAINS` and `sanitize!` exist and are proven (by `test/utils/shop_validator_test.rb`) to reject non-Shopify hosts. [4](#0-3) 
2. `Auth::Oauth.validate_auth_callback` never references `ShopValidator` and builds the token-exchange request host straight from `auth_query.shop`: [7](#0-6) 
3. Grepping the codebase confirms `ShopValidator` is used in `token_exchange.rb`, `client_credentials.rb`, `refresh_token.rb`, and `clients/graphql/storefront.rb`, but not in `auth/oauth.rb`, confirming the callback path is inconsistent with the gem's own established trust-boundary pattern.

### Citations

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

**File:** lib/shopify_api/utils/shop_validator.rb (L29-64)
```ruby
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
