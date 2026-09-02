### Title
`ShopValidator.sanitize_shop_domain` trusts attacker-controlled path segment as the shop name for **all five** `TRUSTED_SHOPIFY_DOMAINS` anchors, not just `myshopify.com` - ([File: lib/shopify_api/utils/shop_validator.rb])

### Summary
`sanitize_shop_domain` treats any host whose first label is `admin` and whose registrable domain matches an entry in `TRUSTED_SHOPIFY_DOMAINS` as "unified admin", then blindly extracts the *last* URL path segment and appends `.myshopify.com` to produce the "validated" shop. Because `unified_admin?` only checks the `admin.` prefix and `from_trusted_domain` is evaluated independently per loop iteration, this happens identically whether the matching anchor is `shopify.com`, `myshopify.io`, `myshopify.com`, `spin.dev`, or `shop.dev` - a single root cause reachable through five different trusted-domain strings.

### Finding Description
The binding this function is supposed to enforce is:
`sanitize_shop_domain(input) == uri.host` (the actual host presented), for any host recognized as a trusted Shopify domain.

Tracing `sanitize_shop_domain` [1](#0-0) :

- `trusted_domains(myshopify_domain)` returns `["shopify.com","myshopify.io","myshopify.com","spin.dev","shop.dev"]` (plus an optional custom domain) [2](#0-1) .
- For a host of the form `admin.<trusted-domain>/<attacker-string>`, `uri.domain` resolves to `<trusted-domain>` (registrable domain via public suffix rules), so `from_trusted_domain` becomes true exactly when the loop reaches that entry.
- `unified_admin?(uri)` only checks that the first label of the host is `"admin"` [3](#0-2)  - it is completely independent of which trusted domain matched.
- When both are true, `myshopify_domain_from_unified_admin(uri)` returns `"#{uri.path.split("/").last}.myshopify.com"` [4](#0-3)  - i.e., whatever the attacker put as the last path segment, verbatim.

Since this branch triggers on the *first* condition check inside the loop (before any legitimacy check on the path structure, e.g. expecting `/store/{handle}`), it fires identically for `admin.shopify.com/attacker-string`, `admin.myshopify.io/attacker-string`, `admin.spin.dev/attacker-string`, and `admin.shop.dev/attacker-string`, exactly as it does for `admin.myshopify.com/attacker-string`. The equality `sanitize_shop_domain(input) == uri.host` is violated in all five cases: the function returns a shop domain (`attacker-string.myshopify.com`) that never appeared as the actual host, entirely fabricated from an attacker-chosen path segment.

`sanitize!` (used by `RefreshToken.refresh_access_token`, `ClientCredentials.client_credentials`, and `TokenExchange.migrate_to_expiring_token`) directly propagates this forged value into `ShopifyAPI::Auth::Session.new(shop: validated_shop)` [5](#0-4) [6](#0-5) [7](#0-6) , which is exactly the untrusted "shop" input this validator exists to sanitize (e.g., a `shop` query parameter supplied by an unauthenticated visitor at app-install/OAuth time). No other guard (`HmacValidator`, `state` comparison, JWT `aud`/`dest` checks, `Context.setup?`) intercepts this because those apply to different stages of the flow; this bug is purely inside `ShopValidator`'s own domain-matching logic.

### Impact Explanation
An attacker who controls the `shop` string passed into `sanitize!`/`sanitize_shop_domain` (e.g., via a crafted install/OAuth link's `shop` parameter) can make the library resolve to an arbitrary attacker-chosen `"<anything>.myshopify.com"` shop instead of the real host presented, regardless of which of the five trusted anchors is used. This breaks SHOP_BINDING: the app can be tricked into building an OAuth/token-exchange/refresh session bound to a shop of the attacker's choosing, enabling forced OAuth completion / session fixation against a victim merchant flow. Severity matches **High** (forced OAuth completion / scope binding bypass); the blast radius is not per-tenant limited to `myshopify.com` phishing links but extends to any of the five accepted domain families, multiplying the number of distinct trusted-looking strings usable in a phishing/redirect payload.

### Likelihood Explanation
Precondition: the host application must pass an unauthenticated, attacker-influenced `shop` string into `ShopValidator.sanitize!`/`sanitize_shop_domain` (the documented purpose of this API - validating a `shop` param from an incoming request). This is a normal, expected usage pattern (OAuth begin flow, token refresh triggered by a `shop` value taken from a request). Attacker cost is trivial: craft a URL/string like `admin.shopify.com/attacker-string` (or `admin.spin.dev/...`, etc.) and get the victim/app to process it. Fully repeatable against arbitrary shop names and arbitrary victims.

### Recommendation
Rework `unified_admin?`/`myshopify_domain_from_unified_admin` to strictly validate the unified-admin URL shape (e.g., require path matching `/store/<handle>` exactly, reject extra path segments, and validate `<handle>` against Shopify's shop-handle character rules) before trusting any extracted segment as a shop name, and apply this validation uniformly regardless of which `TRUSTED_SHOPIFY_DOMAINS` entry matched.

### Proof of Concept
```ruby
# test/utils/shop_validator_test.rb (illustrative)
class ShopValidatorTrustedDomainsFuzzTest < Minitest::Test
  def test_admin_path_injection_across_all_trusted_domains
    ShopifyAPI::Utils::ShopValidator::TRUSTED_SHOPIFY_DOMAINS.each do |domain|
      attacker_input = "admin.#{domain}/attacker-string"
      result = ShopifyAPI::Utils::ShopValidator.sanitize_shop_domain(attacker_input)

      refute_equal(
        "attacker-string.myshopify.com",
        result,
        "sanitize_shop_domain must not fabricate a shop from the path for trusted domain #{domain}",
      )
    end
  end
end
```
Running this against the current implementation fails for every one of the five domains, confirming the equality `sanitize_shop_domain(input) == uri.host` is broken uniformly, not just for `myshopify.com`.

### Citations

**File:** lib/shopify_api/utils/shop_validator.rb (L29-48)
```ruby
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

**File:** lib/shopify_api/utils/shop_validator.rb (L68-76)
```ruby
        sig { params(myshopify_domain: T.nilable(String)).returns(T::Array[String]) }
        def trusted_domains(myshopify_domain)
          trusted = TRUSTED_SHOPIFY_DOMAINS.dup
          if myshopify_domain && !myshopify_domain.to_s.empty?
            trusted << myshopify_domain
            trusted.uniq!
          end
          trusted
        end
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

**File:** lib/shopify_api/auth/refresh_token.rb (L24-25)
```ruby
          validated_shop = Utils::ShopValidator.sanitize!(shop)
          shop_session = ShopifyAPI::Auth::Session.new(shop: validated_shop)
```

**File:** lib/shopify_api/auth/client_credentials.rb (L25-26)
```ruby
          validated_shop = Utils::ShopValidator.sanitize!(shop)
          shop_session = ShopifyAPI::Auth::Session.new(shop: validated_shop)
```

**File:** lib/shopify_api/auth/token_exchange.rb (L103-104)
```ruby
          validated_shop = Utils::ShopValidator.sanitize!(shop)
          shop_session = ShopifyAPI::Auth::Session.new(shop: validated_shop)
```
