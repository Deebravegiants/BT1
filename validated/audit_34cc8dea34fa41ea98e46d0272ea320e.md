This confirms `client_credentials.rb` and `token_exchange.rb` explicitly call `Utils::ShopValidator.sanitize!(shop)` before constructing the `Session` used to build the `HttpClient` request that carries `client_secret`. `ShopifyAPI::Auth::Oauth.validate_auth_callback`, however, never calls `ShopValidator` on `auth_query.shop` — it builds `null_session = Auth::Session.new(shop: auth_query.shop)` directly and hands it to `Clients::HttpClient`, whose constructor sets `@base_uri = "https://#{api_host || session.shop}"` [1](#0-0) , meaning the destination host for the POST carrying `client_id`/`client_secret`/`code` is taken verbatim from `auth_query.shop` [2](#0-1) .

### Title
OAuth Callback `shop` Not Validated Against Trusted Shopify Domains Before `client_secret` Is Sent - (File: lib/shopify_api/auth/oauth.rb)

### Summary
`ShopifyAPI::Auth::Oauth.validate_auth_callback` uses `auth_query.shop` to build the session whose `shop` value becomes the HTTP host that receives the POST containing `client_id`, `client_secret`, and the authorization `code`, without ever passing it through `Utils::ShopValidator.sanitize!`, unlike the sibling `client_credentials.rb` and `token_exchange.rb` flows.

### Finding Description
`validate_auth_callback` first verifies the HMAC over `code`, `host`, `shop`, `state`, `timestamp` via `Utils::HmacValidator.validate(auth_query)` [3](#0-2) . This proves the *bytes* of `shop` weren't tampered with relative to what was HMAC-signed, but it does not prove the *semantic* identity binding that other flows in this gem enforce: that `shop` is a `*.myshopify.com`/trusted Shopify domain. Compare with `ClientCredentials.client_credentials`, which calls `validated_shop = Utils::ShopValidator.sanitize!(shop)` before constructing the session used for the `client_secret`-bearing request [4](#0-3) , and `TokenExchange`, which derives the shop from a cryptographically-verified JWT `dest` claim [5](#0-4) .

In `validate_auth_callback`, `auth_query.shop` flows unchecked into `null_session = Auth::Session.new(shop: auth_query.shop)` and then into `Clients::HttpClient.new(session: null_session, ...)` [6](#0-5) , and `HttpClient#initialize` builds the request's base URI directly from `session.shop`: `@base_uri = "https://#{api_host || session.shop}"` [1](#0-0) . The identity binding broken is: *the host that receives the app's `client_secret`* should equal *a trusted Shopify domain*, but the code only checks that `shop` equals whatever value the HMAC happened to be computed over — it never checks that value is actually `*.myshopify.com` (or another `TRUSTED_SHOPIFY_DOMAINS` entry) the way `ShopValidator.sanitize!` does [7](#0-6) .

### Impact Explanation
Whether this is exploitable by an unprivileged internet user depends entirely on whether the host application passes a raw, attacker-influenced `shop` value into `ShopifyAPI::Auth::Oauth.begin_auth`/`validate_auth_callback` without its own validation. This gem's own `begin_auth` also builds the authorize redirect URL directly from the caller-supplied `shop` with no `ShopValidator` check: `auth_route = auth_base_uri(shop) + "/oauth/authorize?..."` [8](#0-7) . If a host app is misled by a crafted `shop` query parameter through the whole round trip, `validate_auth_callback` will faithfully send this library's `client_secret` to whatever host is embedded in `shop`, since neither `begin_auth` nor `validate_auth_callback` restrict it to trusted Shopify domains the way the other credential-exchange paths in this same gem do.

### Likelihood Explanation
Low-to-moderate on its own within this gem, because a valid HMAC over the crafted `shop`/`code`/`state` combination is still required, and this gem does not expose a way to forge that without the `api_secret_key`. The realistic risk surface is that this inconsistency (missing `sanitize!` call present in the analogous `client_credentials.rb`/`token_exchange.rb` flows) means this specific credential-exfiltration guard that exists elsewhere in the gem is absent here, which is the same "field acted upon but not properly re-validated" bug class as the FCN report (which trusted a value on one code path but not on the sibling path that produced the actual state transition).

### Recommendation
In `ShopifyAPI::Auth::Oauth.validate_auth_callback` (and `begin_auth`), call `Utils::ShopValidator.sanitize!(auth_query.shop)` (mirroring `client_credentials.rb`/`token_exchange.rb`) before constructing `null_session`/the authorize URL, so the host that ultimately receives `client_secret` is guaranteed to be a `TRUSTED_SHOPIFY_DOMAINS` member.

### Proof of Concept
1. A host application built on this gem passes a browser-supplied `shop` parameter straight through to `ShopifyAPI::Auth::Oauth.begin_auth(shop: params[:shop], ...)` without its own domain check (the gem itself does no such check in `begin_auth`/`auth_base_uri`).
2. The corresponding `auth_query.shop` value is echoed through the OAuth flow with a valid Shopify-issued HMAC.
3. `validate_auth_callback` accepts this `shop` as-is (no `ShopValidator.sanitize!` call), builds `null_session` from it, and `Clients::HttpClient` sends the POST containing `client_secret`/`code` to `https://#{auth_query.shop}/admin/oauth/access_token` — a host not verified to be a genuine Shopify domain.

### Citations

**File:** lib/shopify_api/clients/http_client.rb (L16-19)
```ruby
        api_host = Context.api_host

        @base_uri = T.let("https://#{api_host || session.shop}", String)
        @base_uri_and_path = T.let("#{@base_uri}#{base_path}", String)
```

**File:** lib/shopify_api/auth/oauth.rb (L60-71)
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
```

**File:** lib/shopify_api/auth/oauth.rb (L73-94)
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
          rescue ShopifyAPI::Errors::HttpResponseError => e
            raise Errors::RequestAccessTokenError,
              "Cannot complete OAuth process. Received a #{e.code} error while requesting access token."
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

**File:** lib/shopify_api/auth/token_exchange.rb (L39-51)
```ruby
          # Validate the session token and use the shop from the token's `dest` claim
          jwt_payload = ShopifyAPI::Auth::JwtPayload.new(session_token)
          dest_shop = jwt_payload.shop

          if shop
            ShopifyAPI::Logger.deprecated(
              "The `shop` parameter for `exchange_token` is deprecated and will be removed in v17. " \
                "The shop is now always taken from the session token's `dest` claim.",
              "17.0.0",
            )
          end

          shop_session = ShopifyAPI::Auth::Session.new(shop: dest_shop)
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
