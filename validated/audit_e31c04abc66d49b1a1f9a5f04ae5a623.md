### Title
`Oauth.begin_auth`/`validate_auth_callback` construct the OAuth token-exchange request using an unvalidated `shop`, allowing the app's `client_id`, `scope`, and `redirect_uri` to be sent to an attacker-controlled host - (File: lib/shopify_api/auth/oauth.rb)

### Summary
Every other credential-issuing entry point in this gem (`ClientCredentials.client_credentials`, `RefreshToken.refresh_access_token`, `TokenExchange.migrate_to_expiring_token`, `Clients::Graphql::Storefront.new`) runs the caller-supplied `shop` string through `Utils::ShopValidator.sanitize!` before using it to build a request host, rejecting anything that isn't a `myshopify.com`/`myshopify.io`/`shopify.com`/`spin.dev`/`shop.dev` domain. `Auth::Oauth.begin_auth` and `Auth::Oauth.validate_auth_callback` never call `ShopValidator` at all. [1](#0-0) [2](#0-1) [3](#0-2) 

### Finding Description
`begin_auth(shop:, redirect_path:, ...)` takes `shop` directly from the request (the docs' own example reads it straight from `request.headers["Shop"]`) and passes it unvalidated into `auth_base_uri(shop)`, which builds `https://#{shop}/admin`. This URL then receives `client_id`, `scope`, `redirect_uri` (the app's own callback URL) and the CSRF `state` nonce as query parameters: [4](#0-3) [5](#0-4) 

The identity binding that should hold is: `shop` (the host that will receive `client_id`/`redirect_uri`/`state`) == a Shopify-trusted domain. Before the request: `shop` is fully attacker/user-controlled free text. After the request: `auth_base_uri` uses that same unvalidated string as the destination host, with no check that it equals a `TRUSTED_SHOPIFY_DOMAINS` suffix (the exact check `ShopValidator.sanitize!` performs). This is the same bug class as the referenced report's "missing check for the second half of a pair" — here the pair is (validate shop for token/callback flows) vs (validate shop for the interactive-authorization flow), and the check exists for one and is silently absent for the other.

`validate_auth_callback` compounds this: it takes `auth_query.shop` (which does pass through HMAC verification, so it is authentic if `Context.api_secret_key` is correct) and uses it directly to build `null_session = Auth::Session.new(shop: auth_query.shop)` and the final `Session.from(shop: auth_query.shop, ...)`, again without `ShopValidator.sanitize!`, unlike `TokenExchange.exchange_token`/`migrate_to_expiring_token` and `ClientCredentials.client_credentials`, which all sanitize `shop` before constructing a session/host.

### Impact Explanation
Because `begin_auth` builds the authorization redirect target directly from unvalidated `shop`, a caller (or a user-supplied `Shop` header/param in a typical Rails integration as shown in this gem's own docs) can force the app to redirect the browser to an attacker-chosen host with the app's `client_id`, requested `scope`, and legitimate `redirect_uri` attached as query parameters, and with the CSRF `state` value the app just set in the user's cookie. This is a forced-OAuth-flow-initiation primitive: the attacker's site (posing as the OAuth authorize endpoint) fully controls what happens next in the browser and can immediately bounce the browser back to the real `redirect_uri` with a `state` value it now knows (since it observed it in the query string) and a `code`/`shop` of the attacker's choosing, setting up a forced OAuth completion / session-fixation-style attack against the app's callback route — the callback's `state == auth_query.state` check alone is not a sufficient defense once the state value has been handed to an attacker-controlled origin via the unvalidated redirect.

### Likelihood Explanation
This requires the host application to pass an unvalidated `shop` value into `begin_auth`, which is exactly what this gem's own documentation demonstrates (`shop = request.headers["Shop"]`) with no sanitization step shown or provided by the library. Given `ShopValidator` exists in the codebase specifically to close this exact class of issue in every other credential flow, its absence here is a straightforward oversight rather than a hypothetical misuse.

### Recommendation
Call `Utils::ShopValidator.sanitize!(shop)` (or `sanitize_shop_domain`) at the top of `begin_auth`, and use the sanitized value in `auth_base_uri`. Likewise sanitize `auth_query.shop` in `validate_auth_callback` before it is used to build `null_session`/`Session.from`, mirroring the pattern already used in `ClientCredentials`, `RefreshToken`, and `TokenExchange`.

### Proof of Concept
```ruby
# App code following this gem's own documented pattern (docs/usage/oauth.md):
shop = request.headers["Shop"]  # attacker supplies: "attacker.example"
auth_response = ShopifyAPI::Auth::Oauth.begin_auth(shop: shop, redirect_path: "/auth/callback")
# auth_response[:auth_route] ==
#   "https://attacker.example/admin/oauth/authorize?client_id=<APP_CLIENT_ID>&scope=...&redirect_uri=https://app.example.com/auth/callback&state=<nonce>&grant_options%5B%5D=per-user"
```
`ShopifyAPI::Auth::Oauth.begin_auth` has no equivalent of `Utils::ShopValidator.sanitize!(shop)` unlike `ShopifyAPI::Auth::ClientCredentials.client_credentials`, so the resulting redirect host is entirely attacker-controlled. [6](#0-5) [7](#0-6)

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
