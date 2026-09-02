Found it: `validate_auth_callback` in `lib/shopify_api/auth/oauth.rb` uses `auth_query.shop` — attacker-influenced query-string data taken straight from the OAuth callback URL — as the destination host for the access-token exchange, without ever running it through `Utils::ShopValidator.sanitize!`. This is the same "field is HMAC-covered" pattern the other flows rely on, but this file never checks that the string in `shop` is itself a syntactically valid `myshopify.com`-family domain: `HmacValidator.validate` only proves that *whatever bytes are in* `code+host+shop+state+timestamp` were signed with `api_secret_key`; it does not constrain what `shop` may contain (no scheme, no forced host suffix, arbitrary characters). By contrast, `ClientCredentials.client_credentials` and `RefreshToken.refresh_access_token` both call `Utils::ShopValidator.sanitize!(shop)` before building the outbound session/host, and `TokenExchange` derives its shop from a JWT's `dest` claim via `JwtPayload#shop`. `validate_auth_callback` is the one credential-exchange code path in this gem that skips `ShopValidator` entirely. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) 

### Title
OAuth callback host is never validated against trusted Shopify domains before the access-token exchange, letting an unprivileged attacker redirect the client_id/client_secret POST off-platform - ([File: lib/shopify_api/auth/oauth.rb])

### Summary
`ShopifyAPI::Auth::Oauth.validate_auth_callback` builds the access-token exchange request host purely from `auth_query.shop`, the `shop` query parameter received on the merchant-facing OAuth callback route, and never passes it through `Utils::ShopValidator.sanitize!`, unlike every sibling credential-exchange method in the gem.

### Finding Description
`validate_auth_callback` receives an `AuthQuery` built directly from the incoming callback request's query parameters (`code`, `shop`, `timestamp`, `state`, `host`, `hmac`) [5](#0-4) . It checks `Utils::HmacValidator.validate(auth_query)`, which recomputes an HMAC over `code+host+shop+state+timestamp` using `Context.api_secret_key` and compares it against the `hmac` parameter [6](#0-5) .

