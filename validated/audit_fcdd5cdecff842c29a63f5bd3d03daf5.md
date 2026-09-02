This confirms the pattern: `ClientCredentials.client_credentials` [1](#0-0)  and `RefreshToken.refresh_access_token` [2](#0-1)  both call `Utils::ShopValidator.sanitize!(shop)` before ever constructing an `Auth::Session` or reaching `HttpClient`, which derives the request host directly from `session.shop`. `Oauth.begin_auth`, the sibling entry point in the same module, contains no such check.

### Title
Unvalidated `shop` parameter in `Oauth.begin_auth` allows forced-redirect to attacker-controlled OAuth host - (File: lib/shopify_api/auth/oauth.rb)

### Summary
`ShopifyAPI::Auth::Oauth.begin_auth` builds the authorization redirect URL directly from a caller-supplied `shop` string via `auth_base_uri(shop)`, with no call to `Utils::ShopValidator.sanitize!`, unlike every other credential-bearing flow in the same `Auth` module (`ClientCredentials`, `RefreshToken`, `TokenExchange`).

### Finding Description
`begin_auth` takes `shop:` as a raw string and does: `auth_route = auth_base_uri(shop) + "/oauth/authorize?#{query_string}"`, where `auth_base_uri` returns `"https://#{shop}/admin"` for any string that isn't a `.my.shop.dev` dev-server host [3](#0-2) . The `query_string` embeds the app's real, non-secret `client_id`, `scope`, and `redirect_uri` [4](#0-3) . The docs' documented usage pattern takes `shop` straight from a request header (`shop = request.headers["Shop"]`) and passes it to `begin_auth` [5](#0-4) .

By contrast, `ClientCredentials.client_credentials`, `RefreshToken.refresh_access_token`, and `TokenExchange` all invoke `Utils::ShopValidator.sanitize!(shop)` — which restricts the resulting host to `TRUSTED_SHOPIFY_DOMAINS` (`shopify.com`, `myshopify.io`, `myshopify.com`, `spin.dev`, `shop.dev`) — before that shop value is ever used to build a request host [6](#0-5) [7](#0-6) [8](#0-7) . `begin_auth` is the one place in `lib/shopify_api/auth/` where a client-influenced value becomes a redirect target's authority without going through that same trusted-domain check.

Since `validate_auth_callback` still requires a valid HMAC signed with `Context.api_secret_key` over `code`/`host`/`shop`/`state`/`timestamp` before it will call `/admin/oauth/access_token` [9](#0-8) , an attacker who does not know the secret cannot forge a callback that causes the gem itself to POST `client_secret` to a wrong host. The break is upstream: the redirect step itself sends the merchant's browser to an attacker-chosen host carrying the app's `client_id` and the OAuth `state` nonce/cookie, before any signature check exists to bind that destination back to a genuine Shopify shop domain.

The binding broken as an equality: `redirect_target_host` (attacker-supplied `shop`) should equal `validated_shopify_domain ∈ ShopValidator::TRUSTED_SHOPIFY_DOMAINS`, but the code only enforces `redirect_target_host == shop` (an unchecked identity), unlike the parallel flows where `validated_shop == ShopValidator.sanitize!(shop)`.

### Impact Explanation
This matches the "session fixation or forced OAuth completion" High-impact category: an attacker can craft a link to the app's login route with an arbitrary `shop` value, forcing any visiting merchant's browser to be redirected — with the app's genuine `client_id`, requested `scope`, and `redirect_uri` — to an attacker-controlled domain masquerading as a Shopify authorization page. This can be used to phish the merchant's Shopify credentials or to complete a forced/attacker-initiated OAuth grant flow against a spoofed authorize endpoint, without needing any secret.

### Likelihood Explanation
Reachable by any unprivileged internet user who can get a merchant to click a link or who controls a header/query parameter feeding the app's login endpoint, exactly as shown in the gem's own documented integration pattern (`request.headers["Shop"]` passed straight into `begin_auth`) [5](#0-4) . No credential, TLS interception, or privileged access is required.

### Recommendation
Validate and sanitize `shop` in `Oauth.begin_auth` using `Utils::ShopValidator.sanitize!` (or an equivalent trusted-domain check) before it is used in `auth_base_uri`, matching the pattern already used in `ClientCredentials`, `RefreshToken`, and `TokenExchange`.

### Proof of Concept
1. Host app calls `ShopifyAPI::Auth::Oauth.begin_auth(shop: params[:shop], redirect_path: "/auth/callback")` as documented.
2. Attacker sends a victim merchant a link to the app's login route with `shop=attacker-controlled.example`.
3. `auth_base_uri("attacker-controlled.example")` returns `"https://attacker-controlled.example/admin"` [3](#0-2) .
4. The app issues a 307 redirect to `https://attacker-controlled.example/admin/oauth/authorize?client_id=<real_client_id>&scope=<real_scope>&redirect_uri=<real_redirect_uri>&state=<nonce>` (per the documented callback controller pattern) [5](#0-4) , sending the victim to an attacker-hosted page instead of Shopify.

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

**File:** lib/shopify_api/auth/oauth.rb (L40-49)
```ruby
          query = {
            client_id: ShopifyAPI::Context.api_key,
            scope: scope.to_s,
            redirect_uri: "#{ShopifyAPI::Context.host}#{redirect_path}",
            state: state,
            "grant_options[]": is_online ? "per-user" : "",
          }

          query_string = URI.encode_www_form(query)
          auth_route = auth_base_uri(shop) + "/oauth/authorize?#{query_string}"
```

**File:** lib/shopify_api/auth/oauth.rb (L64-79)
```ruby
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
```

**File:** lib/shopify_api/auth/oauth.rb (L117-119)
```ruby
        sig { params(shop: String).returns(String) }
        def auth_base_uri(shop)
          return "https://#{shop}/admin" unless defined?(DevServer) && shop.include?(".my.shop.dev")
```

**File:** docs/usage/oauth.md (L181-198)
```markdown
  def login
    shop = request.headers["Shop"]

    # Builds the authorization URL route to redirect the user to
    auth_response = ShopifyAPI::Auth::Oauth.begin_auth(shop: domain, redirect_path: "/auth/callback")

    # Store the authorization cookie
    cookies[auth_response[:cookie].name] = {
      expires: auth_response[:cookie].expires,
      secure: true,
      http_only: true,
      value: auth_response[:cookie].value
    }

    # Redirect the user to "auth_response[:auth_route]" to allow user to grant the app permission
    # This will lead the user to the Shopify Authorization page
    head 307
    response.set_header("Location", auth_response[:auth_route])
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
