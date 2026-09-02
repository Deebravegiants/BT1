### Title
`begin_auth` builds the OAuth authorize redirect from an unvalidated `shop`, letting an attacker force the app to leak `client_id` and the OAuth `state` nonce to an attacker-controlled host - ([File: lib/shopify_api/auth/oauth.rb])

### Summary
`ShopifyAPI::Auth::Oauth.begin_auth` accepts a `shop:` string and uses it, unsanitized, to build the OAuth authorization URL that the merchant's browser is redirected to. Although the gem ships `ShopifyAPI::Utils::ShopValidator.sanitize!`/`sanitize_shop_domain` specifically to confirm a shop string is a trusted `*.myshopify.com`/`*.myshopify.io`/etc. domain, `begin_auth` never calls it. Documentation for `shop` in `docs/usage/oauth.md` says it must be "A Shopify domain name in the form `{exampleshop}.myshopify.com`" but nothing in the gem enforces that shape before the value is embedded into `auth_base_uri(shop)`.

### Finding Description
`begin_auth` computes the redirect target as: [1](#0-0) 

and `auth_base_uri` does nothing more than string-interpolate the caller-supplied `shop` value into an HTTPS URL: [2](#0-1) 

The library's own `ShopValidator` module exists precisely to bind an untrusted "shop" string to the set of trusted Shopify domains (`TRUSTED_SHOPIFY_DOMAINS`: `shopify.com`, `myshopify.io`, `myshopify.com`, `spin.dev`, `shop.dev`): [3](#0-2) [4](#0-3) 

but `begin_auth` never invokes `ShopValidator.sanitize!` (or `sanitize_shop_domain`) on `shop` before using it to build `auth_route`. This breaks the intended identity binding:

`shop == a value validated as a real *.myshopify.com (or other trusted) domain`

which the gem's own validator module was built to enforce, but does not enforce on this specific code path.

Concretely, an app built on this gem that takes `shop` from an unauthenticated source (e.g. a query string parameter on the login route, as shown as the documented usage pattern with `request.headers["Shop"]`) will pass whatever string the visitor supplies straight into `auth_base_uri`. Devin's mapping of the report's bug class ("value used for a sensitive operation but not checked against the value that should gate it") is: the report's oracle used the wrong reference price for a swap bound; here, the redirect target is built from a shop string that is never bound to the "is this really a Shopify domain" check the gem itself provides.

### Impact Explanation
`auth_route` embeds the app's `client_id`, requested `scope`, `redirect_uri`, and — critically — the freshly generated anti-CSRF `state` nonce: [5](#0-4) 

If `shop` is attacker-controlled and unsanitized, the app will redirect the victim's browser to `https://<attacker-domain>/admin/oauth/authorize?...&state=<nonce>&...`. This is a "forced OAuth completion" style primitive explicitly listed as a valid High-impact class in scope: the app discloses its `client_id` and issues a genuine `state` nonce (bound to a cookie the app sets for that exact nonce) to a domain the attacker controls, enabling the attacker to complete/redirect the flow, replay the nonce back to the app's own callback, or otherwise manipulate which "shop" the app associates its session-setup logic with before the HMAC-protected callback is ever reached.

### Likelihood Explanation
Likelihood is High for any app built directly on this gem's `begin_auth` following the documented pattern (`shop = request.headers["Shop"]` or an equivalent query param) without adding its own shop-domain validation, since:
- No secret or credential is required by the attacker — this is purely an unauthenticated redirect construction issue reachable by any internet user who can influence the `shop` value passed into `begin_auth`.
- The gem ships a validator (`ShopValidator`) for exactly this purpose, showing the maintainers recognize the risk class, but it is wired into `sanitize!`/`sanitize_shop_domain` only, not into `Oauth.begin_auth`.

### Recommendation
In `ShopifyAPI::Auth::Oauth.begin_auth`, call `ShopifyAPI::Utils::ShopValidator.sanitize!(shop)` (or `sanitize_shop_domain`) before using `shop` in `auth_base_uri`, raising `Errors::InvalidShopError` for any value that doesn't resolve to a trusted Shopify domain, mirroring the protection already implemented for `ShopifyAPI::Auth::TokenExchange`.

### Proof of Concept
1. Host app implements the documented pattern:
```ruby
def login
  shop = request.headers["Shop"] # attacker-influenced, e.g. via query param proxied into this header
  auth_response = ShopifyAPI::Auth::Oauth.begin_auth(shop: shop, redirect_path: "/auth/callback")
  cookies[auth_response[:cookie].name] = { value: auth_response[:cookie].value, ... }
  redirect_to auth_response[:auth_route]
end
```
2. Attacker sends a victim a link causing `shop` to be set to `evil.attacker.com`.
3. `begin_auth` builds `auth_route = "https://evil.attacker.com/admin/oauth/authorize?client_id=...&scope=...&redirect_uri=...&state=<nonce>&grant_options[]=..."` — verified directly from `auth_base_uri`'s unsanitized interpolation: [6](#0-5) 
4. Victim's browser is redirected there, disclosing `client_id`, `redirect_uri`, and the app-issued `state` nonce to the attacker-controlled host, while the app has already set a cookie binding that same `state` value for the eventual callback — enabling forced/attacker-influenced completion of the OAuth flow against the app's callback route.

### Citations

**File:** lib/shopify_api/auth/oauth.rb (L36-52)
```ruby
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

**File:** lib/shopify_api/utils/shop_validator.rb (L50-64)
```ruby
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
