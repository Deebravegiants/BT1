## Finding

### Title
SSRF via unsanitized `shop` parameter in `Oauth.begin_auth` allows OAuth flow to be directed to an attacker-controlled host with the app's `client_id` and scope - (File: `lib/shopify_api/auth/oauth.rb`)

### Summary
`ShopifyAPI::Auth::ClientCredentials.client_credentials` and `ShopifyAPI::Auth::TokenExchange`/`RefreshToken` all call `Utils::ShopValidator.sanitize!(shop)` before using the caller-supplied `shop` value to build a request host, ensuring the domain belongs to `TRUSTED_SHOPIFY_DOMAINS`. `ShopifyAPI::Auth::Oauth.begin_auth`, however, takes the `shop:` argument directly (unauthenticated at this point in the flow — this is literally the entry point of OAuth, so no session or HMAC exists yet) and passes it straight into `auth_base_uri(shop)`, which builds `"https://#{shop}/admin"` with zero validation against `ShopValidator`.

### Finding Description
Compare the binding that should hold: `shop` used to build the authorize-redirect host == a value drawn from `Utils::ShopValidator::TRUSTED_SHOPIFY_DOMAINS`.

- In `lib/shopify_api/auth/client_credentials.rb:25`, `shop` is passed through `Utils::ShopValidator.sanitize!(shop)` before being used anywhere.
- In `lib/shopify_api/auth/oauth.rb:22-52` (`begin_auth`) and `lib/shopify_api/auth/oauth.rb:117-128` (`auth_base_uri`), the `shop` argument is used verbatim to construct `"https://#{shop}/admin"`, with no call to `Utils::ShopValidator` anywhere in the file. [1](#0-0) [2](#0-1) 

The gem's own docs instruct integrators to source this value directly from an inbound, unauthenticated request header (`request.headers["Shop"]`), reinforcing that `begin_auth`'s `shop` parameter is expected to be attacker-influenced at this stage of the flow: [3](#0-2) 

Because `auth_base_uri` performs no allow-list check, an attacker who controls the `shop` value passed into `begin_auth` (e.g., because the host application echoes a query parameter or header into this call, as the documented example does) can make the gem issue an outbound-influencing redirect URL whose host is entirely attacker-controlled, e.g. `shop = "evil.attacker.com"` → `auth_route = "https://evil.attacker.com/admin/oauth/authorize?client_id=<app client_id>&scope=<app scopes>&redirect_uri=<app host>/auth/callback&state=<nonce>"`. This leaks the app's `client_id`, requested `scope`, and legitimate `redirect_uri`/callback path to a third-party host chosen by the attacker, and can be used to construct a convincing phishing page that captures the OAuth `state` nonce and drives the victim through a forced/attacker-initiated OAuth completion against the real Shopify endpoint of the attacker's choosing (or simply harvest the nonce/cookie pair to attempt to force-complete an OAuth grant later). This directly parallels the reported bug class: an identity-binding value (the trusted-domain host) is enforced in some code paths (`ClientCredentials`, `TokenExchange`, `RefreshToken`) but not in this one, the same way `addToPosition()` skipped a check applied everywhere else in the original report.

Contrast this with the deliberate design of `ShopValidator`, whose entire purpose is exactly to prevent this class of bug for shop-domain inputs (verified via dedicated tests): [4](#0-3) [5](#0-4) 

### Impact Explanation
This is High severity per the accepted impact list: SSRF-style redirect carrying the app's credentials/identity (`client_id`, `scope`, `redirect_uri`) to an attacker-chosen host, and it can be leveraged to set up a forced/incomplete OAuth completion or phishing flow — both explicitly listed as in-scope High impacts. It does not require any privileged credential, TLS interception, or social engineering beyond controlling the `shop` value the host app passes through (which the gem's own documented usage pattern takes from an unauthenticated inbound header).

### Likelihood Explanation
Likelihood is High for any app that follows the gem's documented pattern of forwarding request-derived data (header/param) into `begin_auth`, since `ShopValidator` exists specifically to guard this and is used everywhere else in the OAuth/token-exchange code paths but is missing here.

### Recommendation
In `lib/shopify_api/auth/oauth.rb`, sanitize the `shop` parameter through `Utils::ShopValidator.sanitize!(shop)` at the top of `begin_auth` (and ideally `auth_base_uri`) before using it to construct `auth_base_uri`, mirroring the pattern already used in `client_credentials.rb`, `token_exchange.rb`, and `refresh_token.rb`.

### Proof of Concept
```ruby
ShopifyAPI::Context.setup(api_key: "app_key", api_secret_key: "app_secret", host_name: "myapp.example.com", scope: "read_orders")

result = ShopifyAPI::Auth::Oauth.begin_auth(shop: "evil.attacker.com", redirect_path: "/auth/callback")
result[:auth_route]
# => "https://evil.attacker.com/admin/oauth/authorize?client_id=app_key&scope=read_orders&redirect_uri=https://myapp.example.com/auth/callback&state=<15-char nonce>&grant_options%5B%5D=per-user"
```
No exception is raised and no domain check occurs, unlike the equivalent call path through `ShopifyAPI::Auth::ClientCredentials.client_credentials(shop: "evil.attacker.com")`, which raises `ShopifyAPI::Errors::InvalidShopError` via `Utils::ShopValidator.sanitize!`.

### Citations

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

**File:** lib/shopify_api/auth/client_credentials.rb (L19-26)
```ruby
        def client_credentials(shop:)
          unless ShopifyAPI::Context.setup?
            raise ShopifyAPI::Errors::ContextNotSetupError,
              "ShopifyAPI::Context not setup, please call ShopifyAPI::Context.setup"
          end

          validated_shop = Utils::ShopValidator.sanitize!(shop)
          shop_session = ShopifyAPI::Auth::Session.new(shop: validated_shop)
```

**File:** docs/usage/oauth.md (L181-185)
```markdown
  def login
    shop = request.headers["Shop"]

    # Builds the authorization URL route to redirect the user to
    auth_response = ShopifyAPI::Auth::Oauth.begin_auth(shop: domain, redirect_path: "/auth/callback")
```

**File:** lib/shopify_api/utils/shop_validator.rb (L1-18)
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
