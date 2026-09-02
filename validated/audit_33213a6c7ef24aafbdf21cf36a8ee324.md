## Analog Identified

### Title
Missing Shop Domain Validation in `Oauth.begin_auth` Enables Nonce/Client-ID Leak to Attacker-Controlled Host (Forced OAuth Completion) - (File: `lib/shopify_api/auth/oauth.rb`)

### Summary
`ShopifyAPI::Auth::Oauth.begin_auth` builds the OAuth authorization redirect URL directly from a caller-supplied `shop` string without ever validating that it is a legitimate Shopify domain, unlike every other module in the same `Auth` namespace that talks to a shop host.

### Finding Description
`begin_auth` accepts `shop:` and feeds it straight into `auth_base_uri(shop)`, which returns `"https://#{shop}/admin"` with no format check: [1](#0-0) [2](#0-1) 

The resulting `auth_route` embeds `client_id`, `redirect_uri`, and the freshly generated anti-CSRF `state` nonce, and the same `state` value is placed in a cookie bound to the victim's browser: [3](#0-2) 

Every sibling module that constructs a request host from a `shop` string first calls `Utils::ShopValidator.sanitize!`, which restricts the host to `TRUSTED_SHOPIFY_DOMAINS` (`shopify.com`, `myshopify.io`, `myshopify.com`, `spin.dev`, `shop.dev`): [4](#0-3) [5](#0-4) [6](#0-5) [7](#0-6) 

`Oauth.begin_auth` (and `auth_base_uri`) has no such call, so the identity binding that should hold — *"the host that receives the OAuth authorize request equals a trusted Shopify domain"* — is broken. The `shop` value is only ever bytes chosen by whoever calls `begin_auth`, typically taken from an unauthenticated query parameter on the host application's `/login?shop=` route, as described in the gem's own usage documentation.

### Impact Explanation
Because the authorize URL host is unvalidated, an attacker can supply `shop=attacker.example.com` to the host app's login route. The victim's browser is then redirected to `https://attacker.example.com/admin/oauth/authorize?client_id=...&redirect_uri=...&state=<nonce>&...`, leaking the app's `client_id`, the configured `redirect_uri`, and — critically — the CSRF-protection `state` nonce to a server the attacker controls (e.g., via HTTP request logs). With the nonce and the cookie already set on the victim's browser, the attacker can drive a forced OAuth completion: they complete a real, validly-signed Shopify OAuth flow for a shop *they* control, then get the victim's browser to load the app's callback URL carrying the attacker's `code`/`shop`/valid `hmac` together with the leaked `state`. `validate_auth_callback` only checks that the state cookie equals `auth_query.state`; it does not otherwise bind the flow to a specific shop chosen by the victim: [8](#0-7) 

This lets the victim's session become bound to the attacker's shop/access token — a form of session fixation / forced OAuth completion (accepted High-impact category), reachable entirely by an unprivileged internet user with no access to `api_secret_key` or any token.

### Likelihood Explanation
The `shop` parameter to `begin_auth` is documented to come from the incoming request (`shop` query param on the login route) before any Shopify validation has occurred, so it is fully attacker-controlled in the typical integration pattern. No secret material or privileged access is required to trigger the open redirect; only a link click by the victim is needed. All other shop-consuming code paths in this same file (`client_credentials.rb`, `refresh_token.rb`, `token_exchange.rb#migrate_to_expiring_token`) already treat this as untrusted input and sanitize it, indicating the omission in `oauth.rb` is inconsistent with the library's own established pattern.

### Recommendation
Call `Utils::ShopValidator.sanitize!(shop)` (or `sanitize_shop_domain`) at the top of `Oauth.begin_auth`, and use the sanitized value for `auth_base_uri`, mirroring `ClientCredentials.client_credentials`, `RefreshToken.refresh_access_token`, and `TokenExchange.migrate_to_expiring_token`. Additionally validate/sanitize `auth_query.shop` in `validate_auth_callback` before it is used to construct the host that receives `client_id`/`client_secret`, rather than relying solely on HMAC validation of the raw byte value.

### Proof of Concept
1. Host application exposes `GET /login?shop=<param>` and calls `ShopifyAPI::Auth::Oauth.begin_auth(shop: params[:shop], redirect_path: "/callback")`.
2. Attacker sends victim a link: `https://app.example.com/login?shop=attacker.example.com`.
3. `begin_auth` builds `auth_route = "https://attacker.example.com/admin/oauth/authorize?client_id=<APP_CLIENT_ID>&scope=...&redirect_uri=https://app.example.com/callback&state=<nonce>&grant_options[]=per-user"` and sets a `state` cookie on the victim's browser (`oauth.rb:36-51`).
4. Victim's browser is redirected to `attacker.example.com`; attacker's server logs the full query string, capturing `client_id`, `redirect_uri`, and `state`.
5. Attacker separately completes a legitimate Shopify OAuth authorize flow on a shop they control, obtaining a validly-signed callback (`code`, `shop=attacker-shop.myshopify.com`, valid `hmac`).
6. Attacker gets the victim's browser to visit `https://app.example.com/callback?shop=attacker-shop.myshopify.com&code=...&state=<leaked_nonce>&hmac=<valid>`. Since the victim's browser still carries the cookie with `state=<leaked_nonce>` set in step 3, `validate_auth_callback`'s state check passes (`oauth.rb:67-71`), and the victim's session becomes associated with the attacker's shop/access token.

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

**File:** lib/shopify_api/auth/oauth.rb (L60-72)
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