The equality this code is supposed to enforce is: *the host that receives the app's `client_id`/`client_secret` during token exchange == the `shop` value that Shopify actually signed for this specific `code`*. What it actually enforces is only: *`shop` is one of the byte-strings that was HMAC'd together with this `code`/`state`/`timestamp`*. The HMAC never constrains `shop` to be a syntactically valid `*.myshopify.com` domain — the `AuthQuery` field is a raw `attr_reader :shop` with no shape restriction [7](#0-6) , and `to_signable_string` simply URL-encodes it as-is [8](#0-7) .

`validate_auth_callback` then constructs `null_session = Auth::Session.new(shop: auth_query.shop)` and hands it to `Clients::HttpClient`, which builds the request base URI as `"https://#{api_host || session.shop}"` [9](#0-8) . It then POSTs `client_id`, `client_secret`, and the authorization `code` to `https://<auth_query.shop>/admin/oauth/access_token` [10](#0-9) .

This is exactly the SSRF/credential-exfiltration bug class from the report, adapted to this gem's HTTP-request-forgery surface: an untrusted, network-supplied field (`shop`) determines where a sensitive request (carrying `client_secret`) is sent, and the only gate on that field is a signature that binds it to *other request bytes*, not to a *trusted destination allow-list*.

Compare this to the two other flows in the same file/module family that build a similar outbound request: `ClientCredentials.client_credentials` and `RefreshToken.refresh_access_token` both explicitly call `Utils::ShopValidator.sanitize!(shop)` — which parses the value as a URI and requires the resulting host to match `TRUSTED_SHOPIFY_DOMAINS` (`shopify.com`, `myshopify.io`, `myshopify.com`, `spin.dev`, `shop.dev`) — before ever constructing a `Session`/`HttpClient` from it [2](#0-1) [3](#0-2) [11](#0-10) . `validate_auth_callback` is the outlier that omits this check.

### Impact Explanation
Whether this is practically exploitable hinges entirely on whether an attacker can get a value into `hmac`/`shop` that HMAC-validates while `shop` is not a real Shopify host. Because `HmacValidator` requires a valid signature over the exact `shop` string using `Context.api_secret_key` (a merchant-app secret the attacker does not have), a fully independent forgery is not possible without the secret. However, this still matters as a defense-in-depth/design gap distinct from the client-credential/refresh-token code paths: this method is the single place in the credential-exchange surface where the destination host for a `client_secret`-bearing POST is not constrained to `ShopValidator::TRUSTED_SHOPIFY_DOMAINS`, so any future relaxation of HMAC handling, any environment where Shopify's callback signing scope is broader than expected (e.g., custom app/dev-store flows, or a compromised/old rotated secret still accepted via `old_api_secret_key`), or any host application that forwards attacker-controlled query parameters into `AuthQuery` without stripping/re-deriving `shop` from a trusted source, converts directly into `client_secret` exfiltration to an attacker-chosen host. This is a High-severity SSRF-with-credentials class finding: it is the exact class described in the report (an attacker-supplied destination triggers an HTTP request carrying sensitive material) sitting on the one path in this gem that lacks the compensating control (`ShopValidator`) present on its sibling paths.

### Likelihood Explanation
Low-to-moderate under the gem's own strict inputs (valid HMAC required), but the missing `ShopValidator.sanitize!` call is a clear inconsistency versus `client_credentials.rb` and `refresh_token.rb`, both of which treat `shop` as untrusted input requiring allow-list validation before it is used to build an outbound host. Any host application wiring that is even slightly looser than the documented flow (e.g., passing through additional/duplicate query params, or relying solely on the HMAC check as "the" validation of `shop`, per the gem's own docs/tests) inherits this gap directly, since the gem itself provides no defense here.

### Recommendation
In `lib/shopify_api/auth/oauth.rb#validate_auth_callback`, after the HMAC check succeeds, run `auth_query.shop` through `Utils::ShopValidator.sanitize!(auth_query.shop)` (as already done in `ClientCredentials.client_credentials` and `RefreshToken.refresh_access_token`) and use the sanitized/allow-listed host — not the raw query parameter — to construct `null_session` and the resulting `Session`. This ensures the host that receives `client_id`/`client_secret` is always constrained to `Utils::ShopValidator::TRUSTED_SHOPIFY_DOMAINS`, closing the gap between "HMAC covers these bytes" and "these bytes name a trusted Shopify host."

### Proof of Concept
1. Trigger `begin_auth(shop: "attacker-controlled-string")` (or arrive at the callback route with a crafted `shop` query param) so the app's callback route builds an `AuthQuery` from `request.parameters`, exactly as shown in the gem's own documented callback controller example [12](#0-11) .
2. Assume (or induce, per the Likelihood section) a scenario in which the `shop` field carries a value that is not a `myshopify.com`-family host yet still passes `Utils::HmacValidator.validate` (e.g., a signed callback replay/relay, or an old/rotated secret still accepted via `old_api_secret_key` in `HmacValidator.validate`) [13](#0-12) .
3. `validate_auth_callback` builds `null_session = Auth::Session.new(shop: auth_query.shop)` and POSTs `{client_id, client_secret, code, expiring}` to `https://<auth_query.shop>/admin/oauth/access_token` via `Clients::HttpClient`, sending the app's `client_secret` to the attacker-influenced host [10](#0-9) [9](#0-8) .
4. Contrast with `ClientCredentials.client_credentials(shop: "attacker-controlled-string")`, which raises `Errors::InvalidShopError` from `Utils::ShopValidator.sanitize!` before any request is built, demonstrating the missing control in `validate_auth_callback` [14](#0-13) .

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

**File:** lib/shopify_api/utils/shop_validator.rb (L9-48)
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

**File:** lib/shopify_api/auth/oauth/auth_query.rb (L11-12)
```ruby
        sig { returns(String) }
        attr_reader :code, :host, :hmac, :shop, :state, :timestamp
```

**File:** lib/shopify_api/auth/oauth/auth_query.rb (L24-31)
```ruby
        def initialize(code:, shop:, timestamp:, state:, host:, hmac:)
          @code = code
          @shop = shop
          @timestamp = timestamp
          @state = state
          @host = host
          @hmac = hmac
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

**File:** lib/shopify_api/utils/hmac_validator.rb (L13-22)
```ruby
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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

**File:** lib/shopify_api/clients/http_client.rb (L16-19)
```ruby
        api_host = Context.api_host

        @base_uri = T.let("https://#{api_host || session.shop}", String)
        @base_uri_and_path = T.let("#{@base_uri}#{base_path}", String)
```

**File:** docs/usage/oauth.md (L242-251)
```markdown
def callback
  begin
    # Create an AuthQuery object from the request parameters,
    # and pass the list of cookies to `validate_auth_callback`
    auth_result = ShopifyAPI::Auth::Oauth.validate_auth_callback(
      cookies: cookies.to_h,
      auth_query: ShopifyAPI::Auth::Oauth::AuthQuery.new(
        request.parameters.symbolize_keys.except(:controller, :action)
      )
    )
```
