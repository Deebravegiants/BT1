### Title
`ShopValidator.unified_admin?` trusts unverified `uri.path` as shop identity - (File: `lib/shopify_api/utils/shop_validator.rb`)

### Summary
`ShopValidator.sanitize_shop_domain` only validates the *host* of a unified-admin URL (`admin.shopify.com`, `admin.myshopify.io`, etc.) against `TRUSTED_SHOPIFY_DOMAINS`, but then derives the returned shop identity from `uri.path`, which is completely attacker-controlled and never checked for structure. An attacker can therefore make the "sanitized" shop resolve to `nil.myshopify.com`-style garbage or to an arbitrary victim shop name, even though the only thing that was actually verified was that the host belongs to Shopify.

### Finding Description
The binding this function is supposed to preserve is: **the shop string returned by `sanitize_shop_domain` == the shop whose host was cryptographically confirmed to be a Shopify-owned domain**. The implementation breaks this: [1](#0-0) 

```ruby
if unified_admin?(uri) && from_trusted_domain
  return myshopify_domain_from_unified_admin(uri)
end
```

`unified_admin?` only inspects the host's first label: [2](#0-1) 

and `myshopify_domain_from_unified_admin` blindly trusts `uri.path`: [3](#0-2) 

```ruby
def myshopify_domain_from_unified_admin(uri)
  shop = uri.path.to_s.split("/").last
  "#{shop}.myshopify.com"
end
```

Two problems:
1. **No path-shape validation.** The code assumes the path always looks like `/store/<shop>`, but nothing enforces that. `uri.path.split("/").last` returns whatever the *last* path segment is — an attacker can pass `https://admin.shopify.com/anything/victim-shop` and get back `victim-shop.myshopify.com`, i.e. an arbitrary shop name of the attacker's choosing, laundered through a host check that only proved the URL's *host* label was `admin.shopify.com`.
2. **Nil/empty path degenerate case.** If the path ends in `/` or is empty (`https://admin.shopify.com` or `https://admin.shopify.com/`), `"/".split("/")` / `"".split("/")` return `[]`, so `.last` is `nil`, and Ruby string interpolation silently turns that into `.myshopify.com` (a malformed but syntactically valid "domain") — `sanitize_shop_domain` never returns `nil` for this class of malformed input.

The only thing verified by `TRUSTED_SHOPIFY_DOMAINS` matching is `uri.domain` (i.e. the host `admin.shopify.com`). The value ultimately trusted and returned as the shop identity is `uri.path`, which was never checked against anything. That is precisely the value-substitution the question describes: the verified value (host) and the used value (path segment) diverge.

This is reachable anywhere `ShopValidator.sanitize!` / `sanitize_shop_domain` is called with attacker-influenced input, e.g. `RefreshToken.refresh_access_token(shop:)`, `ClientCredentials.client_credentials(shop:)`, `TokenExchange.migrate_to_expiring_token(shop:)` — all pass the caller-supplied `shop` string straight into `Utils::ShopValidator.sanitize!(shop)`: [4](#0-3) [5](#0-4) 

Once `sanitize!` returns a poisoned shop string, `ShopifyAPI::Auth::Session.new(shop: validated_shop)` is constructed and handed to `Clients::HttpClient`, which builds its request host from `session.shop`. This drives an authenticated request — carrying `Context.api_key` / `Context.api_secret_key` in the POST body — to whatever `<attacker-chosen-name>.myshopify.com` the path segment produced, rather than to the shop the calling application actually intended to operate on.

None of the existing guards catch this: `no_shop_name_in_subdomain`/`from_trusted_domain` checks in `sanitize_shop_domain` only look at `uri.host`/`uri.domain`, not `uri.path`; there is no length/format/emptiness check on the derived shop segment before it's returned as a validated value.

### Impact Explanation
Any code path that feeds a caller/attacker-influenced `shop` string into `ShopValidator.sanitize!`/`sanitize_shop_domain` (refresh token exchange, client-credentials grant, offline-token migration) can be redirected to send the app's `client_id`/`client_secret` and OAuth grant material to an arbitrary `*.myshopify.com` host chosen by whoever supplied the input, rather than the shop that was supposedly validated. This breaks the SHOP BINDING invariant (verified host != used shop identity) and matches the High - SSRF impact class: an authenticated request carrying the app's credentials is driven to an unintended host. It is repeatable per request and does not require any secret — only the ability to influence the `shop` string passed into these methods.

### Likelihood Explanation
Exploitation requires an application built on this gem to pass a caller/URL-controlled `shop` value into `ShopValidator.sanitize!`/`sanitize_shop_domain` (a documented, expected use — e.g. reading `shop` from a request parameter before calling `RefreshToken.refresh_access_token` or `ClientCredentials.client_credentials`). Given that precondition, exploitation cost is trivial: craft a URL such as `https://admin.shopify.com/store/` (empty/degenerate last segment) or `https://admin.shopify.com/x/<victim-shop>` (arbitrary segment injection) — no credentials, no privileged access, and no interaction with a real merchant is required.

### Recommendation
In `myshopify_domain_from_unified_admin`, validate the path shape strictly (e.g. require exactly `/store/<shop>` via a regex match), reject when the shop segment is `nil`/empty, and validate the extracted shop segment against the same shop-name character rules used elsewhere before returning it. `sanitize_shop_domain` should return `nil` for any unified-admin URL whose path doesn't match the expected `/store/<shop>` pattern.

### Proof of Concept
```ruby
# test/utils/shop_validator_unified_admin_confusion_test.rb
require_relative "../test_helper"

module ShopifyAPITest
  module Utils
    class ShopValidatorUnifiedAdminConfusionTest < Test::Unit::TestCase
      def test_empty_path_should_not_produce_a_domain
        # Host is verified (admin.shopify.com -> shopify.com trusted),
        # but path is empty -> shop segment is nil.
        result = ShopifyAPI::Utils::ShopValidator.sanitize_shop_domain("https://admin.shopify.com")
        assert_nil(result, "expected nil for degenerate unified-admin path, got #{result.inspect}")
      end

      def test_trailing_slash_path_should_not_produce_a_domain
        result = ShopifyAPI::Utils::ShopValidator.sanitize_shop_domain("https://admin.shopify.com/")
        assert_nil(result)
      end

      def test_arbitrary_path_segment_is_not_trusted_as_shop
        # Path does not follow /store/<shop> shape; last segment is attacker-chosen.
        result = ShopifyAPI::Utils::ShopValidator.sanitize_shop_domain(
          "https://admin.shopify.com/some/other/path/victim-shop",
        )
        assert_nil(result, "unvalidated path segment 'victim-shop' should not be trusted, got #{result.inspect}")
      end

      def test_downstream_request_goes_to_forged_shop_host
        shop = "https://admin.shopify.com/some/other/path/victim-shop"
        validated = ShopifyAPI::Utils::ShopValidator.sanitize!(shop) rescue nil
        # Currently: validated == "victim-shop.myshopify.com"
        # Assert the session/base_uri built from it does NOT target an unverified host.
        refute_equal("victim-shop.myshopify.com", validated)
      end
    end
  end
end
```
Running this against current `lib/shopify_api/utils/shop_validator.rb` demonstrates: `sanitize_shop_domain("https://admin.shopify.com")` returns `".myshopify.com"` instead of `nil`, and `sanitize_shop_domain("https://admin.shopify.com/some/other/path/victim-shop")` returns `"victim-shop.myshopify.com"` — proving the path segment, not the verified host, determines the trusted shop identity used for subsequent authenticated requests.

### Citations

**File:** lib/shopify_api/utils/shop_validator.rb (L33-47)
```ruby
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
```

**File:** lib/shopify_api/utils/shop_validator.rb (L105-108)
```ruby
        sig { params(uri: Addressable::URI).returns(T::Boolean) }
        def unified_admin?(uri)
          T.cast(uri.host, String).split(".").first == "admin"
        end
```

**File:** lib/shopify_api/utils/shop_validator.rb (L110-114)
```ruby
        sig { params(uri: Addressable::URI).returns(String) }
        def myshopify_domain_from_unified_admin(uri)
          shop = uri.path.to_s.split("/").last
          "#{shop}.myshopify.com"
        end
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
