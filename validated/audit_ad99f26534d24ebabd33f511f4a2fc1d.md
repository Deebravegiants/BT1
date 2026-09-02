This confirms the finding. `Oauth.begin_auth` never calls `Utils::ShopValidator.sanitize!` on the `shop` parameter, unlike `ClientCredentials.client_credentials` and `RefreshToken.refresh_access_token`, both of which validate first. `auth_base_uri` directly interpolates the raw `shop` string into `https://#{shop}/admin`, and this becomes the `auth_route` returned to the host app to redirect the merchant's browser, carrying `client_id` in the query string.

### Title
`Oauth.begin_auth` builds `auth_route` from unsanitized `shop`, enabling attacker-controlled OAuth redirect - (File: lib/shopify_api/auth/oauth.rb)

### Summary
`Oauth.begin_auth` interpolates the caller-supplied `shop` string directly into `auth_base_uri` (`https://#{shop}/admin`) without ever calling `Utils::ShopValidator.sanitize!`, unlike `ClientCredentials.client_credentials` and `RefreshToken.refresh_access_token`, which both validate `shop` before use. Since README-documented usage passes the raw `params[:shop]` installer query parameter straight into `begin_auth`, an attacker can craft an install link with a `shop` value pointing at attacker-controlled infrastructure, causing the merchant's browser to be redirected to `https://attacker.example.com/admin/oauth/authorize?client_id=...` instead of a real `*.myshopify.com` domain.

### Finding Description
The binding under test: shop interpolated into `auth_base_uri` should equal shop as returned by `Utils::ShopValidator.sanitize!`, but the code path never calls the validator, so equality is not enforced — `auth_base_uri(shop)` uses the raw, unvalidated string.

