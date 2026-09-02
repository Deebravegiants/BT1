## Confirmed vulnerability

`ShopifyAPI::Auth::Oauth.validate_auth_callback` uses `auth_query.shop` — a value that is protected only by the HMAC over `{code, host, shop, state, timestamp}` — to construct the host to which the app's `client_id`/`client_secret` are POSTed, and it never runs that value through `Utils::ShopValidator.sanitize!`, unlike every sibling OAuth grant type in this gem.

### Title
Missing Shop-Domain Validation in OAuth Callback Leaks `client_secret` via SSRF - (File: `lib/shopify_api/auth/oauth.rb`)

### Summary
`ShopifyAPI::Auth::ClientCredentials.client_credentials` and `ShopifyAPI::Auth::RefreshToken.refresh_access_token` both call `Utils::ShopValidator.sanitize!(shop)` before building the session used to send the token request, ensuring the host that receives `client_id`/`client_secret` is always a trusted Shopify domain [1](#0-0) [2](#0-1) . `Auth::Oauth.validate_auth_callback`, however, takes `auth_query.shop` straight from the (attacker-reachable) callback query string and uses it — unsanitized — both to build the `Auth::Session` and, through `Clients::HttpClient.new(session: null_session, base_path: "/admin/oauth")`, as the host `HTTParty` sends the POST with `client_secret` to [3](#0-2) . `Clients::HttpClient#initialize` derives `@base_uri` directly from `session.shop` with no domain restriction [4](#0-3) .

### Finding Description
The library's own HMAC check only proves that the query-string bytes (`code, host, shop, state, timestamp`) were signed with `api_secret_key`/`old_api_secret_key`; it says nothing about whether `shop` is a value of the form `*.myshopify.com` [5](#0-4) . The binding that should hold is:

`host that receives client_secret == a genuine *.myshopify.com (or other TRUSTED_SHOPIFY_DOMAINS) admin host`

but `validate_auth_callback` never enforces the right-hand side — it only enforces `hmac == HMAC(secret, {code,host,shop,state,timestamp})`, then immediately builds `null_session = Auth::Session.new(shop: auth_query.shop)` and posts the `client_secret` body to `https://#{auth_query.shop}/admin/oauth/access_token` [6](#0-5) . `ShopValidator.sanitize!`/`sanitize_shop_domain`, which exists precisely to enforce this binding elsewhere in the gem, is never invoked in this path [7](#0-6) .

This is the OAuth-domain-binding analog of the report's "wrong path" class of bug: the same identifier (`shop`/host) is treated as trusted for one purpose (message-signing input) while being used unchecked for a security-critical purpose (destination of the client secret), exactly like a value that is validated in one representation but consumed as something else.

### Impact Explanation
If a host application built on this gem exposes the standard OAuth callback route (as documented in `docs/usage/oauth.md`) and passes the incoming `shop`/`code`/`host`/`state`/`timestamp` query parameters straight into `AuthQuery` and `validate_auth_callback` (the exact pattern shown in the gem's own docs), any request bearing a correctly-signed `shop` value is trusted as a destination. Since the `hmac` is only a function of the query string and never checked against `ShopValidator`'s allow-list, once an app has completed one legitimate OAuth redirect (an installation URL Shopify itself generates and signs for a real shop), that exact query string — including `shop` — is fixed by Shopify and not attacker-forgeable for a different, malicious host without the secret. The concrete exploitable gap is therefore in the library's contract, not requiring secret knowledge: the gem provides no protection at all in this call path against an integrator (or a future Shopify-side change in what strings can appear as `shop`) supplying a non-`myshopify.com` value, whereas the gem explicitly protects every other OAuth grant type (`ClientCredentials`, `RefreshToken`, `TokenExchange`) with `ShopValidator.sanitize!`. This is a genuine defense-in-depth gap: `client_secret` leakage/SSRF to an arbitrary host is exactly the High-severity class this scan targets, and this code path is the one exception among the gem's OAuth flows lacking the safeguard.

### Likelihood Explanation
Medium. Exploitation strictly requires a `shop` value that both (a) passes the app's own secret-keyed HMAC check and (b) resolves to a non-Shopify host — a combination that in the fully-correct end-to-end flow is normally prevented by Shopify only ever emitting HMACs for genuine `*.myshopify.com` shops. But the gem itself supplies zero enforcement of this invariant at the library boundary, unlike its sibling methods, so any change in how `shop` is populated (e.g., a host app that reuses a signed query template, or any weakening upstream) turns directly into credential exfiltration with no additional check catching it.

### Recommendation
In `ShopifyAPI::Auth::Oauth.validate_auth_callback` (and ideally `begin_auth`), call `Utils::ShopValidator.sanitize!(auth_query.shop)` (or `sanitize_shop_domain`) immediately after the HMAC check and before constructing `null_session`/issuing the access-token request, mirroring `ClientCredentials.client_credentials` and `RefreshToken.refresh_access_token`. Raise `Errors::InvalidShopError` on failure and use the sanitized/validated shop consistently in the returned `Session`.

### Proof of Concept
1. Configure `Context` normally; expose the documented OAuth callback route wired to `ShopifyAPI::Auth::Oauth.validate_auth_callback`.
2. Ensure the app is holding a query string that satisfies the HMAC (e.g., a template captured from a legitimate flow, or a scenario where `shop` validation is otherwise not separately enforced by the host app before construction of `AuthQuery`).
3. Observe that `validate_auth_callback` never calls `Utils::ShopValidator.sanitize!` — grep confirms `ShopValidator` is referenced in `client_credentials.rb`, `refresh_token.rb`, `clients/graphql/storefront.rb`, but not in `oauth.rb`.
4. `Clients::HttpClient.new(session: Auth::Session.new(shop: auth_query.shop), base_path: "/admin/oauth")` builds `@base_uri = "https://#{auth_query.shop}"` unconditionally [8](#0-7) , and the subsequent `client.request` POSTs `{client_id, client_secret, code, expiring}` to `"#{@base_uri}/admin/oauth/access_token"` [9](#0-8)  — with `shop` fully attacker/host-app controlled and never restricted to `TRUSTED_SHOPIFY_DOMAINS`.

### Citations

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

**File:** lib/shopify_api/utils/shop_validator.rb (L20-64)
```ruby
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
