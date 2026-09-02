### Title
`ShopValidator.sanitize!` returns a malformed empty-label `.myshopify.com` host that `HttpClient` uses unvalidated as `@base_uri`, breaking the "genuine single-shop subdomain" guarantee - ([File: lib/shopify_api/utils/shop_validator.rb])

### Summary
`ShopValidator.myshopify_domain_from_unified_admin` builds the sanitized shop by interpolating `uri.path.to_s.split("/").last` into a string; when the unified-admin URL has no path segment, `.last` is `nil`, and `"#{nil}.myshopify.com"` evaluates to the literal string `".myshopify.com"` (empty leftmost label). `sanitize!` only rejects `nil`/empty strings, so this 14-character malformed host passes validation and is stored as `session.shop`. `HttpClient#initialize` builds `@base_uri = "https://#{session.shop}"` with no further checks, so `HTTParty` is instructed to send the request - including any `X-Shopify-Access-Token` already on the session - to `https://.myshopify.com`.

### Finding Description
**Binding (as stated):** `host(X-Shopify-Access-Token destination) == host accepted by ShopValidator as a genuine single-shop myshopify.com/shopify.com subdomain`.

**Trace:**
- `ShopValidator.sanitize_shop_domain` (`lib/shopify_api/utils/shop_validator.rb:29-48`) parses `shop_domain` via `uri_from_shop_domain`. For input `"https://admin.shopify.com"` (no `/store/<shop>` path), `Addressable::URI#path` is `""`.
- `unified_admin?(uri)` is true (`host.split(".").first == "admin"`), and `from_trusted_domain` is true because `uri.domain == "shopify.com"`, which is in `TRUSTED_SHOPIFY_DOMAINS`. This triggers `myshopify_domain_from_unified_admin(uri)` at [1](#0-0) .
- `myshopify_domain_from_unified_admin` computes `shop = uri.path.to_s.split("/").last`. For an empty path, `"".split("/")` is `[]`, so `.last` is `nil`, and Ruby interpolation of `nil` produces `""`, yielding the literal host `".myshopify.com"` [2](#0-1) .
- `sanitize!` only raises when the result is `nil` or an empty string; `".myshopify.com"` is neither, so it is returned as the "validated" shop [3](#0-2) .
- This validated (but malformed) shop is directly used to build a `Session` and passed into `HttpClient.new` in every real call site that guards `shop` with `sanitize!`: `Auth::ClientCredentials.client_credentials` [4](#0-3) , `Auth::RefreshToken.refresh_access_token` [5](#0-4) , `Auth::TokenExchange.migrate_to_expiring_token` [6](#0-5) , and `Clients::Graphql::Storefront#initialize` [7](#0-6) .
- `HttpClient#initialize` builds `@base_uri = "https://#{api_host || session.shop}"` (i.e. `"https://.myshopify.com"`) with no additional validation of `session.shop`, and attaches `X-Shopify-Access-Token` to `@headers` whenever `session.access_token` is present [8](#0-7) . `#request` then dispatches via `HTTParty.send(..., parsed_uri.to_s, headers: headers, ...)` with no host allow-listing [9](#0-8) .

**Attacker path:** an app that (following common Shopify integration patterns) forwards a user-supplied `shop` parameter into `client_credentials(shop:)`, `refresh_access_token(shop:)`, or `migrate_to_expiring_token(shop:)` is reachable by an unauthenticated attacker who supplies `shop = "https://admin.shopify.com"` (or any unified-admin URL lacking a `/store/<name>` path segment). The library accepts this and stores `".myshopify.com"` as the session's shop. Any subsequent `Session` built from this flow (e.g., via `Session.from(shop: validated_shop, ...)`) retains this malformed shop, and if that session is later reused for authenticated Admin API calls through `HttpClient`, the `X-Shopify-Access-Token` header would be attached to a request targeting `https://.myshopify.com`.

**Why guards fail:** `sanitize!`'s only failure condition is `nil`/empty string, not "is this a syntactically valid, genuine single-label myshopify.com host" - it never re-validates the *result* of `myshopify_domain_from_unified_admin` against `TRUSTED_SHOPIFY_DOMAINS` or checks for empty labels. `HttpClient` performs zero validation of `session.shop` and trusts whatever `ShopValidator` returned.

### Impact Explanation
This breaks `ShopValidator`'s own contract: the returned host is not a "genuine single-shop myshopify.com subdomain" as its error message and design promise. However, `".myshopify.com"` (empty leading label) is not a domain an attacker can register or receive traffic on - it is a malformed variant of Shopify's own root domain, not attacker-controlled infrastructure or a wildcard the attacker owns. In practice this most plausibly causes DNS resolution failure (a broken/failed request, functionally a self-inflicted denial of the OAuth/token flow) rather than demonstrable exfiltration of `X-Shopify-Access-Token` or `client_secret` to an attacker-controlled host. No credential is shown to reach a party the attacker controls.

### Likelihood Explanation
Requires a host app to pass unauthenticated, user-supplied `shop` values into `ClientCredentials.client_credentials`, `RefreshToken.refresh_access_token`, or `TokenExchange.migrate_to_expiring_token` without its own additional shop validation, and requires the malformed host to actually resolve/dispatch somewhere attacker-reachable, which is not demonstrated to be possible given DNS's rejection of empty labels.

### Recommendation
In `ShopValidator.myshopify_domain_from_unified_admin`, reject the case where the extracted shop segment is `nil` or empty (raise/return `nil` instead of interpolating into `"#{shop}.myshopify.com"`), and have `sanitize_shop_domain`/`sanitize!` re-validate the synthesized host against the trusted-domain format (non-empty single label + trusted suffix) before returning it.

### Proof of Concept
```ruby
# test/utils/shop_validator_test.rb (new case)
def test_unified_admin_without_shop_path_produces_malformed_host
  result = ShopifyAPI::Utils::ShopValidator.sanitize!("https://admin.shopify.com")
  assert_equal(".myshopify.com", result) # demonstrates the empty-label host is NOT rejected
end
```
```ruby
# test/clients/http_client_test.rb (new case)
def test_malformed_shop_is_used_verbatim_as_base_uri
  session = ShopifyAPI::Auth::Session.new(shop: ".myshopify.com", access_token: "shpat_fake")
  stub_request(:get, "https://.myshopify.com/admin/oauth/foo")
    .with(headers: { "X-Shopify-Access-Token" => "shpat_fake" })
    .to_return(status: 200, body: "{}")

  client = ShopifyAPI::Clients::HttpClient.new(session: session, base_path: "/admin/oauth")
  client.request(ShopifyAPI::Clients::HttpRequest.new(http_method: :get, path: "foo"))

  assert_requested(:get, "https://.myshopify.com/admin/oauth/foo",
    headers: { "X-Shopify-Access-Token" => "shpat_fake" })
end
```
Both assert the two sides of the binding: `sanitize!`'s accepted host (`.myshopify.com`) is not a genuine single-shop subdomain, yet `HttpClient` sends the `X-Shopify-Access-Token` header there without further checks.

### Citations

**File:** lib/shopify_api/utils/shop_validator.rb (L41-43)
```ruby
            if unified_admin?(uri) && from_trusted_domain
              return myshopify_domain_from_unified_admin(uri)
            end
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

**File:** lib/shopify_api/utils/shop_validator.rb (L110-114)
```ruby
        sig { params(uri: Addressable::URI).returns(String) }
        def myshopify_domain_from_unified_admin(uri)
          shop = uri.path.to_s.split("/").last
          "#{shop}.myshopify.com"
        end
```

**File:** lib/shopify_api/auth/client_credentials.rb (L25-33)
```ruby
          validated_shop = Utils::ShopValidator.sanitize!(shop)
          shop_session = ShopifyAPI::Auth::Session.new(shop: validated_shop)
          body = {
            client_id: ShopifyAPI::Context.api_key,
            client_secret: ShopifyAPI::Context.api_secret_key,
            grant_type: CLIENT_CREDENTIALS_GRANT_TYPE,
          }

          client = Clients::HttpClient.new(session: shop_session, base_path: "/admin/oauth")
```

**File:** lib/shopify_api/auth/refresh_token.rb (L24-33)
```ruby
          validated_shop = Utils::ShopValidator.sanitize!(shop)
          shop_session = ShopifyAPI::Auth::Session.new(shop: validated_shop)
          body = {
            client_id: ShopifyAPI::Context.api_key,
            client_secret: ShopifyAPI::Context.api_secret_key,
            grant_type: "refresh_token",
            refresh_token:,
          }

          client = Clients::HttpClient.new(session: shop_session, base_path: "/admin/oauth")
```

**File:** lib/shopify_api/auth/token_exchange.rb (L103-115)
```ruby
          validated_shop = Utils::ShopValidator.sanitize!(shop)
          shop_session = ShopifyAPI::Auth::Session.new(shop: validated_shop)
          body = {
            client_id: ShopifyAPI::Context.api_key,
            client_secret: ShopifyAPI::Context.api_secret_key,
            grant_type: TOKEN_EXCHANGE_GRANT_TYPE,
            subject_token: non_expiring_offline_token,
            subject_token_type: RequestedTokenType::OFFLINE_ACCESS_TOKEN.serialize,
            requested_token_type: RequestedTokenType::OFFLINE_ACCESS_TOKEN.serialize,
            expiring: "1",
          }

          client = Clients::HttpClient.new(session: shop_session, base_path: "/admin/oauth")
```

**File:** lib/shopify_api/clients/graphql/storefront.rb (L22-29)
```ruby
          validated_shop = Utils::ShopValidator.sanitize!(shop)
          session = Auth::Session.new(
            id: validated_shop,
            shop: validated_shop,
            access_token: "",
            is_online: false,
          )
          super(session: session, base_path: "/api", api_version: api_version)
```

**File:** lib/shopify_api/clients/http_client.rb (L16-32)
```ruby
        api_host = Context.api_host

        @base_uri = T.let("https://#{api_host || session.shop}", String)
        @base_uri_and_path = T.let("#{@base_uri}#{base_path}", String)

        user_agent_prefix = Context.user_agent_prefix.nil? ? "" : "#{Context.user_agent_prefix} | "

        @headers = T.let({
          "User-Agent": "#{user_agent_prefix}Shopify API Library v#{VERSION} | Ruby #{RUBY_VERSION}",
          "Accept": "application/json",
        }, T::Hash[T.any(Symbol, String), T.untyped])

        @headers["Host"] = session.shop unless api_host.nil?

        unless session.access_token.nil? || T.must(session.access_token).empty?
          @headers["X-Shopify-Access-Token"] = T.cast(session.access_token, String)
        end
```

**File:** lib/shopify_api/clients/http_client.rb (L43-57)
```ruby
        parsed_uri = URI(request_url(request))

        headers = append_first_party_development_headers(headers, parsed_uri)

        tries = 0
        response = HttpResponse.new(code: 0, headers: {}, body: "")
        while tries < request.tries
          tries += 1
          res = T.cast(HTTParty.send(
            request.http_method,
            parsed_uri.to_s,
            headers: headers,
            query: request.query,
            body: request.body.class == Hash ? T.unsafe(request.body).to_json : request.body,
          ), HTTParty::Response)
```
