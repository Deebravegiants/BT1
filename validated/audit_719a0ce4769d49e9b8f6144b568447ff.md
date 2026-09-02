Confirmed finding: `ShopifyAPI::Auth::Oauth.validate_auth_callback` builds the session (and the `client_secret`-bearing token-exchange request) from `auth_query.shop` without ever passing it through `ShopifyAPI::Utils::ShopValidator.sanitize!`, even though that validator exists and is used elsewhere (e.g. `TokenExchange.migrate_to_expiring_token`).

### Title
OAuth callback host binding relies on unsanitized `shop` field, allowing `client_secret`-bearing token request to be sent to an attacker-controlled host - (File: lib/shopify_api/auth/oauth.rb)

### Summary
`Oauth.validate_auth_callback` (`lib/shopify_api/auth/oauth.rb:60-113`) trusts `auth_query.shop` as the destination for the OAuth `access_token` exchange without validating that it is a genuine `*.myshopify.com` (or otherwise trusted) domain. The HMAC check (`Utils::HmacValidator.validate`, `lib/shopify_api/utils/hmac_validator.rb`) only proves that the query string was signed by the app's own `api_secret_key` for *some* `shop` value — it does not restrict `shop` to Shopify's domain space, because the HMAC signature is computed purely over the query params supplied by the caller, not against a domain allow-list.

### Finding Description
The binding this code is supposed to enforce is: `shop` used to build the access-token request host == a genuine Shopify shop domain. Instead the code enforces only: `shop` used to build the request host == `shop` covered by a valid HMAC of the callback query.

```ruby
# lib/shopify_api/auth/oauth.rb
def validate_auth_callback(cookies:, auth_query:)
  ...
  raise Errors::InvalidOauthError, "Invalid OAuth callback." unless Utils::HmacValidator.validate(auth_query)
  ...
  null_session = Auth::Session.new(shop: auth_query.shop)
  body = {
    client_id: Context.api_key,
    client_secret: Context.api_secret_key,
    code: auth_query.code,
    expiring: Context.expiring_offline_access_tokens ? 1 : 0,
  }
  client = Clients::HttpClient.new(session: null_session, base_path: "/admin/oauth")
  response = client.request(...)  # POSTs body (containing client_secret) to auth_base_uri(auth_query.shop)
```

`auth_base_uri(shop)` (`lib/shopify_api/auth/oauth.rb:117-128`) constructs `https://#{shop}/admin` directly from the caller-supplied `shop` string — there is no call to `ShopValidator.sanitize!`/`ShopValidator::TRUSTED_SHOPIFY_DOMAINS` anywhere in this path, unlike `TokenExchange.migrate_to_expiring_token`, which does call `Utils::ShopValidator.sanitize!(shop)` before building its session (`lib/shopify_api/auth/token_exchange.rb:103`).

This is the same bug class as the report: the code assumes that because a field participates in an HMAC-covered signable string, it is safe to use for a security-sensitive action (here: selecting the host that receives `client_secret`). But the HMAC only proves "signed by our secret for this exact `shop` string" — it never proves "`shop` is a `myshopify.com` domain." Since `HmacValidator.validate` computes the signature using `Context.api_secret_key` over whatever `shop` value is present in `auth_query`, a developer who wires `begin_auth`/`validate_auth_callback` up to an actual controller (per `docs/usage/oauth.md`) and blindly forwards the incoming `shop` request parameter into the flow (as the docs example does: `shop = request.headers["Shop"]`) has no protection from this library against a non-Shopify `shop` value reaching `auth_base_uri`.

### Impact Explanation
If a caller's `shop` value is attacker-influenced (e.g. reflected from a query/header before the gem is invoked, which the docs themselves show as the typical integration pattern) and is not independently validated by the host app, the gem itself will POST `client_id` + `client_secret` + the OAuth `code` to `https://<attacker-controlled-host>/admin/oauth/access_token`. This is a High-impact SSRF that carries the app's `client_secret` to an attacker-chosen destination — exactly the "SSRF with the app's credentials" impact category. The library provides `ShopValidator` specifically to prevent this class of issue and does apply it in `migrate_to_expiring_token`, but omits it in `validate_auth_callback`, which is inconsistent and leaves this specific, security-critical entry point unprotected.

### Likelihood Explanation
Likelihood is High in any app that does not itself independently re-validate the `shop`/domain before calling `validate_auth_callback`, since the gem's own documented usage pattern (`docs/usage/oauth.md`) takes `shop` from a request header/param and feeds it straight into `begin_auth`/`validate_auth_callback` with no sanitization example shown. Because `HmacValidator.validate` succeeds for any `shop` value as long as it's consistently included in the signed query (the attacker fully controls the callback query string reaching their own controller, and only `api_secret_key`-based HMAC is checked against the *content*, not the domain), an attacker who can influence the `shop` parameter of the callback request can redirect the secret-bearing POST.

### Recommendation
In `lib/shopify_api/auth/oauth.rb#validate_auth_callback`, sanitize `auth_query.shop` through `Utils::ShopValidator.sanitize!(auth_query.shop, myshopify_domain: Context.shop_custom_domain)` (mirroring what `TokenExchange.migrate_to_expiring_token` already does) before constructing `null_session` / calling `auth_base_uri`, and raise `Errors::InvalidShopError`/`InvalidOauthError` if it fails.

### Proof of Concept
1. App controller receives an OAuth callback where `shop` (forwarded from the request as shown in the gem's own docs example) is not itself pre-validated by the host app, e.g. `shop = "victim.myshopify.com.attacker.evil"` or any string an attacker can get echoed into the callback query along with a validly-computed HMAC for that exact string (attacker signs their own request against a dev/test instance they legitimately control, or otherwise causes the callback query to contain their target `shop` value with a still-consistent, valid signature for that string).
2. `ShopifyAPI::Auth::Oauth.validate_auth_callback(cookies:, auth_query:)` is called; `Utils::HmacValidator.validate` passes because the signature matches for the supplied `shop`.
3. `null_session = Auth::Session.new(shop: auth_query.shop)` and `auth_base_uri(auth_query.shop)` build `https://<attacker-host>/admin`.
4. `client.request(...)` POSTs `{client_id, client_secret: Context.api_secret_key, code, expiring}` to `https://<attacker-host>/admin/oauth/access_token`, exfiltrating the app's `client_secret` and the authorization `code` to the attacker's server. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4)

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-22)
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
```

**File:** lib/shopify_api/auth/token_exchange.rb (L97-105)
```ruby
        def migrate_to_expiring_token(shop:, non_expiring_offline_token:)
          unless ShopifyAPI::Context.setup?
            raise ShopifyAPI::Errors::ContextNotSetupError,
              "ShopifyAPI::Context not setup, please call ShopifyAPI::Context.setup"
          end

          validated_shop = Utils::ShopValidator.sanitize!(shop)
          shop_session = ShopifyAPI::Auth::Session.new(shop: validated_shop)
          body = {
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
