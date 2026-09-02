## Title
OAuth authorization redirect built from an unvalidated `shop` parameter enables state-nonce leakage and forced OAuth completion — (`lib/shopify_api/auth/oauth.rb`)

### Summary
`ShopifyAPI::Auth::Oauth.begin_auth` builds the URL to which the user's browser is redirected to start OAuth directly from the caller-supplied `shop` string, with no validation that it is a legitimate `*.myshopify.com` (or dev-server) hostname. [1](#0-0)  Because the library's own documentation instructs hosting apps to source `shop` straight from an unauthenticated request header, an attacker can cause the redirect target (`auth_route`) to be their own server. [2](#0-1)  That redirect carries the CSRF/session-fixation-protection `state` nonce that the library also stores in the victim's session cookie. [3](#0-2)  Because `state` is compared only for equality with the cookie in `validate_auth_callback`, and the HMAC over the callback binds `code`/`shop`/`state` but is computed by Shopify for *whatever* real shop completed the flow (including one owned by the attacker), an attacker can capture the leaked nonce, complete a legitimate OAuth grant for their own store, and inject that forged-but-genuinely-signed callback into the victim's browser/session — binding the victim's session cookie to the attacker's shop/access token. [4](#0-3) 

### Finding Description
`begin_auth` is:
```ruby
def begin_auth(shop:, redirect_path:, is_online: true, scope_override: nil)
  ...
  state = SecureRandom.alphanumeric(NONCE_LENGTH)
  cookie = SessionCookie.new(value: state, expires: Time.now + 60)
  query = { client_id: ..., scope: ..., redirect_uri: ..., state: state, "grant_options[]": ... }
  query_string = URI.encode_www_form(query)
  auth_route = auth_base_uri(shop) + "/oauth/authorize?#{query_string}"
  { auth_route: auth_route, cookie: cookie }
end
``` [5](#0-4) 

`auth_base_uri` performs no format check on `shop` beyond a special-case for local dev servers — any string is turned into `https://#{shop}/admin`:
```ruby
def auth_base_uri(shop)
  return "https://#{shop}/admin" unless defined?(DevServer) && shop.include?(".my.shop.dev")
  ...
end
``` [1](#0-0) 

There is no shop-domain sanitizer anywhere else in the library (confirmed by searching for shop-validation helpers across `lib/`), so this is the only gate on the value before it becomes a redirect target that carries the anti-CSRF `state` nonce. The gem's own documentation instructs implementers to pull `shop` from a raw request header:
```ruby
def login
  shop = request.headers["Shop"]
  auth_response = ShopifyAPI::Auth::Oauth.begin_auth(shop: domain, redirect_path: "/auth/callback")
  cookies[auth_response[:cookie].name] = { ... value: auth_response[:cookie].value }
  response.set_header("Location", auth_response[:auth_route])
end
``` [2](#0-1) 

On the callback side, the only binding that protects the session is: the callback HMAC (proves the code/shop/state tuple was genuinely issued by Shopify for *some* shop) and equality between `state` and the value stored in the victim's session cookie:
```ruby
raise Errors::InvalidOauthError, "Invalid OAuth callback." unless Utils::HmacValidator.validate(auth_query)
state = cookies[SessionCookie::SESSION_COOKIE_NAME]
raise Errors::InvalidOauthError, "Invalid state in OAuth callback." unless state == auth_query.state
null_session = Auth::Session.new(shop: auth_query.shop)
...
session = Session.from(shop: auth_query.shop, access_token_response: ...)
``` [4](#0-3) 

The identity binding that is broken: **the `state` nonce is meant to bind "the browser that started this specific OAuth flow" to "the browser that completes it,"** but the redirect used to *start* the flow is sent to a host the gem never validates is a Shopify domain. Once that nonce leaks to an attacker-controlled `auth_base_uri(shop)` host, the equality check `state == auth_query.state` no longer distinguishes the legitimate flow from a forged one, because the HMAC only proves Shopify-authenticity of *a* shop/code pair, not that it's the *same* shop the victim intended to install. Concretely:

1. Attacker gets a victim to hit the app's login endpoint with `shop` set to a value that is not `*.myshopify.com` (e.g. via the `Shop` header path shown in the docs) but resolves/redirects to attacker infrastructure.
2. The app calls `begin_auth`, sets the `state` cookie on the victim's browser, and redirects the browser to `https://attacker-host/admin/oauth/authorize?...&state=NONCE`.
3. Attacker's server captures `NONCE` from the incoming request.
4. Attacker separately (out-of-band, using their own Shopify store) completes a legitimate OAuth authorize+consent flow against the real Shopify servers for the same app `client_id`, obtaining a genuine `code`/`hmac` pair for the attacker's own shop.
5. Attacker gets the victim's browser (which still holds the `state` cookie from step 2) to hit the app's real `/auth/callback` with `shop=attacker-shop.myshopify.com&code=<attacker's real code>&hmac=<genuine>&state=NONCE`.
6. `validate_auth_callback` passes: HMAC is genuinely valid (signed by Shopify for the attacker's own shop) and `state == cookie` matches, so the app completes the token exchange and binds the victim's session/cookie to a `ShopifyAPI::Auth::Session` for the **attacker's** shop and access token.

### Impact Explanation
This is a forced OAuth completion / session-fixation-class issue: the app's session gets bound to a shop/access token chosen by the attacker rather than the one the victim intended, without the attacker needing `api_secret_key`, an access token, or any privileged credential. Depending on how the host app uses the resulting `Session`, this can let an attacker's store impersonate or hijack the victim's authenticated app session.

### Likelihood Explanation
Exploitability depends on the host application following the documented pattern of deriving `shop` from unauthenticated input (explicitly shown in this repo's own docs) and not independently validating the domain before calling `begin_auth`. The gem provides no defense-in-depth (no `*.myshopify.com` format check) at the point where the state nonce is dispatched, so any host app that trusts this gem's documented flow is exposed.

### Recommendation
Validate `shop` against the expected Shopify domain pattern (e.g. `^[a-zA-Z0-9][a-zA-Z0-9-]*\.myshopify\.com$`, plus any explicitly supported custom-domain allowlist) inside `ShopifyAPI::Auth::Oauth.begin_auth` (and ideally in `AuthQuery`/`validate_auth_callback` too) before constructing `auth_base_uri`, raising `Errors::InvalidOauthError` for anything that doesn't match, so the state nonce can never be sent to a non-Shopify host.

### Proof of Concept
1. Host app implements login exactly as documented: `shop = request.headers["Shop"]; ShopifyAPI::Auth::Oauth.begin_auth(shop: shop, redirect_path: "/auth/callback")`.
2. Attacker sends victim a link to the login endpoint with `Shop: attacker.example` (or any value resolvable to attacker infra, since no domain check exists in `auth_base_uri`).
3. `begin_auth` sets the `state` cookie on victim's browser and redirects to `https://attacker.example/admin/oauth/authorize?client_id=...&state=NONCE...`.
4. Attacker's server logs `NONCE`.
5. Attacker completes a real OAuth consent using their own Shopify dev store against the same app, obtaining a genuine `code`+`hmac`.
6. Attacker causes victim's browser to GET `/auth/callback?shop=attacker-shop.myshopify.com&code=<real code>&hmac=<real hmac>&timestamp=...&state=NONCE`.
7. `validate_auth_callback` accepts the request (valid HMAC, matching state/cookie) and stores a `Session` for `attacker-shop.myshopify.com` under the victim's session context. [4](#0-3)

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

**File:** lib/shopify_api/auth/oauth.rb (L60-113)
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

          cookie = if Context.embedded?
            SessionCookie.new(
              value: "",
              expires: Time.now,
            )
          else
            SessionCookie.new(
              value: session.id,
              expires: session.expires ? session.expires : nil,
            )
          end

          { session: session, cookie: cookie }
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
