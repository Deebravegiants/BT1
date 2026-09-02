### Title
`Oauth.begin_auth` builds `auth_route` from an unsanitized `shop` string, allowing host/query/fragment injection - ([File: lib/shopify_api/auth/oauth.rb])

### Summary
`ShopifyAPI::Auth::Oauth.begin_auth` concatenates the caller-supplied `shop` string directly into `auth_base_uri(shop) + "/oauth/authorize?#{query_string}"` without ever calling `Utils::ShopValidator.sanitize!`. Every other OAuth entry point in the gem (`ClientCredentials.client_credentials`, `RefreshToken.refresh_access_token`, `TokenExchange.migrate_to_expiring_token`) validates `shop` through `ShopValidator.sanitize!` before using it, but `begin_auth` (and `validate_auth_callback`, which builds a `Session` from `auth_query.shop` unchecked) do not.

### Finding Description
The broken binding: `auth_route.host == ShopValidator.sanitize!(shop)` is assumed but never enforced for `begin_auth`.

Code path: [1](#0-0)  builds `query_string` (containing the real `client_id`, `state`, `redirect_uri`) and appends it to `auth_base_uri(shop)`, and `auth_base_uri` is a raw string interpolation of `shop` [2](#0-1) . No call to `ShopValidator.sanitize!` (or any character-class check) exists anywhere in `oauth.rb`, unlike the sibling flows: [3](#0-2) [4](#0-3) [5](#0-4) .

If the host app forwards a raw, attacker-controlled `shop` value (as the gem's own documented example does: `shop = request.headers["Shop"]` then `Oauth.begin_auth(shop: ...)`), a value such as `evil.com` (no special characters even required) turns `auth_route` into `https://evil.com/admin/oauth/authorize?client_id=<real client_id>&state=<real state>&redirect_uri=<real redirect_uri>&...`. A value containing `?`/`#` (e.g. `real-shop.myshopify.com?evil=1#`) causes the browser to parse the host as `real-shop.myshopify.com`, but treats everything after `?` as query and everything after `#` as a client-side-only fragment, so the legitimate `client_id`/`state`/`redirect_uri` never reach Shopify's authorize endpoint.

Existing guards do not stop this: `ShopValidator.sanitize!` is simply never invoked on this path, `HmacValidator.validate` and the `state` cookie comparison only run in `validate_auth_callback` (after the redirect), and Sorbet's `params(shop: String)` only enforces type, not content. Importantly, `HmacValidator.validate` on the callback side does prevent an attacker from forging a fake completed OAuth callback (since they lack `api_secret_key`), so full authentication bypass / token theft is **not** achievable through this bug alone — the exploitable outcome is limited to open-redirect / forced-navigation to an attacker-chosen or malformed host carrying the app's `client_id`, `state`, and `redirect_uri` in the URL, i.e., a phishing/redirect-confusion primitive, not credential exfiltration or session takeover.

### Impact Explanation
An attacker who can influence the raw `shop` value handed to `begin_auth` (via a host app that forwards it unsanitized, as the gem's own docs show) can force the merchant's browser to navigate to an attacker-chosen host instead of Shopify, exposing the app's `client_id`, OAuth `state`, and `redirect_uri` to that host and breaking the intended authorize request (redirect confusion / open redirect enabling a phishing consent page). It does not, by itself, grant authentication bypass, token theft, or cross-tenant access, because `HmacValidator.validate` still blocks a forged callback. This falls short of the Critical bar and is a partial match for the High "forced OAuth completion"/redirect-confusion category, contingent entirely on the host app not validating `shop` itself — a precondition explicitly assumed by the question.

### Likelihood Explanation
Requires a host app that passes attacker-controlled `shop` straight to `begin_auth` without its own validation — which matches the gem's documented usage pattern (`shop = request.headers["Shop"]`). No credentials or victim interaction beyond following the injected redirect are needed, and the attack is repeatable against any victim who initiates OAuth through such a host app.

### Recommendation
Call `Utils::ShopValidator.sanitize!(shop)` at the top of `Oauth.begin_auth` (and validate `auth_query.shop` in `validate_auth_callback`) before using it to build `auth_base_uri`/`Session`, consistent with `ClientCredentials`, `RefreshToken`, and `TokenExchange.migrate_to_expiring_token`.

### Proof of Concept
```ruby
# test/auth/oauth_test.rb
def test_begin_auth_does_not_sanitize_shop
  malicious_shop = "evil.example.com"
  result = ShopifyAPI::Auth::Oauth.begin_auth(shop: malicious_shop, redirect_path: "/redirect")
  uri = URI.parse(result[:auth_route])
  assert_equal("evil.example.com", uri.host) # host should have been rejected by ShopValidator.sanitize!
end
```
This demonstrates `auth_route.host` diverges from any trusted-domain-validated value, proving `ShopValidator.sanitize!` never runs in `begin_auth`.

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

**File:** lib/shopify_api/auth/oauth.rb (L117-119)
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
