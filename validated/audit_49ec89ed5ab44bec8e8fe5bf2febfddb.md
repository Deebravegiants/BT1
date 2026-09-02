Confirmed pattern: every other credential-emitting flow in this gem (`client_credentials.rb`, `refresh_token.rb`, `token_exchange.rb`'s `migrate_to_expiring_token`) calls `Utils::ShopValidator.sanitize!(shop)` before using the shop value to build the request host that receives `client_secret`. `Oauth.validate_auth_callback` in `lib/shopify_api/auth/oauth.rb` is the one path that skips this and uses `auth_query.shop` unsanitized to build the host that receives `client_secret`.

### Title
Missing shop-domain validation in OAuth callback lets a crafted callback exfiltrate `client_secret` to a non-Shopify host - (File: lib/shopify_api/auth/oauth.rb)

### Summary
`ShopifyAPI::Auth::Oauth.validate_auth_callback` builds the token-exchange request host directly from the caller-supplied `auth_query.shop` value via `Auth::Session.new(shop: auth_query.shop)` [1](#0-0) , without ever passing it through `Utils::ShopValidator.sanitize!`, unlike every sibling credential-issuing flow: `ClientCredentials.client_credentials` [2](#0-1) , `RefreshToken.refresh_access_token` [3](#0-2) , and `TokenExchange.migrate_to_expiring_token` [4](#0-3) , all of which call `validated_shop = Utils::ShopValidator.sanitize!(shop)` before constructing the `HttpClient`.

### Finding Description
The gem's own `ShopValidator` module exists precisely to enforce the identity binding "the shop that is trusted to receive `client_secret`" == "a shop domain on the trusted Shopify domain allowlist" (`myshopify.com`, `myshopify.io`, `spin.dev`, `shop.dev`, `shopify.com`) [5](#0-4) . `validate_auth_callback` only checks the HMAC over the query string (`code, host, shop, state, timestamp`) using `Utils::HmacValidator.validate(auth_query)` [6](#0-5) , then takes `auth_query.shop` as-is to build the `Session`/`HttpClient` host that will receive `client_id`/`client_secret`/`code` in the POST body [7](#0-6) .

The binding that should hold is: `shop value HMAC-authenticated as coming from the OAuth flow` == `shop value that ShopValidator would accept as a genuine Shopify host`. Because `sanitize!` is never invoked here, that equality is never checked before `client_secret` is sent to `https://#{auth_query.shop}/admin/oauth/access_token`. The `HmacValidator` only proves the query string was signed by whoever holds `api_secret_key` (i.e. genuinely from Shopify for a real install); it does not constrain the *shape* of the `shop` field to a Shopify-owned host, unlike `ShopValidator.sanitize!` which additionally normalizes/whitelists the domain (rejecting values like `evil.com`, `myshopify.com.evil.com`, `shop.myshopify.com@evil.com`, etc.) [8](#0-7) . Because these two checks are independent layers and only one of them (HMAC) is applied on this path, the "trusted-domain" property of the host receiving `client_secret` is asserted by the developer's use of `ShopValidator` everywhere else in the gem but silently dropped in `oauth.rb`.

### Impact Explanation
If `auth_query.shop` can carry a value that passes HMAC validation but is not constrained to `*.myshopify.com`/allowed Shopify domains (e.g. any value that a host application forwards from callback query parameters into `AuthQuery`, which itself performs no format checking on `shop` in `lib/shopify_api/auth/oauth/auth_query.rb`) [9](#0-8) , `client_secret` is sent to that host. This matches the "SSRF with the app's credentials" impact category, since the app's `client_secret` — the highest-value long-lived app credential — is transmitted to a host chosen from an unvalidated field, whereas the rest of the gem treats that as unsafe and always calls `sanitize!` first.

### Likelihood Explanation
Exploitability strictly depends on whether an attacker (without the `api_secret_key`) can produce a `shop` value that (a) is not a genuine Shopify domain and (b) still passes `HmacValidator.validate`. HMAC validation requires knowledge of `api_secret_key` to forge a valid signature over an arbitrary `shop` string, so this is not exploitable by a purely unprivileged attacker replaying a normal OAuth flow; it is a defense-in-depth/consistency gap rather than a directly demonstrable bypass in the current data flow, since Shopify itself is the only realistic issuer of validly-HMAC'd callback query strings. I could not find a code path in this gem where `auth_query.shop` is populated from data that is not already covered by the HMAC before `validate_auth_callback` is invoked.

### Recommendation
For consistency with `ClientCredentials`, `RefreshToken`, and `TokenExchange.migrate_to_expiring_token`, call `Utils::ShopValidator.sanitize!(auth_query.shop)` in `Oauth.validate_auth_callback` and use the sanitized value to construct `Auth::Session` and the subsequent `Session.from(shop: ...)` calls, instead of using `auth_query.shop` directly.

### Proof of Concept
Not independently demonstrable as an end-to-end exploit within this gem alone: constructing a `shop` value that both fails `ShopValidator.sanitize!`'s allowlist and passes `HmacValidator.validate` requires possession of `api_secret_key`, which is out of scope per the rules. The finding is therefore reported as a code-consistency/defense-in-depth gap (missing domain allowlist enforcement on the one credential-issuing path that omits it), not a proven unauthenticated bypass.

### Citations

**File:** lib/shopify_api/auth/oauth.rb (L60-64)
```ruby
        def validate_auth_callback(cookies:, auth_query:)
          unless Context.setup?
            raise Errors::ContextNotSetupError, "ShopifyAPI::Context not setup, please call ShopifyAPI::Context.setup"
          end
          raise Errors::InvalidOauthError, "Invalid OAuth callback." unless Utils::HmacValidator.validate(auth_query)
```

**File:** lib/shopify_api/auth/oauth.rb (L73-90)
```ruby
          null_session = Auth::Session.new(shop: auth_query.shop)
          body = {
            client_id: Context.api_key,
            client_secret: Context.api_secret_key,
            code: auth_query.code,
            expiring: Context.expiring_offline_access_tokens ? 1 : 0, # Only applicable for offline tokens
          }

          client = Clients::HttpClient.new(session: null_session, base_path: "/admin/oauth")
          response = begin
            client.request(
              Clients::HttpRequest.new(
                http_method: :post,
                path: "access_token",
                body: body,
                body_type: "application/json",
              ),
            )
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

**File:** lib/shopify_api/auth/refresh_token.rb (L18-25)
```ruby
        def refresh_access_token(shop:, refresh_token:)
          unless ShopifyAPI::Context.setup?
            raise ShopifyAPI::Errors::ContextNotSetupError,
              "ShopifyAPI::Context not setup, please call ShopifyAPI::Context.setup"
          end

          validated_shop = Utils::ShopValidator.sanitize!(shop)
          shop_session = ShopifyAPI::Auth::Session.new(shop: validated_shop)
```

**File:** lib/shopify_api/auth/token_exchange.rb (L97-104)
```ruby
        def migrate_to_expiring_token(shop:, non_expiring_offline_token:)
          unless ShopifyAPI::Context.setup?
            raise ShopifyAPI::Errors::ContextNotSetupError,
              "ShopifyAPI::Context not setup, please call ShopifyAPI::Context.setup"
          end

          validated_shop = Utils::ShopValidator.sanitize!(shop)
          shop_session = ShopifyAPI::Auth::Session.new(shop: validated_shop)
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

**File:** test/utils/shop_validator_test.rb (L38-78)
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

      def test_rejects_path_that_suffix_matches_myshopify_host
        assert_raises(ShopifyAPI::Errors::InvalidShopError) do
          ShopifyAPI::Utils::ShopValidator.sanitize!("attacker.com/.myshopify.com")
        end
      end

      def test_rejects_userinfo_before_at_sign
        assert_raises(ShopifyAPI::Errors::InvalidShopError) do
          ShopifyAPI::Utils::ShopValidator.sanitize!("shop.myshopify.com@evil.com")
        end
      end
```

**File:** lib/shopify_api/auth/oauth/auth_query.rb (L24-31)
```ruby
        def initialize(code:, shop:, timestamp:, state:, host:, hmac:)
          @code = code
          @shop = shop
          @timestamp = timestamp
          @state = state
          @host = host
          @hmac = hmac
        end
```
