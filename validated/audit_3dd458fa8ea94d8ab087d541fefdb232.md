### Title
`begin_auth` builds the OAuth `/admin/oauth/authorize` redirect from an unvalidated `shop` parameter, allowing a forced/attacker-steered OAuth flow - (File: `lib/shopify_api/auth/oauth.rb`)

### Summary
`ShopifyAPI::Auth::Oauth.begin_auth` accepts a caller-supplied `shop:` string and uses it, unsanitized, to build the destination host of the OAuth authorize redirect (`auth_base_uri(shop)` → `https://#{shop}/admin/oauth/authorize?...`). Unlike every other credential-issuing entry point in this gem (`ClientCredentials.client_credentials`, `RefreshToken.refresh_access_token`, `Clients::Graphql::Storefront#initialize`), which all call `Utils::ShopValidator.sanitize!(shop)` before using the value to build a session/host, `begin_auth` performs no such check. This mirrors the report's bug class: a value (`shop`) that drives a security-sensitive action (choosing the host that will receive the OAuth authorization request and subsequently issue the authorization `code`/`state` round-trip) is not bound/validated the way parallel code paths in the same codebase require.

### Finding Description
`begin_auth` is documented as the first step of the Authorization Code Grant flow: an app route (e.g. `/login?shop=...`) calls it with a `shop` value that in practice comes from an unauthenticated request (a query parameter on the merchant-installation URL), before any Shopify HMAC exists to authenticate the value. [1](#0-0) 

`auth_base_uri` builds the redirect target directly from this raw `shop` string with no domain validation: [2](#0-1) 

Compare this with `RefreshToken.refresh_access_token` and `ClientCredentials.client_credentials`, both of which call `Utils::ShopValidator.sanitize!(shop)` before constructing the session/target host, specifically to reject non-Shopify domains such as `attacker.example` or `myshopify.com.evil.com`: [3](#0-2) [4](#0-3) 

The `ShopValidator` module exists precisely to enforce the equality "the shop value used to build a request host" == "a value confirmed to be `*.myshopify.com`/`*.myshopify.io`/`*.spin.dev`/etc.", and its test suite explicitly documents attacker-domain rejection scenarios (`attacker.example`, `evil.com`, `myshopify.com.evil.com`, `test-shop.notmyshopify.com`) as the threat model it defends against: [5](#0-4) 

`begin_auth` breaks this equality: the redirect host is taken from the caller-supplied `shop` with no equivalent check, so if the host application forwards a raw, attacker-controlled query parameter into `begin_auth` (a common integration pattern, since the documented `shop` input is simply "A Shopify domain name"), the resulting `auth_route` can point the merchant's browser to an attacker-chosen host instead of a genuine `*.myshopify.com` shop. [6](#0-5) 

### Impact Explanation
The consequence is a forced/steered OAuth flow: the state nonce, `client_id`, `scope`, and `redirect_uri` are sent (via browser redirect) to a host chosen by the attacker rather than to Shopify. Because `begin_auth`'s only defense-in-depth against a malformed `shop` value is absent here (while present in sibling methods `ClientCredentials.client_credentials` and `RefreshToken.refresh_access_token`), this is a session-fixation/forced-OAuth-completion class issue — explicitly one of the qualifying High-severity impacts. It does not by itself leak `client_secret` (that is only sent in the callback's `access_token` POST, gated by the shop value that Shopify HMAC-signs on legitimate callbacks), so the impact is bounded to the initiation step, but it still breaks the same "field acted on but not validated against the trusted-domain allowlist used elsewhere in this gem" invariant that the report highlights for `PuttyV2.sol`'s missing strike check.

### Likelihood Explanation
Exploitability depends entirely on whether the host application passes an unvalidated, request-derived `shop` value into `begin_auth` — which the gem's own documentation encourages by describing `shop` simply as "A Shopify domain name" with no mention of required pre-validation, and by not performing the check itself (unlike its sibling OAuth-adjacent methods). Given that `Utils::ShopValidator` was added specifically to close this gap for other entry points, its absence in `begin_auth` is a real, code-level inconsistency and not merely a theoretical host-application misuse scenario.

### Recommendation
Call `Utils::ShopValidator.sanitize!(shop)` (or `sanitize_shop_domain`) inside `begin_auth` before constructing `auth_base_uri(shop)`, mirroring the pattern already used in `ClientCredentials.client_credentials` and `RefreshToken.refresh_access_token`, so the OAuth authorize redirect can only ever target a trusted Shopify domain regardless of what the host application passes in.

### Proof of Concept
1. Host application exposes `/login?shop=<value>` and calls `ShopifyAPI::Auth::Oauth.begin_auth(shop: params[:shop], redirect_path: "/auth/callback")` without validating `shop` first (the gem provides no built-in requirement to do so, and does not validate internally).
2. Attacker sends a victim merchant admin/staff a link to `/login?shop=attacker-controlled.example`.
3. `begin_auth` computes `auth_route = "https://attacker-controlled.example/admin/oauth/authorize?client_id=...&scope=...&redirect_uri=...&state=<nonce>"` via `auth_base_uri`: [7](#0-6) 
4. The victim's browser is redirected to the attacker's host carrying the app's `client_id`, requested `scope`, `redirect_uri`, and the session's `state` nonce, enabling the attacker to steer or fixate the subsequent OAuth completion instead of the flow terminating at a genuine Shopify shop.

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

**File:** lib/shopify_api/auth/refresh_token.rb (L18-26)
```ruby
        def refresh_access_token(shop:, refresh_token:)
          unless ShopifyAPI::Context.setup?
            raise ShopifyAPI::Errors::ContextNotSetupError,
              "ShopifyAPI::Context not setup, please call ShopifyAPI::Context.setup"
          end

          validated_shop = Utils::ShopValidator.sanitize!(shop)
          shop_session = ShopifyAPI::Auth::Session.new(shop: validated_shop)
          body = {
```

**File:** lib/shopify_api/utils/shop_validator.rb (L20-48)
```ruby
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
```

**File:** test/utils/shop_validator_test.rb (L38-66)
```ruby
      def test_rejects_attacker_controlled_domain
        assert_raises(ShopifyAPI::Errors::InvalidShopError) do
          ShopifyAPI::Utils::ShopValidator.sanitize!("attacker.example")
        end
      end

      def test_rejects_empty_string
        assert_raises(ShopifyAPI::Errors::InvalidShopError) do
          ShopifyAPI::Utils::ShopValidator.sanitize!("")
        end
      end

      def test_rejects_non_shopify_domain
        assert_raises(ShopifyAPI::Errors::InvalidShopError) do
          ShopifyAPI::Utils::ShopValidator.sanitize!("evil.com")
        end
      end

      def test_rejects_shopify_suffix_as_subdomain_of_attacker
        assert_raises(ShopifyAPI::Errors::InvalidShopError) do
          ShopifyAPI::Utils::ShopValidator.sanitize!("myshopify.com.evil.com")
        end
      end

      def test_rejects_similar_looking_domain
        assert_raises(ShopifyAPI::Errors::InvalidShopError) do
          ShopifyAPI::Utils::ShopValidator.sanitize!("test-shop.notmyshopify.com")
        end
      end
```

**File:** docs/usage/oauth.md (L148-154)
```markdown
#### Input
| Parameter      | Type                   | Required? | Default Value | Notes                                                                                                       |
| -------------- | ---------------------- | :-------: | :-----------: | ----------------------------------------------------------------------------------------------------------- |
| `shop`          | `String`               |    Yes    |       -       | A Shopify domain name in the form `{exampleshop}.myshopify.com`.                                            |
| `redirect_path` | `String`               |    Yes    |       -       | The redirect path used for callback with a leading `/`. The route should be allowed under the app settings. |
| `is_online`     | `Boolean`              |    No     |    `true`     | `true` if the session is online and `false` otherwise.                                                      |
| `scope_override`| `String` or `[String]` |    No     |     `nil`     |  `nil` will request access scopes configured in `ShopifyAPI::Context.setup` during OAuth flow. Modify this to override the access scopes being requested. Accepts array or string: "read_orders, write_products" or ["read_orders", "write_products"]. |
```
