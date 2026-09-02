## Finding

### Title
Missing shop-domain validation in `TokenExchange.exchange_token` and `Oauth.validate_auth_callback` allows the app's `client_secret` to be sent to an unvalidated host - (File: `lib/shopify_api/auth/token_exchange.rb`, `lib/shopify_api/auth/oauth.rb`)

### Summary
The gem ships a dedicated `Utils::ShopValidator.sanitize!` helper that restricts a shop value to a small allowlist of trusted Shopify domains (`myshopify.com`, `myshopify.io`, `shopify.com`, `spin.dev`, `shop.dev`) before that value is used to build the host that will receive the app's `client_secret`. This validation is applied in `RefreshToken.refresh_access_token`, `TokenExchange.migrate_to_expiring_token`, and `ClientCredentials`, but it is **not** applied in the two most commonly used OAuth entry points: `TokenExchange.exchange_token` and `Oauth.validate_auth_callback`.

### Finding Description
`Utils::ShopValidator` enforces the binding `host used for the token endpoint == a value present in TRUSTED_SHOPIFY_DOMAINS`: [1](#0-0) [2](#0-1) 

This check is correctly wired up before any request that carries the client secret in `RefreshToken.refresh_access_token`: [3](#0-2) 

and in `TokenExchange.migrate_to_expiring_token`: [4](#0-3) 

However, the primary `TokenExchange.exchange_token` method derives the shop directly from the JWT `dest` claim and never routes it through `ShopValidator`: [5](#0-4) 

`JwtPayload#shop` only strips the `https://` prefix from `dest` — it performs no domain-format validation, and `dest` is never checked against a trusted-domain allowlist: [6](#0-5) 

Similarly, `Oauth.validate_auth_callback` uses `auth_query.shop` (taken straight from the callback query string) to build the session/host that receives `client_id`/`client_secret`, without ever calling `ShopValidator`: [7](#0-6) 

In both vulnerable paths, the only check performed is `HmacValidator.validate` (for the OAuth callback) or JWT signature/`aud` verification (for the session token) — neither of which constrains the *value* of `shop`/`dest` to a `*.myshopify.com`-shaped, Shopify-owned host. The equality that should hold — "the host receiving `client_secret` is a member of the trusted Shopify domain set" — is enforced in three call sites but silently skipped in these two, which is precisely the "host validated versus host that receives the `client_secret`" analog called out in scope.

### Impact Explanation
`HttpClient` builds the outbound request host directly from `session.shop`, and both vulnerable flows POST a JSON body containing `client_id` and `client_secret` to that host: [8](#0-7) [9](#0-8) [10](#0-9) 

If `dest`/`shop` can ever carry a value outside the trusted domain set (e.g. a spoofed or malformed subdomain that still passes signature checks, or a host application that forwards attacker-influenced query parameters into `AuthQuery`/`JwtPayload` before this library's own checks run), the app's `client_secret` — a Critical-impact credential per the scope rules — would be exfiltrated to that host. This is exactly the SSRF-with-credentials class the library's own `ShopValidator` was introduced to prevent (per `CHANGELOG.md`'s `#1443` entry), but the mitigation was inconsistently applied across the OAuth surface.

### Likelihood Explanation
The likelihood is moderated by the fact that both call sites are additionally protected by HMAC (`AuthQuery`) or JWT signature (`JwtPayload`) checks that require possession of `api_secret_key` to fully forge the `shop`/`dest` field from scratch. However, the analogous, already-fixed call sites (`refresh_token.rb`, `token_exchange.rb#migrate_to_expiring_token`) demonstrate that the library's own maintainers consider signature validity alone insufficient — hence the extra `ShopValidator.sanitize!` guard. The two vulnerable code paths (`exchange_token` and `validate_auth_callback`) are also the two most heavily used entry points (main OAuth callback handler and the recommended token-exchange flow for embedded apps), making the inconsistency high-impact if any bypass of the signature/JWT check surfaces.

### Recommendation
Route `auth_query.shop` in `Oauth.validate_auth_callback` and `jwt_payload.shop`/`dest` in `TokenExchange.exchange_token` through `Utils::ShopValidator.sanitize!` before constructing the `Session`/`HttpClient` that will transmit `client_id`/`client_secret`, exactly as already done in `RefreshToken.refresh_access_token` and `TokenExchange.migrate_to_expiring_token`.

### Proof of Concept
Conceptual (mirrors the loop-counter bug's pattern of an unenforced invariant leading to unsafe state):
1. Compare `lib/shopify_api/auth/refresh_token.rb:24` (`validated_shop = Utils::ShopValidator.sanitize!(shop)`) against `lib/shopify_api/auth/token_exchange.rb:41` (`dest_shop = jwt_payload.shop` — no sanitize call) and `lib/shopify_api/auth/oauth.rb:73` (`Auth::Session.new(shop: auth_query.shop)` — no sanitize call).
2. In both unguarded paths, the unsanitized shop value is passed straight into `Clients::HttpClient.new(session: ..., base_path: "/admin/oauth")`, which uses `session.shop` as the request host and includes `client_secret` in the POST body (`lib/shopify_api/auth/oauth.rb:74-90`, `lib/shopify_api/auth/token_exchange.rb:51-65`).
3. Any code path that allows `dest`/`shop` to diverge from the trusted-domain allowlist (whether through host-application misuse of the constructors, or a future weakening of the signature checks) results in the app's `client_secret` being sent to that arbitrary host — the exact SSRF-with-credentials outcome `ShopValidator` was built to prevent, but which is not enforced here.

### Citations

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

**File:** lib/shopify_api/auth/token_exchange.rb (L39-65)
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
          body = {
            client_id: ShopifyAPI::Context.api_key,
            client_secret: ShopifyAPI::Context.api_secret_key,
            grant_type: TOKEN_EXCHANGE_GRANT_TYPE,
            subject_token: session_token,
            subject_token_type: ID_TOKEN_TYPE,
            requested_token_type: requested_token_type.serialize,
          }

          if requested_token_type == RequestedTokenType::OFFLINE_ACCESS_TOKEN
            body.merge!({ expiring: ShopifyAPI::Context.expiring_offline_access_tokens ? 1 : 0 })
          end

          client = Clients::HttpClient.new(session: shop_session, base_path: "/admin/oauth")
```

**File:** lib/shopify_api/auth/token_exchange.rb (L97-115)
```ruby
        def migrate_to_expiring_token(shop:, non_expiring_offline_token:)
          unless ShopifyAPI::Context.setup?
            raise ShopifyAPI::Errors::ContextNotSetupError,
              "ShopifyAPI::Context not setup, please call ShopifyAPI::Context.setup"
          end

          validated_shop = Utils::ShopValidator.sanitize!(shop)
          shop_session = ShopifyAPI::Auth::Session.new(shop: validated_shop)
          body = {
            client_id: ShopifyAPI::Context.api_key,
            client_secret: ShopifyAPI::Context.api_secret_key,
            grant_type: TOKEN_EXCHANGE_GRANT_TYPE,
            subject_token: non_expiring_offline_token,
            subject_token_type: RequestedTokenType::OFFLINE_ACCESS_TOKEN.serialize,
            requested_token_type: RequestedTokenType::OFFLINE_ACCESS_TOKEN.serialize,
            expiring: "1",
          }

          client = Clients::HttpClient.new(session: shop_session, base_path: "/admin/oauth")
```

**File:** lib/shopify_api/auth/jwt_payload.rb (L33-50)
```ruby
        @iss = T.let(payload_hash["iss"], String)
        @dest = T.let(payload_hash["dest"], String)
        @aud = T.let(payload_hash["aud"], String)
        @sub = T.let(payload_hash["sub"], T.nilable(String))
        @exp = T.let(payload_hash["exp"], Integer)
        @nbf = T.let(payload_hash["nbf"], Integer)
        @iat = T.let(payload_hash["iat"], Integer)
        @jti = T.let(payload_hash["jti"], String)
        @sid = T.let(payload_hash["sid"], T.nilable(String))

        raise ShopifyAPI::Errors::InvalidJwtTokenError,
          "Session token had invalid API key" unless @aud == Context.api_key
      end

      sig { returns(String) }
      def shop
        @dest.gsub("https://", "")
      end
```

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

**File:** lib/shopify_api/clients/http_client.rb (L11-33)
```ruby
      sig { params(base_path: String, session: T.nilable(Auth::Session)).void }
      def initialize(base_path:, session: nil)
        session ||= Context.active_session
        raise Errors::NoActiveSessionError, "No passed or active session" unless session

        api_host = Context.api_host

        @base_uri = T.let("https://#{api_host || session.shop}", String)
        @base_uri_and_path = T.let("#{@base_uri}#{base_path}", String)

        user_agent_prefix = Context.user_agent_prefix.nil? ? "" : "#{Context.user_agent_prefix} | "

        @headers = T.let({
          "User-Agent": "#{user_agent_prefix}Shopify API Library v#{VERSION} | Ruby #{RUBY_VERSION}",
          "Accept": "application/json",
        }, T::Hash[T.any(Symbol, String), T.untyped])

        @headers["Host"] = session.shop unless api_host.nil?

        unless session.access_token.nil? || T.must(session.access_token).empty?
          @headers["X-Shopify-Access-Token"] = T.cast(session.access_token, String)
        end
      end
```
