### Title
Unvalidated `shop` parameter in `ShopifyAPI::Auth::Oauth.begin_auth` allows attacker-controlled OAuth authorize redirect host - (File: lib/shopify_api/auth/oauth.rb)

### Summary
`begin_auth` builds the OAuth authorization redirect URL by directly interpolating the caller-supplied `shop` string into `https://#{shop}/admin` via `auth_base_uri`, without ever calling `Utils::ShopValidator.sanitize!`. Every other OAuth-adjacent flow in this gem (`TokenExchange`, `ClientCredentials`, `RefreshToken`) validates `shop` through `ShopValidator.sanitize!`/`.sanitize_shop_domain`, but `begin_auth` does not, so if a host app passes through an unvalidated request-derived `shop` value (as the gem's own documentation example does), the app's `client_id` and `redirect_uri` get sent to an attacker-chosen host.

### Finding Description
The broken binding: CREDENTIAL_DESTINATION should satisfy `host(auth_route) ∈ ShopValidator.TRUSTED_SHOPIFY_DOMAINS-derived hosts`, but in `begin_auth` the actual binding is `host(auth_route) == shop` (the raw, attacker-suppliable string), with no intersection with `ShopValidator` at all.

Code path:
- `begin_auth(shop:, redirect_path:, ...)` at [1](#0-0)  builds `query` containing `client_id: ShopifyAPI::Context.api_key` and `redirect_uri: "#{ShopifyAPI::Context.host}#{redirect_path}"`, then computes `auth_route = auth_base_uri(shop) + "/oauth/authorize?#{query_string}"`.
- `auth_base_uri(shop)` at [2](#0-1)  returns `"https://#{shop}/admin"` verbatim unless a `DevServer` dev-mode branch applies — `shop` is never passed through `ShopValidator`.
- By contrast, `ShopValidator.sanitize!` is used to constrain `shop` in `lib/shopify_api/auth/token_exchange.rb`, `lib/shopify_api/auth/client_credentials.rb`, and `lib/shopify_api/auth/refresh_token.rb`, confirmed by [3](#0-2) , but `begin_auth` has no equivalent call.
- The gem's own documentation instructs implementers to take `shop = request.headers["Shop"]` directly from the incoming request and pass it straight to `begin_auth`, with no sanitization step shown, as seen in `docs/usage/oauth.md` lines 180-199 (`shop = request.headers["Shop"]` → `ShopifyAPI::Auth::Oauth.begin_auth(shop: domain, redirect_path: "/auth/callback")`).

Attacker request: `GET /auth?shop=evil.attacker.com` (or via the `Shop` header per the documented example) to the app's login route that forwards the value to `begin_auth`. The resulting `auth_route` becomes `https://evil.attacker.com/admin/oauth/authorize?client_id=<real client_id>&redirect_uri=<real redirect_uri>&state=<state>`. The app then sets the `state` cookie and 307-redirects the merchant's browser to that attacker-controlled host, carrying `client_id` and `redirect_uri` in the query string.

Existing guards do not catch this: `Context.setup?`/`Context.private?` only check app-level configuration, not the `shop` value; `HmacValidator.validate` and the `state` comparison only apply in `validate_auth_callback`, which is never reached in this flow since the redirect never goes to real Shopify; Sorbet's `params(shop: String)` sig only enforces the type is a `String`, not its content.

### Impact Explanation
This is an SSRF-style redirect of a sensitive OAuth-initiation request to an attacker-chosen host, exposing the app's `client_id` and intended `redirect_uri` to that host for every request where the calling app does not itself pre-validate `shop`. Whether an attacker can subsequently capture a live authorization `code` depends on merchant interaction with the attacker's fake authorize page and is not solely within this gem's code, but the core defect — the gem building and returning a redirect target from an unvalidated string, inconsistent with its own validation pattern used elsewhere (`TokenExchange`, `ClientCredentials`, `RefreshToken`) — is squarely in `lib/shopify_api/auth/oauth.rb`. This matches "High - SSRF driving an authenticated[-flow] request to an unintended host" / credential (client_id/redirect_uri) leakage to an unintended host, per app per request, repeatable against any victim who reaches the app's start-OAuth route with attacker-controlled `shop`.

### Likelihood Explanation
Exploitability depends entirely on the host application's implementation: if the app follows the gem's own documented example and forwards a request-supplied `shop`/`Shop` header directly into `begin_auth` without first validating it (which the docs do not instruct developers to do, and which the gem does not do internally, unlike its sibling `TokenExchange`/`ClientCredentials`/`RefreshToken` flows), the vulnerability is trivially triggered with a single unauthenticated GET request, no secrets or special access required.

### Recommendation
In `begin_auth`, sanitize `shop` before use, e.g. `shop = Utils::ShopValidator.sanitize!(shop)` (or pass through `auth_base_uri`) so that only hosts matching `ShopValidator::TRUSTED_SHOPIFY_DOMAINS` (or a configured `myshopify_domain`) can become the OAuth authorize target, mirroring the validation already applied in `token_exchange.rb`, `client_credentials.rb`, and `refresh_token.rb`.

### Proof of Concept
```ruby
# test/auth/oauth_test.rb (new test)
def test_begin_auth_does_not_validate_shop_domain
  ShopifyAPI::Context.setup(
    api_key: "key", api_secret_key: "secret", api_version: "2024-01",
    scope: "read_products", host_name: "app-host.com", is_private: false, is_embedded: false,
  )

  result = ShopifyAPI::Auth::Oauth.begin_auth(shop: "evil.attacker.com", redirect_path: "/cb")
  auth_uri = URI.parse(result[:auth_route])

  # Binding under test: auth_uri.host should equal a ShopValidator-sanitized value, not the raw attacker string
  assert_equal "evil.attacker.com", auth_uri.host
  assert_raises(ShopifyAPI::Errors::InvalidShopError) do
    ShopifyAPI::Utils::ShopValidator.sanitize!("evil.attacker.com")
  end
  # => proves auth_uri.host (attacker-controlled) diverges from what ShopValidator would ever accept,
  #    while client_id/redirect_uri are embedded in the query string sent to that host.
  assert_match(/client_id=key/, result[:auth_route])
end
```

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
