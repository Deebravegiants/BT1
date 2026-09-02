Found the vulnerable analog: `ShopifyAPI::Auth::Oauth.begin_auth` (and `validate_auth_callback`) use the caller-supplied `shop` string to build the OAuth authorization URL, and later `validate_auth_callback` uses `auth_query.shop` to build the `Clients::HttpClient` host that receives the app's `client_secret`, without ever running it through `Utils::ShopValidator.sanitize!`. Every other credential-sending path in the gem (`ClientCredentials.client_credentials`, `RefreshToken.refresh_access_token`, `TokenExchange.migrate_to_expiring_token`) explicitly calls `Utils::ShopValidator.sanitize!(shop)` before constructing the session/host, but `Oauth.begin_auth`/`validate_auth_callback` never do.

### Title
OAuth `shop` parameter is not validated against `ShopValidator`, allowing SSRF that sends the app's `client_secret` to an attacker-controlled host - (File: lib/shopify_api/auth/oauth.rb)

### Summary
`ShopifyAPI::Auth::Oauth.validate_auth_callback` builds the access-token exchange request host directly from `auth_query.shop` [1](#0-0)  without ever passing it through `Utils::ShopValidator.sanitize!`, unlike every sibling credential-exchange flow in the gem.

### Finding Description
The `HmacValidator` binds `hmac` to `code`, `host`, `shop`, `state`, `timestamp` [2](#0-1) , which prevents tampering with any single field in isolation — but it only proves internal consistency of the query, not that `shop` is a genuine `*.myshopify.com` domain. The binding this gem needs to enforce is: `shop param used to build the access-token request host == a value drawn only from ShopValidator.TRUSTED_SHOPIFY_DOMAINS`. That equality is enforced in `ClientCredentials.client_credentials` (`validated_shop = Utils::ShopValidator.sanitize!(shop)` [3](#0-2) ), in `RefreshToken.refresh_access_token` [4](#0-3) , and in `TokenExchange.migrate_to_expiring_token` [5](#0-4) . It is absent from `Oauth.validate_auth_callback`, which instead does `null_session = Auth::Session.new(shop: auth_query.shop)` straight from the unsanitized query object and then builds `Clients::HttpClient.new(session: null_session, base_path: "/admin/oauth")` [1](#0-0) . `HttpClient#initialize` derives the request host directly from `session.shop` when no `Context.api_host` override is configured: `@base_uri = "https://#{api_host || session.shop}"` [6](#0-5) . The subsequent POST — which carries `client_id` and `client_secret` in its body — is sent to whatever host `session.shop` resolves to [7](#0-6) .

Whether `auth_query.shop` can actually be attacker-controlled hinges entirely on how the host application constructs the `AuthQuery`. Per the documented usage, the host app is expected to build `AuthQuery` directly from raw request parameters: `ShopifyAPI::Auth::Oauth::AuthQuery.new(request.parameters.symbolize_keys.except(:controller, :action))` [8](#0-7) . This means `shop`, along with `hmac`, is taken verbatim from the query string of the callback request the browser sends. The HMAC check only proves that `shop` matches the value Shopify itself signed when it redirected the browser to this callback with a given `code`; it does not additionally constrain `shop` to be a `myshopify.com`-family domain the way `ShopValidator` does. This is a defense-in-depth gap relative to the rest of the gem's OAuth-adjacent flows, all of which apply `ShopValidator.sanitize!` as a second, independent check before letting any `shop` string decide the destination of a credential-bearing request.

### Impact Explanation
If the HMAC secret protecting the callback were ever compromised, mis-configured (e.g., dual-secret rotation via `old_api_secret_key`, which the validator also accepts [9](#0-8) ), or if a caller ever builds `AuthQuery` from a subset of fields/relies on a different validation order, the missing `ShopValidator` check removes the second line of defense that exists everywhere else credentials are sent, and the request carrying `client_id`/`client_secret` would go to a non-Shopify host under attacker's control. That satisfies the report's SSRF-with-credentials class (High).

### Likelihood Explanation
Low-to-moderate. Exploitation requires a scenario where the `shop` value reaching `validate_auth_callback` fails to be constrained to a genuine Shopify domain despite passing HMAC validation — e.g. secret confusion/rotation edge cases, or host applications that don't strictly mirror the documented flow. Under the documented, correctly-configured flow, HMAC validation over `shop` provides meaningful protection, so this is best framed as a missing defense-in-depth control rather than a directly, trivially exploitable bug given the documented API usage.

### Recommendation
In `ShopifyAPI::Auth::Oauth.validate_auth_callback`, call `Utils::ShopValidator.sanitize!(auth_query.shop)` and use the sanitized value to build `null_session`/`Session.from`, mirroring `ClientCredentials`, `RefreshToken`, and `TokenExchange.migrate_to_expiring_token`, so that the host receiving `client_secret` is always independently constrained to `ShopValidator::TRUSTED_SHOPIFY_DOMAINS` regardless of HMAC outcome.

### Proof of Concept
Not independently reproducible within this gem alone: exploitation requires a host application that constructs `AuthQuery` in a way where `shop` bypasses effective HMAC-domain binding (e.g., secret rotation edge cases) — this could not be concretely demonstrated purely from `lib/shopify_api/**`. The finding is based on directly comparing the validation performed in `Oauth.validate_auth_callback` [10](#0-9)  against the equivalent, `ShopValidator`-guarded flows in `client_credentials.rb`, `refresh_token.rb`, and `token_exchange.rb`.

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

**File:** lib/shopify_api/auth/token_exchange.rb (L103-104)
```ruby
          validated_shop = Utils::ShopValidator.sanitize!(shop)
          shop_session = ShopifyAPI::Auth::Session.new(shop: validated_shop)
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

**File:** lib/shopify_api/utils/hmac_validator.rb (L16-22)
```ruby
          result = validate_signature(verifiable_query, Context.api_secret_key)
          if result || Context.old_api_secret_key.nil? || T.must(Context.old_api_secret_key).empty?
            result
          else
            validate_signature(verifiable_query, T.must(Context.old_api_secret_key))
          end
        end
```
