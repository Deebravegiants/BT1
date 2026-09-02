### Title
Unsanitized `shop` parameter in `Oauth.begin_auth` enables forced-OAuth redirect to an attacker-controlled host - (File: lib/shopify_api/auth/oauth.rb)

### Summary
`ShopifyAPI::Auth::Oauth.begin_auth` builds the OAuth "authorize" redirect URL directly from the caller-supplied `shop` string via `auth_base_uri(shop)`, with no domain validation. Every other entry point in the gem that accepts a raw `shop`/domain value (`ClientCredentials`, `RefreshToken`, `TokenExchange`, the Storefront GraphQL client) routes it through `ShopifyAPI::Utils::ShopValidator.sanitize!` first, but `begin_auth` does not. This breaks the intended binding `shop == a trusted *.myshopify.com/myshopify.io/shop.dev domain` and lets an unauthenticated caller redirect the merchant's browser, together with the app's `client_id`, requested `scope`, and `redirect_uri`, to an arbitrary attacker-controlled host.

### Finding Description
`begin_auth` is documented and intended to be called with a `shop` value taken straight from the incoming request (the gem's own docs show `shop = request.headers["Shop"]`, an unauthenticated, attacker-influenced value): [1](#0-0) 

Inside `begin_auth`, this `shop` value is passed unmodified to `auth_base_uri`, which simply interpolates it into a URL: [2](#0-1) [3](#0-2) 

No call to `ShopValidator` (or any other domain check) occurs anywhere in `oauth.rb`. Compare this to the other OAuth-adjacent flows in the same library, which all sanitize the shop domain before using it: [4](#0-3) 

`ShopValidator.sanitize!`/`sanitize_shop_domain` is referenced in `token_exchange.rb`, `client_credentials.rb`, `refresh_token.rb`, and the storefront GraphQL client, confirming this validation is the library's established, intended safeguard for exactly this class of input — but it is absent from `Oauth.begin_auth`.

The binding that should hold is:
`shop param used to build auth_route == sanitized value that is provably a *.myshopify.com/myshopify.io/spin.dev/shop.dev/custom myshopify_domain host`

Instead, the actual check is:
`shop param used to build auth_route == raw, attacker-suppliable string`

Because `auth_base_uri` performs no equality/allowlist check, any string (e.g. `evil.attacker.com`) is accepted and directly used to construct `https://evil.attacker.com/admin/oauth/authorize?client_id=...&scope=...&redirect_uri=<app's real callback>&state=<nonce>`.

### Impact Explanation
This qualifies as High severity per the "forced OAuth completion" category: an unauthenticated internet user who can influence the `shop` value passed to `begin_auth` (which, by the library's own documented usage pattern, comes straight from a request header/param) causes the merchant's browser to be redirected to an attacker-chosen host along with the app's `client_id`, requested `scope`, and legitimate `redirect_uri`/`state` nonce. The attacker-controlled page can then complete its own genuine Shopify authorization for a shop of the attacker's choosing and redirect the victim back to the real app's callback with a `code` that the app will exchange for a valid access token — installing the attacker's shop session into the victim's browser/cookie flow (forced OAuth completion), or otherwise leveraging the app's `client_id`/scope disclosure and redirect flow for phishing/hijacking the installation process. `validate_auth_callback` still separately verifies the callback's HMAC, but that only protects the callback step — the initial redirect leak/hijack via `begin_auth` happens before any HMAC is computed, so the missing shop validation is a real, independent break in the identity binding between "shop" and "trusted Shopify domain".

### Likelihood Explanation
Likelihood is high: the gem's own documentation instructs integrators to source `shop` from `request.headers["Shop"]`, i.e., directly from client-controlled input, with no guidance to call `ShopValidator` first. Any app that follows the documented usage pattern verbatim (as many do, mirroring `docs/usage/oauth.md`) is exposed without any additional attacker capability beyond sending a normal HTTP request with a crafted `shop` value to the app's login route.

### Recommendation
In `ShopifyAPI::Auth::Oauth.begin_auth`, sanitize the incoming `shop` argument through `ShopifyAPI::Utils::ShopValidator.sanitize!` (raising `Errors::InvalidShopError` on failure) before it is used in `auth_base_uri`, exactly as is already done in `client_credentials.rb`, `refresh_token.rb`, and `token_exchange.rb`. Update `docs/usage/oauth.md` to show this sanitization step explicitly so integrators following the documented pattern are protected by default.

### Proof of Concept
1. App exposes a login route implementing the documented pattern:
   ```ruby
   def login
     shop = request.headers["Shop"] # or params[:shop]
     auth_response = ShopifyAPI::Auth::Oauth.begin_auth(shop: shop, redirect_path: "/auth/callback")
     redirect_to auth_response[:auth_route]
   end
   ```
2. Attacker lures a victim merchant admin to `https://victim-app.example.com/login` with header/param `Shop: evil.attacker.com`.
3. `begin_auth` computes `auth_base_uri("evil.attacker.com")` → `"https://evil.attacker.com/admin"` (no validation rejects this), producing:
   `auth_route = "https://evil.attacker.com/admin/oauth/authorize?client_id=<APP_CLIENT_ID>&scope=<SCOPES>&redirect_uri=https://victim-app.example.com/auth/callback&state=<nonce>&grant_options%5B%5D=per-user"`
4. The victim's browser is redirected (307) to `evil.attacker.com`, disclosing the app's `client_id`, requested scopes, and real callback URL to the attacker's server, and the attacker can drive the victim through a genuine Shopify OAuth grant for a shop of the attacker's choosing, then forward the resulting `code`/`state` to `https://victim-app.example.com/auth/callback` to force-complete OAuth for that attacker-chosen shop in the victim's session.

### Citations

**File:** docs/usage/oauth.md (L179-199)
```markdown
```ruby
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

**File:** lib/shopify_api/utils/shop_validator.rb (L1-64)
```ruby
# typed: strict
# frozen_string_literal: true

require "addressable/uri"

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
