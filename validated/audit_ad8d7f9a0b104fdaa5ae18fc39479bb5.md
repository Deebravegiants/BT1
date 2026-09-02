### Title
`ShopifyAPI::Auth::Oauth.validate_auth_callback` sends the app's `client_secret` to an unsanitized `shop` host - (File: `lib/shopify_api/auth/oauth.rb`)

### Summary
`Oauth.validate_auth_callback` builds an `Auth::Session` from the raw `auth_query.shop` value and uses it, unsanitized, as the destination host to which the app's `client_secret` and `client_id` are POSTed when exchanging the authorization code for an access token. Every sibling OAuth-credential-sending method in this gem (`ClientCredentials.client_credentials`, `RefreshToken.refresh_access_token`) explicitly calls `Utils::ShopValidator.sanitize!(shop)` before doing the same thing — `validate_auth_callback` is the outlier that skips this domain check.

### Finding Description
`HttpClient#initialize` derives the request host directly from `session.shop`: [1](#0-0) . In `validate_auth_callback`, this `session.shop` comes straight from `auth_query.shop` with no domain validation, and the request body includes `Context.api_secret_key`: [2](#0-1) 

Compare this to the two other flows in the same module tree that also send `client_secret` over HTTP to a shop-derived host — both call `Utils::ShopValidator.sanitize!(shop)` first: [3](#0-2) [4](#0-3) 

The only protection on `auth_query.shop` in the callback path is the HMAC check: [5](#0-4) . The HMAC (`AuthQuery#to_signable_string`) does bind `shop` as one of the signed fields [6](#0-5) , so a value can only pass `HmacValidator.validate` if it was signed with `Context.api_secret_key` — meaning under normal operation only genuine Shopify-issued callbacks (with a genuine `.myshopify.com` shop) can reach this code path. The identity-binding gap is that the equality the gem should enforce — *"the host that receives `client_secret` == a domain in `ShopValidator::TRUSTED_SHOPIFY_DOMAINS`"* — is never checked here, unlike in the sibling flows. The HMAC only proves *integrity of the message contents*, not that `shop` is a legitimate Shopify domain.

### Impact Explanation
I was not able to construct a concrete exploit path in which an unprivileged internet user (without already possessing `Context.api_secret_key`) can force `auth_query.shop` to be an attacker-controlled host while still passing `HmacValidator.validate`. `begin_auth` does redirect the browser to `https://#{shop}/admin/oauth/authorize` using an unvalidated `shop` [7](#0-6) , which could send a victim's browser to an attacker-chosen host, but I could not verify a way for that attacker-controlled host to subsequently forge a valid `hmac` for a crafted callback without the shared secret. Because the rules require a concrete, credential-boundary-crossing exploit (SSRF carrying the app's credentials, without requiring the secret itself), and I cannot demonstrate that the missing `ShopValidator.sanitize!` call is independently reachable by an attacker who does not already hold `api_secret_key`, this does not meet the bar for a confirmed High/Critical finding under the stated rules.

### Likelihood Explanation
Low/unconfirmed as a standalone exploit given current analysis — the missing validation is a genuine inconsistency with the rest of the gem's own credential-sending code paths (defense-in-depth gap), but exploitability without the shared secret was not established.

### Recommendation
For consistency and defense-in-depth, `validate_auth_callback` should call `Utils::ShopValidator.sanitize!(auth_query.shop)` (as `client_credentials` and `refresh_access_token` already do) before constructing `null_session` and sending `client_id`/`client_secret` to that host, so the destination of the credential-bearing POST is always constrained to a `ShopValidator::TRUSTED_SHOPIFY_DOMAINS` domain regardless of HMAC outcome.

### Proof of Concept
Not established — I could not confirm an attacker-reachable path to control `auth_query.shop` while still producing a valid `hmac` without possessing `Context.api_secret_key`. This is noted as an unverified/incomplete area of the investigation rather than a proven vulnerability.

### Citations

**File:** lib/shopify_api/clients/http_client.rb (L16-19)
```ruby
        api_host = Context.api_host

        @base_uri = T.let("https://#{api_host || session.shop}", String)
        @base_uri_and_path = T.let("#{@base_uri}#{base_path}", String)
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

**File:** lib/shopify_api/auth/oauth.rb (L60-64)
```ruby
        def validate_auth_callback(cookies:, auth_query:)
          unless Context.setup?
            raise Errors::ContextNotSetupError, "ShopifyAPI::Context not setup, please call ShopifyAPI::Context.setup"
          end
          raise Errors::InvalidOauthError, "Invalid OAuth callback." unless Utils::HmacValidator.validate(auth_query)
```

**File:** lib/shopify_api/auth/oauth.rb (L73-81)
```ruby
          null_session = Auth::Session.new(shop: auth_query.shop)
          body = {
            client_id: Context.api_key,
            client_secret: Context.api_secret_key,
            code: auth_query.code,
            expiring: Context.expiring_offline_access_tokens ? 1 : 0, # Only applicable for offline tokens
          }

          client = Clients::HttpClient.new(session: null_session, base_path: "/admin/oauth")
```

**File:** lib/shopify_api/auth/client_credentials.rb (L19-33)
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
