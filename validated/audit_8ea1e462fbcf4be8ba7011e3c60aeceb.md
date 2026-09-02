This is a strong finding: `oauth.rb`'s `validate_auth_callback` and `token_exchange.rb`'s `exchange_token` both send `client_secret` to a host derived directly from an unsanitized `shop` value, unlike `client_credentials.rb` and `refresh_token.rb`, which call `Utils::ShopValidator.sanitize!` first.

### Title
SSRF with app's `client_secret` via unsanitized `shop`/`dest` host in OAuth callback and Token Exchange - (File: lib/shopify_api/auth/oauth.rb, lib/shopify_api/auth/token_exchange.rb)

### Summary
`ShopifyAPI::Auth::Oauth.validate_auth_callback` and `ShopifyAPI::Auth::TokenExchange.exchange_token` build a `Session` whose `shop` is used directly as the destination host for the `access_token` request that carries the app's `client_id`/`client_secret`, without ever passing it through `Utils::ShopValidator.sanitize!`. By contrast, the sibling flows `ClientCredentials.client_credentials` and `RefreshToken.refresh_access_token` explicitly call `Utils::ShopValidator.sanitize!(shop)` before constructing the session used for the same credential-carrying request.

### Finding Description
`Clients::HttpClient#initialize` builds the request host straight from `session.shop`: [1](#0-0) 

`ClientCredentials.client_credentials` and `RefreshToken.refresh_access_token` both sanitize the `shop` argument via `Utils::ShopValidator.sanitize!` — which restricts the host to `TRUSTED_SHOPIFY_DOMAINS` (`shopify.com`, `myshopify.io`, `myshopify.com`, `spin.dev`, `shop.dev`) — before creating the `Session` used to send the `client_secret`-bearing request: [2](#0-1) [3](#0-2) 

However, `Oauth.validate_auth_callback` uses `auth_query.shop` directly, with no call to `ShopValidator`, to build the `null_session` that is used to POST the `client_secret` to `#{auth_query.shop}/admin/oauth/access_token`: [4](#0-3) 

Likewise, `TokenExchange.exchange_token` takes `dest_shop = jwt_payload.shop` (the JWT `dest` claim, only stripped of `"https://"` in `JwtPayload#shop`) and uses it unsanitized to build the session that receives the `client_secret`: [5](#0-4) [6](#0-5) 

The identity binding that should hold is: *the host that receives the `client_secret`* == *a value validated to be a trusted `*.myshopify.com`/`*.myshopify.io`/etc. domain*. In `client_credentials.rb`/`refresh_token.rb` this equality is enforced via `ShopValidator.sanitize!`. In `oauth.rb` and `token_exchange.rb` it is not — the `shop` used for the outbound host is only checked for HMAC/JWT-signature validity, not for being a Shopify-owned domain string.

For the OAuth callback path specifically: `AuthQuery#to_signable_string` does include `shop` in the HMAC-signed payload: [7](#0-6) 
so the `shop` value is itself only bound to "was signed by our secret," not to "is a `*.myshopify.com` domain." Since the HMAC in the callback is computed by Shopify server-side over the redirect query string, and Shopify is expected to only ever populate `shop` with a real store domain, this path is not attacker-forgeable purely from the client side under normal operation — the exploitability hinges on whether an upstream/legitimate redirect could ever place an unexpected value into `shop` (e.g., open-redirect style query tampering before HMAC verification is not possible because HMAC covers `shop`). Given `shop` is HMAC-covered, this specific path is largely mitigated by the signature itself, unlike a pure "field not covered by HMAC" case.

For `TokenExchange.exchange_token`, the `dest` claim comes from a JWT that is decoded and signature-verified against `Context.api_secret_key` in `JwtPayload#initialize`: [8](#0-7) 
Only `aud` (must equal `Context.api_key`) is validated as an identity binding; `dest`/`iss` are decoded but never checked for domain trustworthiness (no `ShopValidator` call), and there's no cross-check that `dest`'s host is consistent with `iss`'s host. Because the JWT is HMAC-signed with the shared `api_secret_key`, an external attacker without that secret cannot forge an arbitrary `dest`, so this also is not exploitable by an unprivileged internet user without already possessing `api_secret_key`.

### Impact Explanation
If this inconsistency were exploitable, the impact would be High: SSRF carrying the app's `client_id`/`client_secret` to an attacker-chosen host, since both `validate_auth_callback` and `exchange_token` `POST` the app's `client_secret` to a host derived from `shop`/`dest`. This matches the report's bug class (a value used for a security-relevant computation bypassing an accrual/validation step that a sibling code path performs correctly).

### Likelihood Explanation
Low/not concretely exploitable by an unprivileged internet user: both `shop` (in the OAuth callback) and `dest` (in the JWT for token exchange) are protected by HMAC/JWT signatures computed with `Context.api_secret_key`, which per the scope rules is not something an attacker possesses. Without a way to get an unprivileged party to obtain or forge a validly-signed HMAC/JWT containing an attacker-controlled `shop`/`dest`, there's no concrete path from an internet user to this SSRF — it exists as a code hygiene gap (missing `ShopValidator.sanitize!` compared to the other two auth flows) rather than a provable remote exploit.

### Recommendation
For defense in depth and consistency with `ClientCredentials`/`RefreshToken`, apply `Utils::ShopValidator.sanitize!` to `auth_query.shop` in `Oauth.validate_auth_callback` and to `jwt_payload.shop`/`dest` in `TokenExchange.exchange_token` before constructing the `Session` used to send the `client_secret`-bearing request, ensuring the host that receives credentials is always constrained to `ShopValidator::TRUSTED_SHOPIFY_DOMAINS`.

### Proof of Concept
Not reproducible as a concrete remote exploit: both code paths require a validly-signed HMAC (OAuth callback, signed with `api_secret_key`) or JWT (token exchange, signed with `api_secret_key`) containing an attacker-controlled `shop`/`dest` value, and forging either requires possession of `api_secret_key`, which is explicitly out of scope. This is reported as a code-path inconsistency (missing `ShopValidator.sanitize!` call present in the two sibling flows) rather than a demonstrated end-to-end SSRF.

### Citations

**File:** lib/shopify_api/clients/http_client.rb (L16-19)
```ruby
        api_host = Context.api_host

        @base_uri = T.let("https://#{api_host || session.shop}", String)
        @base_uri_and_path = T.let("#{@base_uri}#{base_path}", String)
```

**File:** lib/shopify_api/auth/client_credentials.rb (L25-33)
```ruby
          validated_shop = Utils::ShopValidator.sanitize!(shop)
          shop_session = ShopifyAPI::Auth::Session.new(shop: validated_shop)
          body = {
            client_id: ShopifyAPI::Context.api_key,
            client_secret: ShopifyAPI::Context.api_secret_key,
            grant_type: CLIENT_CREDENTIALS_GRANT_TYPE,
          }

          client = Clients::HttpClient.new(session: shop_session, base_path: "/admin/oauth")
```

**File:** lib/shopify_api/auth/refresh_token.rb (L24-33)
```ruby
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

**File:** lib/shopify_api/auth/oauth.rb (L60-94)
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
```

**File:** lib/shopify_api/auth/jwt_payload.rb (L23-45)
```ruby
      sig { params(token: String).void }
      def initialize(token)
        payload_hash = begin
          decode_token(token, Context.api_secret_key)
        rescue ShopifyAPI::Errors::InvalidJwtTokenError
          raise unless Context.old_api_secret_key

          decode_token(token, T.must(Context.old_api_secret_key))
        end

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
```

**File:** lib/shopify_api/auth/jwt_payload.rb (L47-51)
```ruby
      sig { returns(String) }
      def shop
        @dest.gsub("https://", "")
      end
      alias_method :shopify_domain, :shop
```

**File:** lib/shopify_api/auth/token_exchange.rb (L39-66)
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
          response = begin
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
