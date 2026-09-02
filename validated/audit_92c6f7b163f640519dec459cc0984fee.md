The documented example confirms the attack surface: the docs (`docs/usage/oauth.md:182-185`) explicitly show `shop` being taken straight from an inbound request header (`request.headers["Shop"]`) and passed unsanitized to `begin_auth`, matching the input table which only documents the expected format (`{exampleshop}.myshopify.com`) without requiring or performing library-side validation.

### Title
Unvalidated `shop` in `Oauth.begin_auth` enables forced OAuth completion / session fixation via attacker-controlled authorization host - (File: lib/shopify_api/auth/oauth.rb)

### Summary
`ShopifyAPI::Auth::Oauth.begin_auth` builds the Shopify authorization redirect URL from a caller-supplied `shop` string with no domain validation, while a `ShopifyAPI::Utils::ShopValidator` module exists elsewhere in the gem specifically to sanitize shop domains against `TRUSTED_SHOPIFY_DOMAINS` and is never invoked here. This lets a `shop` value that is not a genuine Shopify domain redirect the victim's browser to an attacker-controlled server carrying the freshly minted, cookie-bound `state` nonce, enabling the attacker to complete a real, validly-HMAC-signed OAuth callback on their own store and fixate that session (their shop, their access token) into the victim's browser session.

