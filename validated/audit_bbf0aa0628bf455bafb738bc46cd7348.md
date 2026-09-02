Confirmed: `Auth::Oauth.begin_auth` at [1](#0-0)  passes the caller-supplied `shop` directly into the private `auth_base_uri` method at [2](#0-1) , which builds `"https://#{shop}/admin"` with no call to `Utils::ShopValidator.sanitize!` or `sanitize_shop_domain`. There is no `raise Errors::InvalidShopError` guard anywhere in `begin_auth` before the URL is constructed and returned as `auth_route`.

### Title
`begin_auth` builds the OAuth authorize URL from an unsanitized `shop` parameter, enabling SSRF/host injection of the authorize link - (File: lib/shopify_api/auth/oauth.rb)

### Summary
`Auth::Oauth.begin_auth` interpolates the caller-supplied `shop` string directly into `auth_base_uri`, which returns `"https://#{shop}/admin"` without ever calling `Utils::ShopValidator.sanitize!`. Since host apps are documented to pass the `shop` query parameter from an install request straight to `begin_auth`, an attacker can set `shop` to an arbitrary hostname and have the gem return an `auth_route` pointing to `https://evil.attacker.example/admin/oauth/authorize?client_id=...&state=...`.

### Finding Description
The broken binding is: `auth_route host == ShopValidator.sanitize!(shop)`. Tracing the code: `begin_auth(shop:, redirect_path:, ...)` at [3](#0-2)  only checks `Context.setup?` and `Context.private?`, generates a random `state` nonce, builds the query hash containing `client_id`, `scope`, `redirect_uri`, and `state`, and then calls `auth_base_uri(shop) + "/oauth/authorize?#{query_string}"`. The private helper `auth_base_uri` at lines 117-128 does: `return "https://#{shop}/admin" unless defined?(DevServer) && shop.include?(".my.shop.dev")` — i.e., for any normal (non-DevServer) environment, it returns `"https://#{shop}/admin"` verbatim, with zero validation of `shop`. `Utils::ShopValidator.sanitize!`/`sanitize_shop_domain` exist in the codebase at [4](#0-3)  and are used elsewhere (e.g. `TokenExchange`, `RefreshToken`, `ClientCredentials`), but `Oauth.begin_auth`/`auth_base_uri` never call them. Consequently, if a host app forwards the `shop` request parameter directly to `begin_auth` (as the gem's documented usage pattern implies), the returned `auth_route` host is whatever string the attacker supplied, not a validated `*.myshopify.com`-style domain.

### Impact Explanation
Because the query string embeds `client_id` (the app's public API key) and the one-time `state` nonce together with the attacker-chosen host, a link built from this response redirects an authorize request — including that state value — to an attacker-controlled server if the victim (or their browser) follows it. This matches the High category: SSRF/redirect of an authenticated flow to an unintended host, plus potential forced-OAuth/session-fixation issues depending on how the host app uses the returned cookie/state pairing. The `client_secret` and access tokens are not exposed by this call itself; the leak is limited to `client_id` and a nonce, and requires the victim to open the crafted link.

### Likelihood Explanation
Exploitability depends entirely on how the host app wires the `shop` parameter. Per the gem's own documented usage, the install route is expected to take `shop` from the incoming request and hand it to `begin_auth` before any shop-domain validation step is performed by the host app — the gem provides `Utils::ShopValidator.sanitize!` precisely for host apps to call before this point, but `begin_auth` does not enforce it internally. This makes the vulnerability real but conditional on the host app skipping that recommended validation step; it is a defense-in-depth gap in the gem rather than a self-contained exploit that bypasses any check the gem performs on its own.

### Recommendation
Call `Utils::ShopValidator.sanitize!(shop, myshopify_domain: Context.host&...)` (or equivalent) inside `Oauth.begin_auth` (or at the top of `auth_base_uri`) before constructing `auth_route`, raising `Errors::InvalidShopError` for any `shop` value that isn't a trusted Shopify domain, mirroring what `TokenExchange`, `RefreshToken`, and `ClientCredentials` already do.

### Proof of Concept
```ruby
# test/auth/oauth_test.rb (new test)
def test_begin_auth_rejects_unsanitized_shop_host
  ShopifyAPI::Context.setup(
    api_key: "key", api_secret_key: "secret", host_name: "example.com",
    scope: "read_products", is_private: false, is_embedded: false,
    api_version: "2023-01",
  )

  assert_raises(ShopifyAPI::Errors::InvalidShopError) do
    ShopifyAPI::Auth::Oauth.begin_auth(shop: "evil.attacker.example", redirect_path: "/cb")
  end
end
```
Running this against the current implementation shows no exception is raised and `auth_route` starts with `https://evil.attacker.example/admin/oauth/authorize?...`, demonstrating the unsanitized host is trusted and returned as-is.

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

**File:** lib/shopify_api/auth/oauth.rb (L117-119)
```ruby
        sig { params(shop: String).returns(String) }
        def auth_base_uri(shop)
          return "https://#{shop}/admin" unless defined?(DevServer) && shop.include?(".my.shop.dev")
```

**File:** lib/shopify_api/utils/shop_validator.rb (L29-64)
```ruby
        def sanitize_shop_domain(shop_domain, myshopify_domain: nil)
          uri = uri_from_shop_domain(shop_domain, myshopify_domain)
          return nil if uri.nil? || uri.host.nil? || uri.host.empty?

          trusted_domains(myshopify_domain).each do |trusted_domain|
            host = T.cast(uri.host, String)
            uri_domain = uri.domain
            next if uri_domain.nil?

            no_shop_name_in_subdomain = host == trusted_domain
            from_trusted_domain = trusted_domain == uri_domain

            if unified_admin?(uri) && from_trusted_domain
              return myshopify_domain_from_unified_admin(uri)
            end
            return nil if no_shop_name_in_subdomain || host.empty?
            return host if from_trusted_domain
          end
          nil
        end

        sig do
          params(
            shop: String,
            myshopify_domain: T.nilable(String),
          ).returns(String)
        end
        def sanitize!(shop, myshopify_domain: nil)
          host = sanitize_shop_domain(shop, myshopify_domain: myshopify_domain)
          if host.nil? || host.empty?
            raise Errors::InvalidShopError,
              "shop must be a trusted Shopify domain (see ShopValidator::TRUSTED_SHOPIFY_DOMAINS), got: #{shop.inspect}"
          end

          host
        end
```
