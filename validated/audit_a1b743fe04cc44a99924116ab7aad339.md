### Title
`Oauth.validate_auth_callback` sends the app's `client_secret` to a host derived from the unsanitized `shop` HMAC field - (File: `lib/shopify_api/auth/oauth.rb`)

### Summary
`ShopifyAPI::Auth::Oauth.validate_auth_callback` uses the `shop` value from the incoming OAuth callback query directly to build the `Session` that is later used to select the HTTP host the access-token exchange request is sent to, without ever passing it through `Utils::ShopValidator.sanitize!`. Every other credential-exchange entry point in the gem (`RefreshToken.refresh_access_token`, `ClientCredentials`, `TokenExchange` via the JWT `dest`) validates the shop against `ShopValidator::TRUSTED_SHOPIFY_DOMAINS` before using it to build the request host, but the OAuth authorization-code callback path does not.

### Finding Description
`validate_auth_callback` only checks that the HMAC over the query is valid and that `state` matches the cookie: [1](#0-0) 

The `shop` field is part of the HMAC-signable string, so its bytes are integrity-protected, but its *value* is never validated to be a trusted `*.myshopify.com` / Shopify domain before being used: [2](#0-1) 

That raw `auth_query.shop` is used to construct a `null_session`, which is then handed to `Clients::HttpClient`: [3](#0-2) 

`HttpClient#initialize` builds the request's base URI directly from `session.shop` with no further validation: [4](#0-3) 

The POST body for that request contains the app's `client_id` and `client_secret`: [5](#0-4) 

This is exactly the binding the gem enforces everywhere else: `RefreshToken.refresh_access_token` calls `Utils::ShopValidator.sanitize!(shop)` before building the session used for the token request: [6](#0-5) 

`ShopValidator.sanitize!`/`sanitize_shop_domain` only accept hosts matching `TRUSTED_SHOPIFY_DOMAINS` (`shopify.com`, `myshopify.io`, `myshopify.com`, `spin.dev`, `shop.dev`) or an explicitly configured `myshopify_domain`: [7](#0-6) 

`Oauth.validate_auth_callback` is missing this same call, so the equality the gem is supposed to enforce — *"host that receives `client_secret`" == "a Shopify-trusted domain"* — is broken specifically on this path. Because the `shop` field is inside the signed query, an attacker cannot forge a valid HMAC without the app's `api_secret_key`; but if the host application forwards `request.parameters` largely unfiltered into `AuthQuery` (as shown in the gem's own documented usage pattern) and a genuine Shopify-signed callback contains a `shop` value that resolves outside `TRUSTED_SHOPIFY_DOMAINS` (e.g. via edge cases in domain parsing, or a value crafted by a merchant/attacker with the ability to influence the redirect target during a proxied/spin/custom-domain OAuth flow), the gem itself has no defense-in-depth check and will happily send `client_secret` to whatever host `session.shop` computes to.

### Impact Explanation
This matches the High-impact class: "SSRF with the app's credentials" — an unsanitized shop value drives the request host for a call that carries the `client_id`/`client_secret` in the POST body. If the resulting host is attacker-influenced, the app's `client_secret` is exfiltrated to that host.

### Likelihood Explanation
Likelihood is moderate-to-low in isolation, since a valid HMAC over the query (computed with the still-secret `api_secret_key`) is required, matching the original report's mitigation pattern (removing an unchecked/uncontrolled parameter from a privileged, credential-bearing operation). It is elevated by the fact that this check exists in three sibling methods (`RefreshToken`, `ClientCredentials`, `TokenExchange`) but was omitted specifically from `Oauth.validate_auth_callback`, indicating an inconsistency/gap rather than an intentional design decision.

### Recommendation
In `Oauth.validate_auth_callback`, replace direct use of `auth_query.shop` with `Utils::ShopValidator.sanitize!(auth_query.shop)` (mirroring `RefreshToken.refresh_access_token`) before constructing `null_session`, and use the sanitized value consistently for both the token request and the resulting `Session.from(shop: ...)` call.

### Proof of Concept
1. App's callback controller builds `ShopifyAPI::Auth::Oauth::AuthQuery.new(request.parameters...)` and calls `ShopifyAPI::Auth::Oauth.validate_auth_callback(cookies:, auth_query:)`, per the gem's documented pattern (`docs/usage/oauth.md`).
2. A callback request arrives with a `shop` value that is not a `TRUSTED_SHOPIFY_DOMAINS` member/subdomain but for which a valid `hmac` exists (e.g., a value the developer's Shopify Partner/OAuth setup would still sign, or a value smuggled through an intermediary that recomputes/forwards a valid HMAC).
3. `validate_auth_callback` passes HMAC and state checks (`lib/shopify_api/auth/oauth.rb:64-71`) and builds `null_session = Auth::Session.new(shop: auth_query.shop)` unfiltered.
4. `Clients::HttpClient.new(session: null_session, base_path: "/admin/oauth")` sets `@base_uri = "https://#{session.shop}"` (`lib/shopify_api/clients/http_client.rb:18`).
5. The subsequent `POST /admin/oauth/access_token` request — containing `client_id` and `client_secret` in the JSON body — is sent to `https://<attacker-controlled-shop-value>/admin/oauth/access_token`, leaking the app's `client_secret` off-platform.

### Citations

**File:** lib/shopify_api/auth/oauth.rb (L60-81)
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

**File:** lib/shopify_api/clients/http_client.rb (L16-19)
```ruby
        api_host = Context.api_host

        @base_uri = T.let("https://#{api_host || session.shop}", String)
        @base_uri_and_path = T.let("#{@base_uri}#{base_path}", String)
```

**File:** lib/shopify_api/auth/refresh_token.rb (L18-33)
```ruby
        def refresh_access_token(shop:, refresh_token:)
          unless ShopifyAPI::Context.setup?
            raise ShopifyAPI::Errors::ContextNotSetupError,
              "ShopifyAPI::Context not setup, please call ShopifyAPI::Context.setup"
          end

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
