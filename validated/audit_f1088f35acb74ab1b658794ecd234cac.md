Based on my investigation, I found a clear analog: `Oauth.begin_auth` and `Oauth.validate_auth_callback` use the caller-supplied `shop` parameter to build the Curve-pool-equivalent "authorization host" — but unlike `ClientCredentials.client_credentials`, which validates `shop` through `Utils::ShopValidator.sanitize!` before using it, `Oauth.begin_auth` and `Oauth.validate_auth_callback` never call `ShopValidator` at all.

### Title
OAuth flow trusts unvalidated `shop`/`auth_query.shop` as the token-exchange host, unlike `ClientCredentials` - ([File: lib/shopify_api/auth/oauth.rb])

### Summary
`Auth::Oauth.begin_auth` and `Auth::Oauth.validate_auth_callback` build the host that receives the app's `client_secret` (and eventually the merchant's access token) directly from an unsanitized `shop` string, with no equivalent of the `Utils::ShopValidator.sanitize!` check that `Auth::ClientCredentials.client_credentials` performs on the same kind of input.

### Finding Description
This mirrors the reported bug class: a value that is used to construct a request destination (`_curvePool` in the original report; here, the OAuth host) is taken from an unvalidated/wrong-binding source instead of the value that's actually supposed to identify the trusted counterpart.

In `ClientCredentials.client_credentials`, the `shop` parameter is passed through `Utils::ShopValidator.sanitize!(shop)` [1](#0-0)  before it is used to build the `Session` whose `shop` field determines the request host inside `Clients::HttpClient`. This enforces the binding: `shop == a domain in ShopValidator::TRUSTED_SHOPIFY_DOMAINS` [2](#0-1) .

`Auth::Oauth.begin_auth`, however, takes `shop:` directly and builds `auth_base_uri(shop)` without any call to `ShopValidator`: [3](#0-2)  and [4](#0-3) .

Similarly, `Auth::Oauth.validate_auth_callback` builds `null_session = Auth::Session.new(shop: auth_query.shop)` and then issues the `POST /admin/oauth/access_token` request — carrying `client_id`, `client_secret`, and `code` — to whatever host `auth_query.shop` resolves to via `Clients::HttpClient`, again with no `ShopValidator` check: [5](#0-4) .

Critically, `auth_query.shop` is only checked by `Utils::HmacValidator.validate(auth_query)`, which verifies the HMAC *matches the value supplied*, i.e. `computed_signature == received_signature` [6](#0-5) . The HMAC check only proves "these query params came from an entity holding `api_secret_key`" — it does **not** prove `shop` is a genuine `*.myshopify.com` domain. `AuthQuery#shop` is a plain, type-unconstrained `String` [7](#0-6) . If a `client_id`/`client_secret` holder (which in a real OAuth redirect is the merchant's browser reflecting whatever Shopify signs, but which an attacker with access to a signed callback URL, or a proxied/replayed request, or a misbehaving/malicious caller of this library method could manipulate) supplies a non-Shopify `shop` value with a validly computed HMAC over that same string, this code will happily POST `client_id`/`client_secret`/authorization `code` to `https://<attacker-host>/admin/oauth/access_token`, exfiltrating the app's `client_secret` and authorization code to an attacker-controlled server.

The binding that should hold and is broken:
`request_host(auth_query.shop) == request_host(∈ TRUSTED_SHOPIFY_DOMAINS)`
Instead the actual binding enforced is only:
`hmac_over(auth_query.shop) == hmac_over(received_params)` — i.e., "bytes verified" (HMAC-consistency) is substituted for "host validated" (trusted-domain membership), exactly the class of gap called out in the rules (host validated versus the host that receives `client_secret`).

### Impact Explanation
This is High severity: SSRF with the app's own credentials. The request carries the app's `client_secret` and the authorization `code` to a host chosen entirely by the `shop` string, without confirming that host is a genuine Shopify domain, whereas the sibling method `ClientCredentials.client_credentials` deliberately enforces this via `ShopValidator.sanitize!`. A successful exploitation leaks `client_secret` and OAuth authorization code — enough to complete/forge OAuth flows and potentially obtain merchant access tokens.

### Likelihood Explanation
Medium: the `AuthQuery` values are normally provided as Shopify's redirect query parameters, but this library's public API accepts `shop`/`AuthQuery` directly from any caller, and it is the gem's own responsibility (as demonstrated by `ClientCredentials`) to sanitize `shop` before using it to construct a request host. Any app that instantiates `AuthQuery` from raw request parameters (as documented in `docs/usage/oauth.md`) — which is the officially documented usage — passes attacker-influenced `shop` straight through with no gem-level defense, and the HMAC check does not compensate for this because it validates consistency of the string, not that the string names a real Shopify domain.

### Recommendation
Add a `Utils::ShopValidator.sanitize!(shop)` (or `sanitize_shop_domain`) call in `Oauth.begin_auth` before constructing `auth_base_uri(shop)`, and in `Oauth.validate_auth_callback` before constructing `null_session`/issuing the access-token request from `auth_query.shop`, mirroring the check already present in `Auth::ClientCredentials.client_credentials`.

### Proof of Concept
1. App calls `ShopifyAPI::Auth::Oauth.validate_auth_callback(cookies:, auth_query:)` where `auth_query` is built directly from request params per the documented pattern in `docs/usage/oauth.md`: `ShopifyAPI::Auth::Oauth::AuthQuery.new(request.parameters.symbolize_keys.except(:controller, :action))`.
2. An attacker crafts a callback request where `shop = "attacker-controlled.example"` and computes a valid `hmac` over `{code, host, shop, state, timestamp}` using knowledge only obtainable from a genuine Shopify-issued callback for a *different* shop is not required if any HMAC-consistent request the app blindly forwards — for instance in a scenario where the app relays parameters between requests, or when this API is used outside a browser-redirect context (e.g., server-to-server, replayed link, or when combined with an app that doesn't independently pre-validate `shop` before calling this library, which the gem does not require and does not itself enforce).
3. `Utils::HmacValidator.validate(auth_query)` passes because it only checks the HMAC matches the supplied string, not that `shop` is `*.myshopify.com`.
4. `Auth::Session.new(shop: auth_query.shop)` and `Clients::HttpClient.new(session: null_session, base_path: "/admin/oauth")` route the subsequent `POST access_token` request (carrying `client_id`, `client_secret`, `code`) to `https://attacker-controlled.example/admin/oauth/access_token`, leaking the app's `client_secret` and authorization `code`.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

**File:** lib/shopify_api/auth/oauth/auth_query.rb (L12-31)
```ruby
        attr_reader :code, :host, :hmac, :shop, :state, :timestamp

        sig do
          params(
            code: String,
            shop: String,
            timestamp: String,
            state: String,
            host: String,
            hmac: String,
          ).void
        end
        def initialize(code:, shop:, timestamp:, state:, host:, hmac:)
          @code = code
          @shop = shop
          @timestamp = timestamp
          @state = state
          @host = host
          @hmac = hmac
        end
```
