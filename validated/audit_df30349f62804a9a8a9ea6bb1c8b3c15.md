Missing shop-domain validation in `ShopifyAPI::Auth::Oauth.begin_auth` is the concrete analog. Every other OAuth-adjacent entry point in this gem (`client_credentials`, `token_exchange`, `refresh_token`, the storefront GraphQL client) forces the caller-supplied `shop` through `Utils::ShopValidator.sanitize!` before it is used to build a request host [1](#0-0) , but `begin_auth` builds the redirect host directly from the untrusted `shop:` keyword argument with no such check [2](#0-1) .

### Title
Missing trusted-domain validation of `shop` in `Oauth.begin_auth` allows the app's OAuth redirect host to be attacker-controlled - (File: lib/shopify_api/auth/oauth.rb)

### Summary
`ShopifyAPI::Auth::Oauth.begin_auth` builds the OAuth authorization URL by directly interpolating the caller-supplied `shop` value into `auth_base_uri(shop)`, without ever validating that `shop` is a trusted `*.myshopify.com`/`myshopify.io`/`spin.dev`/`shop.dev` domain. Every other place in the gem that turns a caller-supplied `shop` string into a request host (`ClientCredentials`, `TokenExchange`, `RefreshToken`, the storefront GraphQL client) explicitly calls `Utils::ShopValidator.sanitize!` first.

### Finding Description
`begin_auth` is documented to be called with a shop value taken straight from the incoming HTTP request (the gem's own docs show `shop = request.headers["Shop"]`) [3](#0-2) . That value flows unchecked into `auth_base_uri`:

```ruby
def auth_base_uri(shop)
  return "https://#{shop}/admin" unless defined?(DevServer) && shop.include?(".my.shop.dev")
  ...
end
``` [4](#0-3) 

and directly into the returned `auth_route`:
```ruby
auth_route = auth_base_uri(shop) + "/oauth/authorize?#{query_string}"
``` [5](#0-4) 

The query string embeds the app's `client_id` and requested `scope`:
```ruby
query = {
  client_id: ShopifyAPI::Context.api_key,
  scope: scope.to_s,
  redirect_uri: "#{ShopifyAPI::Context.host}#{redirect_path}",
  state: state,
  "grant_options[]": is_online ? "per-user" : "",
}
``` [6](#0-5) 

By contrast, the gem's other public entry points that convert a caller-supplied shop string into a request host all call `ShopValidator.sanitize!`, e.g. `ClientCredentials`:
```ruby
def test_client_credentials_rejects_non_shopify_domain
  assert_raises(ShopifyAPI::Errors::InvalidShopError) do
    ShopifyAPI::Auth::ClientCredentials.client_credentials(shop: "attacker.example")
  end
end
``` [7](#0-6) 

`ShopValidator.sanitize!` is the mechanism that binds "shop domain acted upon" to "shop domain trusted as `*.myshopify.com`" [8](#0-7) . `begin_auth` breaks exactly this binding: the host that receives the app's `client_id`/`scope`/`redirect_uri` is never checked against `TRUSTED_SHOPIFY_DOMAINS`.

Downstream, `validate_auth_callback` is protected because `auth_query.shop` is covered by the OAuth HMAC signed with `Context.api_secret_key` [9](#0-8) , so an attacker who cannot compute that HMAC cannot forge the callback that leads to `client_secret` disclosure. The gap is isolated to the pre-authentication `begin_auth` step, where no secret is involved yet and the identity-binding check (`sanitize!`) that exists everywhere else in the gem is simply absent.

### Impact Explanation
If the host application passes user-controlled input into `begin_auth`'s `shop:` parameter (which the gem's own documentation explicitly recommends), an unauthenticated attacker can cause the merchant's browser to be redirected to `https://attacker-domain/admin/oauth/authorize?client_id=<app_client_id>&scope=<app_scopes>&redirect_uri=<app_callback>&state=<nonce>` instead of a genuine Shopify domain. This discloses the app's `client_id`, its requested OAuth `scope` list, and the app's registered `redirect_uri` to an attacker-controlled host, and can be used to stage a forced/spoofed OAuth completion flow against the merchant (the attacker's page can mimic Shopify's consent screen and drive the victim back to the app's real callback with attacker-influenced parameters). This falls under the defined "session fixation or forced OAuth completion" High-impact category, since the missing validation removes the trust boundary the gem enforces everywhere else for the same input.

### Likelihood Explanation
Likelihood is elevated by the fact that the gem's own documentation example wires `begin_auth`'s `shop` parameter directly from a request header with no sanitization shown, and no code path inside `begin_auth` itself performs that sanitization — unlike `ClientCredentials`, `TokenExchange`, and `RefreshToken`, which all explicitly guard against this via `ShopValidator.sanitize!`. Any host app that follows the documented pattern literally (or trusts the gem to validate `shop`, given every sibling method does) is exposed.

### Recommendation
Call `Utils::ShopValidator.sanitize!(shop)` (or `sanitize_shop_domain`, raising `Errors::InvalidShopError` on failure) at the top of `Oauth.begin_auth`, mirroring the existing pattern in `ClientCredentials.client_credentials`, `TokenExchange.exchange_token`, and `RefreshToken.refresh_access_token`, before the value is used to construct `auth_base_uri`.

### Proof of Concept
1. App calls `ShopifyAPI::Auth::Oauth.begin_auth(shop: params[:shop], redirect_path: "/auth/callback")` following the gem's documented pattern, where `params[:shop]` is attacker-supplied (e.g., a query/header value an attacker can set for a victim, such as via a crafted install link the merchant clicks).
2. Attacker sets `shop = "attacker.example"`.
3. `auth_base_uri("attacker.example")` returns `"https://attacker.example/admin"` [10](#0-9) , and `begin_auth` returns `auth_route = "https://attacker.example/admin/oauth/authorize?client_id=<real_client_id>&scope=<real_scopes>&redirect_uri=<real_callback>&state=<nonce>"`.
4. The host app 307-redirects the merchant's browser to this attacker-controlled URL, disclosing `client_id`/`scope`/`redirect_uri` and allowing the attacker to present a fake consent page to the merchant.

### Citations

**File:** lib/shopify_api/utils/shop_validator.rb (L9-18)
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

**File:** docs/usage/oauth.md (L181-199)
```markdown
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

**File:** test/auth/client_credentials_test.rb (L33-37)
```ruby
      def test_client_credentials_rejects_non_shopify_domain
        assert_raises(ShopifyAPI::Errors::InvalidShopError) do
          ShopifyAPI::Auth::ClientCredentials.client_credentials(shop: "attacker.example")
        end
      end
```

**File:** lib/shopify_api/auth/oauth/auth_query.rb (L34-43)
```ruby
        def to_signable_string
          params = {
            code: code,
            host: host,
            shop: shop,
            state: state,
            timestamp: timestamp,
          }
          URI.encode_www_form(params)
        end
```
