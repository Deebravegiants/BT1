This confirms the key finding: `ShopValidator.sanitize!` is used to bind the `shop` value before sending credentials in `TokenExchange`, `ClientCredentials`, `RefreshToken`, and `Clients::Graphql::Storefront` [1](#0-0) , but `Oauth.validate_auth_callback` never calls `ShopValidator` on `auth_query.shop` before using it to build the URL that receives the app's `client_id`/`client_secret` during the authorization-code exchange.

### Title
OAuth authorization-code callback sends `client_secret` to an unsanitized `shop` host - (File: lib/shopify_api/auth/oauth.rb)

### Summary
`ShopifyAPI::Auth::Oauth.validate_auth_callback` builds the access-token exchange request URL directly from `auth_query.shop`, the `shop` query parameter, without ever passing it through `ShopValidator.sanitize!`/`sanitize_shop_domain`, unlike every other OAuth entry point in this gem (`TokenExchange`, `ClientCredentials`, `RefreshToken`) that explicitly sanitizes `shop` against `ShopValidator::TRUSTED_SHOPIFY_DOMAINS` before contacting it.

### Finding Description
`validate_auth_callback` only validates the HMAC over the callback query string (`code`, `host`, `shop`, `state`, `timestamp`) and the `state` cookie/nonce: [2](#0-1) 

It then uses `auth_query.shop` verbatim to build the base URI for the token exchange POST that carries the app's `client_secret`: [3](#0-2) [4](#0-3) 

Critically, HMAC validation only proves the query string is unmodified/authentic relative to whoever computed it with the correct `api_secret_key` — it does **not** prove `shop` is a legitimate `*.myshopify.com` (or other trusted Shopify) domain. The equality this code implicitly (and wrongly) assumes is:

`shop value verified by HMAC == shop value safe to use as a network destination for client_secret`

But HMAC coverage and domain-trust are two different properties. Every sibling OAuth flow in this codebase enforces the second property explicitly via `Utils::ShopValidator`: [5](#0-4) [6](#0-5) 

`validate_auth_callback` is the only OAuth code path that skips this check — grep confirms `ShopValidator` is referenced in `token_exchange.rb`, `client_credentials.rb`, `refresh_token.rb`, and `clients/graphql/storefront.rb`, but not in `oauth.rb`.

Whether this is practically exploitable depends on where the host application sources the `shop` value that goes into `begin_auth`/is echoed back in the callback. If the host app's own routing/session doesn't independently pin the shop domain (which the gem's docs example does not enforce — it just forwards `request.parameters` into `AuthQuery`), an app whose Shopify Partner OAuth redirect can be triggered with an attacker-influenced `shop=` (many Rails-based `ShopifyApp`-style callback controllers accept `shop` from the query string on the initial visit and merely relay it into `begin_auth`), causes the app's own backend to send its `client_secret` and the merchant's one-time `code` to whatever host is embedded in `shop`, since `auth_base_uri` performs no domain restriction.

### Impact Explanation
This matches the "SSRF with the app's credentials" impact category: the server-side POST containing `client_secret` (and the authorization `code`, which is exchangeable for an access token) is sent to a host controlled by whoever supplied the unsanitized `shop` value, rather than to `*.myshopify.com`. That constitutes credential leakage of the app's `client_secret` to an attacker-controlled endpoint plus theft of the resulting access token.

### Likelihood Explanation
Likelihood depends entirely on the host application: if the host app treats the `shop` param (as forwarded through `AuthQuery`) as already trusted at the point it calls `begin_auth`/`validate_auth_callback` — which is exactly the pattern shown in this gem's own documentation example (`request.parameters.symbolize_keys.except(:controller, :action)` fed straight into `AuthQuery`) — the unsanitized `shop` flows straight to the network call. Given the gem itself sanitizes `shop` in three other OAuth-adjacent flows but omits it here, this looks like an inconsistency/omission rather than a deliberate design decision.

### Recommendation
In `ShopifyAPI::Auth::Oauth.validate_auth_callback`, sanitize `auth_query.shop` with `Utils::ShopValidator.sanitize!(auth_query.shop, myshopify_domain: Context.myshopify_domain)` (or equivalent) before using it to build `auth_base_uri`/`null_session`, raising `Errors::InvalidOauthError` if the shop is not a trusted Shopify domain — mirroring the pattern already used in `token_exchange.rb`, `client_credentials.rb`, and `refresh_token.rb`.

### Proof of Concept
1. Host application's callback route accepts `shop`, `code`, `state`, `hmac`, `host`, `timestamp` from the query string and constructs `AuthQuery` directly from `request.parameters`, per the documented pattern.
2. Attacker who can trigger/influence the OAuth flow (e.g., via a crafted "Install" link where the host app does not independently pin the shop before calling `begin_auth`) sets `shop=evil.example.com`.
3. `begin_auth` builds `auth_route = "https://evil.example.com/admin/oauth/authorize?..."` — no validation rejects this.
4. Because HMAC only certifies the query string, not the domain, an attacker who can get any resulting callback processed with `shop=evil.example.com` (with `code`, `state` matching the app's own cookie/nonce, once the flow reaches the app's callback) causes `validate_auth_callback` to call `auth_base_uri("evil.example.com") + "/admin/oauth/access_token"`, POSTing `client_id`, `client_secret`, and `code` to `https://evil.example.com/admin/oauth/access_token`.
5. Compare against `TokenExchange.exchange_token`, which calls `ShopValidator.sanitize!` on `shop` before ever making a network call: [7](#0-6)

### Citations

**File:** lib/shopify_api/auth/token_exchange.rb (L1-10)
```ruby
# typed: strict
# frozen_string_literal: true

module ShopifyAPI
  module Auth
    module TokenExchange
      extend T::Sig

      TOKEN_EXCHANGE_GRANT_TYPE = "urn:ietf:params:oauth:grant-type:token-exchange"
      ID_TOKEN_TYPE = "urn:ietf:params:oauth:token-type:id_token"
```

**File:** lib/shopify_api/auth/token_exchange.rb (L29-51)
```ruby
        def exchange_token(session_token:, requested_token_type:, shop: nil)
          unless ShopifyAPI::Context.setup?
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

          shop_session = ShopifyAPI::Auth::Session.new(shop: dest_shop)
```

**File:** lib/shopify_api/auth/oauth.rb (L60-79)
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
```

**File:** lib/shopify_api/auth/oauth.rb (L81-98)
```ruby
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

          session_params = T.cast(response.body, T::Hash[String, T.untyped]).to_h
          session = Session.from(shop: auth_query.shop,
            access_token_response: Oauth::AccessTokenResponse.from_hash(session_params))
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

**File:** lib/shopify_api/utils/shop_validator.rb (L8-18)
```ruby
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
