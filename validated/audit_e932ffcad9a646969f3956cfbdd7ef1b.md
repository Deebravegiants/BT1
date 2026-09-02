Confirmed: `ShopValidator.sanitize!`/`sanitize_shop_domain` is used in `lib/shopify_api/auth/token_exchange.rb`, `lib/shopify_api/auth/client_credentials.rb`, `lib/shopify_api/auth/refresh_token.rb`, and `lib/shopify_api/clients/graphql/storefront.rb`, but is **not** called anywhere in `lib/shopify_api/auth/oauth.rb`. `Oauth.begin_auth` takes a caller-supplied `shop:` string and passes it directly into `auth_base_uri(shop)` (`lib/shopify_api/auth/oauth.rb:22,49,117-128`), building `https://#{shop}/admin/oauth/authorize?...` with no validation that `shop` is a real `*.myshopify.com`/trusted domain.

### Title
OAuth `begin_auth` fails to validate the `shop` domain before redirecting, enabling forced/spoofed OAuth authorization - (File: lib/shopify_api/auth/oauth.rb)

### Summary
`ShopifyAPI::Auth::Oauth.begin_auth` builds the OAuth authorization redirect URL by directly interpolating the caller-supplied `shop` parameter into a URL host, without ever passing it through `Utils::ShopValidator.sanitize!`, which every other credential-flow entry point in the gem (`token_exchange.rb`, `client_credentials.rb`, `refresh_token.rb`) does use.

### Finding Description
`begin_auth` constructs the authorization redirect as: [1](#0-0) 
via `auth_base_uri(shop)`: [2](#0-1) 

`shop` here is whatever value the host application forwards from the incoming request (typically a `?shop=` query parameter on the app's login route). The gem never enforces that this value equals a trusted `myshopify.com`/`myshopify.io`/`shop.dev` domain, unlike the parallel OAuth-adjacent flows which do enforce it, e.g.: [3](#0-2) 

The identity binding that should hold is: `shop parameter used to build the OAuth authorize redirect == a shop domain within Shopify's trusted domain set`. Because `begin_auth` never checks this, the equality is broken — any string can be used to build `https://<shop>/admin/oauth/authorize?...`, redirecting the merchant's browser to an attacker-controlled host that mimics the Shopify OAuth grant screen.

This is the classic case the report's "subtraction might revert" bug class generalizes to: one code path (`token_exchange.rb`/`client_credentials.rb`/`refresh_token.rb`) enforces the invariant, but the counterpart entry point (`begin_auth`, the very first step of the OAuth flow) does not, so the overall protocol is inconsistent — the check exists in the codebase but is not applied uniformly across the code paths that need it.

### Impact Explanation
If the host application does not itself sanitize the `shop` value before calling `begin_auth` (which the library's own docs/examples largely delegate to callers, and which the gem does for every other flow), an attacker can supply `shop=attacker-controlled-host` and cause the merchant's browser to be redirected there instead of to Shopify. Combined with the `state` cookie set by `begin_auth`, this enables a forced/spoofed OAuth completion scenario: the victim is sent to an attacker page instead of Shopify, and the attacker can harvest data or trick the merchant, or exploit downstream apps that trust the returned `shop` value at the callback step. This matches the "session fixation or forced OAuth completion" High-impact category.

### Likelihood Explanation
Likelihood depends on the host application's own input handling — if the host app already validates the `shop` query parameter itself before invoking `begin_auth`, this is not exploitable. However, since the gem provides `ShopValidator` specifically for this purpose and applies it consistently in every other OAuth-adjacent flow, its omission in `begin_auth` is the one inconsistent gap, and a caller reasonably relying on the library to be internally consistent (i.e., assuming `begin_auth` performs the same validation `token_exchange`/`client_credentials` perform) would be exposed.

### Recommendation
Call `Utils::ShopValidator.sanitize!(shop)` (or `sanitize_shop_domain`) at the top of `begin_auth` before constructing `auth_base_uri`, raising `Errors::InvalidShopError` for untrusted domains, mirroring the pattern already used in `lib/shopify_api/auth/token_exchange.rb`, `lib/shopify_api/auth/client_credentials.rb`, and `lib/shopify_api/auth/refresh_token.rb`.

### Proof of Concept
1. A host application built on this gem exposes a login route that calls `ShopifyAPI::Auth::Oauth.begin_auth(shop: params[:shop], redirect_path: "/auth/callback")` without independently validating `params[:shop]` (reasonable, since the gem exposes `ShopValidator` for exactly this purpose but doesn't apply it here).
2. Attacker sends the victim merchant a link to the app's login route with `?shop=attacker.example`.
3. `begin_auth` builds `auth_route = "https://attacker.example/admin/oauth/authorize?client_id=...&state=...&redirect_uri=..."` [4](#0-3)  and sets the `state` cookie, then the app redirects the victim's browser there.
4. The victim's browser is sent to the attacker's host with the app's `client_id`, `state`, and `redirect_uri` in the query string, allowing the attacker to harvest/replay them or serve a spoofed consent page, defeating the purpose of the state/HMAC protections applied later in `validate_auth_callback`.

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
