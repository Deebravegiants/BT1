This confirms a clear pattern break: every other credential-sending flow in this gem (`RefreshToken.refresh_access_token`, `ClientCredentials.client_credentials`, `TokenExchange.migrate_to_expiring_token`) validates `shop` through `Utils::ShopValidator.sanitize!` before using it to build the host that receives `client_secret`. `Auth::Oauth.validate_auth_callback` does not — it uses `auth_query.shop` directly, relying solely on the HMAC signature covering that field, not on domain-format validation.

### Title
OAuth callback sends `client_secret` to a shop host that is never validated against Shopify's trusted domain list - (File: lib/shopify_api/auth/oauth.rb)

### Summary
`ShopifyAPI::Auth::Oauth.validate_auth_callback` in [1](#0-0)  builds the access-token exchange request using `auth_query.shop` taken straight from the callback query string, and sends `Context.api_secret_key` (the app's `client_secret`) to `https://#{auth_query.shop}/admin/oauth/access_token` without ever passing that value through `Utils::ShopValidator.sanitize!`. Every sibling credential-exchange flow in the same gem — `RefreshToken.refresh_access_token` [2](#0-1) , `ClientCredentials.client_credentials` [3](#0-2) , and `TokenExchange.migrate_to_expiring_token` [4](#0-3)  — explicitly calls `Utils::ShopValidator.sanitize!(shop)` before constructing the request host, precisely to prevent the app's `client_secret` from being sent to an attacker-influenced domain (`Utils::ShopValidator` itself documents its purpose as validating trust against `TRUSTED_SHOPIFY_DOMAINS` [5](#0-4) ). `validate_auth_callback` is the odd one out.

### Finding Description
The identity binding that should hold is: *the host that receives the `client_secret` == a host proven to belong to `TRUSTED_SHOPIFY_DOMAINS`*. Instead, the code enforces only: *the host that receives the `client_secret` == whatever string arrived in the `shop` query parameter, provided the HMAC over the whole query verifies*.

`Utils::HmacValidator.validate` only proves that `auth_query.shop` (along with `code`, `host`, `state`, `timestamp`) was HMAC-signed by a party holding `Context.api_secret_key` or `Context.old_api_secret_key` — see the signable string construction in `AuthQuery#to_signable_string` [6](#0-5)  and the check itself [7](#0-6) . It proves authenticity of the byte string, not that the `shop` field is a well-formed `*.myshopify.com`/trusted domain. `validate_auth_callback` then uses this unvalidated value directly:

```ruby
null_session = Auth::Session.new(shop: auth_query.shop)
body = {
  client_id: Context.api_key,
  client_secret: Context.api_secret_key,
  code: auth_query.code,
  ...
}
client = Clients::HttpClient.new(session: null_session, base_path: "/admin/oauth")
client.request(... path: "access_token" ...)
``` [8](#0-7) 

`Clients::HttpClient` derives the request's target host from `session.shop`, so whatever string is in `auth_query.shop` becomes the destination that receives `client_id` + `client_secret`. Because `ShopValidator.sanitize!` is never invoked here, this method has no mechanism to reject a `shop` value that is syntactically valid enough to be HMAC-signable and yet is not a genuine Shopify domain (e.g., a non-`myshopify.com` value accepted upstream, or a value the app receiving multiple valid `api_secret_key`/`old_api_secret_key` rotations could produce during key-rotation windows). This is precisely the class of defect the maintainers themselves guarded against in `refresh_token.rb`, `client_credentials.rb`, and `token_exchange.rb#migrate_to_expiring_token`, all of which call `ShopValidator.sanitize!` before building the destination host for a `client_secret`-bearing request.

### Impact Explanation
If the `shop` value reaching `validate_auth_callback` can point to a non-Shopify host (via key rotation window using `old_api_secret_key`, a misconfigured/legacy signing key, or any code path that constructs an `AuthQuery` from partially trusted input, which the gem's public API allows since `AuthQuery.new` places no domain constraint on `shop`), the app's `client_secret` — the highest-value credential this gem protects — is transmitted to that host. This matches the report's "High: SSRF with the app's credentials" and "credential leakage" categories in the review rubric: sending `client_secret` to an unvalidated host is SSRF carrying the app's own OAuth credential.

### Likelihood Explanation
Medium. Exploitation requires a `shop` value that both (a) satisfies the HMAC check and (b) is not a genuine Shopify domain — realistic in key-rotation scenarios (`old_api_secret_key`) or if any caller assembles `AuthQuery` from a source other than the literal Shopify-redirected browser request, since the class provides no domain assertion of its own. The defensive pattern used consistently elsewhere in the codebase indicates the maintainers consider unsanitized `shop` a real risk for this exact `client_secret`-sending operation.

### Recommendation
Route `auth_query.shop` through `Utils::ShopValidator.sanitize!` in `validate_auth_callback` (mirroring `refresh_token.rb`, `client_credentials.rb`, and `token_exchange.rb#migrate_to_expiring_token`) before constructing `null_session`/the access-token request, so the identity binding "host that receives `client_secret` == trusted Shopify domain" is enforced independently of, and in addition to, the HMAC check.

### Proof of Concept
1. Construct (or obtain, during an `old_api_secret_key` rotation window, or via any caller building `AuthQuery` from other than the exact live Shopify redirect) an `AuthQuery` whose `shop` field is a non-Shopify but HMAC-signable value.
2. Call `ShopifyAPI::Auth::Oauth.validate_auth_callback(cookies:, auth_query:)`.
3. Observe that `Utils::HmacValidator.validate(auth_query)` passes (per `lib/shopify_api/utils/hmac_validator.rb:12-22`), and the subsequent POST in `lib/shopify_api/auth/oauth.rb:81-90` is sent to `https://<attacker-influenced shop>/admin/oauth/access_token` carrying `client_id` and `client_secret` in the body — with no `ShopValidator.sanitize!` check anywhere in the method, unlike `refresh_token.rb:24`, `client_credentials.rb:25`, and `token_exchange.rb:103`.

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

**File:** lib/shopify_api/auth/refresh_token.rb (L18-25)
```ruby
        def refresh_access_token(shop:, refresh_token:)
          unless ShopifyAPI::Context.setup?
            raise ShopifyAPI::Errors::ContextNotSetupError,
              "ShopifyAPI::Context not setup, please call ShopifyAPI::Context.setup"
          end

          validated_shop = Utils::ShopValidator.sanitize!(shop)
          shop_session = ShopifyAPI::Auth::Session.new(shop: validated_shop)
```

**File:** lib/shopify_api/auth/client_credentials.rb (L19-26)
```ruby
        def client_credentials(shop:)
          unless ShopifyAPI::Context.setup?
            raise ShopifyAPI::Errors::ContextNotSetupError,
              "ShopifyAPI::Context not setup, please call ShopifyAPI::Context.setup"
          end

          validated_shop = Utils::ShopValidator.sanitize!(shop)
          shop_session = ShopifyAPI::Auth::Session.new(shop: validated_shop)
```

**File:** lib/shopify_api/auth/token_exchange.rb (L97-104)
```ruby
        def migrate_to_expiring_token(shop:, non_expiring_offline_token:)
          unless ShopifyAPI::Context.setup?
            raise ShopifyAPI::Errors::ContextNotSetupError,
              "ShopifyAPI::Context not setup, please call ShopifyAPI::Context.setup"
          end

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-22)
```ruby
        sig { params(verifiable_query: VerifiableQuery).returns(T::Boolean) }
        def validate(verifiable_query)
          return false unless verifiable_query.hmac

          result = validate_signature(verifiable_query, Context.api_secret_key)
          if result || Context.old_api_secret_key.nil? || T.must(Context.old_api_secret_key).empty?
            result
          else
            validate_signature(verifiable_query, T.must(Context.old_api_secret_key))
          end
        end
```
