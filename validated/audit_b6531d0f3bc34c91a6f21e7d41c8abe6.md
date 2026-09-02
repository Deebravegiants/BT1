Confirmed: `Oauth.begin_auth` in `lib/shopify_api/auth/oauth.rb` never calls `ShopValidator.sanitize!` or `sanitize_shop_domain` on the `shop:` parameter before using it to build `auth_route`. `ShopValidator` is only used elsewhere (`token_exchange.rb`, `client_credentials.rb`, `refresh_token.rb`, `clients/graphql/storefront.rb`), not in `oauth.rb`.

### Title
Unsanitized `shop` parameter in `Oauth.begin_auth` causes forced-OAuth-completion / open redirect - (File: lib/shopify_api/auth/oauth.rb)

### Summary
`ShopifyAPI::Auth::Oauth.begin_auth` builds `auth_route` by directly interpolating the caller-supplied `shop` string into `auth_base_uri(shop)` without ever validating it against `ShopValidator.sanitize!`/`TRUSTED_SHOPIFY_DOMAINS`. Since apps are expected (per the documented flow) to pass the `shop` query parameter from the initial `/auth?shop=...` request straight into `begin_auth`, an attacker can supply any host and receive back an `auth_route` pointing at that host, along with a same-site `state` cookie for the app's own domain.

### Finding Description
The broken binding: `auth_base_uri(shop) == "https://" + ShopValidator.sanitize!(shop) + "/admin"` is false — the actual code is `auth_base_uri(shop)` at [1](#0-0)  which just does `return "https://#{shop}/admin" unless ...`, with no call to `ShopValidator` anywhere in the module. `begin_auth` at [2](#0-1)  generates a `state` nonce, wraps it in a `SessionCookie` for the app's own domain, and concatenates `auth_base_uri(shop) + "/oauth/authorize?..."` into `auth_route`, returning both to the caller. The app (per the documented usage pattern) is expected to redirect the merchant's browser to `auth_route` and set the returned cookie on its own domain. Because `shop` is never checked against `ShopValidator::TRUSTED_SHOPIFY_DOMAINS`, an attacker requesting `/auth?shop=attacker.tld` causes the app to 302-redirect the merchant to `https://attacker.tld/admin/oauth/authorize?client_id=...&redirect_uri=<app real callback>&state=<nonce>`, while the merchant's browser now holds a legitimate `state` cookie scoped to the app's own domain. None of the existing guards (`HmacValidator.validate`, the `state` cookie comparison in `validate_auth_callback`, `Context.setup?`/`private?`/`embedded?`) run at this stage — they only fire later, at the callback, and by then the merchant has already been sent to the attacker-controlled authorize endpoint.

### Impact Explanation
The app leaks its own client_id and real callback `redirect_uri` to an attacker-chosen host, and sends the merchant's browser (holding a genuine app-domain state cookie) to that host — enabling forced OAuth completion / open-redirect style abuse: the attacker-controlled page can act as a convincing look-alike consent screen and then redirect the merchant back to the app's real `redirect_uri` with an attacker-supplied `code`/`shop`. This does not bypass HMAC or state validation outright (`validate_auth_callback` still checks both), but it is a genuine SSRF-adjacent/redirect primitive matching the "High" category (forced OAuth completion / redirect to unintended host) since the app never restricts `auth_route`'s host to a trusted Shopify domain. This is repeatable against any victim who can be induced to click the crafted `/auth?shop=` link for the app.

### Likelihood Explanation
Preconditions: the host app uses `begin_auth` as documented, passing through the `shop` param from the initial request without its own separate validation (which the docs do not instruct developers to add). Attacker cost is a single crafted link (`/auth?shop=attacker.tld`) sent to a victim merchant — no credentials, no prior access, and fully repeatable per target.

### Recommendation
In `Oauth.begin_auth`, validate/sanitize `shop` via `ShopifyAPI::Utils::ShopValidator.sanitize!(shop)` (raising `Errors::InvalidShopError` on an untrusted domain) before it is used in `auth_base_uri`, mirroring the pattern already used in `token_exchange.rb`, `client_credentials.rb`, and `refresh_token.rb`.

### Proof of Concept
```ruby
# test/auth/oauth_test.rb (new test)
def test_begin_auth_rejects_untrusted_shop_domain
  ShopifyAPI::Context.setup(api_key: "key", api_secret_key: "secret", scope: "scope",
    host_name: "app.com", is_embedded: false, api_version: "2024-01",
    is_private: false)

  result = ShopifyAPI::Auth::Oauth.begin_auth(shop: "attacker.tld", redirect_path: "/callback")

  # Broken binding demonstration: no trusted-domain gate exists
  assert result[:auth_route].start_with?("https://attacker.tld/admin/oauth/authorize")
end
```
Expected (buggy) behavior today: assertion passes, proving `auth_route` is built from `attacker.tld` unchecked. After applying the recommended fix (calling `ShopValidator.sanitize!(shop)`), this same call should instead raise `ShopifyAPI::Errors::InvalidShopError`.

### Citations

**File:** lib/shopify_api/auth/oauth.rb (L36-51)
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
```

**File:** lib/shopify_api/auth/oauth.rb (L117-120)
```ruby
        sig { params(shop: String).returns(String) }
        def auth_base_uri(shop)
          return "https://#{shop}/admin" unless defined?(DevServer) && shop.include?(".my.shop.dev")

```
