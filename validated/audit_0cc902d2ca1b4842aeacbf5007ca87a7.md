### Title
`Oauth.begin_auth` Builds the Authorization Redirect From an Unvalidated `shop` Parameter, Enabling Forced OAuth Completion / State Fixation - (File: `lib/shopify_api/auth/oauth.rb`)

### Summary
`ShopifyAPI::Auth::Oauth.begin_auth` builds the OAuth "authorize" redirect URL by string-interpolating the caller-supplied `shop:` argument directly into the target host, without ever validating that it is a genuine Shopify domain. Every other place in the gem that turns a raw `shop` string into a request host that carries the app's `state`/credentials (`ClientCredentials.client_credentials`, `RefreshToken.refresh_access_token`, `TokenExchange.migrate_to_expiring_token`) explicitly calls `Utils::ShopValidator.sanitize!(shop)` first. `begin_auth` is the odd one out, breaking the binding: `redirect target host == a domain the gem has certified as *.myshopify.com/spin.dev/etc.` should hold, but instead `redirect target host == whatever string the caller passed in`.

### Finding Description
`Oauth.begin_auth` takes an unvalidated `shop:` string and uses it to build the authorization redirect: [1](#0-0) 

The nonce (`state`) is placed both in an httpOnly cookie and in the query string of the redirect URL, and the redirect host is derived from `auth_base_uri(shop)`: [2](#0-1) 

`auth_base_uri` performs no domain check at all — it just does `"https://#{shop}/admin"` unless a dev-only condition is met. Contrast this with the other three flows in the same module family that also turn a caller-supplied `shop` into a request host, all of which call `Utils::ShopValidator.sanitize!(shop)` before using it: [3](#0-2) [4](#0-3) [5](#0-4) 

`Utils::ShopValidator` exists precisely to prevent an attacker-controlled string from being treated as a trusted Shopify host: [6](#0-5) [7](#0-6) 

`begin_auth`'s documented contract states the `shop` parameter should be `"{exampleshop}.myshopify.com"`, but nothing in the method enforces that — the host application is the sole source of this value (typically taken straight from an unauthenticated `?shop=` query parameter at install time, as shown in the docs' example controller reading `request.headers["Shop"]`): [8](#0-7) 

Because `begin_auth` skips the sanitize step that the rest of the credential-bearing flows in this exact module perform, an unvalidated `shop` value flows straight into the redirect target: `https://#{attacker-controlled}/admin/oauth/authorize?...&state=<nonce>&...`. Since the redirect goes to an attacker-controlled host instead of a real Shopify domain, the attacker's server directly receives the `state` nonce (which was also just set in the victim's httpOnly cookie) as part of the incoming HTTP request — the attacker never needs to read the cookie, they receive the nonce value as the query string of the request delivered to their own server.

### Impact Explanation
This breaks the equality that should hold for the OAuth anti-CSRF binding: `state value only known to {app, browser via cookie}` should never equal `state value known to an arbitrary third-party host`. Once `begin_auth` redirects to a host the attacker controls, the attacker learns the `state` nonce that was written into the victim's `SESSION_COOKIE`. If the attacker can subsequently get the victim's browser to visit a legitimate Shopify-hosted install flow completion tied to the attacker's own shop/session with a matching `state`, they can force-complete an OAuth flow / fixate the session under attacker control, matching the "session fixation or forced OAuth completion" category called out explicitly as a valid High-impact finding. It does not directly leak `client_secret` (that stays server-side, sent later in `validate_auth_callback` to the shop obtained from the HMAC-signed callback query, which is a separate, correctly-guarded path), so the severity is bounded to the forced-OAuth-completion / state-fixation category rather than credential exfiltration.

### Likelihood Explanation
Likelihood is significant: the `shop` value passed to `begin_auth` is, per the gem's own documentation and usage example, sourced from unauthenticated request data (`request.headers["Shop"]` / an install-time query parameter) supplied by whoever visits the app's login route — exactly the class of caller-controlled, unauthenticated input this analog targets. No credential, TLS interception, or privileged access is required to trigger it; an attacker simply needs to initiate the app's OAuth "login" route with a `shop` value pointing at infrastructure they control.

### Recommendation
In `Oauth.begin_auth` (and in `auth_base_uri`), validate `shop` with `Utils::ShopValidator.sanitize!(shop)` before it is used to construct the redirect host, exactly as is already done in `ClientCredentials.client_credentials`, `RefreshToken.refresh_access_token`, and `TokenExchange.migrate_to_expiring_token`. This ensures the redirect (and therefore the `state` nonce embedded in it) can only ever be sent to a domain in `ShopValidator::TRUSTED_SHOPIFY_DOMAINS` (or the app's configured `myshopify_domain`), closing the forced-OAuth-completion path.

### Proof of Concept
1. App exposes a login route that calls `ShopifyAPI::Auth::Oauth.begin_auth(shop: params[:shop], redirect_path: "/auth/callback")`, mirroring the documented example (`shop = request.headers["Shop"]`).
2. Attacker requests `GET /login?shop=attacker-controlled.example.com` (or any header/param path the host app maps to `shop:`).
3. `begin_auth` computes `auth_base_uri("attacker-controlled.example.com")` → `"https://attacker-controlled.example.com/admin"`, and returns `auth_route = "https://attacker-controlled.example.com/admin/oauth/authorize?client_id=...&scope=...&redirect_uri=...&state=<NONCE>&grant_options[]=..."`.
4. The victim's browser is issued the `SESSION_COOKIE` containing `<NONCE>` and is redirected (307) to the attacker's host with `state=<NONCE>` in the query string.
5. Attacker's server, which is the actual recipient of this request, now has `<NONCE>` without needing access to the victim's cookies, enabling it to be replayed against the real callback route to attempt forced completion of the OAuth flow under attacker-influenced conditions.

### Citations

**File:** lib/shopify_api/auth/oauth.rb (L36-52)
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

**File:** docs/usage/oauth.md (L179-199)
```markdown
```ruby
class ShopifyAuthController < ApplicationController
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
  end
```
