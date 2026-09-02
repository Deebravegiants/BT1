Confirmed: the gem's own security-sensitive OAuth entry points show an inconsistent binding pattern. `ClientCredentials.client_credentials`, `RefreshToken.refresh_access_token`, and `TokenExchange.migrate_to_expiring_token` all call `Utils::ShopValidator.sanitize!(shop)` before using the value to build the request host that receives `client_secret` [1](#0-0) [2](#0-1) [3](#0-2) . But `Oauth.begin_auth` and `Oauth.validate_auth_callback` — the authorization-code grant flow — never call `ShopValidator` at all: `begin_auth` builds `auth_base_uri(shop)` directly from the caller-supplied `shop` string [4](#0-3) , and `validate_auth_callback` builds `null_session = Auth::Session.new(shop: auth_query.shop)` and passes that session straight into `Clients::HttpClient.new(session: null_session, base_path: "/admin/oauth")`, which derives the request host directly from `session.shop` and then POSTs a body containing `client_secret` to that host [5](#0-4) [6](#0-5) .

The binding that should hold is: `host receiving client_secret == a validated *.myshopify.com/myshopify.io host`. Instead it holds only `host receiving client_secret == auth_query.shop`, where `auth_query.shop` is merely one of the several fields covered by the callback's HMAC — the HMAC proves the query was signed by Shopify with this app's secret, but Shopify itself does not constrain what merchant-supplied "shop" string ends up in that redirect; `AuthQuery#to_signable_string` simply signs whatever `shop` value is present, it doesn't assert that value is a genuine `myshopify.com` domain [7](#0-6) . The gem itself, in `ShopValidator`, documents exactly this attack surface (rejecting `evil.com`, `myshopify.com.evil.com`, path/userinfo tricks, etc.) [8](#0-7) , showing the library authors are aware this value must be sanitized before being trusted as an HTTP host — yet the sanitize step is present in three of the four credential-sending OAuth code paths and missing specifically from `Oauth.begin_auth`/`Oauth.validate_auth_callback`.

### Title
Missing shop-domain validation in `Oauth.begin_auth`/`validate_auth_callback` allows attacker-controlled host to receive `client_secret` - (File: lib/shopify_api/auth/oauth.rb)

### Summary
`ShopifyAPI::Auth::Oauth.begin_auth` and `ShopifyAPI::Auth::Oauth.validate_auth_callback` use the caller/request-supplied `shop` value directly as an HTTP host, without routing it through `Utils::ShopValidator.sanitize!` the way `ClientCredentials`, `RefreshToken`, and `TokenExchange` do for the same `client_secret`-bearing request.

