Confirmed. `ShopValidator.sanitize!`/`sanitize_shop_domain` is used in `token_exchange.rb`, `client_credentials.rb`, and `refresh_token.rb`, but is **not** used anywhere in `lib/shopify_api/auth/oauth.rb`. This means the authorization-code grant flow (`begin_auth`/`validate_auth_callback`) is the one flow in this gem that builds a request host directly from an unsanitized `shop` string, unlike the other three OAuth flows which explicitly validate the shop domain against `ShopValidator::TRUSTED_SHOPIFY_DOMAINS`.

### Title
Missing shop-domain validation lets a crafted `shop` value redirect the OAuth authorize request and misdirect the access-token exchange host - (File: `lib/shopify_api/auth/oauth.rb`)

### Summary
`ShopifyAPI::Auth::Oauth.begin_auth` and `ShopifyAPI::Auth::Oauth.validate_auth_callback` both take a caller-supplied `shop` string and use it verbatim to construct the host that receives OAuth traffic, without ever calling `Utils::ShopValidator.sanitize!` (used by every other OAuth flow — `TokenExchange`, `ClientCredentials`, `RefreshToken`) to constrain it to a trusted Shopify domain.

### Finding Description
In `begin_auth`, the authorize URL is built as `auth_base_uri(shop) + "/oauth/authorize?..."`, where `auth_base_uri` returns `"https://#{shop}/admin"` with no domain check: [1](#0-0) 

In `validate_auth_callback`, the value comes from `auth_query.shop`, and after HMAC validation a `null_session` is built directly from it and handed to `HttpClient`, which sends the app's `client_id`/`client_secret` (`Context.api_secret_key`) to `https://#{session.shop}` in an `access_token` POST: [2](#0-1) [3](#0-2) 

Contrast this with the other OAuth flows that all call `Utils::ShopValidator.sanitize!` (or `sanitize_shop_domain`) before constructing any request host, restricting `shop` to `TRUSTED_SHOPIFY_DOMAINS` (`shopify.com`, `myshopify.io`, `myshopify.com`, `spin.dev`, `shop.dev`) or the configured `myshopify_domain`: [4](#0-3) 

The binding that should hold is: *host that receives `client_secret` == a domain in `ShopValidator::TRUSTED_SHOPIFY_DOMAINS`*. In `oauth.rb`, that equality is never checked; `auth_query.shop` is only checked by `Utils::HmacValidator.validate` (i.e., the bytes match what was signed with `api_secret_key`), not that the *value itself* is a legitimate Shopify host. The HMAC proves message integrity for whatever `shop` string was signed — it does not constrain the shop string's format, so if the host application forwards a `shop` value at `begin_auth`-time that was never format-validated (this gem provides no such validation for this flow, unlike its own other flows), the resulting authorize redirect and, if such a query is echoed back with a matching signature, the token-exchange POST target are attacker-influenced.

### Impact Explanation
If `auth_base_uri`/`validate_auth_callback`'s host resolution is reachable with an attacker-influenced `shop` (e.g., a host app that passes through a user-supplied `shop=` query parameter, as is typical for the install-initiation step, without itself validating it — since this gem, unlike its sibling flows, offers no built-in `ShopValidator` call here to protect that path), the `client_secret` can be POSTed to an attacker-controlled host during `validate_auth_callback`, and the authorize redirect can be steered off-Shopify at `begin_auth`. This lines up with the SSRF/credential-leakage impact category (SSRF with the app's credentials, credential leakage in transit) since `client_secret` — the same credential the report's bug class centers on — is sent based on an unchecked identity field.

### Likelihood Explanation
Medium: exploitation requires the host application not to independently vet `shop` before calling `begin_auth`/before accepting `validate_auth_callback`'s output — many `shopify_app`-style integrations do perform their own shop-format checks — but this gem itself, unlike its own `TokenExchange`/`ClientCredentials`/`RefreshToken` counterparts, provides no defense-in-depth `ShopValidator.sanitize!` call in the authorization-code grant path, which is inconsistent and is the direct analog of the missing-equality-check pattern in the report (a value trusted for one purpose — HMAC integrity — is treated as if it were also validated for another purpose — trusted host).

### Recommendation
Call `Utils::ShopValidator.sanitize!(shop, myshopify_domain: Context.custom_shop_domains)` (mirroring `token_exchange.rb`/`client_credentials.rb`/`refresh_token.rb`) at the top of `begin_auth` and immediately after HMAC validation succeeds in `validate_auth_callback`, before `auth_query.shop` is used to build `null_session` or any request host, raising `Errors::InvalidShopError` on failure just as the other flows do.

### Proof of Concept
1. A host application exposes an install endpoint that calls `ShopifyAPI::Auth::Oauth.begin_auth(shop: params[:shop], redirect_path: "/callback")` without itself validating `params[:shop]` (the gem offers no validation to fall back on for this flow).
2. Attacker requests `.../install?shop=attacker.example.com`.
3. `auth_base_uri("attacker.example.com")` returns `"https://attacker.example.com/admin"`, and `begin_auth` returns `auth_route = "https://attacker.example.com/admin/oauth/authorize?client_id=...&scope=...&redirect_uri=https://app.example.com/callback&state=NONCE"`, which the host app then redirects the merchant's browser to — compare with `lib/shopify_api/auth/oauth.rb:117-128` where no call to `Utils::ShopValidator` occurs, unlike `lib/shopify_api/auth/token_exchange.rb`'s use of the same validator.
4. If the host app subsequently constructs a session from an unvalidated `shop` and calls `validate_auth_callback` on a request whose `hmac` was computed by whatever party controls that flow, `client.request` in `lib/shopify_api/clients/http_client.rb:11-19` sends `Context.api_secret_key` in the POST body to `https://#{session.shop}/admin/oauth/access_token`, i.e., to `attacker.example.com`.

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

**File:** lib/shopify_api/utils/shop_validator.rb (L6-18)
```ruby
module ShopifyAPI
  module Utils
    module ShopValidator
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
