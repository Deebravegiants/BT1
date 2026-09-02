### Title
OAuth callback exchanges the app's `client_secret` with an unvalidated `shop` host, allowing SSRF/token exfiltration via `Auth::Oauth.validate_auth_callback` - (File: `lib/shopify_api/auth/oauth.rb`)

### Summary
`ShopifyAPI::Auth::Oauth.validate_auth_callback` takes the `shop` value from the incoming `AuthQuery`, HMAC-verifies the query bytes, and then uses that same unsanitized `shop` string to build the URL that receives the app's `client_id`/`client_secret` and the OAuth `code` — without ever routing it through `Utils::ShopValidator.sanitize!`, unlike the sibling flows `TokenExchange` and `ClientCredentials`.

### Finding Description
`AuthQuery#to_signable_string` builds the HMAC-covered string from `code, host, shop, state, timestamp` [1](#0-0) , and `HmacValidator.validate` confirms these bytes were signed by `Context.api_secret_key` [2](#0-1) . This only proves the *bytes were not tampered with after signing* — it does not prove `shop` is a legitimate `*.myshopify.com` host.

`validate_auth_callback` then takes `auth_query.shop` directly (no `ShopValidator.sanitize!` call anywhere in `oauth.rb`) and uses it to:
1. Build a `null_session` with `shop: auth_query.shop` [3](#0-2) 
2. Compose the request body containing `client_id`, `client_secret` (the app's secret), and `code` [4](#0-3) 
3. Send that body via `Clients::HttpClient.new(session: null_session, base_path: "/admin/oauth")`, where `HttpClient#initialize` builds `@base_uri = "https://#{api_host || session.shop}"` directly from `session.shop` [5](#0-4) , then POSTs to `access_token` on that host [6](#0-5) 

Compare this to `ClientCredentials.client_credentials` and `TokenExchange.migrate_to_expiring_token`, which both call `Utils::ShopValidator.sanitize!(shop)` before constructing the session used to derive the request host [7](#0-6) , [8](#0-7) . `oauth.rb` has no equivalent check — the binding "host validated == host that receives the `client_secret`" is broken: the host is HMAC-*verified-as-unmodified* but never *validated* against `ShopValidator::TRUSTED_SHOPIFY_DOMAINS`.

Root cause: `Auth::Oauth.validate_auth_callback` (`lib/shopify_api/auth/oauth.rb`, lines 60–113) omits the `ShopValidator.sanitize!` call that exists in the parallel `TokenExchange`/`ClientCredentials` code paths.

### Impact Explanation
If a host application accepts an OAuth query string (e.g., copies query params from the callback URL into `AuthQuery.new`) whose `shop` value can be influenced to a non-`myshopify.com` value while still satisfying the app's own record of a valid `state` cookie (e.g., a merchant with an active OAuth session), the library will POST the app's `client_id` and `client_secret` and the OAuth authorization `code` to an attacker-controlled host at `https://<shop>/admin/oauth/access_token`. This is SSRF carrying the app's credentials and can result in exfiltration of the `client_secret` and authorization code (usable to mint an access token), i.e., Critical-tier impact (theft of the app's `client_secret`/authorization artifacts).

### Likelihood Explanation
Exploitation requires the attacker to produce an `AuthQuery` (or otherwise reach `validate_auth_callback`) with a `shop` value that isn't Shopify's own domain. Because `Utils::HmacValidator.validate` requires a signature computed with `Context.api_secret_key`, in the normal browser-redirect flow the `shop`/`hmac` pair originates from Shopify and can't be forged without the secret — this substantially limits real-world reachability of the SSRF from a purely external, credential-less attacker. The higher-likelihood risk is defense-in-depth failure: this is the only OAuth-completion path in the gem lacking the same-domain check that `ClientCredentials`/`TokenExchange` enforce, so any host application flow that lets a non-Shopify-originated `shop` reach `validate_auth_callback` (e.g. replaying/crafting query parameters, or environments where the HMAC secret has been rotated/leaked through another channel) loses this safety net entirely.

### Recommendation
In `lib/shopify_api/auth/oauth.rb`, validate `auth_query.shop` with `Utils::ShopValidator.sanitize!(auth_query.shop)` immediately after HMAC validation and before it is used to build `null_session` / the access-token request, mirroring the pattern already used in `client_credentials.rb` and `token_exchange.rb`.

### Proof of Concept
1. Craft (or obtain) an `AuthQuery` where `shop` is not a `*.myshopify.com`/trusted domain (e.g. `attacker.example.com`) but whose HMAC still validates for the current `Context.api_secret_key`/`old_api_secret_key` (e.g., in a test/dev environment, or via key rotation windows where the old secret is exposed through another vector).
2. Set a matching `state` cookie so `validate_auth_callback` passes the state check.
3. Call `ShopifyAPI::Auth::Oauth.validate_auth_callback(cookies: cookies, auth_query: auth_query)`.
4. Observe that `Clients::HttpClient` sends a POST containing `client_id`, `client_secret`, and `code` to `https://attacker.example.com/admin/oauth/access_token` [9](#0-8) [5](#0-4) , exfiltrating the app's `client_secret` to the attacker-controlled host.

### Citations

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

**File:** lib/shopify_api/auth/oauth.rb (L64-94)
```ruby
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

**File:** lib/shopify_api/clients/http_client.rb (L16-19)
```ruby
        api_host = Context.api_host

        @base_uri = T.let("https://#{api_host || session.shop}", String)
        @base_uri_and_path = T.let("#{@base_uri}#{base_path}", String)
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
