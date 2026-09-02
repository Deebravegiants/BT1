### Title
Unvalidated `shop` parameter in `Oauth.begin_auth` allows forced/hijacked OAuth authorization redirect - (File: `lib/shopify_api/auth/oauth.rb`)

### Summary
`ShopifyAPI::Auth::Oauth.begin_auth` builds the merchant-facing OAuth authorization redirect URL directly from the caller-supplied `shop` string, without ever validating that it is a genuine Shopify domain. Every other credential-bearing entry point in the gem (`ClientCredentials.client_credentials`, `TokenExchange.exchange_token` via the signed JWT `dest` claim, and `Oauth.validate_auth_callback` via HMAC-covered `shop`) constrains the host that receives app secrets/tokens, but `begin_auth` has no equivalent binding.

### Finding Description
`begin_auth` accepts `shop:` as a plain, unauthenticated `String` and passes it straight into `auth_base_uri(shop)`: [1](#0-0) 

```ruby
def auth_base_uri(shop)
  return "https://#{shop}/admin" unless defined?(DevServer) && shop.include?(".my.shop.dev")
  ...
```

This result is concatenated with `/oauth/authorize?#{query_string}` to form `auth_route`, which the calling app is instructed to redirect the merchant's browser to: [2](#0-1) 

The `query_string` embeds the app's real `client_id`, the configured OAuth `scope`, the app's real `redirect_uri`, and a freshly generated `state` nonce that is simultaneously written into a `SessionCookie` set on the victim's browser: [3](#0-2) 

Compare this to `ClientCredentials.client_credentials`, which sanitizes `shop` before it is ever used to build a request host that carries `client_secret`: [4](#0-3) 

```ruby
def client_credentials(shop:)
  ...
  validated_shop = Utils::ShopValidator.sanitize!(shop)
  shop_session = ShopifyAPI::Auth::Session.new(shop: validated_shop)
```

`ShopValidator.sanitize!` exists precisely to enforce this binding — it only accepts hosts on `TRUSTED_SHOPIFY_DOMAINS` (`shopify.com`, `myshopify.io`, `myshopify.com`, `spin.dev`, `shop.dev`) and raises `Errors::InvalidShopError` otherwise: [5](#0-4) [6](#0-5) 

`Oauth.begin_auth` never calls `ShopValidator` at all, so the identity binding "host redirected to == a trusted Shopify authorization domain" does not hold: `auth_base_uri(attacker.example) == "https://attacker.example/admin"`, not `"https://{real-store}.myshopify.com/admin"`.

`Oauth.validate_auth_callback` also uses `auth_query.shop` directly (`Auth::Session.new(shop: auth_query.shop)`, later used by `HttpClient` to build the host that receives `client_secret` in the POST body) without a `ShopValidator` call, but that value is protected because it must satisfy `Utils::HmacValidator.validate(auth_query)` first, which requires knowledge of `Context.api_secret_key`: [7](#0-6) 

`begin_auth`'s `shop`, by contrast, has no such protection — it is typically taken straight from an unauthenticated request parameter (as shown in the gem's own documentation example, `shop = request.headers["Shop"]`), so an attacker fully controls its value.

### Impact Explanation
An attacker can supply an arbitrary `shop` value to the host application's login route, causing `begin_auth` to return an `auth_route` on an attacker-controlled domain (e.g. `https://attacker.example/admin/oauth/authorize?...`) while still carrying the legitimate `client_id`, `redirect_uri`, `scope`, and the `state` nonce that has been bound into a cookie on the victim's browser. If the host application redirects the user to this `auth_route` as documented, the merchant's browser is sent to the attacker's page instead of Shopify's real authorization screen. This maps directly to the "session fixation or forced OAuth completion" High-impact category: the attacker controls where the authorization step of the flow is completed while the app's own `client_id`/`redirect_uri`/`state` are exposed and bound to the victim's session, enabling capture or replay of the subsequent authorization `code` against the real token endpoint under attacker control of timing/flow.

### Likelihood Explanation
The `shop` value passed to `begin_auth` is explicitly documented and expected to come from unauthenticated request input, and no validation call exists in the code path, so exploitation only requires supplying a crafted `shop` string to whatever login route a host app builds around `begin_auth` — no privileged access, tokens, or secrets are required.

### Recommendation
Call `Utils::ShopValidator.sanitize!` (or `sanitize_shop_domain`) on `shop` at the start of `Oauth.begin_auth`, exactly as `ClientCredentials.client_credentials` does, raising `Errors::InvalidShopError` before constructing `auth_base_uri`/`auth_route` for any non-trusted domain.

### Proof of Concept
1. Host app exposes a login route that calls:
   `ShopifyAPI::Auth::Oauth.begin_auth(shop: params[:shop], redirect_path: "/auth/callback")`
   with `params[:shop]` taken directly from the query string, per the gem's documented usage pattern.
2. Attacker sends the victim a link to that route with `shop=attacker.example`.
3. `auth_base_uri("attacker.example")` returns `"https://attacker.example/admin"` (no validation performed), and `begin_auth` returns:
   `auth_route = "https://attacker.example/admin/oauth/authorize?client_id=<real_client_id>&scope=<real_scope>&redirect_uri=<real_redirect_uri>&state=<nonce>&grant_options[]=..."`
   along with a `SessionCookie` containing `state` set in the victim's browser.
4. The host app redirects the victim's browser to `auth_route`, landing on the attacker's server with the real `client_id`, `redirect_uri`, and `state` nonce exposed, enabling a forced/attacker-directed OAuth flow.

### Citations

**File:** lib/shopify_api/auth/oauth.rb (L36-51)
```ruby
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
```

**File:** lib/shopify_api/auth/oauth.rb (L60-81)
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
```

**File:** lib/shopify_api/auth/oauth.rb (L117-120)
```ruby
        sig { params(shop: String).returns(String) }
        def auth_base_uri(shop)
          return "https://#{shop}/admin" unless defined?(DevServer) && shop.include?(".my.shop.dev")

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
