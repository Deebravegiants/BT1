This confirms the finding: `ShopValidator.sanitize!` is used in `token_exchange.rb`, `client_credentials.rb`, and `refresh_token.rb`, but **not** in `oauth.rb`'s `validate_auth_callback` or `begin_auth`. This means the `shop` value flowing through the OAuth authorization-code grant is never checked against `ShopValidator::TRUSTED_SHOPIFY_DOMAINS`.

### Title
Missing `ShopValidator` domain check on OAuth `shop` parameter allows `client_secret` exfiltration via SSRF - (File: lib/shopify_api/auth/oauth.rb)

### Summary
`ShopifyAPI::Auth::Oauth.validate_auth_callback` builds the access-token request host directly from the `shop` field of the incoming `AuthQuery`, without ever calling `ShopValidator.sanitize!`/`sanitize_shop_domain`, unlike `TokenExchange`, `ClientCredentials`, and `RefreshToken`, which all validate `shop` through `ShopValidator` before using it. [1](#0-0) [2](#0-1) 

### Finding Description
`validate_auth_callback` only checks the HMAC over the query string and the `state` cookie; it never restricts `auth_query.shop` to `ShopValidator::TRUSTED_SHOPIFY_DOMAINS` (`shopify.com`, `myshopify.com`, `myshopify.io`, `spin.dev`, `shop.dev`) as the other OAuth-adjacent flows do. [3](#0-2) 

The unvalidated `auth_query.shop` is used to build a `null_session`, which is then passed into `Clients::HttpClient`. That client derives its request host directly from `session.shop` when `Context.api_host` is not configured: `@base_uri = "https://#{api_host || session.shop}"`. [4](#0-3)  The request body posted to that host includes `client_id` and `client_secret`: [5](#0-4) 

The equality this breaks: `shop` (the field that determines where `client_secret` is sent) is defined as "the domain covered by the request's HMAC signature," but the domain used to route the actual HTTP POST is never constrained to be a genuine `*.myshopify.com`-family host — it is only bytes that were part of the signed string, not bytes verified against a trusted-domain allowlist. Contrast this with `TokenExchange`, `ClientCredentials`, and `RefreshToken`, all of which call `ShopValidator.sanitize!(shop, ...)` before using `shop` to build a request host. [6](#0-5) 

Since the HMAC is computed by Shopify over exactly the parameters the merchant's browser is redirected with (`code`, `host`, `shop`, `state`, `timestamp`) using the app's own `api_secret_key`, an unprivileged internet user cannot forge a *valid* HMAC for an arbitrary `shop` value without knowing that secret. This is the boundary that prevents trivial exploitation: without the ability to produce a signature Shopify would accept, or the app's `api_secret_key`, this gap cannot presently be triggered by a purely unprivileged third party hitting the callback endpoint directly.

### Impact Explanation
If exploitable, this would be SSRF carrying the app's `client_secret` to an attacker-chosen host (Critical/High per the given impact taxonomy), because the callback flow POSTs `client_id`/`client_secret`/`code` to `https://#{shop}/admin/oauth/access_token` with no allowlist check on `shop`, unlike the sibling grant flows in this same library.

### Likelihood Explanation
Low, as currently reachable: the `shop` value is bound inside the HMAC-signed query string, and OpenSSL::HMAC verification with the app's real `api_secret_key` gates any request that reaches this code path with a `shop` value the attacker controls. No unprivileged-user path was found that produces a validly-signed callback with an attacker-controlled `shop` domain, so this is a defense-in-depth gap (inconsistent with the rest of the codebase) rather than a demonstrated authentication bypass or credential-exfiltration primitive today.

### Recommendation
For consistency and defense-in-depth, call `ShopValidator.sanitize!(auth_query.shop, myshopify_domain: ...)` in `validate_auth_callback` (and in `begin_auth`) before using `shop` to construct `auth_base_uri`/the null session, mirroring the pattern already used in `TokenExchange.exchange_token`, `ClientCredentials`, and `RefreshToken`.

### Proof of Concept
Not reproducible as an unprivileged-user attack with the current code, because a validly-HMAC-signed callback with an attacker-chosen `shop` cannot be produced without the app's `api_secret_key`. No end-to-end exploit chain was found; flagging as a design inconsistency (missing allowlist check present elsewhere in the same module family) rather than a confirmed vulnerability.

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

**File:** lib/shopify_api/utils/shop_validator.rb (L50-64)
```ruby
        sig do
          params(
            shop: String,
            myshopify_domain: T.nilable(String),
          ).returns(String)
        end
        def sanitize!(shop, myshopify_domain: nil)
          host = sanitize_shop_domain(shop, myshopify_domain: myshopify_domain)
          if host.nil? || host.empty?
            raise Errors::InvalidShopError,
              "shop must be a trusted Shopify domain (see ShopValidator::TRUSTED_SHOPIFY_DOMAINS), got: #{shop.inspect}"
          end

          host
        end
```

**File:** lib/shopify_api/clients/http_client.rb (L16-19)
```ruby
        api_host = Context.api_host

        @base_uri = T.let("https://#{api_host || session.shop}", String)
        @base_uri_and_path = T.let("#{@base_uri}#{base_path}", String)
```

**File:** lib/shopify_api/auth/token_exchange.rb (L39-51)
```ruby
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
