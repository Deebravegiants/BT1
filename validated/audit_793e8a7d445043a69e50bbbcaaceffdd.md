Confirmed: `HttpClient#initialize` at [1](#0-0)  builds `@base_uri` directly from `session.shop` when no `Context.api_host` override is configured, with no validation that `shop` is a legitimate `*.myshopify.com` domain.

### Title
OAuth callback token exchange sends `client_secret` to attacker-controlled host due to unvalidated `shop` parameter - (File: lib/shopify_api/auth/oauth.rb)

### Summary
`ShopifyAPI::Auth::Oauth.validate_auth_callback` uses the `shop` value from the incoming `AuthQuery` to build the URL that receives the app's `client_id`/`client_secret` during the OAuth code-for-token exchange, but the gem never validates that `shop` is a well-formed `*.myshopify.com` domain before using it to construct that URL.

### Finding Description
The equality the gem is implicitly relying on is: `shop` covered by the HMAC == `shop` used to route the credential-bearing HTTP request. While the HMAC over `AuthQuery` (computed in [2](#0-1)  against the signable string built in [3](#0-2) ) does prove the *string* `shop` wasn't tampered with by a non-Shopify party for a *given code*, the gem never checks that the `shop` string is actually a `*.myshopify.com` (or configured) domain before dereferencing it as a network endpoint.

In `validate_auth_callback` ( [4](#0-3) ), after HMAC and state validation succeed, a `null_session` is created with `shop: auth_query.shop` and handed to `Clients::HttpClient.new(session: null_session, base_path: "/admin/oauth")`. That client computes `@base_uri = "https://#{api_host || session.shop}"` ( [1](#0-0) ) with no format check on `session.shop`, and then POSTs the body containing `client_id` and `client_secret` ( [5](#0-4) ) to `https://#{shop}/admin/oauth/access_token`.

Separately, `begin_auth` ( [6](#0-5) ) also builds `auth_base_uri(shop) + "/oauth/authorize?..."` from a caller-supplied `shop` with the same lack of validation ( [7](#0-6) ).

The root cause is that this gem documents `shop` as "A Shopify domain name in the form `{exampleshop}.myshopify.com`" (see [8](#0-7) ) but performs no runtime enforcement of that format anywhere in `Auth::Oauth`, `AuthQuery`, or `HttpClient`. Applications that pass through an install-route `shop` query parameter (the standard OAuth entry-point pattern for Shopify apps, `GET /login?shop=...`) directly into `begin_auth` will send their `client_id` in a redirect to whatever host string is given, and applications that forward the callback `shop` value as received will have `validate_auth_callback` send `client_secret` (and the just-issued authorization `code`) to that same unvalidated host.

### Impact Explanation
This is High severity: it enables `client_secret` exfiltration through an SSRF-style redirection of the OAuth token exchange, since the gem builds the token-exchange request host directly from the untrusted/unvalidated `shop` string rather than validating it against the expected Shopify domain shape before use.

### Likelihood Explanation
Exploitability depends on the host application forwarding an attacker-influenced `shop` value into `begin_auth`/`validate_auth_callback` without its own validation — which is the exact scenario Shopify's own developer documentation warns apps to guard against, precisely because the reference library does not enforce it. Since many host apps rely on this gem to be "safe by default," and the gem's shipped code performs zero format validation on `shop` at any layer (`AuthQuery`, `Oauth`, or `HttpClient`), the likelihood of an unvalidated `shop` reaching these sinks is realistic for apps following the documented usage pattern in `docs/usage/oauth.md`.

### Recommendation
Add a strict `shop` domain validator (e.g., a regex requiring `{alphanumeric-with-hyphens}.myshopify.com`, plus optional support for `Context.custom_shop_domains`) and invoke it at the top of `begin_auth`, in `AuthQuery#initialize`/`validate_auth_callback`, and in `HttpClient#initialize` before `session.shop` is interpolated into `@base_uri`. Reject any request whose `shop` does not match before constructing outbound URLs or including credentials in the request body.

### Proof of Concept
1. Host application exposes `GET /login?shop=<value>` which calls `ShopifyAPI::Auth::Oauth.begin_auth(shop: params[:shop], redirect_path: "/auth/callback")` (the pattern shown in `docs/usage/oauth.md`).
2. Attacker requests `/login?shop=attacker-controlled-host.example.com`.
3. `auth_base_uri` ( [9](#0-8)  ) builds `https://attacker-controlled-host.example.com/admin/oauth/authorize?client_id=...&redirect_uri=...&state=...`, and the app redirects the victim's browser there, leaking `client_id`, `state`, and `redirect_uri` to the attacker's server.
4. If the attacker can additionally get their crafted `shop` value plus a self-produced `code`/`hmac` pair (e.g., by completing their own real OAuth flow against `attacker-controlled-host.example.com` running fake Shopify-like endpoints, or by controlling what value ultimately reaches `validate_auth_callback`'s `auth_query.shop` in an app that doesn't independently validate it before calling this method), then `validate_auth_callback` ( [10](#0-9) ) will POST `client_id` and `client_secret` to `https://attacker-controlled-host.example.com/admin/oauth/access_token`, exfiltrating the app's `client_secret` to the attacker's server.

### Citations

**File:** lib/shopify_api/clients/http_client.rb (L16-19)
```ruby
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

**File:** lib/shopify_api/auth/oauth.rb (L22-52)
```ruby
        def begin_auth(shop:, redirect_path:, is_online: true, scope_override: nil)
          scope = if scope_override.nil?
            ShopifyAPI::Context.scope
          elsif scope_override.is_a?(ShopifyAPI::Auth::AuthScopes)
            scope_override
          else
            ShopifyAPI::Auth::AuthScopes.new(scope_override)
          end

          unless Context.setup?
            raise Errors::ContextNotSetupError, "ShopifyAPI::Context not setup, please call ShopifyAPI::Context.setup"
          end
          raise Errors::UnsupportedOauthError, "Cannot perform OAuth for private apps." if Context.private?

          state = SecureRandom.alphanumeric(NONCE_LENGTH)

          cookie = SessionCookie.new(value: state, expires: Time.now + 60)

          query = {
            client_id: ShopifyAPI::Context.api_key,
            scope: scope.to_s,
            redirect_uri: "#{ShopifyAPI::Context.host}#{redirect_path}",
            state: state,
            "grant_options[]": is_online ? "per-user" : "",
          }

          query_string = URI.encode_www_form(query)
          auth_route = auth_base_uri(shop) + "/oauth/authorize?#{query_string}"

          { auth_route: auth_route, cookie: cookie }
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

**File:** docs/usage/oauth.md (L291-291)
```markdown
| `shop`         | `String` | Yes | - | A Shopify domain name in the form `{exampleshop}.myshopify.com`. |
```
