## Finding: Unsanitized `shop` in `Oauth.validate_auth_callback` used as SSRF target for `client_secret` (`lib/shopify_api/auth/oauth.rb`)

### Summary
`refresh_access_token`, `client_credentials`, and `migrate_to_expiring_token` all call `Utils::ShopValidator.sanitize!(shop)` before using the `shop` value to build the request host that receives the app's `client_id`/`client_secret` [1](#0-0) [2](#0-1) [3](#0-2) . `ShopifyAPI::Auth::Oauth.validate_auth_callback`, the analogous authorization-code-grant flow, does **not**: it takes `auth_query.shop` straight from the incoming callback request and passes it unsanitized into `auth_base_uri(shop)`, which becomes the host that the app's `client_secret` is POSTed to [4](#0-3) [5](#0-4) .

### Finding Description
The binding that should hold is: **shop == a domain in `ShopValidator::TRUSTED_SHOPIFY_DOMAINS`** before it is used as the destination host for a request carrying `client_secret`. That invariant is enforced in three of the four OAuth-adjacent flows via `Utils::ShopValidator.sanitize!` [6](#0-5) , but it is missing from `validate_auth_callback`.

Instead, `validate_auth_callback` only checks that `auth_query.shop` — along with `code`, `host`, `state`, `timestamp` — matches the `hmac` supplied in the same query, using `Utils::HmacValidator.validate` [7](#0-6) [8](#0-7) . HMAC validation proves that `shop` was not tampered with in transit relative to the query that was signed — it does **not** prove that `shop` is a `*.myshopify.com`/trusted admin host. There is no format/domain check on `shop` anywhere in `oauth.rb`.

That unsanitized value is then used directly:
```ruby
client = Clients::HttpClient.new(session: null_session, base_path: "/admin/oauth")
...
path: "access_token"
```
`HttpClient` derives its request host from `session.shop`, and `null_session = Auth::Session.new(shop: auth_query.shop)` [9](#0-8) , so the POST — containing `client_id` and `client_secret` in the body — is sent to `https://#{auth_query.shop}/admin/oauth/access_token` [10](#0-9) .

Compounding this, `begin_auth` (the entry point of the flow) also accepts an arbitrary `shop:` string with no `ShopValidator` check, and the library's own documentation instructs integrators to source it straight from a request header (`shop = request.headers["Shop"]`) [11](#0-10) . The `state` nonce set in that call is bound only to a short-lived cookie, not to the shop domain, so an attacker who can influence the `shop` value used to start OAuth (via that unvalidated host input) can steer the whole flow, including the final access-token POST target, to an attacker-controlled host of their choosing.

This directly matches the report's bug class ("a check that answers permissively" / a value that is validated for integrity but not for the specific identity binding required) but manifests here as: **host validated (HMAC-integrity-checked) versus host that receives `client_secret` (must be a trusted Shopify domain) — never checked to be equal to a trusted domain.**

### Impact Explanation
If `shop` ends up pointing at a non-Shopify host, the library sends the app's `client_id` and `client_secret` — its most sensitive credential — to that host in the `access_token` exchange request. This is SSRF carrying the app's credentials to an attacker-controlled destination, matching the report's "High: SSRF with the app's credentials... or credential leakage" impact bucket. Every other credential-bearing OAuth-family method in this gem (`refresh_access_token`, `client_credentials`, `migrate_to_expiring_token`) enforces `ShopValidator.sanitize!` first; `validate_auth_callback`/`begin_auth` is the outlier that does not, which is the same class of "some validators check it, one doesn't" inconsistency the external report flags for chain-id checks in the analog code.

### Likelihood Explanation
Exploitability is bounded by how the host application sources the `shop` value passed to `begin_auth`/used to reach `validate_auth_callback`. The library's own docs recommend taking it from a request header, and the gem provides no internal enforcement to catch a non-Shopify value before it reaches the credential-bearing request. Given `ShopValidator` already exists and is applied in three sibling methods, its absence here is a real gap in the gem itself, not merely a caller mistake against documented behavior.

### Recommendation
Apply the same guard used elsewhere in the codebase: call `Utils::ShopValidator.sanitize!(shop)` (or equivalent) on `auth_query.shop` in `validate_auth_callback` before constructing `null_session`/`auth_base_uri`, and likewise sanitize the `shop:` argument in `begin_auth` before building `auth_route`, e.g.:
```ruby
def validate_auth_callback(cookies:, auth_query:)
  ...
  raise Errors::InvalidOauthError, "Invalid OAuth callback." unless Utils::HmacValidator.validate(auth_query)
  validated_shop = Utils::ShopValidator.sanitize!(auth_query.shop)
  ...
  null_session = Auth::Session.new(shop: validated_shop)
  ...
  session = Session.from(shop: validated_shop, ...)
```

### Proof of Concept
1. Attacker-influenced input reaches `ShopifyAPI::Auth::Oauth.begin_auth(shop: attacker_controlled_value, redirect_path: "/auth/callback")`, exactly per the documented pattern `shop = request.headers["Shop"]` [11](#0-10) .
2. No domain check occurs; `auth_route` is built from `attacker_controlled_value` via `auth_base_uri` [5](#0-4) .
3. On callback, the app calls `validate_auth_callback(cookies:, auth_query:)` with `auth_query.shop == attacker_controlled_value`. HMAC validation only confirms parameter integrity against the app's own `api_secret_key`/`old_api_secret_key` [7](#0-6) ; it performs no check that `shop` is `*.myshopify.com` or otherwise trusted.
4. `client = Clients::HttpClient.new(session: null_session, base_path: "/admin/oauth")` then POSTs `{client_id, client_secret, code, expiring}` to `https://#{attacker_controlled_value}/admin/oauth/access_token` [9](#0-8) , disclosing the app's `client_secret` to the attacker-controlled host.

### Citations

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

**File:** lib/shopify_api/auth/oauth.rb (L64-64)
```ruby
          raise Errors::InvalidOauthError, "Invalid OAuth callback." unless Utils::HmacValidator.validate(auth_query)
```

**File:** lib/shopify_api/auth/oauth.rb (L73-91)
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

**File:** lib/shopify_api/utils/shop_validator.rb (L56-64)
```ruby
        def sanitize!(shop, myshopify_domain: nil)
          host = sanitize_shop_domain(shop, myshopify_domain: myshopify_domain)
          if host.nil? || host.empty?
            raise Errors::InvalidShopError,
              "shop must be a trusted Shopify domain (see ShopValidator::TRUSTED_SHOPIFY_DOMAINS), got: #{shop.inspect}"
          end

          host
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
