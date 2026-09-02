### Title
`ShopifyAPI::Auth::Oauth.begin_auth` uses an unauthenticated, unsanitized `shop` to build the OAuth redirect target, enabling nonce leakage and forced OAuth/session-fixation - ([File: lib/shopify_api/auth/oauth.rb])

### Summary
`begin_auth` builds the authorize-redirect URL directly from a caller-supplied `shop` string via `auth_base_uri(shop)` without ever validating it against `Utils::ShopValidator`, unlike every other credential-issuing OAuth entry point in the gem (`client_credentials`, `refresh_token`, `token_exchange`), which all call `Utils::ShopValidator.sanitize!(shop)` before using `shop` to build the outbound request host.

### Finding Description
`begin_auth(shop:, redirect_path:, ...)` is the very first step of the Authorization Code Grant flow and, by design, runs before any Shopify-issued signature exists — `shop` at this point is fully attacker/user controlled input (the docs even show it read straight from a request header: `shop = request.headers["Shop"]`). [1](#0-0) 

That raw `shop` is passed straight into `auth_base_uri(shop)`, which constructs `"https://#{shop}/admin"` with no domain validation, and the method returns an `auth_route` built from this attacker-controlled host plus `client_id`, `redirect_uri`, `scope`, and the CSRF `state` nonce: [2](#0-1) 

The `state` nonce is simultaneously placed in a `SessionCookie` set on the victim's browser for the app's own domain: [3](#0-2) 

Contrast this with the other OAuth-token-issuing entry points in the same module tree, which all sanitize `shop` before using it to construct the host that receives the app's `client_secret`: [4](#0-3) [5](#0-4) 

The identity binding that should hold is: *the `shop` host that the app's browser session is redirected to == a legitimate `myshopify.com`/trusted Shopify domain*, i.e. `auth_base_uri(shop)` should equal `auth_base_uri(ShopValidator.sanitize!(shop))`. Because `begin_auth` never enforces this, an application integrating this gem (following its own documented usage pattern) will redirect a victim's browser to an arbitrary attacker-controlled host, carrying the app's public `client_id`, the intended `redirect_uri`, and — critically — the CSRF `state` nonce that is also stored in a cookie on the victim's browser for the app's real domain.

Once the attacker's server receives that request, it captures the leaked `state` nonce. The attacker (as the legitimate owner of their own Shopify store) can then independently start and complete Shopify's real OAuth authorize flow for their own store, requesting the exact same `redirect_uri` and supplying `state=<leaked nonce>`. Shopify will issue a validly signed callback (real `hmac`, `code`, `shop=attacker-shop.myshopify.com`, `state=<leaked nonce>`). The attacker relays/redirects this callback URL to the victim. The victim's browser — which still holds the matching `state` cookie set moments earlier by the vulnerable `begin_auth` call (valid for 60 seconds per `SessionCookie.new(value: state, expires: Time.now + 60)`) — hits `validate_auth_callback`, which only checks HMAC validity and `state == cookie` before completing the flow: [6](#0-5) 

Both checks pass (the HMAC and state are genuinely valid, just for the attacker's shop instead of the victim's), so the app finalizes OAuth for the attacker's shop and, for non-embedded apps, sets the victim's browser session cookie to the resulting `session.id` — fixating the victim's browser into an attacker-controlled shop context.

### Impact Explanation
This is a session-fixation / forced-OAuth-completion primitive: the victim's app session becomes bound to a shop the attacker controls, without the victim ever intending to install/connect to that shop. Any subsequent data the victim enters into the app under the assumption they're interacting with their own store is instead delivered into the attacker's shop context — a cross-tenant confusion attack rooted purely in the gem's failure to bind the OAuth redirect host to a trusted Shopify domain during `begin_auth`. This matches the explicitly in-scope "session fixation or forced OAuth completion" High-impact category.

### Likelihood Explanation
Exploitation requires only: (1) the integrating app follows the gem's own documented pattern of passing user-supplied `shop` straight to `begin_auth` (as shown in `docs/usage/oauth.md`), (2) the attacker owns/controls a real Shopify store to complete their own leg of the OAuth flow, and (3) timing within the 60-second cookie window. No access token, `client_secret`, or privileged account is required — only a normal internet user tricking a victim into clicking a crafted login link. This is a plausible, unprivileged, root-caused analog to the identity-binding-not-checkpointed class of bug in the reference report.

### Recommendation
In `ShopifyAPI::Auth::Oauth.begin_auth`, call `Utils::ShopValidator.sanitize!(shop)` (as already done in `client_credentials.rb` and `refresh_token.rb`) before using `shop` to construct `auth_base_uri`, so that the OAuth authorize redirect can only ever target a trusted `myshopify.com`/allow-listed domain.

### Proof of Concept
1. App exposes a login route that calls `ShopifyAPI::Auth::Oauth.begin_auth(shop: params[:shop], redirect_path: "/auth/callback")` (per the gem's documented usage).
2. Attacker sends victim a link to `https://victim-app.example/login?shop=attacker.evil` (or via a `Shop` header the app forwards, per the doc example `shop = request.headers["Shop"]`).
3. The app sets a `state` cookie on the victim's browser and returns `auth_route = "https://attacker.evil/admin/oauth/authorize?client_id=...&redirect_uri=https://victim-app.example/auth/callback&state=<nonce>&..."`, then redirects the victim's browser there.
4. Attacker's server (`attacker.evil`) logs the leaked `state=<nonce>` value from the request.
5. Attacker independently authorizes the real app against their own Shopify store, passing `state=<nonce>` in the real Shopify OAuth authorize request, and receives a genuine Shopify callback URL: `https://victim-app.example/auth/callback?code=...&shop=attacker-shop.myshopify.com&state=<nonce>&hmac=<valid>&timestamp=...&host=...`.
6. Attacker causes the victim's browser (still holding the matching `state` cookie, within 60s) to load that callback URL.
7. `ShopifyAPI::Auth::Oauth.validate_auth_callback` accepts it (HMAC valid, state matches cookie) and completes OAuth for `attacker-shop.myshopify.com`, fixating the victim's app session to the attacker's shop.

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

**File:** lib/shopify_api/auth/oauth.rb (L60-112)
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
