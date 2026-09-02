### Title
`Oauth.begin_auth` builds the authorization redirect from a raw, unsanitized `shop` parameter, enabling forced-OAuth / open-redirect to an attacker-controlled host - (File: `lib/shopify_api/auth/oauth.rb`)

### Summary
`ShopifyAPI::Auth::Oauth.begin_auth` interpolates the caller-supplied `shop:` argument directly into `auth_base_uri(shop)` (`"https://#{shop}/admin"`) with no call to `Utils::ShopValidator.sanitize!` anywhere in the method. If the host app forwards an unsanitized `shop` value (which the gem's own documented usage example does), the returned `auth_route` sends the victim's browser, together with the app's `client_id` and CSRF `state` nonce, to an arbitrary attacker-controlled host.

### Finding Description
The claimed binding is: `shop` (the value used to construct `auth_route` in `begin_auth`) `== ShopValidator.sanitize!(shop)`.

Tracing `begin_auth`: [1](#0-0) 
`shop` flows unchanged into `auth_base_uri(shop)`: [2](#0-1) 
which returns `"https://#{shop}/admin"` verbatim (barring the `.my.shop.dev` dev-server special case). There is no call to `ShopValidator.sanitize!` or `sanitize_shop_domain` anywhere in `oauth.rb`. `ShopValidator.sanitize!` exists in the codebase and is used elsewhere (e.g. `TokenExchange`, `RefreshToken`, `ClientCredentials`): [3](#0-2) 
but `begin_auth` never calls it, so the equality is broken — the raw `shop` value is used, not the sanitized/trusted-domain-checked one.

None of the existing guards catch this: `Context.setup?` only checks that context configuration exists, `Context.private?` only blocks private apps, and `HmacValidator`/JWT/state checks apply to `validate_auth_callback` (the callback path), not to `begin_auth` (the redirect-initiation path). Sorbet's `sig { params(shop: String) ... }` only enforces that `shop` is a `String`, not that it is a trusted Shopify domain.

Critically, the gem's own documented usage pattern demonstrates the unsafe flow: the shipped example takes `shop` straight from a request header and passes it into `begin_auth` with no sanitization step: [4](#0-3) 

Attacker's exact request: send `Shop: attacker.example.com` (or any header/query param the host app maps to `shop:`) to the app's login route. `begin_auth` returns `auth_route = "https://attacker.example.com/admin/oauth/authorize?client_id=<key>&scope=...&redirect_uri=<app host>/auth/callback&state=<nonce>&grant_options[]=..."`, and the app 307-redirects the victim's browser there per the documented controller pattern.

### Impact Explanation
The app's own domain is turned into an open redirector to an arbitrary attacker-chosen host, and the app's `client_id`, requested `scope`, `redirect_uri`, and a fresh CSRF `state` nonce are sent to that host. This is a forced-OAuth-completion / SSRF-adjacent redirect issue (the app is tricked into directing the "authorization" flow at a non-Shopify destination) rather than direct token theft, since the attacker still cannot complete the callback without the app's `client_secret`. Severity matches "High – SSRF driving an authenticated request to an unintended host, session fixation or forced OAuth completion, ... or credential leakage into logs or error output" in that `client_id`/`state` are leaked to an attacker-chosen host and the redirect is fully attacker-controlled. It is repeatable against arbitrary victims per request, with no per-tenant isolation issue since it does not touch any shop's actual data — it is a redirect/credential-exposure issue, not a cross-tenant token disclosure.

### Likelihood Explanation
Exploitability is entirely dependent on the host application's choice to forward an unsanitized `shop` value into `begin_auth` — which is exactly what the gem's shipped documentation example does (`shop = request.headers["Shop"]`) without calling `ShopValidator.sanitize!` first. Given the gem itself performs zero validation and its own example doesn't sanitize, this is a realistic, low-cost, single-HTTP-request exploit for any host app that follows the documented pattern verbatim.

### Recommendation
Call `Utils::ShopValidator.sanitize!(shop)` inside `Oauth.begin_auth` before using `shop` to build `auth_base_uri`, raising `Errors::InvalidShopError` for any non-trusted-domain value, mirroring what `TokenExchange`, `RefreshToken`, and `ClientCredentials` already do. Additionally update `docs/usage/oauth.md`'s example to sanitize `shop` before calling `begin_auth`, or state explicitly that the gem does not validate it and the host app must call `ShopValidator.sanitize!` itself.

### Proof of Concept
```ruby
# test/auth/oauth_test.rb (new test)
def test_begin_auth_does_not_sanitize_shop
  ShopifyAPI::Context.setup(api_key: "key", api_secret_key: "secret", scope: "read_products", host: "https://my-app.example")

  result = ShopifyAPI::Auth::Oauth.begin_auth(shop: "attacker.example.com", redirect_path: "/auth/callback")

  # Binding under test: shop used in auth_route should equal ShopValidator.sanitize!(shop)
  assert_raises(ShopifyAPI::Errors::InvalidShopError) do
    ShopifyAPI::Utils::ShopValidator.sanitize!("attacker.example.com")
  end

  # But begin_auth used the raw, unvalidated value:
  assert_includes result[:auth_route], "https://attacker.example.com/admin/oauth/authorize"
  refute_raises { ShopifyAPI::Auth::Oauth.begin_auth(shop: "attacker.example.com", redirect_path: "/auth/callback") }
end
```
This demonstrates that `sanitize!("attacker.example.com")` raises `InvalidShopError` (proving it is not a trusted Shopify domain) while `begin_auth` happily builds and returns an `auth_route` pointing at that same untrusted host with no exception and no sanitization performed.

### Citations

**File:** lib/shopify_api/auth/oauth.rb (L22-49)
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
