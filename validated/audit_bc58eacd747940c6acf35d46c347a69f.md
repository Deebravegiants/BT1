This confirms the pattern: `Auth::ClientCredentials.client_credentials` and `Auth::TokenExchange.exchange_token`/`Auth::RefreshToken` all route the `shop` value through `Utils::ShopValidator.sanitize!` before it is used to build the request host that receives `client_secret`. `Auth::Oauth.begin_auth`, however, does not.

### Title
`Auth::Oauth.begin_auth` builds the OAuth authorize URL from an unvalidated `shop` parameter, unlike every other credential-bearing flow in the gem - (File: `lib/shopify_api/auth/oauth.rb`)

### Summary
`ShopifyAPI::Auth::Oauth.begin_auth` takes a caller-supplied `shop:` string and feeds it directly into `auth_base_uri(shop)` to build `auth_route`, the URL to which the app redirects the merchant's browser (with `client_id`, `scope`, and `redirect_uri` in the query string) to begin OAuth. [1](#0-0)  Unlike `ClientCredentials.client_credentials`, `TokenExchange.exchange_token`, and `RefreshToken`, which all call `Utils::ShopValidator.sanitize!(shop)` before using the shop value to build a request host, `begin_auth` performs no such check. [2](#0-1)  `auth_base_uri` uses the raw string verbatim: `"https://#{shop}/admin"`. [3](#0-2) 

### Finding Description
The binding that should hold is: *the host that the merchant's browser is redirected to for authorization == a trusted `*.myshopify.com` (or configured) domain*, the same binding enforced by `Utils::ShopValidator.sanitize!` for every other host-building path in this gem (`client_credentials.rb`, `token_exchange.rb`, `refresh_token.rb`). [4](#0-3)  `begin_auth` breaks that binding: it never calls `ShopValidator`, so `shop` can be any string reachable from host-application input (the gem's own docs show `shop = request.headers["Shop"]` feeding this call directly). [5](#0-4) 

Downstream in `validate_auth_callback`, the callback's `shop`/`hmac`/`state`/`code` are properly HMAC-verified against `Context.api_secret_key` before the access-token request is issued [6](#0-5) , so the token-exchange leg cannot be forged by someone who doesn't hold the app secret. The exposure is confined to `begin_auth`: it discloses `client_id`, the requested `scope`, and the app's `redirect_uri` to an attacker-chosen host, and it lets an attacker fully control where the merchant's browser is sent for "authorization" before any HMAC protection applies.

### Impact Explanation
This does not by itself yield `client_secret` or an access token — the OAuth callback HMAC check still gates the token exchange. The impact is bounded to: open-redirect of the authorization step to an attacker-controlled host, disclosure of `client_id`/`scope`/`redirect_uri`, and a forced/likely confusing OAuth initiation flow that could be used as one leg of a phishing chain against the merchant. It does not meet the "High: forced OAuth completion" bar cleanly because the callback-side HMAC binding (already present and correct) prevents the attacker from completing the flow without the app secret.

### Likelihood Explanation
Reachable only if the host application passes attacker-influenced input as `shop:` to `begin_auth` without its own validation — which the gem's own documented usage pattern (`shop = request.headers["Shop"]`) explicitly encourages. [7](#0-6) 

### Recommendation
Call `Utils::ShopValidator.sanitize!(shop)` at the top of `Auth::Oauth.begin_auth`, mirroring `ClientCredentials.client_credentials`, so the `shop` used to build `auth_route` is bound to a trusted Shopify domain before any redirect is constructed.

### Proof of Concept
Given the documented usage pattern:
```ruby
shop = request.headers["Shop"]   # attacker-influenced
ShopifyAPI::Auth::Oauth.begin_auth(shop: shop, redirect_path: "/auth/callback")
```
calling `begin_auth(shop: "attacker.example", redirect_path: "/auth/callback")` returns `auth_route = "https://attacker.example/admin/oauth/authorize?client_id=...&scope=...&redirect_uri=https://myapp.com/auth/callback&state=...&grant_options%5B%5D=..."` with no `InvalidShopError` raised, whereas the equivalent `ShopifyAPI::Auth::ClientCredentials.client_credentials(shop: "attacker.example")` correctly raises `ShopifyAPI::Errors::InvalidShopError` per `test_client_credentials_rejects_non_shopify_domain`. [8](#0-7)

### Citations

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

**File:** lib/shopify_api/utils/shop_validator.rb (L20-64)
```ruby
      class << self
        extend T::Sig

        sig do
          params(
            shop_domain: String,
            myshopify_domain: T.nilable(String),
          ).returns(T.nilable(String))
        end
        def sanitize_shop_domain(shop_domain, myshopify_domain: nil)
          uri = uri_from_shop_domain(shop_domain, myshopify_domain)
          return nil if uri.nil? || uri.host.nil? || uri.host.empty?

          trusted_domains(myshopify_domain).each do |trusted_domain|
            host = T.cast(uri.host, String)
            uri_domain = uri.domain
            next if uri_domain.nil?

            no_shop_name_in_subdomain = host == trusted_domain
            from_trusted_domain = trusted_domain == uri_domain

            if unified_admin?(uri) && from_trusted_domain
              return myshopify_domain_from_unified_admin(uri)
            end
            return nil if no_shop_name_in_subdomain || host.empty?
            return host if from_trusted_domain
          end
          nil
        end

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

**File:** docs/usage/oauth.md (L180-199)
```markdown
class ShopifyAuthController < ApplicationController
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

**File:** test/auth/client_credentials_test.rb (L33-37)
```ruby
      def test_client_credentials_rejects_non_shopify_domain
        assert_raises(ShopifyAPI::Errors::InvalidShopError) do
          ShopifyAPI::Auth::ClientCredentials.client_credentials(shop: "attacker.example")
        end
      end
```
