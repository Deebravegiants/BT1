### Title
Unvalidated `shop` parameter in `Oauth.begin_auth` forces OAuth initiation against an attacker-controlled host - (File: `lib/shopify_api/auth/oauth.rb`)

### Summary
`ShopifyAPI::Auth::Oauth.begin_auth` builds the OAuth authorization redirect URL directly from the caller-supplied `shop` string, with no verification that it is a genuine, trusted Shopify domain. The library ships a purpose-built domain-binding utility, `ShopifyAPI::Utils::ShopValidator`, but it is never invoked from the OAuth flow. This lets an unprivileged party who controls the value passed as `shop` (e.g. via a crafted install link `/auth?shop=<attacker-host>`) force the app to redirect a merchant's browser — carrying the real `client_id`, `redirect_uri`, and `state` — to an arbitrary attacker-controlled host instead of `*.myshopify.com`.

### Finding Description
`begin_auth` accepts `shop:` and immediately uses it, unchecked, to compute the authorization host: [1](#0-0) 

The host is derived by `auth_base_uri`, which simply interpolates the raw `shop` string into a URL: [2](#0-1) 

The gem defines `ShopifyAPI::Utils::ShopValidator.sanitize!` / `sanitize_shop_domain`, whose explicit purpose is to bind an incoming shop string to one of the `TRUSTED_SHOPIFY_DOMAINS` (`shopify.com`, `myshopify.io`, `myshopify.com`, `spin.dev`, `shop.dev`) before it is trusted: [3](#0-2) 

This validator is never called anywhere in `lib/shopify_api/auth/oauth.rb`. The binding that should hold is:

`host used to build the OAuth authorize URL == a shop domain proven to belong to the `TRUSTED_SHOPIFY_DOMAINS` set`

but the actual code enforces:

`host used to build the OAuth authorize URL == whatever string the caller passed in as shop, unchecked`

Because `begin_auth` is the very first, pre-authentication step of the OAuth flow, the `shop` value at this point carries no HMAC or other proof of Shopify origin — it typically comes straight from a query parameter on the app's own "install"/"login" route, which is itself often populated from an unauthenticated browser request. The absence of `ShopValidator` here means the redirect target host is fully attacker-controlled.

### Impact Explanation
This matches the "forced OAuth completion" analog explicitly called out as a High-impact class: the app can be tricked into initiating and directing its OAuth authorization request (carrying `client_id`, `redirect_uri`, and the app's freshly generated `state` nonce) to a host chosen by the attacker rather than Shopify. An attacker who controls the target host can:
- Serve a convincing Shopify-lookalike consent page to phish the merchant's Shopify credentials, since the merchant's browser is being sent by the trusted app itself.
- Capture the `state` value and `redirect_uri`, then attempt to complete or manipulate the flow back at the app's callback endpoint.

This is a real, historically-documented bug class for Shopify's own client libraries (unsanitized shop domain in OAuth redirect), which is exactly why `ShopValidator` exists in this codebase — but it is dead code with respect to the OAuth entry point.

### Likelihood Explanation
`begin_auth` is a standard, commonly wired-up entry point (e.g., `/auth?shop=...`) that host applications call with the incoming `shop` request parameter to kick off installation/login. No credentials, secrets, or prior authentication are needed to trigger it — an unprivileged internet user only needs to get a merchant to click a crafted link pointing at the app's own auth route with a malicious `shop` value.

### Recommendation
Call `ShopifyAPI::Utils::ShopValidator.sanitize!(shop)` (or `sanitize_shop_domain`) at the top of `begin_auth` (and ideally also in `validate_auth_callback`) and raise `Errors::InvalidShopError` before constructing `auth_base_uri`, so the authorize-request host is always provably bound to `ShopValidator::TRUSTED_SHOPIFY_DOMAINS`.

### Proof of Concept
1. Host application exposes `GET /auth?shop=:shop` which calls `ShopifyAPI::Auth::Oauth.begin_auth(shop: params[:shop], redirect_path: "/auth/callback")`, matching the documented usage of this method.
2. Attacker sends a merchant a link: `https://victim-app.example.com/auth?shop=evil-phish.example.net`.
3. `begin_auth` computes `auth_base_uri("evil-phish.example.net")` → `"https://evil-phish.example.net/admin"` [4](#0-3)  and returns `auth_route = "https://evil-phish.example.net/admin/oauth/authorize?client_id=<real_key>&scope=...&redirect_uri=https://victim-app.example.com/auth/callback&state=<nonce>"`.
4. The merchant's browser is redirected to the attacker's server, which can present a phishing page or otherwise abuse the leaked `client_id`/`redirect_uri`/`state`, none of which were validated against `ShopValidator::TRUSTED_SHOPIFY_DOMAINS`.

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

**File:** lib/shopify_api/utils/shop_validator.rb (L6-64)
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
