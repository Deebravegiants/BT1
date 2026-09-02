### Title
OAuth callback sends `client_secret` to an attacker-influenced `shop` host without domain validation - (File: `lib/shopify_api/auth/oauth.rb`)

### Summary
`ShopifyAPI::Auth::Oauth.validate_auth_callback` builds the token-exchange request to `https://#{auth_query.shop}/admin/oauth/access_token` (via `HttpClient` using `Session#shop`) using the raw `shop` value taken from the OAuth callback query parameters, without ever passing it through `Utils::ShopValidator.sanitize!`, unlike the sibling flows `ClientCredentials.client_credentials` and `RefreshToken.refresh_access_token`, which both explicitly call `Utils::ShopValidator.sanitize!(shop)` before constructing a session/host.

### Finding Description
`validate_auth_callback` only checks the HMAC over the query string, and that the `state` in the cookie matches `auth_query.state`: [1](#0-0) 

The `shop` field is part of the HMAC-signable string, so it is bound to a signature produced by Shopify with the app's own `api_secret_key`: [2](#0-1) 

The resulting `shop` string is used, unsanitized, to build the `Auth::Session` and then the token-exchange request host in `HttpClient#initialize`, which derives `@base_uri` directly from `session.shop`: [3](#0-2) 

By contrast, `ClientCredentials.client_credentials` and `RefreshToken.refresh_access_token` both call `Utils::ShopValidator.sanitize!(shop)`, which restricts the resolved host to `TRUSTED_SHOPIFY_DOMAINS` (`shopify.com`, `myshopify.io`, `myshopify.com`, `spin.dev`, `shop.dev`) before it is used to build a `Session`/host: [4](#0-3) [5](#0-4) [6](#0-5) 

`validate_auth_callback` has no equivalent call, so the equality this code implicitly relies on — "the `shop` string that was HMAC-verified as coming from Shopify" == "a host that is actually `*.myshopify.com`/a trusted Shopify domain" — is never enforced.

### Impact Explanation
The client review rules require this to route the app's `client_secret` (and, in the offline-token case, an OAuth `code`) to a host not equal to `*.myshopify.com`/trusted Shopify domain in order to count as SSRF-with-credentials. Reaching this requires Shopify's own OAuth server to produce a valid HMAC for a non-`myshopify.com` `shop` value in the redirect — which is outside Shopify's documented behavior (Shopify's OAuth authorization endpoint only issues callbacks for real, already-validated shop domains it controls). I could not find, within this gem's own code, any attacker-reachable way to obtain a validly-HMAC'd `AuthQuery` for an arbitrary non-Shopify `shop` value, since the HMAC secret (`api_secret_key`) is never exposed to an unprivileged internet user and the signature is produced/verified only against values that originated from Shopify's real callback. Without control over the HMAC or over the value Shopify signs, an external attacker cannot force this codepath to send the `client_secret` to an arbitrary host.

### Likelihood Explanation
Low/not concretely exploitable by an unprivileged internet user through this gem alone. The missing `ShopValidator.sanitize!` call is a real inconsistency relative to `ClientCredentials`/`RefreshToken`, but it is a defense-in-depth gap rather than a directly triggerable vulnerability, because the `shop` value reaching this code is already constrained by Shopify's HMAC over the OAuth callback, and there is no reachable path in this codebase for an attacker to inject an arbitrary `shop` string that still carries a valid signature.

### Recommendation
For defense-in-depth and consistency with `ClientCredentials`/`RefreshToken`, add `Utils::ShopValidator.sanitize!(auth_query.shop)` in `validate_auth_callback` before constructing `null_session`/`Session.from`, so the token-exchange request host is always constrained to `Utils::ShopValidator::TRUSTED_SHOPIFY_DOMAINS` regardless of how `shop` reached this method.

### Proof of Concept
Not reproducible as a standalone external attack with the tools/context available: exploitation would require Shopify's OAuth server to sign (`hmac`) an `AuthQuery` containing a non-`myshopify.com` `shop`, which is not achievable by an unprivileged internet user through this gem's code paths alone.

### Citations

**File:** lib/shopify_api/auth/oauth.rb (L60-98)
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

          session_params = T.cast(response.body, T::Hash[String, T.untyped]).to_h
          session = Session.from(shop: auth_query.shop,
            access_token_response: Oauth::AccessTokenResponse.from_hash(session_params))
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

**File:** lib/shopify_api/clients/http_client.rb (L11-19)
```ruby
      sig { params(base_path: String, session: T.nilable(Auth::Session)).void }
      def initialize(base_path:, session: nil)
        session ||= Context.active_session
        raise Errors::NoActiveSessionError, "No passed or active session" unless session

        api_host = Context.api_host

        @base_uri = T.let("https://#{api_host || session.shop}", String)
        @base_uri_and_path = T.let("#{@base_uri}#{base_path}", String)
```

**File:** lib/shopify_api/auth/client_credentials.rb (L25-26)
```ruby
          validated_shop = Utils::ShopValidator.sanitize!(shop)
          shop_session = ShopifyAPI::Auth::Session.new(shop: validated_shop)
```

**File:** lib/shopify_api/auth/refresh_token.rb (L24-25)
```ruby
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
