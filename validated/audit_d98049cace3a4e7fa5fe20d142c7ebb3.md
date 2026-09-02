### Title
Unvalidated `shop` parameter in `Oauth.begin_auth` enables forced OAuth completion via attacker-controlled redirect host - (File: `lib/shopify_api/auth/oauth.rb`)

### Summary
`ShopifyAPI::Auth::Oauth.begin_auth` builds the OAuth authorization redirect URL directly from the caller-supplied `shop` string without ever passing it through `ShopifyAPI::Utils::ShopValidator`, unlike every other entry point in the gem that accepts a `shop` parameter.

### Finding Description
`Oauth.begin_auth` takes `shop:` directly from the caller and passes it straight into `auth_base_uri(shop)`, which returns `"https://#{shop}/admin"` with no domain validation: [1](#0-0) [2](#0-1) 

That `shop` string is used to construct the full authorization URL, which also embeds the CSRF `state` nonce that is simultaneously written into the victim's browser via `SessionCookie`: [3](#0-2) 

By contrast, every other place in the gem that accepts an untrusted `shop` value normalizes/validates it against `ShopifyAPI::Utils::ShopValidator::TRUSTED_SHOPIFY_DOMAINS` (`shopify.com`, `myshopify.io`, `myshopify.com`, `spin.dev`, `shop.dev`) before it is used to build any URL that carries credentials or session-binding data — this is confirmed in `lib/shopify_api/auth/token_exchange.rb`, `lib/shopify_api/auth/client_credentials.rb`, and `lib/shopify_api/auth/refresh_token.rb`, all of which reference `ShopValidator`. `Oauth.begin_auth` and `Oauth.validate_auth_callback` in `lib/shopify_api/auth/oauth.rb` do not call `ShopValidator` at all — confirmed by `grep_search` showing zero matches for `ShopValidator` in that file.

This is the exact identity-binding gap described in the rules: the trust decision "is this a real Shopify host" is enforced for some `shop`-consuming flows (`ShopValidator.sanitize!`) but not for the flow that actually redirects the user's browser and issues a CSRF-binding cookie (`begin_auth`). The equality that should hold — `host redirected to == a domain in ShopValidator::TRUSTED_SHOPIFY_DOMAINS` — is not checked here even though the sibling code paths enforce it. [4](#0-3) 

### Impact Explanation
Because `begin_auth`'s host-application-facing `shop` parameter typically originates from an unauthenticated request (e.g., a Shopify app install/login link like `/auth?shop=...`), an attacker can supply an arbitrary non-Shopify domain. The gem will then construct an authorization redirect and CSRF `state` cookie pointed at that attacker-controlled host instead of a genuine `*.myshopify.com` endpoint. This is a "forced OAuth completion" style primitive: the app sets a CSRF-binding cookie on the victim's browser and redirects them off-platform under the app's own trust context, undermining the state-nonce protection that `validate_auth_callback` later relies on (`state == auth_query.state`), since the flow never had to originate from Shopify at all.

### Likelihood Explanation
No credentials, tokens, or `api_secret_key` access are required — the attacker only needs to control the `shop` value passed to the host application's OAuth-initiation endpoint (a standard unauthenticated parameter in this flow), and the gem itself performs no domain check before redirecting.

### Recommendation
Call `ShopifyAPI::Utils::ShopValidator.sanitize!(shop, myshopify_domain: ...)` on the `shop` parameter inside `Oauth.begin_auth` (and ideally re-validate in `validate_auth_callback`) before it is used to build `auth_base_uri`, consistent with `token_exchange.rb`, `client_credentials.rb`, and `refresh_token.rb`.

### Proof of Concept
1. Host application exposes `/auth?shop=<value>` which calls `ShopifyAPI::Auth::Oauth.begin_auth(shop: params[:shop], redirect_path: "/auth/callback")`.
2. Attacker sends a victim merchant a link with `shop=attacker.example`.
3. `auth_base_uri("attacker.example")` returns `"https://attacker.example/admin"` (no domain check), and `begin_auth` returns `auth_route = "https://attacker.example/admin/oauth/authorize?client_id=...&scope=...&redirect_uri=...&state=<nonce>"` plus a `SessionCookie` binding `<nonce>` to the victim's browser. [5](#0-4) 
4. The victim's browser is redirected to the attacker's server with the app's `client_id`, requested `scope`, and CSRF `state` — none of which required Shopify's involvement, because the gem never verified `shop` was a Shopify-trusted domain.

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
