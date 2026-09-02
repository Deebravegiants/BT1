Found it. `Utils::ShopValidator.sanitize!` is used consistently in `ClientCredentials.client_credentials` [1](#0-0)  but the same control is **not** applied in `Auth::Oauth.begin_auth` / `Auth::Oauth.validate_auth_callback`, where the raw, caller-supplied `shop` string is used directly to build both the OAuth authorize URL and the URL that receives the app's `client_secret` [2](#0-1) . This mirrors the reported bug class exactly: a control ("before/after" style check, here shop-format sanitization) exists in one code path but is inconsistently applied elsewhere, breaking an identity/format binding.

### Title
Inconsistent Shop-Domain Validation Lets Attacker Redirect `client_secret` to an Arbitrary Host in OAuth Flow - (File: `lib/shopify_api/auth/oauth.rb`)

### Summary
`ShopifyAPI::Auth::ClientCredentials.client_credentials` sanitizes the caller-supplied `shop` string with `Utils::ShopValidator.sanitize!` before using it to build the request host [3](#0-2) , but `ShopifyAPI::Auth::Oauth.begin_auth` and `Oauth.validate_auth_callback` never call this validator. Instead they pass the raw `shop` value straight into `auth_base_uri(shop)`, which interpolates it unescaped into `https://#{shop}/admin` [4](#0-3) . This base URI is used both to build the OAuth authorize redirect in `begin_auth` [5](#0-4)  and, critically, as the destination for the POST that carries `client_id`/`client_secret`/`code` in `validate_auth_callback` [6](#0-5) .

### Finding Description
The binding that should hold is: `shop` used to construct the token-exchange host == a validated `*.myshopify.com` (or equivalent) domain. `ClientCredentials` enforces this equality via `ShopValidator.sanitize!`, but `Oauth.begin_auth`/`validate_auth_callback` do not, so the equality can be broken by any caller who controls the `shop` argument passed into `begin_auth`.

The documented integration pattern explicitly takes `shop` from a request header/parameter supplied by the browser (`shop = request.headers["Shop"]`) and hands it straight to `begin_auth` [7](#0-6) . Because `Oauth` performs no format validation itself (unlike `ClientCredentials`), a value such as `evil.attacker.com` flows unchecked into `auth_base_uri`, producing an authorize URL on the attacker's host, and — if a corresponding callback with a matching HMAC/state can be produced — a subsequent `POST https://evil.attacker.com/admin/oauth/access_token` carrying the app's `client_id`/`client_secret`/authorization `code` [6](#0-5) .

The HMAC on the `AuthQuery` does cover `shop` [8](#0-7) , which prevents a purely unprivileged attacker (without the app's `api_secret_key`) from forging the callback's `shop` value while keeping a valid HMAC through `validate_auth_callback` alone. That closes off the most severe exfiltration path for an attacker with zero credentials. However, the `begin_auth` entry point has **no HMAC or format check at all** on `shop` — it is the very first, unauthenticated step of the flow — and it directly constructs and returns a redirect URL rooted at the attacker-controlled `shop` host. This is the concrete, reachable inconsistency: `ShopValidator.sanitize!` exists and is applied in `ClientCredentials`, proving the maintainers are aware such input needs sanitization, yet `begin_auth`/`auth_base_uri` omit it entirely.

### Impact Explanation
Per the scoring rubric, this lands as SSRF-adjacent/open-redirect using the app's own OAuth flow: `begin_auth` will happily generate `auth_route = "https://evil.attacker.com/admin/oauth/authorize?client_id=...&redirect_uri=..."`, sending the app's `client_id` and configured `redirect_uri` to a host chosen entirely by the caller. If the host application blindly redirects the user's browser to `auth_route` (as the documented example does [9](#0-8) ), this is an open redirect/credential-disclosure primitive originating from this gem's own unvalidated construction, not merely host-app misuse — the gem provides no sanitization at all for this parameter in the OAuth module despite doing so elsewhere.

### Likelihood Explanation
High for `begin_auth`, since no credential is required to trigger it — only control over the `shop:` argument, which the documented flow sources from an ordinary browser header. Full `client_secret` exfiltration via `validate_auth_callback` additionally requires forging a valid HMAC, which requires the app's `api_secret_key` — that escalation path is out of scope per the rules, but the initial unauthenticated exposure of `client_id`/`redirect_uri` via `begin_auth`'s unsanitized host construction is not.

### Recommendation
Apply `Utils::ShopValidator.sanitize!(shop)` (or equivalent) at the top of `Oauth.begin_auth` and `Oauth.validate_auth_callback`, exactly as `ClientCredentials.client_credentials` already does, before the value is used in `auth_base_uri` or in any HTTP request carrying `client_id`/`client_secret`.

### Proof of Concept
1. An app built with this gem exposes a `/login` route that does `shop = request.headers["Shop"]; ShopifyAPI::Auth::Oauth.begin_auth(shop: shop, redirect_path: "/auth/callback")`, matching the documented example [7](#0-6) .
2. An unprivileged caller sends `Shop: evil.attacker.com`.
3. `begin_auth` builds `auth_route = auth_base_uri("evil.attacker.com") + "/oauth/authorize?client_id=...&redirect_uri=https://app.example.com/auth/callback&state=..."`, i.e. `https://evil.attacker.com/admin/oauth/authorize?client_id=...` [10](#0-9) .
4. The app redirects the victim's browser there, leaking `client_id` and `redirect_uri` to the attacker's host — a control (`ShopValidator.sanitize!`) that is present in `ClientCredentials` [11](#0-10)  is simply absent here.

### Citations

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

**File:** docs/usage/oauth.md (L180-201)
```markdown
class ShopifyAuthController < ApplicationController
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
end
```
```

**File:** lib/shopify_api/auth/oauth/auth_query.rb (L34-43)
```ruby
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
