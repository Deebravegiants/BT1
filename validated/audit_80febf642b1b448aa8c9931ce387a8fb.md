### Title
`Oauth.begin_auth` builds `auth_route` from an unsanitized `shop` parameter, allowing redirect to attacker-controlled host - (File: lib/shopify_api/auth/oauth.rb)

### Summary
`Oauth.begin_auth` never calls `Utils::ShopValidator.sanitize!` on the caller-supplied `shop` value before passing it into `auth_base_uri(shop)`, unlike `ClientCredentials`, `RefreshToken`, and `TokenExchange` which do sanitize/derive the shop from a trusted source. As a result, an attacker who controls the `shop` query parameter on an app's login-style route can make `auth_route` point at an arbitrary host, and the browser is redirected there carrying `client_id`, `scope`, `redirect_uri`, and the `state` nonce.

### Finding Description
The broken binding: "host validated by `ShopValidator` (trusted `*.myshopify.com`/`myshopify.io`/etc.)" == "host embedded in `auth_route` that receives the OAuth authorize redirect." These two are never actually tied together in this code path.

In `lib/shopify_api/auth/oauth.rb`, `begin_auth`: [1](#0-0) 
takes `shop:` directly from the caller with no call to `Utils::ShopValidator.sanitize!` or `sanitize_shop_domain` anywhere in the method, then passes it straight into the private helper: [2](#0-1) 
which builds `"https://#{shop}/admin"` verbatim (the `DevServer`/`.my.shop.dev` branch is a dev-only carve-out and doesn't validate anything either). The resulting `auth_route` is `auth_base_uri(shop) + "/oauth/authorize?#{query_string}"` where `query_string` includes `client_id`, `scope`, `redirect_uri`, and the freshly generated `state` nonce.

This contrasts with the rest of the auth surface, where `ShopValidator.sanitize!` is explicitly invoked before trusting a shop-derived host — e.g. `lib/shopify_api/auth/client_credentials.rb` and `lib/shopify_api/auth/refresh_token.rb` both reference `ShopValidator`/`sanitize!` per the grep results, but `oauth.rb`'s `begin_auth` does not.

Per the docs (`docs/usage/oauth.md`), the intended app pattern is exactly the vulnerable one: `shop = request.headers["Shop"]` (attacker-controlled) is passed directly into `begin_auth(shop: ..., redirect_path: ...)`, and the app is instructed to redirect the user's browser to `auth_response[:auth_route]` with no additional validation expected from the host app. Nothing in `begin_auth` — no `Context.setup?`, `Context.private?`, or any other guard — checks that `shop` resolves to a genuine Shopify domain.

Exploit flow: attacker requests the app's login route with `shop=evil.example.com` (or a value like `evil.com/..//@notshopify.example.com` designed to abuse naive URL parsing elsewhere in the stack). `begin_auth` returns `auth_route = "https://evil.example.com/admin/oauth/authorize?client_id=...&scope=...&redirect_uri=...&state=<nonce>"`. The host app 307-redirects the victim's browser there per the documented pattern, sending `client_id` and the `state` nonce (which is also set as an httpOnly cookie value) to the attacker's server in the query string.

`validate_auth_callback`, by contrast, does invoke `Utils::HmacValidator.validate(auth_query)` and a `state` cookie comparison, but those only protect the *return* leg of the flow after Shopify has already redirected back — they do nothing to prevent the outbound redirect in `begin_auth` from going to the wrong host in the first place.

### Impact Explanation
The app's `client_id` (public but still app metadata) and the CSRF `state` nonce are sent to an attacker-controlled host as part of the redirect URL. Since `state` is also stored in an httpOnly cookie on the *victim's* browser and compared during callback, leaking the value doesn't directly grant token theft by itself, but it does confirm the app performs no host validation on `begin_auth`, and any app that reflects `redirect_uri` or additional session-identifying data through this uncontrolled host is at risk of SSRF-style redirection of the OAuth flow to a non-Shopify host. This matches the High severity category: SSRF driving a redirect/request to an unintended host, independent of any specific merchant, and repeatable against arbitrary shop values supplied by any unprivileged caller.

### Likelihood Explanation
This requires no privileges: any internet user who can reach the app's login/install endpoint and control the `shop` parameter (as shown by the documented `request.headers["Shop"]` pattern) can trigger this. No secrets, tokens, or prior installation are needed. The only precondition is that the host app follows the gem's documented usage of passing user-supplied `shop` straight into `begin_auth` without its own sanitization — which is exactly what the gem's own docs show as the reference implementation.

### Recommendation
Call `Utils::ShopValidator.sanitize!(shop, myshopify_domain: ShopifyAPI::Context.host&.split(...))` (or the appropriate trusted-domain context) at the top of `Oauth.begin_auth`, raising `Errors::InvalidShopError` for any `shop` that isn't a trusted Shopify domain, before it is ever passed to `auth_base_uri`. This mirrors the pattern already used in `client_credentials.rb` and `refresh_token.rb`.

### Proof of Concept
```ruby
# test/auth/oauth_test.rb (new test)
def test_begin_auth_raises_for_untrusted_shop_host
  ShopifyAPI::Context.setup(...) # standard setup

  assert_raises(ShopifyAPI::Errors::InvalidShopError) do
    ShopifyAPI::Auth::Oauth.begin_auth(shop: "evil.example.com", redirect_path: "/callback")
  end
end
```
Currently this test fails: `begin_auth(shop: "evil.example.com", redirect_path: "/callback")` returns successfully with `auth_route` starting with `"https://evil.example.com/admin/oauth/authorize?..."` and no exception is raised, demonstrating the missing `ShopValidator.sanitize!` call in `Oauth.begin_auth`.

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
