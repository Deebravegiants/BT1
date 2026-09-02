### Title
Unsanitized `shop` parameter in `begin_auth` enables OAuth redirect to attacker-controlled host, leaking `client_id` and `state` nonce - (File: lib/shopify_api/auth/oauth.rb)

### Summary
`Oauth.begin_auth` builds the OAuth authorization redirect URL by interpolating the caller-supplied `shop` parameter directly into `auth_base_uri(shop)` without ever calling `ShopValidator.sanitize!`, unlike every other OAuth entry point in this gem (`TokenExchange`, `ClientCredentials`, `RefreshToken`). Because the library's own documentation instructs host apps to source `shop` from an unauthenticated request value (e.g., `request.headers["Shop"]`), an attacker who controls that value can force the browser to redirect to `https://attacker.example.com/admin/oauth/authorize?client_id=<real client_id>&...&state=<nonce>`, disclosing the app's `client_id` and the CSRF `state` nonce to a host they control.

### Finding Description
The broken binding: `auth_base_uri(shop)` should only ever resolve to `https://{trusted-shopify-domain}/admin`, i.e. `sanitize(shop) == shop_used_in_redirect`. In practice, `shop_used_in_redirect == shop` unconditionally, with no sanitization step in between.

Code path: `begin_auth(shop:, redirect_path:, ...)` at [1](#0-0)  builds a `query` hash containing `client_id: ShopifyAPI::Context.api_key` and `state: state` [2](#0-1) , then constructs `auth_route = auth_base_uri(shop) + "/oauth/authorize?#{query_string}"` [3](#0-2) . The private helper `auth_base_uri` returns `"https://#{shop}/admin"` verbatim for any `shop` value that isn't a `.my.shop.dev` dev-server host [4](#0-3) . There is no call to `Utils::ShopValidator.sanitize!` anywhere in `oauth.rb`, whereas the other three OAuth flows in this gem explicitly sanitize the shop before using it, e.g. `lib/shopify_api/auth/client_credentials.rb`, `lib/shopify_api/auth/refresh_token.rb`, and `lib/shopify_api/auth/token_exchange.rb` all reference `ShopValidator`.

The documented usage pattern in `docs/usage/oauth.md` shows the host app reading `shop = request.headers["Shop"]` and passing it straight into `begin_auth` before any Shopify-side authentication has occurred [5](#0-4) . This is exactly the caller pattern the finding describes: an attacker-controlled value flowing unauthenticated into `begin_auth`'s `shop:` parameter.

Attacker request: hit the app's login route with `Shop: attacker.example.com` (or equivalent query/header the host app reads), causing `begin_auth(shop: "attacker.example.com", redirect_path: "/cb")` to return `auth_route = "https://attacker.example.com/admin/oauth/authorize?client_id=<key>&scope=...&redirect_uri=...&state=<nonce>&grant_options%5B%5D=..."`. The host app's controller (per the documented pattern) sets the `SessionCookie` and issues a 307 redirect to this `auth_route`, sending the victim's browser — along with the `client_id` and CSRF `state` — to the attacker's server.

No existing guard intercepts this: `Context.setup?`/`Context.private?` checks only gate whether OAuth is configured, not the `shop` value [6](#0-5) ; `HmacValidator.validate` and the `state` comparison only run in `validate_auth_callback`, which is a separate, later step that never re-checks how `auth_route` was built [7](#0-6) ; and `ShopValidator.sanitize!` is simply never invoked from this file.

### Impact Explanation
`client_id` is not normally secret, but the `state` nonce is a CSRF-protection value that is also set as the value of the `SessionCookie` returned alongside `auth_route` [8](#0-7) . Leaking the nonce/redirect to an attacker-controlled host, combined with the cookie already being set in the victim's browser, undermines the CSRF protection that `state == auth_query.state` is meant to provide in `validate_auth_callback` [9](#0-8) , enabling forced OAuth completion / session fixation style attacks. This matches the High severity category ("session fixation or forced OAuth completion" / "SSRF driving... unintended host"). It is repeatable against any victim who triggers the app's login flow with an attacker-supplied `shop` value, and the blast radius is scoped to whichever merchant's session gets hijacked per request — not a systemic cross-tenant break, since each exploit attempt targets one victim/session at a time.

### Likelihood Explanation
Preconditions: the host app must pass an unauthenticated, attacker-influenceable value into `begin_auth`'s `shop:` parameter — which is exactly the pattern shown in this gem's own documentation (`docs/usage/oauth.md`, reading `shop` from a request header before any Shopify auth). No secrets are required; the attacker only needs to control a request parameter/header consumed by the host app's login route and get a victim to visit a crafted link. This is low-cost and directly reachable through documented gem usage, making it a realistic, repeatable path, contingent on the host app not independently validating `shop` before calling `begin_auth` (which the gem's docs do not instruct it to do).

### Recommendation
Call `Utils::ShopValidator.sanitize!(shop)` at the top of `begin_auth` (and/or inside `auth_base_uri`) before constructing `auth_route`, raising `Errors::InvalidShopError` for any `shop` value that isn't a trusted Shopify domain, consistent with `ClientCredentials`, `RefreshToken`, and `TokenExchange`.

### Proof of Concept
In `test/auth/oauth_test.rb` (or a new test file), add:
```ruby
def test_begin_auth_rejects_untrusted_shop_domain
  ShopifyAPI::Context.setup(api_key: "key", api_secret_key: "secret", ...)

  assert_raises(ShopifyAPI::Errors::InvalidShopError) do
    ShopifyAPI::Auth::Oauth.begin_auth(shop: "attacker.example.com", redirect_path: "/cb")
  end
end
```
Assert both sides of the binding before/after the fix:
- Before fix: `result[:auth_route]` starts with `"https://attacker.example.com/admin/oauth/authorize"` and contains `client_id=<api_key>` and `state=<nonce>` — i.e., `sanitize(shop) != shop_used_in_redirect` (sanitize would reject it, but the redirect uses it anyway).
- After fix: calling with `shop: "attacker.example.com"` raises `Errors::InvalidShopError` before any `auth_route` is built, so no `client_id`/`state` is ever sent to the untrusted host.

### Citations

**File:** lib/shopify_api/auth/oauth.rb (L22-22)
```ruby
        def begin_auth(shop:, redirect_path:, is_online: true, scope_override: nil)
```

**File:** lib/shopify_api/auth/oauth.rb (L31-34)
```ruby
          unless Context.setup?
            raise Errors::ContextNotSetupError, "ShopifyAPI::Context not setup, please call ShopifyAPI::Context.setup"
          end
          raise Errors::UnsupportedOauthError, "Cannot perform OAuth for private apps." if Context.private?
```

**File:** lib/shopify_api/auth/oauth.rb (L36-38)
```ruby
          state = SecureRandom.alphanumeric(NONCE_LENGTH)

          cookie = SessionCookie.new(value: state, expires: Time.now + 60)
```

**File:** lib/shopify_api/auth/oauth.rb (L40-46)
```ruby
          query = {
            client_id: ShopifyAPI::Context.api_key,
            scope: scope.to_s,
            redirect_uri: "#{ShopifyAPI::Context.host}#{redirect_path}",
            state: state,
            "grant_options[]": is_online ? "per-user" : "",
          }
```

**File:** lib/shopify_api/auth/oauth.rb (L48-49)
```ruby
          query_string = URI.encode_www_form(query)
          auth_route = auth_base_uri(shop) + "/oauth/authorize?#{query_string}"
```

**File:** lib/shopify_api/auth/oauth.rb (L60-71)
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

**File:** lib/shopify_api/auth/oauth.rb (L117-119)
```ruby
        sig { params(shop: String).returns(String) }
        def auth_base_uri(shop)
          return "https://#{shop}/admin" unless defined?(DevServer) && shop.include?(".my.shop.dev")
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
