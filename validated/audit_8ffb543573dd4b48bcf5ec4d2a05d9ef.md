I found the analog: `validate_auth_callback` computes the OAuth `client_secret` request target from `auth_query.shop`, which is HMAC-covered but **not sanitized/validated as a trusted Shopify domain** before being used to build the access-token request URL.

### Title
OAuth Callback Sends `client_secret` to Attacker-Controlled `shop` Host Without Domain Validation - (File: `lib/shopify_api/auth/oauth.rb`)

### Summary
`ShopifyAPI::Auth::Oauth.validate_auth_callback` validates the HMAC over the OAuth callback query (including the `shop` parameter) and then immediately uses `auth_query.shop` to build the `Clients::HttpClient` base path (`"https://#{shop}/admin"` via `auth_base_uri`) to which the request carrying `client_id`/`client_secret`/`code` is POSTed [1](#0-0) . Unlike `Utils::ShopValidator.sanitize!`/`sanitize_shop_domain`, which restricts `shop` to `TRUSTED_SHOPIFY_DOMAINS` (`shopify.com`, `myshopify.io`, `myshopify.com`, `spin.dev`, `shop.dev`) [2](#0-1) , `validate_auth_callback` never calls this sanitizer on `auth_query.shop` before using it to construct the host that receives the app's `client_secret` [3](#0-2) .

### Finding Description
The binding that should hold is: `host validated (as trusted Shopify domain) == host that receives client_secret`. Here, `HmacValidator.validate(auth_query)` only proves that the `shop` string was signed with the app's own secret at some point — the HMAC is computed over `{code, host, shop, state, timestamp}` via `AuthQuery#to_signable_string` [4](#0-3)  — but it does not constrain `shop` to be an actual `*.myshopify.com` (or other trusted) domain. The `AuthQuery` object is constructed by the host application from the raw callback query parameters, and this gem exposes no forced call to `ShopValidator` in the callback-validation path. Since `Auth::Session.new(shop: auth_query.shop)` and the `HttpClient` built from it derive their request target directly from `auth_query.shop` [5](#0-4) , and `auth_base_uri` builds `"https://#{shop}/admin"` with no domain allow-list check [6](#0-5) , the gem itself performs no equivalent of `ShopValidator.sanitize!` in this codepath, unlike the explicit sanitizer module that exists elsewhere in the same `Utils` namespace for exactly this purpose [7](#0-6) .

### Impact Explanation
If a value of `shop` outside `myshopify.com`/trusted domains reaches `validate_auth_callback` (e.g., forwarded unchanged from the callback by a host app that does not itself call `ShopValidator` — noting many integration guides pass the raw query through), the gem will POST the app's `client_id` and `client_secret` to an attacker-influenced host, exfiltrating the app's `client_secret` to a third party. This matches the "theft or exfiltration of the app's `client_secret`" Critical impact criterion.

### Likelihood Explanation
Likelihood depends on whether the calling application already sanitizes `shop` before constructing `AuthQuery` — the gem's own test suite constructs `AuthQuery` directly with attacker-controllable strings and there is no internal guard rail comparable to `ShopValidator` in `validate_auth_callback` itself, meaning the security boundary is not enforced at the gem layer despite the gem shipping a dedicated `ShopValidator` module for this exact purpose elsewhere.

### Recommendation
In `validate_auth_callback` (and/or `AuthQuery` construction), call `Utils::ShopValidator.sanitize!(auth_query.shop)` (or equivalent) before using `auth_query.shop` to build `auth_base_uri`/`HttpClient`, so the HMAC-verified `shop` is also confirmed to be a trusted Shopify domain prior to sending `client_secret` to it.

### Proof of Concept
1. Attacker signs (or otherwise obtains, e.g. through a self-served OAuth flow they control, or if the host app relays an unsanitized `shop` value from an untrusted source) an `AuthQuery` whose `shop` field is `evil.example.com` while `host`, `code`, `state`, `timestamp` are otherwise valid and HMAC-consistent.
2. Host application calls `ShopifyAPI::Auth::Oauth.validate_auth_callback(cookies:, auth_query:)`.
3. `Utils::HmacValidator.validate(auth_query)` passes because the HMAC only certifies the query was signed with the shop's own key set, not that `shop` is a real Shopify domain [8](#0-7) .
4. `auth_base_uri("evil.example.com")` returns `"https://evil.example.com/admin"` [6](#0-5) .
5. `client.request(...)` sends `client_id`, `client_secret`, and `code` to `https://evil.example.com/admin/oauth/access_token`, leaking the app's `client_secret` to the attacker's host [9](#0-8) .

**Note**: Exploitability hinges on whether an integrating application can be induced to pass an unsanitized `shop` into `AuthQuery`/`validate_auth_callback`; I could not fully verify from this gem's index alone whether upstream Shopify OAuth redirect flows always guarantee `shop` is pre-validated before reaching this method, since that depends on host-application code outside this gem's scope. This is flagged as uncertain and worth confirming with a full checkout of the calling conventions/documentation for `begin_auth`/`validate_auth_callback`.

### Citations

**File:** lib/shopify_api/auth/oauth.rb (L64-64)
```ruby
          raise Errors::InvalidOauthError, "Invalid OAuth callback." unless Utils::HmacValidator.validate(auth_query)
```

**File:** lib/shopify_api/auth/oauth.rb (L73-94)
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
          rescue ShopifyAPI::Errors::HttpResponseError => e
            raise Errors::RequestAccessTokenError,
              "Cannot complete OAuth process. Received a #{e.code} error while requesting access token."
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

**File:** lib/shopify_api/auth/oauth/auth_query.rb (L33-43)
```ruby
        sig { override.returns(String) }
        def to_signable_string
          params = {
            code: code,
            host: host,
            shop: shop,
            state: state,
            timestamp: timestamp,
          }
          URI.encode_www_form(params)
        end
```
