### Title
OAuth Callback Uses Unvalidated `shop` Domain to Send `client_secret`, Bypassing `ShopValidator` — SSRF-style Credential Leak to Attacker-Controlled Host - ([File: lib/shopify_api/auth/oauth.rb])

### Summary
`ShopifyAPI::Auth::Oauth.validate_auth_callback` builds the token-exchange session directly from `auth_query.shop` without ever passing it through `Utils::ShopValidator.sanitize!`, unlike every other credential-exchange path in the gem (`client_credentials`, `refresh_token`, `migrate_to_expiring_token`). That session's `shop` value is used as the literal host to which the app's `client_id`/`client_secret` and the OAuth `code` are POSTed.

### Finding Description
`Utils::HmacValidator.validate` only proves that the bytes of `code`, `host`, `shop`, `state`, `timestamp` were not altered relative to what was signed with `api_secret_key` — it proves integrity of the query, not that `shop` is a legitimate `*.myshopify.com` (or other trusted) domain. [1](#0-0) [2](#0-1) 

In `validate_auth_callback`, after the HMAC check passes, `auth_query.shop` is used unsanitized to construct the session that performs the access-token exchange: [3](#0-2) 

That session is handed to `Clients::HttpClient`, which derives the literal request host directly from `session.shop`: [4](#0-3) 

So the equality the code implicitly assumes is:
`shop value bound by HMAC == a real Shopify domain that is safe to receive client_secret`

But the HMAC only binds "shop bytes as originally signed" — it says nothing about domain trust. Compare this to the sibling flows in the same file, `client_credentials`, `refresh_token`, and `migrate_to_expiring_token`, which all explicitly call `Utils::ShopValidator.sanitize!(shop)` before constructing the session used for the token exchange: [5](#0-4) [6](#0-5) 

`ShopValidator.sanitize!` exists precisely to reject any domain outside `TRUSTED_SHOPIFY_DOMAINS` (`shopify.com`, `myshopify.io`, `myshopify.com`, `spin.dev`, `shop.dev`): [7](#0-6) 

`validate_auth_callback` is the one OAuth-callback code path that skips this check entirely.

### Impact Explanation
If the host application constructs `AuthQuery` from raw callback request parameters (as the gem's own documentation instructs — `ShopifyAPI::Auth::Oauth::AuthQuery.new(request.parameters.symbolize_keys.except(...))`) and that flow is reachable with a `shop` value that isn't constrained to `*.myshopify.com` upstream, the gem itself performs no defense: it will POST `client_id`, `client_secret`, and the authorization `code` to `https://<shop>/admin/oauth/access_token` where `<shop>` is fully attacker-influenced. This matches the report's flagged impact class: **SSRF with the app's credentials** — the app's `client_secret` (and the merchant's authorization `code`) are sent to a host of the attacker's choosing.

Whether this is exploitable end-to-end depends on whether Shopify's real OAuth redirect always supplies a `shop` restricted to `*.myshopify.com` and whether the HMAC (which requires knowledge of `api_secret_key`) can ever be satisfied for attacker-chosen values. This library performs no defense-in-depth here even though it does so in three sibling functions, which is the security-relevant asymmetry.

### Likelihood Explanation
Medium confidence. The gem's own docs show `AuthQuery` being built straight from callback request parameters, and this specific function is the only OAuth-token-exchange call site in the module lacking the `ShopValidator.sanitize!` call that all its siblings apply. The actual exploitability given Shopify's server-side OAuth flow behavior could not be fully confirmed from static code alone.

### Recommendation
Sanitize `auth_query.shop` through `Utils::ShopValidator.sanitize!` (as is already done in `client_credentials`, `refresh_token`, and `migrate_to_expiring_token`) before constructing `null_session` in `validate_auth_callback`, and use the sanitized value everywhere `auth_query.shop` is currently used (both for the token-exchange session and for the returned `Session.from(shop: ...)`).

### Proof of Concept
Conceptual (not independently executed):
1. A `ShopifyCallbackController` following the gem's documented pattern constructs `AuthQuery` from raw request params, e.g. `ShopifyAPI::Auth::Oauth::AuthQuery.new(request.parameters.symbolize_keys.except(:controller, :action))`.
2. `validate_auth_callback` passes HMAC validation (bytes match what was signed) but never calls `ShopValidator.sanitize!` on `shop`.
3. `null_session = Auth::Session.new(shop: auth_query.shop)` is created with an unvalidated `shop`.
4. `Clients::HttpClient.new(session: null_session, base_path: "/admin/oauth")` builds `@base_uri_and_path = "https://#{session.shop}/admin/oauth"`.
5. The POST containing `client_id`, `client_secret`, and `code` is sent to `https://<shop>/admin/oauth/access_token`, where `<shop>` is not constrained to be `*.myshopify.com`.

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

**File:** lib/shopify_api/auth/oauth.rb (L60-98)
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

          session_params = T.cast(response.body, T::Hash[String, T.untyped]).to_h
          session = Session.from(shop: auth_query.shop,
            access_token_response: Oauth::AccessTokenResponse.from_hash(session_params))
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
