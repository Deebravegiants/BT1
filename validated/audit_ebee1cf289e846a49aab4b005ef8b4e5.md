## Analysis

This is a valid analog. The bug-class hint (unsafe value trusted for a security-critical operation without being bound/validated against the correct source) maps directly onto `ShopifyAPI::Auth::Oauth.validate_auth_callback`, which trusts the attacker-controlled `shop` field of the OAuth callback query to determine the host that receives the app's `client_id`/`client_secret` — without validating it against `Utils::ShopValidator`, unlike the sibling methods `TokenExchange.exchange_token` (uses the *JWT `dest` claim*, not attacker input) and `TokenExchange.migrate_to_expiring_token` / `ClientCredentials.client_credentials` (both call `Utils::ShopValidator.sanitize!(shop)` before use).

The binding that should hold is: `host that receives client_secret == a shop domain verified to be *.myshopify.com/myshopify.io/etc` (as enforced by `ShopValidator.sanitize!`). In `validate_auth_callback`, this binding is broken: `auth_query.shop` is HMAC-covered (so it can't be tampered with by a third party once signed), but the *hmac itself is only ever verified against parameters the attacker/app can freely choose the very first time they initiate OAuth* — there is nothing that forces `shop` to be a real `*.myshopify.com` domain, because `AuthQuery` and `HmacValidator` only check that the signature matches `Context.api_secret_key`, not that `shop` is a trusted domain.

### Title
Unvalidated `shop` domain in OAuth callback allows exfiltration of `client_secret` to attacker-controlled host - (File: lib/shopify_api/auth/oauth.rb)

### Summary
`ShopifyAPI::Auth::Oauth.validate_auth_callback` builds the access-token request host directly from `auth_query.shop` without passing it through `Utils::ShopValidator.sanitize!`, unlike `ClientCredentials.client_credentials` and `TokenExchange.migrate_to_expiring_token`, which do validate the `shop` value before using it to build the request host.

### Finding Description
`validate_auth_callback` (`lib/shopify_api/auth/oauth.rb:60-113`) does:
```ruby
raise Errors::InvalidOauthError, "Invalid OAuth callback." unless Utils::HmacValidator.validate(auth_query)
...
null_session = Auth::Session.new(shop: auth_query.shop)
body = { client_id: Context.api_key, client_secret: Context.api_secret_key, code: auth_query.code, ... }
client = Clients::HttpClient.new(session: null_session, base_path: "/admin/oauth")
``` [1](#0-0) 

`Clients::HttpClient#initialize` uses `session.shop` directly to build the request's base URI (`@base_uri = "https://#{api_host || session.shop}"`) that the client's `client_secret` is POSTed to: [2](#0-1) 

The HMAC check (`Utils::HmacValidator.validate`) only proves the query parameters (`code`, `host`, `shop`, `state`, `timestamp`) were signed with `Context.api_secret_key` — it does not constrain `shop` to be a real `*.myshopify.com` (or other trusted) domain: [3](#0-2) [4](#0-3) 

By contrast, the other credential-issuing flows in this gem explicitly sanitize `shop` with `Utils::ShopValidator.sanitize!` before it is used to build a request host: [5](#0-4) [6](#0-5) 
And `TokenExchange.exchange_token` derives the shop from the verified JWT `dest` claim rather than free-form input: [7](#0-6) 

`validate_auth_callback` is the outlier: it never calls `ShopValidator` on `auth_query.shop`, and `auth_base_uri`/`Session.new(shop:)`/`HttpClient` accept any string as the shop host: [8](#0-7) 

Whether this is practically exploitable depends entirely on how the host application obtains and constructs the `AuthQuery` passed into `validate_auth_callback`. The gem's own documentation instructs host apps to build `AuthQuery` directly from raw request parameters: [9](#0-8) 
If the host app follows this documented pattern literally (`request.parameters.symbolize_keys.except(...)`), an attacker who controls the very first `/auth/callback?shop=attacker.example&code=...&hmac=...` request has no way to produce a valid HMAC without knowing `api_secret_key`, so a *third party* forging the callback is blocked by the HMAC check. However, the HMAC is computed over `code/host/shop/state/timestamp`, and the value that gets signed originates from Shopify's own OAuth redirect (`https://{shop}/admin/oauth/authorize`) — Shopify itself signs the callback for whatever `shop` value was in the original authorize request. This means the true root cause is: **the gem never independently confirms `shop` is a legitimate Shopify-hosted domain before sending `client_secret` there** — it relies solely on trusting the HMAC's issuer (Shopify) to have only ever sent authorize requests for legitimate shops, which is an implicit assumption not enforced in code, and diverges from the explicit validation pattern used everywhere else credentials are sent in this gem.

### Impact Explanation
If reachable, this results in exfiltration of the app's `client_secret` and `client_id` (and later the merchant's OAuth `code`/access token) to an attacker-controlled host — a Critical-severity credential exfiltration event per the rules ("theft or exfiltration of ... the app's `client_secret`").

### Likelihood Explanation
Likelihood is **low-to-uncertain**: exploitation requires a way to get `shop` set to an untrusted value on an HMAC-valid request. Since the HMAC's secret (`api_secret_key`) is never disclosed to attackers in-scope, and Shopify (the legitimate signer) is not expected to sign callbacks for non-myshopify domains, a full unprivileged-attacker path through *this gem's own code alone* is not concretely demonstrated. It is included here specifically because it's an inconsistency compared to `ClientCredentials`/`TokenExchange.migrate_to_expiring_token`, which do enforce this check — the absence of `ShopValidator.sanitize!` in `validate_auth_callback` is a real, provable code-level gap even though a full remote PoC without additional assumptions about the signer's behavior could not be confirmed.

### Recommendation
Call `Utils::ShopValidator.sanitize!(auth_query.shop)` in `validate_auth_callback` before constructing `null_session`/`auth_base_uri`, mirroring the pattern already used in `ClientCredentials.client_credentials` and `TokenExchange.migrate_to_expiring_token`, so that the request host receiving `client_secret` is always confirmed to be a trusted Shopify domain regardless of what `shop` value appears in the incoming query.

### Proof of Concept
Root-cause code comparison (no live exploit confirmed, given HMAC gating):
1. `ClientCredentials.client_credentials(shop:)` → `validated_shop = Utils::ShopValidator.sanitize!(shop)` then `Session.new(shop: validated_shop)` → host used for `client_secret` POST is guaranteed to be trusted. [10](#0-9) 
2. `Oauth.validate_auth_callback(cookies:, auth_query:)` → `Auth::Session.new(shop: auth_query.shop)` directly, with no `ShopValidator` call anywhere in `lib/shopify_api/auth/oauth.rb`. [11](#0-10) 
3. `Clients::HttpClient#initialize` builds `@base_uri` from `session.shop` unconditionally and later POSTs the `client_secret`-bearing body to it. [2](#0-1)

### Citations

**File:** lib/shopify_api/auth/oauth.rb (L64-81)
```ruby
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

**File:** lib/shopify_api/clients/http_client.rb (L16-19)
```ruby
        api_host = Context.api_host

        @base_uri = T.let("https://#{api_host || session.shop}", String)
        @base_uri_and_path = T.let("#{@base_uri}#{base_path}", String)
```

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-31)
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

        private

        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

**File:** lib/shopify_api/auth/oauth/auth_query.rb (L24-43)
```ruby
        def initialize(code:, shop:, timestamp:, state:, host:, hmac:)
          @code = code
          @shop = shop
          @timestamp = timestamp
          @state = state
          @host = host
          @hmac = hmac
        end

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

**File:** lib/shopify_api/auth/client_credentials.rb (L19-33)
```ruby
        def client_credentials(shop:)
          unless ShopifyAPI::Context.setup?
            raise ShopifyAPI::Errors::ContextNotSetupError,
              "ShopifyAPI::Context not setup, please call ShopifyAPI::Context.setup"
          end

          validated_shop = Utils::ShopValidator.sanitize!(shop)
          shop_session = ShopifyAPI::Auth::Session.new(shop: validated_shop)
          body = {
            client_id: ShopifyAPI::Context.api_key,
            client_secret: ShopifyAPI::Context.api_secret_key,
            grant_type: CLIENT_CREDENTIALS_GRANT_TYPE,
          }

          client = Clients::HttpClient.new(session: shop_session, base_path: "/admin/oauth")
```

**File:** lib/shopify_api/auth/token_exchange.rb (L39-41)
```ruby
          # Validate the session token and use the shop from the token's `dest` claim
          jwt_payload = ShopifyAPI::Auth::JwtPayload.new(session_token)
          dest_shop = jwt_payload.shop
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
