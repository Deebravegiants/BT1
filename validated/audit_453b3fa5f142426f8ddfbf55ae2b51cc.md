This confirms the key finding: `TokenExchange.exchange_token` never calls `Utils::ShopValidator.sanitize!` on the shop it uses to build the outbound request, unlike `client_credentials.rb` which does call `Utils::ShopValidator.sanitize!(shop)` before use.

### Title
Unvalidated JWT `dest` claim used to construct the OAuth token-exchange request host, bypassing `ShopValidator` domain trust checks - (File: `lib/shopify_api/auth/token_exchange.rb`)

### Summary
`ShopifyAPI::Auth::TokenExchange.exchange_token` derives the request host from the session token's `dest` claim via `ShopifyAPI::Auth::JwtPayload#shop` [1](#0-0)  and uses that value directly, without ever passing it through `Utils::ShopValidator.sanitize!`, to build the `Session` and the `HttpClient` that sends the request containing the app's `client_secret` [2](#0-1) . By contrast, the sibling `ClientCredentials.client_credentials` flow explicitly calls `Utils::ShopValidator.sanitize!(shop)` before building the equivalent request [3](#0-2) . `HttpClient#initialize` builds the outbound URI directly from `session.shop` when no `Context.api_host` is configured: `@base_uri = "https://#{api_host || session.shop}"` [4](#0-3) .

### Finding Description
The identity binding that should hold is: *the host that receives the app's `client_secret` == a value validated as a trusted Shopify domain* (`ShopValidator::TRUSTED_SHOPIFY_DOMAINS`) [5](#0-4) . In `TokenExchange.exchange_token`, this binding is broken: the `dest` claim is only checked for correct JWT signature/`aud`, never checked against `ShopValidator.trusted_domains` [6](#0-5) . `JwtPayload#shop` merely strips the `https://` prefix and returns the raw claim value verbatim [1](#0-0) , and `exchange_token` passes this raw `dest_shop` straight into `Session.new(shop: dest_shop)` and `Session.from(shop: dest_shop, ...)` [7](#0-6) , which then becomes the request host in `HttpClient`.

While the JWT signature itself is verified with `Context.api_secret_key` (a value only the merchant's Shopify instance and the app know), the `dest` claim's *content* is not independently constrained to be a `myshopify.com`/trusted domain — it is trusted at face value once the signature check passes. This differs from the parallel `client_credentials` code path, and from the documented App Bridge session-token contract, which states the `dest` claim "determines which shop receives the token exchange request" [8](#0-7)  — implying the library is expected to validate that destination, similar to how `ShopValidator` is used elsewhere in this codebase for exactly this purpose.

### Impact Explanation
If the `dest` claim can ever contain a non-myshopify value (e.g., due to a compromised/misconfigured signer, or a different Shopify surface that issues signed JWTs with attacker-influenced `dest`, such as checkout UI extension tokens shown in `docs/usage/oauth.md` context and `jwt_payload_test.rb` — noting the JWT payload class explicitly supports non-`/admin` issuers such as checkout UI extensions [9](#0-8) ), the library will POST the app's `client_id`/`client_secret` and the subject token to that host, resulting in credential leakage/SSRF carrying the app's credentials. This matches the High-impact category: "SSRF with the app's credentials."

### Likelihood Explanation
Exploitability depends entirely on whether an attacker can get any signed JWT (from any legitimate Shopify-controlled signing path) accepted by `JwtPayload` whose `dest` is not a merchant admin domain — e.g. a checkout/extension-issued session token forwarded into `exchange_token` by a confused host app. This is a real gap in defense-in-depth (missing the same `ShopValidator` check performed in the sibling `client_credentials` flow), but it requires a legitimately-signed token with an unexpected `dest`/`iss` combination to be forwarded to this specific call — a scenario the library does not itself prevent, since `TokenExchange.exchange_token` never checks `iss` shape or restricts `dest` to trusted domains.

### Recommendation
In `ShopifyAPI::Auth::TokenExchange.exchange_token`, validate `dest_shop` with `Utils::ShopValidator.sanitize!(dest_shop)` (mirroring `ClientCredentials.client_credentials`) before constructing `shop_session` and issuing the token-exchange request, and/or restrict `JwtPayload` acceptance to tokens whose `iss` ends with `/admin` when used for OAuth/token-exchange flows.

### Proof of Concept
1. Obtain (or have a host application forward) a validly-signed session token whose `dest` claim is set to a non-myshopify but attacker-influenced value (e.g., issued by a different Shopify surface/extension token, or a future signer that reflects an app-supplied redirect/destination).
2. Call `ShopifyAPI::Auth::TokenExchange.exchange_token(session_token: token, requested_token_type: ...)`.
3. `JwtPayload.new(token)` passes signature/`aud` checks and returns `shop` = raw `dest` value [10](#0-9) .
4. `exchange_token` builds `shop_session = Session.new(shop: dest_shop)` and `Clients::HttpClient.new(session: shop_session, base_path: "/admin/oauth")` [11](#0-10) , which computes `@base_uri = "https://#{dest_shop}"` [4](#0-3) .
5. The library POSTs `client_id`, `client_secret`, and the subject token to `https://#{dest_shop}/admin/oauth/access_token`, sending the app's credentials to a host that was never checked against `ShopValidator::TRUSTED_SHOPIFY_DOMAINS`.

### Citations

**File:** lib/shopify_api/auth/jwt_payload.rb (L33-51)
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
      alias_method :shopify_domain, :shop
```

**File:** lib/shopify_api/auth/token_exchange.rb (L39-88)
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
            client.request(
              Clients::HttpRequest.new(
                http_method: :post,
                path: "access_token",
                body: body,
                body_type: "application/json",
              ),
            )
          rescue ShopifyAPI::Errors::HttpResponseError => error
            if error.code == 400 && error.response.body["error"] == "invalid_subject_token"
              raise ShopifyAPI::Errors::InvalidJwtTokenError, "Session token was rejected by token exchange"
            end

            raise error
          end

          session_params = T.cast(response.body, T::Hash[String, T.untyped]).to_h

          Session.from(
            shop: dest_shop,
            access_token_response: Oauth::AccessTokenResponse.from_hash(session_params),
          )
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

**File:** lib/shopify_api/clients/http_client.rb (L16-19)
```ruby
        api_host = Context.api_host

        @base_uri = T.let("https://#{api_host || session.shop}", String)
        @base_uri_and_path = T.let("#{@base_uri}#{base_path}", String)
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

**File:** docs/usage/oauth.md (L75-77)
```markdown
| `session_token` | `String` | Yes| - | The session token (Shopify Id Token) provided by App Bridge in either the request 'Authorization' header or URL param when the app is loaded in Admin. Its `dest` claim determines which shop receives the token exchange request. |
| `requested_token_type` | `TokenExchange::RequestedTokenType` | Yes | - | The type of token requested. Online: `TokenExchange::RequestedTokenType::ONLINE_ACCESS_TOKEN` or offline: `TokenExchange::RequestedTokenType::OFFLINE_ACCESS_TOKEN`. |
| `shop` | `String` | No | `nil` | **Deprecated**, will be removed in v17.0.0. Ignored for the request host; the shop always comes from the session token `dest` claim. If passed, logs a deprecation warning. |
```

**File:** test/auth/jwt_payload_test.rb (L23-32)
```ruby
        @checkout_ui_extension_jwt_payload = {
          iss: "https://test-shop.myshopify.io/checkouts",
          dest: "test-shop.myshopify.io",
          aud: ShopifyAPI::Context.api_key,
          sub: "gid://shopify/Customer/123456789",
          exp: (Time.now + 10).to_i,
          nbf: 1234,
          iat: 1234,
          jti: "4321",
        }
```
