### Title
Missing shop-domain validation in `Oauth.begin_auth`/`validate_auth_callback` breaks the "authenticated shop == host receiving OAuth credentials" binding - (File: `lib/shopify_api/auth/oauth.rb`)

### Summary
`ShopifyAPI::Auth::Oauth.begin_auth` and `ShopifyAPI::Auth::Oauth.validate_auth_callback` accept a raw `shop` string and use it directly to build the URL that (a) receives the app's `client_id`/redirect and (b) later receives the app's `client_secret` in the `access_token` exchange request, without ever passing it through `Utils::ShopValidator.sanitize!`. By contrast, every other OAuth entry point in this gem (`ClientCredentials.client_credentials`, `RefreshToken.refresh_access_token`, `TokenExchange.exchange_token` via the JWT `dest` claim) explicitly binds the shop used for the request host to a trusted `*.myshopify.com`/`*.myshopify.io`/`spin.dev`/etc. domain via `Utils::ShopValidator`.

### Finding Description
`begin_auth` builds the authorization redirect purely from caller-supplied `shop`: [1](#0-0) 

There is no call to `Utils::ShopValidator.sanitize!` anywhere in `oauth.rb`, unlike the sibling entry points: [2](#0-1) [3](#0-2) 

In `validate_auth_callback`, `auth_query.shop` is used both to build the `null_session` (whose `shop` determines the base URI for the `access_token` POST that carries `Context.api_secret_key`) and as the `shop` stored in the resulting `Session`: [4](#0-3) 

`auth_query.shop` is one of the fields covered by the HMAC signature Shopify computes (`code`, `host`, `shop`, `state`, `timestamp`): [5](#0-4) 

So for the *callback* path, the `shop` value is bound to what Shopify itself signed, and could not be substituted by an unprivileged attacker without knowledge of `api_secret_key`. However, `begin_auth` is the *first* step of the flow and has **no HMAC or trust check on `shop` at all** — it is invoked directly from an unauthenticated request (the docs show it taking `shop` straight from a request header/query parameter: `shop = request.headers["Shop"]`). If the host application forwards this untrusted value as-is (a pattern the gem's own documentation demonstrates), `auth_base_uri(shop)` will construct `https://<attacker-controlled-host>/admin/oauth/authorize?client_id=...&redirect_uri=...&state=<nonce>`, and the user's browser is redirected there.

This breaks the intended binding "the shop redirected-to for authorization == the merchant's real Shopify domain," since the gem exposes a validator (`Utils::ShopValidator`) specifically designed to enforce this equality but never applies it in `begin_auth`.

### Impact Explanation
This maps to "session fixation or forced OAuth completion" (High): an attacker who can influence the `shop` value passed into `begin_auth` (e.g., via a crafted install link where the host app naively passes through a `shop`/`Shop` header or query parameter, as literally shown in this gem's own usage example) can force the victim's browser to be redirected to an attacker-controlled host with the app's `client_id` and the CSRF `state` nonce. Combined with a host application that doesn't itself re-validate `shop`, this enables forced completion of an OAuth flow against an attacker-chosen endpoint, or SSRF-like exfiltration of OAuth flow parameters. It does not by itself leak `client_secret` or an access token (that only happens after a validator-covered HMAC check in `validate_auth_callback`), which limits it to the "High" tier rather than "Critical".

### Likelihood Explanation
Likelihood depends heavily on how the host application sources and forwards the `shop` parameter to `begin_auth`; the gem's own documentation demonstrates passing a raw, unauthenticated `request.headers["Shop"]` value directly into `begin_auth`, making this a realistic pattern for real-world integrations. Since the gem provides no defense-in-depth validation at this specific entry point (while enforcing it everywhere else `shop` is used to build a request host), the likelihood of at least some downstream apps being exposed is non-trivial.

### Recommendation
Apply `Utils::ShopValidator.sanitize!(shop)` inside `Oauth.begin_auth` (and, defensively, on `auth_query.shop` inside `validate_auth_callback` before it is used to build `null_session`/request host) so the shop value used to construct the OAuth redirect and access-token exchange host is always constrained to `Utils::ShopValidator::TRUSTED_SHOPIFY_DOMAINS`, consistent with `ClientCredentials`, `RefreshToken`, and `TokenExchange`.

### Proof of Concept
1. Host application implements the documented pattern:
   ```ruby
   def login
     shop = request.headers["Shop"] # or params[:shop], unauthenticated, attacker-controlled
     auth_response = ShopifyAPI::Auth::Oauth.begin_auth(shop: shop, redirect_path: "/auth/callback")
     redirect_to auth_response[:auth_route]
   end
   ```
2. Attacker sends a victim a link that triggers `login` with `Shop: attacker.evil-server.com`.
3. `Oauth.begin_auth` calls `auth_base_uri("attacker.evil-server.com")`, producing `https://attacker.evil-server.com/admin/oauth/authorize?client_id=<APP_CLIENT_ID>&...&state=<nonce>` (`lib/shopify_api/auth/oauth.rb:117-128`), and the victim's browser is redirected there.
4. Because the gem never calls `Utils::ShopValidator.sanitize!` in this path (contrast with `lib/shopify_api/auth/client_credentials.rb:25` and `lib/shopify_api/auth/refresh_token.rb:24`), no error is raised and the flow proceeds against the attacker's host.

Note: full exploitability is contingent on the specific host application's handling of the `shop` input before calling `begin_auth`; this cannot be fully confirmed without seeing a specific downstream integration, which is outside this gem's index.

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