### Finding Description
`begin_auth(shop:, redirect_path:, ...)` builds the authorization URL as `auth_base_uri(shop) + "/oauth/authorize?..."`, where `auth_base_uri` is `"https://#{shop}/admin"` with no domain validation [4](#0-3) . `validate_auth_callback(cookies:, auth_query:)` then constructs `null_session = Auth::Session.new(shop: auth_query.shop)` and uses it to instantiate `Clients::HttpClient`, which sets `@base_uri = "https://#{api_host || session.shop}"` [6](#0-5) ; the client then POSTs `{client_id, client_secret, code, expiring}` to that host's `/admin/oauth/access_token` [5](#0-4) .

`auth_query.shop` is only constrained by the callback HMAC, which is computed over `{code, host, shop, state, timestamp}` [7](#0-6) . That HMAC proves the query was produced by something holding the app's secret (normally Shopify itself, keyed off whatever `shop` the merchant's browser was directed to at `begin_auth` time) — it does not assert that the `shop` string is a genuine `*.myshopify.com`/`*.myshopify.io` domain. Since `begin_auth` never validates the incoming `shop` before using it as the OAuth authorize host, and `validate_auth_callback` never re-validates `auth_query.shop` before using it as the access-token request host, an app that plumbs an unsanitized `shop` value (e.g., from a query parameter or header, as shown in this gem's own docs example `shop = request.headers["Shop"]`) through `begin_auth` will have the entire OAuth code-grant round trip — including the final `client_secret`-bearing POST — target whatever host string was supplied. This is the exact class of host/identity-binding gap the maintainers already recognized and fixed for the sibling grant flows via `ShopValidator.sanitize!`, but the fix was not applied to `Oauth.begin_auth`/`validate_auth_callback`.

### Impact Explanation
This is High severity under the stated impact categories: SSRF with the app's credentials. If an unsanitized `shop` reaches `begin_auth`, `validate_auth_callback`'s access-token exchange sends the app's `client_id` and `client_secret` to an attacker-influenced host rather than a verified Shopify domain, exfiltrating the app's `client_secret` to that host and enabling forced/hijacked OAuth completion.

### Likelihood Explanation
`ClientCredentials`, `RefreshToken`, and `TokenExchange` all treat `shop` as attacker-reachable input requiring `ShopValidator.sanitize!` before it is trusted as a request host — establishing that host applications are expected to (and do) pass raw, unvalidated `shop` strings into this gem's public OAuth API. `Oauth.begin_auth`/`validate_auth_callback` receive the same class of input via the same public API surface but silently skip that check, so any caller following the documented pattern (extracting `shop` from a request parameter/header and calling `begin_auth` directly) is exposed without any indication from the gem that additional validation is required.

### Recommendation
In `Oauth.begin_auth`, call `Utils::ShopValidator.sanitize!(shop)` before computing `auth_base_uri(shop)`. In `Oauth.validate_auth_callback`, sanitize `auth_query.shop` via `Utils::ShopValidator.sanitize!` before constructing `null_session`/`Session.from`, mirroring the pattern already used in `client_credentials.rb`, `refresh_token.rb`, and `token_exchange.rb`.

### Proof of Concept
1. Host app extracts `shop` from an unauthenticated source (per this gem's documented pattern, `request.headers["Shop"]`) and calls `ShopifyAPI::Auth::Oauth.begin_auth(shop: shop, redirect_path: "/auth/callback")` without sanitization.
2. Attacker supplies `shop = "attacker.example"`; `auth_base_uri` produces `https://attacker.example/admin/oauth/authorize?...`, and the merchant's browser (or the attacker directly) completes an authorization step against `attacker.example`, which returns a `code`, `state`, `host`, `timestamp`, and an `hmac` computed with the app's secret if the attacker-controlled endpoint (posing as Shopify, or via a shop the attacker can complete the grant flow for) round-trips these values.
3. The app calls `ShopifyAPI::Auth::Oauth.validate_auth_callback(cookies:, auth_query:)`; because `auth_query.shop` is never sanitized, `Clients::HttpClient` is built with `session.shop == "attacker.example"`, and the subsequent POST to `/admin/oauth/access_token` sends `client_id` and `client_secret` to `https://attacker.example/admin/oauth/access_token` [5](#0-4) .
4. The attacker-controlled host receives the app's `client_secret`, achieving full credential exfiltration.

### Citations

**File:** lib/shopify_api/auth/client_credentials.rb (L25-33)
```ruby
          validated_shop = Utils::ShopValidator.sanitize!(shop)
          shop_session = ShopifyAPI::Auth::Session.new(shop: validated_shop)
          body = {
            client_id: ShopifyAPI::Context.api_key,
            client_secret: ShopifyAPI::Context.api_secret_key,
            grant_type: CLIENT_CREDENTIALS_GRANT_TYPE,
          }

          client = Clients::HttpClient.new(session: shop_session, base_path: "/admin/oauth")
```

**File:** lib/shopify_api/auth/refresh_token.rb (L24-33)
```ruby
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

**File:** lib/shopify_api/auth/token_exchange.rb (L103-115)
```ruby
          validated_shop = Utils::ShopValidator.sanitize!(shop)
          shop_session = ShopifyAPI::Auth::Session.new(shop: validated_shop)
          body = {
            client_id: ShopifyAPI::Context.api_key,
            client_secret: ShopifyAPI::Context.api_secret_key,
            grant_type: TOKEN_EXCHANGE_GRANT_TYPE,
            subject_token: non_expiring_offline_token,
            subject_token_type: RequestedTokenType::OFFLINE_ACCESS_TOKEN.serialize,
            requested_token_type: RequestedTokenType::OFFLINE_ACCESS_TOKEN.serialize,
            expiring: "1",
          }

          client = Clients::HttpClient.new(session: shop_session, base_path: "/admin/oauth")
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

**File:** lib/shopify_api/auth/oauth.rb (L117-119)
```ruby
        sig { params(shop: String).returns(String) }
        def auth_base_uri(shop)
          return "https://#{shop}/admin" unless defined?(DevServer) && shop.include?(".my.shop.dev")
```

**File:** lib/shopify_api/clients/http_client.rb (L12-19)
```ruby
      def initialize(base_path:, session: nil)
        session ||= Context.active_session
        raise Errors::NoActiveSessionError, "No passed or active session" unless session

        api_host = Context.api_host

        @base_uri = T.let("https://#{api_host || session.shop}", String)
        @base_uri_and_path = T.let("#{@base_uri}#{base_path}", String)
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

**File:** test/utils/shop_validator_test.rb (L38-78)
```ruby
      def test_rejects_attacker_controlled_domain
        assert_raises(ShopifyAPI::Errors::InvalidShopError) do
          ShopifyAPI::Utils::ShopValidator.sanitize!("attacker.example")
        end
      end

      def test_rejects_empty_string
        assert_raises(ShopifyAPI::Errors::InvalidShopError) do
          ShopifyAPI::Utils::ShopValidator.sanitize!("")
        end
      end

      def test_rejects_non_shopify_domain
        assert_raises(ShopifyAPI::Errors::InvalidShopError) do
          ShopifyAPI::Utils::ShopValidator.sanitize!("evil.com")
        end
      end

      def test_rejects_shopify_suffix_as_subdomain_of_attacker
        assert_raises(ShopifyAPI::Errors::InvalidShopError) do
          ShopifyAPI::Utils::ShopValidator.sanitize!("myshopify.com.evil.com")
        end
      end

      def test_rejects_similar_looking_domain
        assert_raises(ShopifyAPI::Errors::InvalidShopError) do
          ShopifyAPI::Utils::ShopValidator.sanitize!("test-shop.notmyshopify.com")
        end
      end

      def test_rejects_path_that_suffix_matches_myshopify_host
        assert_raises(ShopifyAPI::Errors::InvalidShopError) do
          ShopifyAPI::Utils::ShopValidator.sanitize!("attacker.com/.myshopify.com")
        end
      end

      def test_rejects_userinfo_before_at_sign
        assert_raises(ShopifyAPI::Errors::InvalidShopError) do
          ShopifyAPI::Utils::ShopValidator.sanitize!("shop.myshopify.com@evil.com")
        end
      end
```
