### Title
Missing Shop Domain Validation in `Oauth.begin_auth` Allows Forced OAuth Completion / Session Fixation - (File: `lib/shopify_api/auth/oauth.rb`)

### Summary
`ShopifyAPI::Auth::Oauth.begin_auth` builds the OAuth authorize redirect URL using the caller-supplied `shop` value without ever validating it against `Utils::ShopValidator`, unlike the sibling grant flows in this same gem (`ClientCredentials`, `RefreshToken`), which explicitly call `Utils::ShopValidator.sanitize!(shop)` before using the shop to build a request host. This breaks the intended binding "the host that receives the OAuth state/nonce == a trusted Shopify domain," letting an unauthenticated caller redirect a victim's browser (and the state nonce/cookie tied to it) to an attacker-controlled host and later force-complete OAuth into the victim's session with the attacker's own shop.

### Finding Description
`begin_auth` generates a random `state` nonce, sets it in a `SessionCookie` on the caller's browser, and then builds the authorize URL directly from the caller-supplied `shop` string via `auth_base_uri(shop)`: [1](#0-0) 

`auth_base_uri` performs no validation of `shop` — it simply interpolates it into `https://#{shop}/admin`: [2](#0-1) 

Compare this to the other two OAuth grant helpers in the same gem, both of which sanitize `shop` before it is used to derive a request host: [3](#0-2) [4](#0-3) 

`Utils::ShopValidator` exists precisely to enforce that a `shop` string resolves to one of the `TRUSTED_SHOPIFY_DOMAINS`: [5](#0-4) 

Because `begin_auth` skips this check, the equality the gem is supposed to enforce — `host redirected to for authorize == trusted Shopify domain` — is broken: a caller-supplied `shop` (typically taken from an unauthenticated request parameter, as illustrated in the docs' `ShopifyAuthController#login` example) is passed straight through to build the redirect target.

`validate_auth_callback`, on the return leg, checks the `state` cookie against `auth_query.state` and validates the OAuth HMAC (which does cover `shop`, `code`, `state`, `host`, `timestamp` and is signed with the app's own secret, so it cannot itself be forged by an outside attacker): [6](#0-5) [7](#0-6) 

The problem is that the HMAC check does not protect the *authorize redirect leg*; it only protects the *callback leg*. Since the attacker fully controls where the browser is sent during `begin_auth` (via the unsanitized `shop`), the attacker's own host receives the `client_id`, `redirect_uri`, and — critically — the `state` nonce that is simultaneously written into the victim's browser cookie. The attacker can then independently start a legitimate Shopify OAuth authorization for their own shop, using the same `client_id`/`redirect_uri`/`state` values they intercepted, and have Shopify redirect the victim's browser back to the real app's callback with a genuinely Shopify-signed HMAC for the attacker's shop but the victim's `state`. `validate_auth_callback` will accept it because `state == auth_query.state` matches the victim's own cookie, completing OAuth for the attacker's shop inside what looks like the victim's session/browser (forced OAuth completion / session fixation).

### Impact Explanation
This matches the High-impact category "session fixation or forced OAuth completion" explicitly called out in scope. An attacker can hijack the OAuth flow's `state` and force a victim's browser session to complete authorization for a shop the attacker controls, which can be leveraged to plant an attacker's session/shop into the victim's app session or to conduct further phishing/redirect abuse using the real app's `client_id` and `redirect_uri`.

### Likelihood Explanation
Likelihood is moderate-to-high in typical deployments: the `shop` parameter is documented as coming from an incoming (unauthenticated) request when starting OAuth (see the `ShopifyAuthController#login` example in `docs/usage/oauth.md`), and the gem itself provides no defense — unlike `ClientCredentials`/`RefreshToken`, which already call the very `ShopValidator.sanitize!` helper that is missing here. This is a gem-level inconsistency, not a host application's misuse of a documented contract, since two of the three OAuth code paths in this exact library already treat shop sanitization as the library's own responsibility.

### Recommendation
In `lib/shopify_api/auth/oauth.rb`, validate/sanitize `shop` with `Utils::ShopValidator.sanitize!(shop)` at the top of `begin_auth` (and re-validate `auth_query.shop` in `validate_auth_callback` before it is used to build `null_session`/`auth_base_uri`), raising `Errors::InvalidShopError` for any non-trusted domain, mirroring the pattern already used in `client_credentials.rb` and `refresh_token.rb`.

### Proof of Concept
1. Application exposes `GET /login?shop=<param>` which calls `ShopifyAPI::Auth::Oauth.begin_auth(shop: params[:shop], redirect_path: "/callback")` (pattern shown in `docs/usage/oauth.md`).
2. Attacker lures victim to `https://app.example.com/login?shop=attacker.evil` (or any non-myshopify host attacker controls, e.g. a domain that can serve HTTP).
3. `begin_auth` builds `auth_route = "https://attacker.evil/admin/oauth/authorize?client_id=<real client id>&scope=<scope>&redirect_uri=https://app.example.com/callback&state=<NONCE>"` and sets a `state=<NONCE>` cookie on the victim's browser for `app.example.com`.
4. Victim's browser is redirected to `attacker.evil`, which now knows `client_id`, `redirect_uri`, and `NONCE`.
5. Attacker's server independently initiates a real Shopify OAuth authorize request to `shopify.com` for the attacker's own shop, using the harvested `client_id`, `redirect_uri=https://app.example.com/callback`, and `state=NONCE`.
6. Shopify authorizes (attacker approves for their own shop) and redirects the victim's browser to `https://app.example.com/callback?code=...&shop=attacker-shop.myshopify.com&state=NONCE&hmac=<valid Shopify-signed hmac>`.
7. `validate_auth_callback` finds `cookies[state cookie] == NONCE == auth_query.state`, the HMAC is genuinely valid (Shopify signed it for attacker's shop), and the flow completes — the victim's browser/session now holds a session bound to the attacker's shop, without the attacker ever needing the app's `client_secret`.

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

**File:** lib/shopify_api/auth/oauth.rb (L60-72)
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

**File:** lib/shopify_api/utils/shop_validator.rb (L9-64)
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

      class << self
        extend T::Sig

        sig do
          params(
            shop_domain: String,
            myshopify_domain: T.nilable(String),
          ).returns(T.nilable(String))
        end
        def sanitize_shop_domain(shop_domain, myshopify_domain: nil)
          uri = uri_from_shop_domain(shop_domain, myshopify_domain)
          return nil if uri.nil? || uri.host.nil? || uri.host.empty?

          trusted_domains(myshopify_domain).each do |trusted_domain|
            host = T.cast(uri.host, String)
            uri_domain = uri.domain
            next if uri_domain.nil?

            no_shop_name_in_subdomain = host == trusted_domain
            from_trusted_domain = trusted_domain == uri_domain

            if unified_admin?(uri) && from_trusted_domain
              return myshopify_domain_from_unified_admin(uri)
            end
            return nil if no_shop_name_in_subdomain || host.empty?
            return host if from_trusted_domain
          end
          nil
        end

        sig do
          params(
            shop: String,
            myshopify_domain: T.nilable(String),
          ).returns(String)
        end
        def sanitize!(shop, myshopify_domain: nil)
          host = sanitize_shop_domain(shop, myshopify_domain: myshopify_domain)
          if host.nil? || host.empty?
            raise Errors::InvalidShopError,
              "shop must be a trusted Shopify domain (see ShopValidator::TRUSTED_SHOPIFY_DOMAINS), got: #{shop.inspect}"
          end

          host
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
