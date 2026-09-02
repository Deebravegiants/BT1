### Title
`begin_auth` builds the OAuth authorization URL from an unvalidated `shop` parameter, enabling forced/attacker-redirected OAuth completion - (File: `lib/shopify_api/auth/oauth.rb`)

### Summary
`ShopifyAPI::Auth::Oauth.begin_auth` accepts a caller-supplied `shop` string and uses it, unsanitized, to construct the URL that the user's browser is redirected to for OAuth authorization. Unlike the other credential-issuing entry points in this gem (`ClientCredentials`, `RefreshToken`, `TokenExchange`), `begin_auth` never runs `shop` through `ShopifyAPI::Utils::ShopValidator.sanitize!`, so it never enforces that the target host is a trusted Shopify domain.

### Finding Description
`begin_auth` takes `shop:` directly and passes it to `auth_base_uri(shop)`: [1](#0-0) 

`auth_base_uri` simply interpolates the string into a host with no domain check: [2](#0-1) 

Compare this with the other OAuth-adjacent flows in the same gem, which explicitly call `ShopifyAPI::Utils::ShopValidator.sanitize!` (a module whose entire purpose is to bind the `shop` value to a `TRUSTED_SHOPIFY_DOMAINS` allow-list) before using the shop to build a request host: [3](#0-2) 

`begin_auth` is documented as being fed straight from request data (e.g. a `Shop` header) by the host application: [4](#0-3) 

The equality this breaks is: *the host that is validated as a genuine Shopify shop* should equal *the host the user's browser is redirected to with the app's real `client_id` and `redirect_uri`*. Because `begin_auth` performs no such validation, an unprivileged actor who can influence the `shop` value the host application forwards into `begin_auth` (e.g. via a spoofable header/query param, which the documented example pulls straight from `request.headers["Shop"]`) can make the library emit an `auth_route` pointing at an attacker-controlled host instead of `*.myshopify.com`. The victim's browser is then sent to that attacker host, which can mimic the real Shopify authorization screen and drive a forced OAuth completion against the real, legitimate `redirect_uri`/`client_id` embedded in the URL.

Note: `validate_auth_callback`'s use of `auth_query.shop` is not vulnerable in the same way, because that `shop` value is bound by the request HMAC (computed with `Context.api_secret_key`), so forging a different `shop` there would require the app secret — out of scope per the rules. The gap is specific to `begin_auth`, where `shop` carries no such binding at all.

### Impact Explanation
This matches the High-severity category "forced OAuth completion": the app can be tricked into redirecting the user to an attacker-controlled endpoint using the app's real client_id/redirect_uri, undermining the shop-authentication boundary the OAuth flow is meant to enforce.

### Likelihood Explanation
Likelihood depends entirely on the host application's handling of the `shop` input passed to `begin_auth`. The gem's own example code sources it from a raw request header, which is a pattern likely to be replicated verbatim by consuming apps that don't independently validate the shop domain before calling into this gem, especially since the library never enforces this validation itself even though it does so in sibling flows (`ClientCredentials`, `RefreshToken`, `TokenExchange`).

### Recommendation
Call `ShopifyAPI::Utils::ShopValidator.sanitize!(shop)` (or `sanitize_shop_domain`) inside `Oauth.begin_auth` before constructing `auth_base_uri`, mirroring the validation already performed in `client_credentials.rb`, `refresh_token.rb`, and `token_exchange.rb`, so that only hosts in `TRUSTED_SHOPIFY_DOMAINS` can ever appear in the generated `auth_route`.

### Proof of Concept
1. A host application built on this gem exposes a login endpoint that reads `shop` from an unauthenticated request header and calls `ShopifyAPI::Auth::Oauth.begin_auth(shop: shop, redirect_path: "/auth/callback")`, following the pattern shown in the gem's own documentation.
2. An attacker sends/crafts a request (or link) with `Shop: attacker-phish.example`.
3. `begin_auth` returns `auth_route = "https://attacker-phish.example/admin/oauth/authorize?client_id=<real_client_id>&redirect_uri=<real_redirect_uri>&state=..."` — no validation rejects `attacker-phish.example`.
4. The application 307-redirects the victim's browser to `attacker-phish.example`, which can present a fake Shopify-authorization-style page under attacker control, using the app's real `client_id`/`redirect_uri` to build a convincing forced-OAuth-completion phishing flow.

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

**File:** lib/shopify_api/utils/shop_validator.rb (L6-18)
```ruby
module ShopifyAPI
  module Utils
    module ShopValidator
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

**File:** docs/usage/oauth.md (L180-199)
```markdown
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
