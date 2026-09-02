This is a critical finding: `client_credentials` and `refresh_token` both call `Utils::ShopValidator.sanitize!(shop)` before using the shop value to build request URLs, but `Oauth.begin_auth` does not, confirming an inconsistency in this gem's own code (not just a documentation gap for callers) [1](#0-0) [2](#0-1) [3](#0-2) .

### Title
Unvalidated `shop` parameter used to build the OAuth authorization redirect host - (File: `lib/shopify_api/auth/oauth.rb`)

### Summary
`ShopifyAPI::Auth::Oauth.begin_auth` builds the authorization redirect URL via `auth_base_uri(shop)`, which returns `"https://#{shop}/admin"` directly from caller-supplied input with no call to `Utils::ShopValidator.sanitize!`, unlike the sibling `ClientCredentials.client_credentials` and `RefreshToken.refresh_access_token` methods, which both sanitize `shop` before use. This causes the merchant's browser to be issued a 307/redirect toward an attacker-chosen host when the host app passes an unsanitized `shop` query parameter through, as documented.

### Finding Description
The broken binding: `shop_used_in_auth_base_uri == shop_validated_by(ShopValidator.sanitize!)` is false, because `begin_auth` never calls `sanitize!` before invoking `auth_base_uri(shop)` [4](#0-3) . Compare this to `ClientCredentials.client_credentials`, which calls `validated_shop = Utils::ShopValidator.sanitize!(shop)` before constructing any request [5](#0-4) , and `RefreshToken.refresh_access_token`, which does the same [6](#0-5) . This confirms the omission in `begin_auth` is an inconsistency in the gem's own code, not merely an unenforced caller responsibility.

Attacker request: a merchant/victim is lured to `GET https://app.example.com/login?shop=evil.attacker.example`. The host app calls `Oauth.begin_auth(shop: params[:shop], redirect_path: "/auth/callback")` as documented [7](#0-6) . `begin_auth` builds `query` containing `client_id`, `scope`, `redirect_uri` (built from the app's own `Context.host` + `redirect_path`, not attacker-controlled) and `state`, then concatenates `auth_base_uri(shop) + "/oauth/authorize?..."` [8](#0-7) . The resulting `auth_route` is `https://evil.attacker.example/admin/oauth/authorize?client_id=...&redirect_uri=https://app.example.com/auth/callback&state=...`. No `InvalidShopError` is ever raised, and the victim's browser is redirected to the attacker's host with the app's `client_id`, requested `scope`, and legitimate `redirect_uri`/`state` disclosed.

Important correction to the question's framing: `redirect_uri` in the query is derived from `ShopifyAPI::Context.host` (trusted server-side config) and `redirect_path` (app-controlled constant), not from `shop` — the attacker cannot redirect the eventual OAuth callback to their own server. Completing OAuth still requires `validate_auth_callback`, which calls `Utils::HmacValidator.validate(auth_query)` [9](#0-8) , an HMAC signed with `api_secret_key`, which the attacker never holds. So the attacker cannot forge a callback that passes HMAC validation, and cannot capture a real authorization `code` bound to a legitimate `access_token` exchange without the merchant separately handing over their real Shopify session/credentials on the attacker-controlled page (i.e., active phishing/proxying), which falls under "social engineering" that the rules explicitly place out of scope.

### Impact Explanation
Confirmed root-cause bug: an unsanitized `shop` value chosen by an unprivileged attacker is used verbatim to construct the destination host for a server-issued redirect, disclosing `client_id`, `scope`, and the app's real `redirect_uri`/`state` to that attacker-controlled host — a CWE-601 open-redirect / SSRF-adjacent flaw in `auth_base_uri`. However, none of this by itself yields a merchant access token, refresh token, authorization code bound to a real grant, or `client_secret`, because (a) `redirect_uri` is not attacker-controlled, and (b) `HmacValidator.validate` blocks any forged callback since the attacker lacks `api_secret_key`. Reaching token theft or auth bypass would require the merchant to be actively phished into approving on a fake, attacker-hosted "Shopify" consent page and then leaking real credentials there — a social-engineering step explicitly excluded by the rules. As specified (impact limited to disclosure of `client_id`/`redirect_uri` to an attacker host, with no forgeable callback), this does not independently satisfy the Critical (auth bypass/token theft/cross-tenant/RCE) or High (SSRF driving an *authenticated* request, forced OAuth completion, credential leakage into logs) categories as strictly defined, since no credential leaves the app server and no unauthenticated value is trusted as authenticated anywhere downstream.

### Likelihood Explanation
Trivial to trigger (a single crafted link with `shop=evil.attacker.example` sent to a merchant), but the value gained by the attacker (disclosure of public/non-secret `client_id` and app-controlled `redirect_uri`/`scope` to their own already-controlled host) is low, and turning this into real compromise requires an additional social-engineering leg (fake consent screen + convincing the merchant to authenticate through it) that is out of scope per the rules.

### Recommendation
Call `Utils::ShopValidator.sanitize!(shop)` at the top of `Oauth.begin_auth` (as already done in `ClientCredentials.client_credentials` and `RefreshToken.refresh_access_token`) and use the sanitized value in `auth_base_uri`, raising `Errors::InvalidShopError` for any `shop` not resolving to a trusted Shopify domain.

### Proof of Concept
```ruby
# test/auth/oauth_test.rb (illustrative)
def test_begin_auth_rejects_untrusted_shop_host
  ShopifyAPI::Context.setup(api_key: "key", api_secret_key: "secret", scope: "read_products", host_name: "app.example.com", api_version: "unstable")
  assert_raises(ShopifyAPI::Errors::InvalidShopError) do
    ShopifyAPI::Auth::Oauth.begin_auth(shop: "evil.attacker.example", redirect_path: "/cb")
  end
end
```
Running this against current `lib/shopify_api/auth/oauth.rb` fails (no exception raised); `auth_route` instead starts with `https://evil.attacker.example/admin`, confirming the missing `sanitize!` call, but this by itself only demonstrates an open-redirect/information-disclosure of `client_id`/`redirect_uri` to an attacker-chosen host, not token theft or authentication bypass without an additional out-of-scope social-engineering step.

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

**File:** lib/shopify_api/auth/oauth.rb (L117-119)
```ruby
        sig { params(shop: String).returns(String) }
        def auth_base_uri(shop)
          return "https://#{shop}/admin" unless defined?(DevServer) && shop.include?(".my.shop.dev")
```

**File:** docs/usage/oauth.md (L179-199)
```markdown
```ruby
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
```
