### Title
`Auth::Oauth.begin_auth` builds the `/oauth/authorize` redirect URL from an unvalidated `shop` parameter - (File: lib/shopify_api/auth/oauth.rb)

### Summary
`Auth::Oauth.begin_auth` interpolates the caller-supplied `shop` string directly into `auth_base_uri(shop)` (`"https://#{shop}/admin"`) with no call to `Utils::ShopValidator.sanitize!` or any allow-list check. Since the documented integration pattern forwards the `shop` query parameter from an install route straight into `begin_auth`, an attacker can make the returned `auth_route` point at an attacker-controlled host while still containing the app's real `client_id` and the freshly generated one-time `state` nonce.

### Finding Description
The broken binding, stated as an equality: `host(auth_route)` should equal `ShopValidator.sanitize!(shop)`, but in the actual code `host(auth_route) == shop` (the raw, unauthenticated input), with `ShopValidator.sanitize!` never invoked anywhere on this path.

Code path:
- `begin_auth(shop:, redirect_path:, ...)` in [1](#0-0)  only checks `Context.setup?` and `Context.private?`, generates `state`, builds the `query` hash containing `client_id: ShopifyAPI::Context.api_key` and `state:`, then calls `auth_base_uri(shop) + "/oauth/authorize?#{query_string}"`.
- `auth_base_uri(shop)` in [2](#0-1)  returns `"https://#{shop}/admin"` unless a `DevServer` constant is defined and the shop string contains `.my.shop.dev` — there is no allow-list/domain check for the normal (non-dev) branch.
- `Utils::ShopValidator.sanitize!` exists precisely to validate that a shop string resolves to a trusted Shopify domain (`TRUSTED_SHOPIFY_DOMAINS`) as seen in [3](#0-2) , but `begin_auth`/`auth_base_uri` never call it.

Attacker request: `GET /install?shop=evil.attacker.example` on the host app's install route (per README/docs pattern), which the app forwards verbatim as `Oauth.begin_auth(shop: params[:shop], redirect_path: "/auth/callback")`. The method returns `auth_route = "https://evil.attacker.example/admin/oauth/authorize?client_id=...&scope=...&redirect_uri=...&state=<nonce>&grant_options%5B%5D=..."`, and the host app redirects the browser there — sending the real `client_id` and the one-time `state` value to an attacker-controlled host.

Existing guards that were checked and do not prevent this:
- `Context.setup?`/`Context.private?` only gate whether OAuth is configured at all, not the validity of `shop`.
- `HmacValidator.validate` and the `state == auth_query.state` check in `validate_auth_callback` ( [4](#0-3) ) run later, on the *callback* leg, and do nothing to stop the *redirect* leg from going to an attacker host in the first place.
- `ShopValidator.sanitize!` is defined and used elsewhere (e.g. `TokenExchange`, `ClientCredentials`, `RefreshToken`) but is not called by `Oauth.begin_auth`, so it provides no protection on this path.

### Impact Explanation
An attacker who controls the crafted install link causes the app to disclose the app's `client_id` and a live one-time `state` nonce to a host of the attacker's choosing (SSRF/redirect of sensitive OAuth parameters). This matches the High-severity category "SSRF driving an authenticated request to an unintended host, session fixation or forced OAuth completion." Any victim who follows a `/install?shop=evil.attacker.example`-style link sent by the attacker is affected; the attack is repeatable against arbitrary victims and does not require any secret or prior session — it only requires the attacker to control the `shop` query parameter, which they always can since it's an unauthenticated URL parameter.

### Likelihood Explanation
Preconditions are minimal and match the documented usage: `Context.setup` called, app not private, and the host app's install route forwarding `shop` to `begin_auth` as shown in `docs/usage/oauth.md`. No app secrets or prior sessions are needed. The attacker only needs to get a victim (or their own browser, to observe leaked parameters) to hit the crafted install URL. This is trivially repeatable at zero cost.

### Recommendation
In `Oauth.begin_auth` (or inside `auth_base_uri`), call `Utils::ShopValidator.sanitize!(shop)` (raising `Errors::InvalidShopError` on failure) before using `shop` to build `auth_base_uri`, mirroring how `TokenExchange`, `ClientCredentials`, and `RefreshToken` already validate the shop domain.

### Proof of Concept
```ruby
# test/auth/oauth_test.rb (new test)
def test_begin_auth_rejects_untrusted_shop_host
  ShopifyAPI::Context.setup(
    api_key: "key", api_secret_key: "secret", host: "https://app.example.com",
    scope: "read_products", is_private: false, is_embedded: false, api_version: "unstable",
  )

  assert_raises(ShopifyAPI::Errors::InvalidShopError) do
    ShopifyAPI::Auth::Oauth.begin_auth(shop: "evil.attacker.example", redirect_path: "/cb")
  end
end
```
Running this against the current code shows `begin_auth` does NOT raise and instead returns `auth_route` with host `evil.attacker.example`, i.e. `URI(result[:auth_route]).host == "evil.attacker.example"` while `ShopifyAPI::Utils::ShopValidator.sanitize!("evil.attacker.example")` itself raises `Errors::InvalidShopError`, proving the two sides of the binding diverge.

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