Code path: `begin_auth(shop:, redirect_path:, ...)` at [1](#0-0)  builds the `query` hash with `client_id: ShopifyAPI::Context.api_key` and other OAuth params, then computes `auth_route = auth_base_uri(shop) + "/oauth/authorize?#{query_string}"`. `auth_base_uri` at [2](#0-1)  does `return "https://#{shop}/admin" unless defined?(DevServer) && shop.include?(".my.shop.dev")` — the raw `shop` is interpolated directly with no sanitization call at all in `begin_auth`.

By contrast, `ClientCredentials.client_credentials` calls `validated_shop = Utils::ShopValidator.sanitize!(shop)` before constructing the session at [3](#0-2) , and `RefreshToken.refresh_access_token` does the same at [4](#0-3) . `Utils::ShopValidator.sanitize!` raises `Errors::InvalidShopError` for any `shop` value whose host does not resolve to one of `TRUSTED_SHOPIFY_DOMAINS` (`shopify.com`, `myshopify.io`, `myshopify.com`, `spin.dev`, `shop.dev`), per [5](#0-4) . For a value like `attacker.example.com`, `sanitize_shop_domain` returns `nil` because no trusted domain matches, so `sanitize!` raises.

Attacker's exact request: the attacker sends the merchant (or lures them) to the host app's install endpoint with `?shop=attacker.example.com` (or any non-myshopify value with attacker-controlled DNS). The host app, per documented usage, calls `Oauth.begin_auth(shop: params[:shop], redirect_path: ...)` directly. `begin_auth` performs no validation of `shop` and returns `auth_route: "https://attacker.example.com/admin/oauth/authorize?client_id=<real_client_id>&scope=...&redirect_uri=<real_redirect_uri>&state=<nonce>"`. The host app redirects the merchant's browser there. Nothing in `Context.setup?`, `Context.private?`, the `state`/nonce generation, or `SessionCookie` logic checks the shop domain itself — those only guard against CSRF/session issues, not domain validity.

Why existing guards fail: `Context.setup?` only checks that global config (API key/secret/host/scope) is present, not per-request shop validity. `Context.private?` guards a different flow. The `state` nonce is generated and stored regardless of `shop`'s value, so state validation later (in `validate_auth_callback`) doesn't protect against redirecting to an untrusted host during `begin_auth` — by the time state is checked, the redirect to the attacker's host has already happened.

### Impact Explanation
An attacker who controls a domain and can get a merchant to click an install link with `shop=attacker.example.com` causes the app to redirect the merchant's browser (with the real `client_id`) to attacker infrastructure. If the attacker's server proxies or mimics Shopify's `/oauth/authorize` flow (e.g., by forwarding to the real target shop's authorize endpoint, or presenting a phishing login), the attacker can end up capturing the authorization `code` intended for the app on the merchant's real shop, or otherwise manipulate the OAuth handshake, since the redirect target is entirely attacker-controlled. This matches "High - SSRF driving an authenticated request to an unintended host" / forced OAuth flow manipulation category — the redirect_uri and client_id (not secret) are disclosed to an attacker-chosen host, and the merchant is steered into an attacker-controlled OAuth entry point. This is repeatable against any victim merchant who can be lured to a crafted install link, and does not require the attacker to hold any credential.

### Likelihood Explanation
Preconditions: the host app must call `Oauth.begin_auth` directly with an unsanitized `shop` parameter, taken from the install request query string, as documented in the README, and must not itself perform shop validation before calling `begin_auth`. `Context.setup?` must be true (normal for any running app) and `Context.private?` false (standard public app). The attacker cost is minimal: register any domain, craft a link with `?shop=<attacker-domain>`, and get a merchant to click it (typical OAuth-install phishing pattern). This is feasible and repeatable per victim.

### Recommendation
In `Oauth.begin_auth`, validate and sanitize `shop` via `Utils::ShopValidator.sanitize!(shop)` (as is already done in `ClientCredentials.client_credentials` and `RefreshToken.refresh_access_token`) before passing it into `auth_base_uri`, and use the validated/sanitized shop value when constructing `auth_route`.

### Proof of Concept
```ruby
# test/auth/oauth_test.rb (new test)
def test_begin_auth_does_not_validate_shop_domain
  ShopifyAPI::Context.setup(
    api_key: "key", api_secret_key: "secret", host: "app-host.com",
    scope: ShopifyAPI::Auth::AuthScopes.new(["read_products"]), is_private: false, is_embedded: false
  )

  result = ShopifyAPI::Auth::Oauth.begin_auth(shop: "attacker.example.com", redirect_path: "/callback")

  # Vulnerable behaviour: no exception, and the auth_route points at attacker infrastructure
  assert result[:auth_route].start_with?("https://attacker.example.com/admin")

  # Contrast: the shared validator used elsewhere in the codebase rejects this same value
  assert_raises(ShopifyAPI::Errors::InvalidShopError) do
    ShopifyAPI::Utils::ShopValidator.sanitize!("attacker.example.com")
  end
end
```
This demonstrates the binding divergence directly: `auth_base_uri`'s interpolated shop (`attacker.example.com`) is accepted with no exception, while `Utils::ShopValidator.sanitize!` on the identical input raises `Errors::InvalidShopError`, proving `begin_auth` never enforces the equality that the other two entry points enforce.

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

**File:** lib/shopify_api/auth/client_credentials.rb (L25-26)
```ruby
          validated_shop = Utils::ShopValidator.sanitize!(shop)
          shop_session = ShopifyAPI::Auth::Session.new(shop: validated_shop)
```

**File:** lib/shopify_api/auth/refresh_token.rb (L24-25)
```ruby
          validated_shop = Utils::ShopValidator.sanitize!(shop)
          shop_session = ShopifyAPI::Auth::Session.new(shop: validated_shop)
```

**File:** lib/shopify_api/utils/shop_validator.rb (L9-64)
```ruby
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

      class << self
        extend T::Sig

        sig do
          params(
            shop_domain: String,
            myshopify_domain: T.nilable(String),
          ).returns(T.nilable(String))
        end
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
