### Title
Missing Shop-Domain Validation in `Auth::Oauth.begin_auth`/`validate_auth_callback` Enables Forced OAuth Completion Against an Attacker-Controlled Host - (File: `lib/shopify_api/auth/oauth.rb`)

### Summary
`ShopifyAPI::Auth::Oauth.begin_auth` and `ShopifyAPI::Auth::Oauth.validate_auth_callback` build the Shopify authorize/token-exchange URL directly from a caller-supplied `shop` string with no validation that it is a trusted `*.myshopify.com` (or other trusted Shopify) domain. Every other credential-issuing flow in this same gem — `Auth::TokenExchange`, `Auth::ClientCredentials`, and `Auth::RefreshToken` — explicitly calls `Utils::ShopValidator.sanitize!` before using the shop value to build a request host, but `Auth::Oauth` does not.

### Finding Description
`ShopValidator.sanitize!` exists specifically to enforce the invariant: "shop domain used to build a Shopify request URL" == "a domain within `ShopValidator::TRUSTED_SHOPIFY_DOMAINS`" [1](#0-0) [2](#0-1) . This check is used in `Auth::TokenExchange`, `Auth::ClientCredentials`, and `Auth::RefreshToken` before those classes build a request host from a `shop` value [3](#0-2) .

`Auth::Oauth.begin_auth`, however, takes an untrusted `shop:` parameter directly and builds the redirect URL with `auth_base_uri(shop) + "/oauth/authorize?..."` with no call to `ShopValidator` at all: [4](#0-3) 

```ruby
def begin_auth(shop:, redirect_path:, is_online: true, scope_override: nil)
  ...
  auth_route = auth_base_uri(shop) + "/oauth/authorize?#{query_string}"
  { auth_route: auth_route, cookie: cookie }
end
```

`auth_base_uri` simply interpolates the raw `shop` string into a URL: [5](#0-4) 

Likewise, `validate_auth_callback` uses `auth_query.shop` — bound only by HMAC, never checked against `ShopValidator` — to build the `client.request(...)` call to `#{shop}/admin/oauth/access_token`, which carries the app's `client_id`/`client_secret` in the POST body: [6](#0-5) 

By contrast, `Auth::TokenExchange` and sibling flows explicitly sanitize the shop before it is used to build any request host, so the same gem enforces the "trusted domain" binding inconsistently across its own OAuth entry points.

### Impact Explanation
Since Shopify apps commonly pass the `shop` query parameter received on their `/login` (or install) route straight into `begin_auth` (as shown in this gem's own docs) [7](#0-6) , and the gem itself performs no domain restriction, a value such as `shop=attacker-controlled-host.example` will be used verbatim to construct the `oauth/authorize` redirect target, sending the merchant's browser — together with the app's `client_id` and requested `scope` — to a host the attacker fully controls. This lets the attacker stage a spoofed Shopify consent page to force/steer OAuth completion against infrastructure it controls (matching the "forced OAuth completion" impact category), rather than the genuine `*.myshopify.com` authorize endpoint the app owner intended.

### Likelihood Explanation
This is directly reachable by any unprivileged actor able to influence the `shop` value handed to `begin_auth` (e.g., via a crafted install/login link containing an arbitrary `shop` query parameter), which is the exact input path documented for this method. No credentials, tokens, or `client_secret` are required to trigger it — only the ability to get a victim to click a link pointing at the host app's own login route with an attacker-chosen `shop` value.

### Recommendation
Call `Utils::ShopValidator.sanitize!` (as already done in `Auth::TokenExchange`, `Auth::ClientCredentials`, and `Auth::RefreshToken`) on the `shop` parameter in `Auth::Oauth.begin_auth` before constructing `auth_base_uri`, and similarly validate `auth_query.shop` in `Auth::Oauth.validate_auth_callback` before it is used to build the access-token request host, raising `Errors::InvalidShopError` for any value that does not resolve to a trusted Shopify domain.

### Proof of Concept
```ruby
ShopifyAPI::Context.setup(api_key: "key", api_secret_key: "secret", api_version: "2024-01",
  is_private: false, is_embedded: true, host: "https://my-app.example.com")

result = ShopifyAPI::Auth::Oauth.begin_auth(
  shop: "attacker-controlled-host.example",   # not a myshopify.com domain, no validation performed
  redirect_path: "/auth/callback",
)

puts result[:auth_route]
# => "https://attacker-controlled-host.example/admin/oauth/authorize?client_id=key&scope=...&redirect_uri=https://my-app.example.com/auth/callback&state=...&grant_options%5B%5D=per-user"
```
The generated `auth_route` sends the merchant's browser to a host fully controlled by the attacker, unlike `TokenExchange.exchange_token`/`ClientCredentials`/`RefreshToken`, which would reject such a `shop` value via `ShopValidator.sanitize!` [8](#0-7) .

### Citations

**File:** lib/shopify_api/utils/shop_validator.rb (L1-8)
```ruby
# typed: strict
# frozen_string_literal: true

require "addressable/uri"

module ShopifyAPI
  module Utils
    module ShopValidator
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

**File:** lib/shopify_api/auth/oauth.rb (L60-94)
```ruby
        def validate_auth_callback(cookies:, auth_query:)
          unless Context.setup?
            raise Errors::ContextNotSetupError, "ShopifyAPI::Context not setup, please call ShopifyAPI::Context.setup"
          end
          raise Errors::InvalidOauthError, "Invalid OAuth callback." unless Utils::HmacValidator.validate(auth_query)
          raise Errors::UnsupportedOauthError, "Cannot perform OAuth for private apps." if Context.private?

          state = cookies[SessionCookie::SESSION_COOKIE_NAME]
          raise Errors::NoSessionCookieError unless state

          raise Errors::InvalidOauthError,
            "Invalid state in OAuth callback." unless state == auth_query.state

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

**File:** lib/shopify_api/auth/oauth.rb (L117-120)
```ruby
        sig { params(shop: String).returns(String) }
        def auth_base_uri(shop)
          return "https://#{shop}/admin" unless defined?(DevServer) && shop.include?(".my.shop.dev")

```

**File:** docs/usage/oauth.md (L104-120)
```markdown
### Authorization Code Grant
##### Steps
1. [Add a route to start OAuth](#1-add-a-route-to-start-oauth)
2. [Add an Oauth callback route](#2-add-an-oauth-callback-route)
3. [Begin OAuth](#3-begin-oauth)
4. [Handle OAuth Callback](#4-handle-oauth-callback)

#### 1. Add a route to start OAuth
Add a route to your app to start the OAuth process.

```ruby
class ShopifyAuthController < ApplicationController
  def login
    # This method will trigger the start of the OAuth process
  end
end
```
```

**File:** lib/shopify_api/auth/token_exchange.rb (L31-50)
```ruby
            raise ShopifyAPI::Errors::ContextNotSetupError,
              "ShopifyAPI::Context not setup, please call ShopifyAPI::Context.setup"
          end
          raise ShopifyAPI::Errors::UnsupportedOauthError,
            "Cannot perform OAuth Token Exchange for private apps." if ShopifyAPI::Context.private?
          raise ShopifyAPI::Errors::UnsupportedOauthError,
            "Cannot perform OAuth Token Exchange for non embedded apps." unless ShopifyAPI::Context.embedded?

          # Validate the session token and use the shop from the token's `dest` claim
          jwt_payload = ShopifyAPI::Auth::JwtPayload.new(session_token)
          dest_shop = jwt_payload.shop

          if shop
            ShopifyAPI::Logger.deprecated(
              "The `shop` parameter for `exchange_token` is deprecated and will be removed in v17. " \
                "The shop is now always taken from the session token's `dest` claim.",
              "17.0.0",
            )
          end

```
