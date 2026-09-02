## Finding: Missing shop-domain validation in `Oauth.begin_auth` allows OAuth redirect to attacker-controlled host

### Title
Unvalidated `shop` Parameter in `Oauth.begin_auth` Enables Forced/Spoofed OAuth Redirection - (File: `lib/shopify_api/auth/oauth.rb`)

### Summary
`ShopifyAPI::Auth::Oauth.begin_auth` builds the OAuth "authorize" redirect URL directly from the caller-supplied `shop` string without ever validating it is a genuine Shopify domain, unlike sibling entry points in the same gem (`ClientCredentials.client_credentials`, `TokenExchange.exchange_token`) which explicitly call `Utils::ShopValidator.sanitize!` before trusting a shop value.

### Finding Description
`begin_auth` takes `shop:` as a plain `String` and passes it straight into `auth_base_uri`: [1](#0-0) 

```ruby
def auth_base_uri(shop)
  return "https://#{shop}/admin" unless defined?(DevServer) && shop.include?(".my.shop.dev")
  ...
```

There is no call to `Utils::ShopValidator.sanitize!`/`sanitize_shop_domain` anywhere in `lib/shopify_api/auth/oauth.rb`, whereas the analogous `shop` inputs in `ClientCredentials.client_credentials` and `TokenExchange` are explicitly sanitized: [2](#0-1) 

The library's own documentation shows `shop` in `begin_auth` being taken directly from an inbound request header (`request.headers["Shop"]`), i.e., unprivileged caller-controlled input, and used to build the redirect target that the merchant's browser is sent to: [3](#0-2) 

Because `auth_base_uri(shop)` performs no allow-list check against `ShopValidator::TRUSTED_SHOPIFY_DOMAINS` (`shopify.com`, `myshopify.com`, `myshopify.io`, `spin.dev`, `shop.dev`), an attacker who controls the `shop` value reaching `begin_auth` (e.g., via a header/param on the host app's login route, as documented) can make the app 307-redirect the victim's browser to `https://attacker-controlled-domain/admin/oauth/authorize?...` instead of the genuine `https://{shop}.myshopify.com/admin/oauth/authorize`.

This is the same class of "host validated vs. host actually used" defect the gem itself already guards against elsewhere (`ShopValidator`), just missing on this specific path — the binding broken is: `shop_trusted_domain == shop_used_for_redirect`, which should hold but doesn't for `begin_auth`.

### Impact Explanation
An attacker-controlled redirect target during the OAuth initiation step is a "forced OAuth completion"-class issue (explicitly a listed High-impact category): the merchant's browser can be steered to an attacker-hosted page mimicking Shopify's OAuth consent screen instead of the real `myshopify.com` authorize endpoint, enabling phishing of merchant credentials or manipulation of the OAuth grant flow presented to the user, undermining the shop-authentication boundary the gem is supposed to enforce consistently across all its OAuth entry points.

### Likelihood Explanation
Reaching this code path requires only that the host application pass an attacker-influenced `shop` value into `begin_auth` — which the gem's own documentation explicitly recommends sourcing from request input (`request.headers["Shop"]`) — with no sanitization step available/called inside the gem itself before the value is used to build a redirect URL. No credentials, tokens, or privileged access are required by the attacker.

### Recommendation
Call `Utils::ShopValidator.sanitize!(shop)` (or `sanitize_shop_domain`) inside `Oauth.begin_auth` before constructing `auth_base_uri`, mirroring the validation already performed in `ClientCredentials.client_credentials` and `TokenExchange.exchange_token`, so only domains in `ShopValidator::TRUSTED_SHOPIFY_DOMAINS` (or a configured custom `myshopify_domain`) can be used to build the redirect target.

### Proof of Concept
1. Host app implements the documented pattern: `shop = request.headers["Shop"]; ShopifyAPI::Auth::Oauth.begin_auth(shop: shop, redirect_path: "/auth/callback")`.
2. Attacker sends `Shop: attacker.evil.example` (or crafts a link that sets this header/param) to the app's login route.
3. `begin_auth` computes `auth_base_uri("attacker.evil.example")` → `"https://attacker.evil.example/admin"`, and the app issues `307` with `Location: https://attacker.evil.example/admin/oauth/authorize?client_id=...&scope=...&redirect_uri=<app_host>/auth/callback&state=<nonce>`.
4. The victim's browser is redirected to the attacker's server instead of Shopify, exposing them to a spoofed consent page while the app's session cookie already carries the OAuth `state` nonce expecting a callback. [4](#0-3)

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

**File:** docs/usage/oauth.md (L181-199)
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
  end
```
