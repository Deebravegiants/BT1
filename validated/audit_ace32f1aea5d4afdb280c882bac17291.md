### Title
`Auth::Oauth.begin_auth` builds `auth_base_uri` from raw, unsanitized `shop` param, enabling redirect to attacker-controlled host - (File: `lib/shopify_api/auth/oauth.rb`)

### Summary
`begin_auth` never calls `ShopValidator.sanitize!`/`sanitize_shop_domain` on the `shop:` argument before using it to build the outer authorization host via `auth_base_uri(shop)`. If the host app passes an unsanitized, attacker-controlled `shop` value (e.g. from a query param on an `/install` route, as the gem's own docs example does: `shop = request.headers["Shop"]`), the browser is redirected to `https://<attacker-string>/admin/oauth/authorize?...` instead of a Shopify-approved domain.

### Finding Description
The binding that should hold is: `URI(auth_route).host == ShopValidator.sanitize!(shop)` (i.e., the host the browser is sent to must be a `TRUSTED_SHOPIFY_DOMAINS`-validated Shopify domain). Tracing `begin_auth` in `lib/shopify_api/auth/oauth.rb` (lines 22-52): it computes `redirect_uri` safely from `ShopifyAPI::Context.host` (trusted), builds `query_string`, then computes `auth_route = auth_base_uri(shop) + "/oauth/authorize?#{query_string}"`. `auth_base_uri` (lines 117-128) does `return "https://#{shop}/admin" unless ...` — using the raw `shop` string with **no** call to `ShopValidator.sanitize!` or `sanitize_shop_domain`, unlike other flows in this gem (e.g. `RefreshToken`, `ClientCredentials`) which do validate shop domains. `ShopValidator.sanitize!` exists at `lib/shopify_api/utils/shop_validator.rb:56-64` precisely for this purpose but is not invoked here.

The gem's own documentation (`docs/usage/oauth.md`, step 1 example) shows host apps deriving `shop` directly from request input (`request.headers["Shop"]`) and passing it straight to `begin_auth`, with no sanitize step demonstrated for the authorization-code-grant flow before calling `begin_auth`. An attacker who controls the `shop` value supplied to `begin_auth` (e.g. via `GET /install?shop=attacker.example`) causes `auth_route` to become `https://attacker.example/admin/oauth/authorize?client_id=...&redirect_uri=<trusted host>/cb&state=<nonce>&...`. The browser is redirected off-Shopify to a host fully controlled by the attacker, which can harvest `client_id` and `state`, and present a fake consent page, setting up forced OAuth completion or phishing.

None of the existing guards catch this: `HmacValidator.validate` and the `state` comparison run only in `validate_auth_callback`, after this redirect has already occurred; `ShopValidator.sanitize!` exists but is simply not called by `begin_auth`; `Context.setup?`/`private?` do not check `shop` validity at all. Sorbet's `sig` only enforces `shop: String`, not domain trust.

### Impact Explanation
An attacker (or a malicious actor who can influence the `shop` parameter passed into `begin_auth`, which per the gem's documented usage pattern comes directly from request input) can force the app to redirect any visiting browser to `https://<attacker-domain>/admin/oauth/authorize?...`, leaking `client_id` and the CSRF `state` nonce to that domain and enabling a convincing phishing page or forced-OAuth-completion setup against arbitrary victims — matching "High: SSRF driving an authenticated request to an unintended host... or forced OAuth completion" since the authorize request is redirected wholesale to an attacker host. This is repeatable per request and not scoped to any specific victim shop.

### Likelihood Explanation
Precondition: the host app must pass a `shop` value into `begin_auth` without first validating it through `ShopValidator.sanitize!`. The gem does not enforce or even document this validation step for the authorization-code-grant flow (`begin_auth`), and its own example code takes `shop` straight from a request header. Attacker cost is a single unauthenticated GET request with an arbitrary `shop`/`Shop` value; no secrets or special preconditions beyond normal `Context.setup` are required.

### Recommendation
In `lib/shopify_api/auth/oauth.rb`, sanitize `shop` at the top of `begin_auth` using `ShopifyAPI::Utils::ShopValidator.sanitize!(shop)` (raising `Errors::InvalidShopError` for untrusted domains) before using it in `auth_base_uri(shop)`, mirroring the validation already used elsewhere in the codebase (e.g. `RefreshToken`, `ClientCredentials`).

### Proof of Concept
```ruby
# test/auth/oauth_test.rb (new test)
def test_begin_auth_raises_or_normalizes_for_untrusted_shop_host
  assert_raises(ShopifyAPI::Errors::InvalidShopError) do
    ShopifyAPI::Auth::Oauth.begin_auth(shop: "attacker.example", redirect_path: "/cb")
  end
end

def test_begin_auth_auth_route_host_matches_sanitized_shop
  result = ShopifyAPI::Auth::Oauth.begin_auth(shop: @shop, redirect_path: "/cb")
  auth_uri = URI.parse(result[:auth_route])
  assert_equal ShopifyAPI::Utils::ShopValidator.sanitize!(@shop), auth_uri.host
end
```
Currently, calling `begin_auth(shop: "attacker.example", redirect_path: "/cb")` does not raise, and `result[:auth_route]` starts with `https://attacker.example/admin/oauth/authorize?...`, violating the binding `URI(auth_route).host == ShopValidator.sanitize!(shop)`. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3)

### Citations

**File:** lib/shopify_api/auth/oauth.rb (L40-52)
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