### Finding Description
`begin_auth` generates a random `state` nonce, sets it as an httpOnly cookie for the victim, and builds the redirect target using `auth_base_uri(shop)`: [1](#0-0) [2](#0-1) 

`auth_base_uri` performs no check that `shop` belongs to `myshopify.com`/`myshopify.io`/etc. It simply interpolates the string into `https://#{shop}/admin`. The gem already ships a purpose-built validator, `ShopifyAPI::Utils::ShopValidator.sanitize!`, that checks a shop string against `TRUSTED_SHOPIFY_DOMAINS`: [3](#0-2) [4](#0-3) 

This validator is used in `TokenExchange.migrate_to_expiring_token` but conspicuously **not** in `begin_auth`, nor in `TokenExchange.exchange_token`'s use of the JWT `dest` claim, nor in `validate_auth_callback`'s use of `auth_query.shop` when constructing the null session passed to `HttpClient`: [5](#0-4) [6](#0-5) 

`HttpClient` then trusts `session.shop` outright to build the base URI that receives the OAuth POST body (containing `client_secret`): [7](#0-6) 

The exploitable gap is `begin_auth`, because it is the only one of these paths reachable **before** any cryptographic binding exists (no HMAC/JWT yet — the `state` nonce is only just being created). The identity-binding equality broken is: *the domain the victim's browser is redirected to (`shop` in `begin_auth`) ≠ the domain that legitimately owns the shared secret used to compute the eventual callback HMAC*. Because `state` is embedded in the query string sent to whatever host `shop` resolves to, an attacker who controls that host learns the nonce and can bind it to a request they generate through *their own legitimate Shopify store* (installing the app for real). Since `AuthQuery#to_signable_string` includes `state`, `shop`, `code`, `host`, `timestamp` and Shopify computes a valid HMAC for whatever `state` the attacker supplied on their own real authorize request, the attacker can produce a genuinely valid `(code, shop=attacker-shop, state=victim-nonce, hmac)` tuple and hand it to the victim's browser to send to the app's real callback endpoint. `validate_auth_callback` will accept it because the HMAC is genuinely valid and the cookie `state` matches: [8](#0-7) 

The result is that the app completes OAuth and stores/activates a `Session` for the **attacker's** shop and access token inside the **victim's** browser/cookie context — a session fixation / forced OAuth completion.

### Impact Explanation
This matches the High-severity impact class "session fixation or forced OAuth completion." No `api_secret_key`, access token, or leaked credential is required by the attacker — only a real (free) Shopify development/trial store to legitimately complete their own OAuth flow with a chosen `state`. The victim ends up with the app "authenticated" as the attacker's shop in their browser session, which can be leveraged for further attacks depending on how the host app uses the resulting session (e.g., tricking the victim into acting within the attacker's shop context, or confusing app-side authorization checks keyed off the active session).

### Likelihood Explanation
Requires the host application to pass a request-controlled `shop` value into `begin_auth` without its own additional domain validation — which is exactly the pattern shown in this gem's own documentation example (`request.headers["Shop"]` passed straight through). Since the gem provides no built-in protection at this specific entry point (unlike `migrate_to_expiring_token`, which does sanitize), and the documented usage pattern doesn't prompt developers to sanitize `shop` themselves, likelihood of real-world exposure is meaningful, though it depends on the host app not adding its own shop validation.

### Recommendation
Call `ShopifyAPI::Utils::ShopValidator.sanitize!(shop)` (or `sanitize_shop_domain`) inside `Oauth.begin_auth` before constructing `auth_base_uri`, raising `Errors::InvalidShopError` for any `shop` that isn't a trusted Shopify domain — mirroring the protection already applied in `TokenExchange.migrate_to_expiring_token`. Consider applying the same validation defensively to `auth_query.shop` in `validate_auth_callback` and to `HttpClient#initialize`'s use of `session.shop` as defense in depth.

### Proof of Concept
1. Host app implements the documented pattern: `ShopifyAPI::Auth::Oauth.begin_auth(shop: request.headers["Shop"], redirect_path: "/auth/callback")` (as shown in `docs/usage/oauth.md:182-185`).
2. Attacker lures victim to the app's login route with `Shop: attacker-controlled.example.com`.
3. `begin_auth` sets cookie `state = N` and returns `auth_route = "https://attacker-controlled.example.com/admin/oauth/authorize?...&state=N..."`; victim's browser is redirected there, revealing `N` to the attacker's server.
4. In parallel (or beforehand), the attacker installs the app for real on their own trial/dev store and drives that store's real Shopify authorize flow using `state=N`, obtaining a genuinely Shopify-signed callback `code, shop=attacker-shop.myshopify.com, state=N, hmac=<valid>`.
5. Attacker's server (in place of the real Shopify authorize page) 302-redirects the victim's browser to the app's real callback URL with that genuine tuple.
6. `validate_auth_callback` (`lib/shopify_api/auth/oauth.rb:60-73`) succeeds — HMAC validates and cookie `state == auth_query.state` — completing OAuth for the attacker's shop inside the victim's session.

### Citations

**File:** lib/shopify_api/auth/oauth.rb (L36-52)
```ruby
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

**File:** lib/shopify_api/auth/oauth.rb (L64-73)
```ruby
          raise Errors::InvalidOauthError, "Invalid OAuth callback." unless Utils::HmacValidator.validate(auth_query)
          raise Errors::UnsupportedOauthError, "Cannot perform OAuth for private apps." if Context.private?

          state = cookies[SessionCookie::SESSION_COOKIE_NAME]
          raise Errors::NoSessionCookieError unless state

          raise Errors::InvalidOauthError,
            "Invalid state in OAuth callback." unless state == auth_query.state

          null_session = Auth::Session.new(shop: auth_query.shop)
```

**File:** lib/shopify_api/auth/oauth.rb (L117-120)
```ruby
        sig { params(shop: String).returns(String) }
        def auth_base_uri(shop)
          return "https://#{shop}/admin" unless defined?(DevServer) && shop.include?(".my.shop.dev")

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

**File:** lib/shopify_api/auth/token_exchange.rb (L103-104)
```ruby
          validated_shop = Utils::ShopValidator.sanitize!(shop)
          shop_session = ShopifyAPI::Auth::Session.new(shop: validated_shop)
```

**File:** lib/shopify_api/clients/http_client.rb (L12-19)
```ruby
      def initialize(base_path:, session: nil)
        session ||= Context.active_session
        raise Errors::NoActiveSessionError, "No passed or active session" unless session

        api_host = Context.api_host

        @base_uri = T.let("https://#{api_host || session.shop}", String)
        @base_uri_and_path = T.let("#{@base_uri}#{base_path}", String)
```
