Found a valid analog: `ShopifyAPI::Auth::Oauth.validate_auth_callback` in `lib/shopify_api/auth/oauth.rb` uses the HMAC-verified `shop` field from the OAuth callback query to build the base URI that the `client_secret` and authorization `code` are sent to, but it never checks that `shop` is a genuine `*.myshopify.com` domain before doing so — unlike `TokenExchange.migrate_to_expiring_token`, which does call `Utils::ShopValidator.sanitize!(shop)` before use.

### Title
SSRF exfiltrating `client_secret` and authorization code via unvalidated `shop` in OAuth callback - (File: lib/shopify_api/auth/oauth.rb)

### Summary
`Oauth.validate_auth_callback` verifies the HMAC over the callback query parameters, but the `shop` parameter itself is never checked to be a real Shopify domain (via `Utils::ShopValidator`) before it is used to construct the base URI to which the app's `client_id`, `client_secret`, and authorization `code` are POSTed.

### Finding Description
`validate_auth_callback` HMAC-validates the query via `Utils::HmacValidator.validate(auth_query)` [1](#0-0) , which is computed over `code`, `host`, `shop`, `state`, `timestamp` as defined in `AuthQuery#to_signable_string` [2](#0-1) . It then builds `null_session = Auth::Session.new(shop: auth_query.shop)` and POSTs `client_id`, `client_secret`, and `code` to `Clients::HttpClient.new(session: null_session, base_path: "/admin/oauth")` [3](#0-2) . `HttpClient#initialize` sets `@base_uri = "https://#{api_host || session.shop}"` and sends the request to that host [4](#0-3) . Unlike `TokenExchange.migrate_to_expiring_token`, which validates the shop with `Utils::ShopValidator.sanitize!(shop)` before constructing the session [5](#0-4) , `validate_auth_callback` has no equivalent check on `auth_query.shop`.

The identity binding broken here is: "the host validated (a trusted `*.myshopify.com`/allow-listed domain) versus the host that receives the access-token request body containing `client_secret`". The HMAC in `validate_auth_callback` proves the query bytes came from Shopify's servers signed with the app's secret, but it does not by itself constrain `shop` to a value matching Shopify's own domain suffixes at the point of use — it only guarantees Shopify signed *some* string called `shop`. If Shopify's authorize endpoint could be coerced into echoing back an attacker-influenced `shop` value in the signed callback (e.g., through an app misusing `begin_auth` with an unsanitized shop, since `begin_auth` also does not call `ShopValidator` on its `shop` parameter before building `auth_base_uri(shop)` and sending the user there [6](#0-5) ), the resulting HMAC-signed callback would carry that same non-Shopify `shop` value, and `validate_auth_callback` would send `client_id`/`client_secret`/`code` to that attacker-controlled host.

### Impact Explanation
If reachable, this results in the app's `client_secret` and a live authorization code being sent to a host outside `myshopify.com`/trusted Shopify domains — classified as SSRF carrying the app's credentials (High/Critical per the exfiltration criteria), since the `client_secret` is the gem's most sensitive credential and its leak enables full OAuth impersonation of the app.

### Likelihood Explanation
This is a **plausible but not conclusively proven** analog. The gem's own `ShopValidator` module (with `TRUSTED_SHOPIFY_DOMAINS`) exists precisely to prevent unvalidated shop domains from being used for host construction, and it is applied in `TokenExchange.migrate_to_expiring_token` and other flows, but conspicuously absent in both `Oauth.begin_auth` and `Oauth.validate_auth_callback`. Whether an unprivileged internet user can actually get Shopify's real `/admin/oauth/authorize` endpoint to sign back an attacker-controlled `shop` value (rather than merely relying on the host application to pass a bad `shop` into `begin_auth`, which would be an integration issue out of this gem's control) could not be fully confirmed with the available tools — the strength of this finding depends on whether a caller can drive `begin_auth`/`validate_auth_callback` with attacker input reaching Shopify's signing service, which requires further tracing of how the host app supplies `shop` and whether Shopify itself validates it before signing the callback.

### Recommendation
Call `Utils::ShopValidator.sanitize!(shop)` (or `sanitize_shop_domain`) on `auth_query.shop` in `validate_auth_callback` before constructing `null_session`/`HttpClient`, mirroring the check already present in `TokenExchange.migrate_to_expiring_token`. Apply the same validation to the `shop` parameter accepted by `begin_auth` before using it in `auth_base_uri`.

### Proof of Concept
Not independently reproducible from the index alone; conceptually: an app integrator (or any flow feeding an un-sanitized `shop` into `begin_auth`) could initiate OAuth with a non-`myshopify.com` `shop` value; if the resulting callback query is signed by Shopify with that same `shop` value intact, `validate_auth_callback` will construct a request to `https://<attacker-controlled-shop>/admin/oauth/access_token` and transmit `client_secret` there, as traced through `lib/shopify_api/auth/oauth.rb` lines 73–90 and `lib/shopify_api/clients/http_client.rb` lines 16–19.

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

**File:** lib/shopify_api/auth/oauth.rb (L60-64)
```ruby
        def validate_auth_callback(cookies:, auth_query:)
          unless Context.setup?
            raise Errors::ContextNotSetupError, "ShopifyAPI::Context not setup, please call ShopifyAPI::Context.setup"
          end
          raise Errors::InvalidOauthError, "Invalid OAuth callback." unless Utils::HmacValidator.validate(auth_query)
```

**File:** lib/shopify_api/auth/oauth.rb (L73-90)
```ruby
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

**File:** lib/shopify_api/clients/http_client.rb (L16-19)
```ruby
        api_host = Context.api_host

        @base_uri = T.let("https://#{api_host || session.shop}", String)
        @base_uri_and_path = T.let("#{@base_uri}#{base_path}", String)
```

**File:** lib/shopify_api/auth/token_exchange.rb (L103-104)
```ruby
          validated_shop = Utils::ShopValidator.sanitize!(shop)
          shop_session = ShopifyAPI::Auth::Session.new(shop: validated_shop)
```
