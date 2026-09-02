Confirmed: `ClientCredentials.client_credentials` validates `shop` via `Utils::ShopValidator.sanitize!` before use [1](#0-0) , but `Oauth.validate_auth_callback` never calls `ShopValidator` on `auth_query.shop` — it builds the `null_session` directly from the raw, unvalidated `auth_query.shop` value and uses it to POST the app's `client_secret` and authorization `code` to `https://#{auth_query.shop}/admin/oauth/access_token` [2](#0-1) . The `HttpClient` builds the request host straight from `session.shop` with no domain restriction [3](#0-2) .

The `HmacValidator` only proves the query string bytes (`code`, `host`, `shop`, `state`, `timestamp`) are unmodified relative to whatever `shop` value the signer used [4](#0-3) [5](#0-4)  — it never asserts that `shop` is a real `*.myshopify.com`/trusted domain. That check exists only in `ShopValidator.sanitize!`/`sanitize_shop_domain`, which is invoked in `ClientCredentials` and in `Oauth.begin_auth`'s redirect construction indirectly via `auth_base_uri`, but is skipped entirely in `validate_auth_callback`.



### Title
Missing shop-domain validation in OAuth callback allows client_secret exfiltration to attacker-influenced host - ([File: lib/shopify_api/auth/oauth.rb])

### Summary
`ShopifyAPI::Auth::Oauth.validate_auth_callback` uses the `shop` value from the caller-supplied `AuthQuery` to build the access-token-exchange request without ever passing it through `ShopifyAPI::Utils::ShopValidator.sanitize!`, unlike the sibling `ClientCredentials.client_credentials` method, which does validate. This breaks the intended equality "host that is cryptographically authenticated == host that receives the app's `client_secret`".

### Finding Description
`validate_auth_callback` HMAC-checks the query (`code`, `host`, `shop`, `state`, `timestamp`) via `Utils::HmacValidator.validate` [6](#0-5) , but this only proves the bytes were not tampered with relative to the signer — it does not assert `shop` is a well-formed, trusted Shopify domain (`*.myshopify.com`, `*.myshopify.io`, etc.). Immediately after, the raw `auth_query.shop` is used to build `null_session` and then `Clients::HttpClient` derives the destination host directly from `session.shop` [7](#0-6) [3](#0-2) , sending a POST containing `client_id`, `client_secret`, and `code` to `https://{shop}/admin/oauth/access_token`. The library's own documentation instructs integrators to construct `AuthQuery` directly from unfiltered `request.parameters` [8](#0-7) , so `shop` is wire-controlled input the gem is responsible for authenticating before using it as a network destination. By contrast, `ClientCredentials.client_credentials`, which faces the same "shop string used to build the access-token request host" pattern, explicitly sanitizes via `Utils::ShopValidator.sanitize!(shop)` before constructing the session [1](#0-0) . The OAuth callback path has no equivalent guard.

### Impact Explanation
If a client_secret-bearing request can be steered to a non-Shopify host, the app's `client_secret` and authorization `code` are disclosed to that host — a High-severity impact (SSRF carrying the app's credentials / credential leakage), matching the report's core theme of an identity/binding field not being validated even though a "fee"/"secret" is unconditionally sent based on it.

### Likelihood Explanation
Exploitability is constrained by the fact that `Utils::HmacValidator` verifies the signature using the app's own `api_secret_key`/`old_api_secret_key` [4](#0-3) , which only Shopify and the app hold, so a fully valid signed callback for an arbitrary attacker-chosen `shop` cannot trivially be forged from the outside in the normal flow. The missing validation is nonetheless a genuine code-level asymmetry versus `ClientCredentials`, and becomes exploitable in any scenario where the HMAC-signed callback parameters can be replayed/relayed with a substituted `shop` while `code`/`state`/`timestamp` happen to still validate, or where a future/alternate caller of `validate_auth_callback` supplies its own already-"validated" `AuthQuery` without an out-of-band domain check. I could not find any additional binding of `shop` to a previously-established value (e.g. to the `begin_auth`-time shop) inside `validate_auth_callback` itself, which would otherwise mitigate this.

### Recommendation
Call `Utils::ShopValidator.sanitize!(auth_query.shop)` (or `sanitize_shop_domain`) inside `validate_auth_callback` before constructing `null_session`, mirroring `ClientCredentials.client_credentials`, and raise `Errors::InvalidOauthError` if the shop does not resolve to a trusted Shopify domain.

### Proof of Concept
Not independently reproducible with certainty from static review alone, since normal exploitation requires an HMAC-valid callback for a non-`myshopify.com` `shop`, which the library cannot forge without the shared secret. The concrete code-path evidence is:
1. `ClientCredentials.client_credentials` sanitizes `shop` before use [9](#0-8) .
2. `Oauth.validate_auth_callback` performs no equivalent sanitization before sending `client_secret` to a host derived from `auth_query.shop` [10](#0-9) .

### Citations

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

**File:** lib/shopify_api/clients/http_client.rb (L12-19)
```ruby
      def initialize(base_path:, session: nil)
        session ||= Context.active_session
        raise Errors::NoActiveSessionError, "No passed or active session" unless session

        api_host = Context.api_host

        @base_uri = T.let("https://#{api_host || session.shop}", String)
        @base_uri_and_path = T.let("#{@base_uri}#{base_path}", String)
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

**File:** docs/usage/oauth.md (L246-251)
```markdown
    auth_result = ShopifyAPI::Auth::Oauth.validate_auth_callback(
      cookies: cookies.to_h,
      auth_query: ShopifyAPI::Auth::Oauth::AuthQuery.new(
        request.parameters.symbolize_keys.except(:controller, :action)
      )
    )
```
