### Title
`validate_auth_callback` trusts a validly-signed but non-myshopify `shop` value with no `ShopValidator.sanitize!` call - ([File: lib/shopify_api/auth/oauth.rb])

### Summary
`AuthQuery#to_signable_string` includes `shop` in the HMAC-signed payload [1](#0-0) , and `HmacValidator.validate` correctly rejects any query where `shop` (or any signed field) is mutated after signing, since it re-derives the signature from `to_signable_string` and compares with `OpenSSL.secure_compare` [2](#0-1) . So signature-coverage of `shop` holds structurally: an attacker cannot tamper with `shop` post-signature and still pass `HmacValidator.validate`. However, `Auth::Oauth.validate_auth_callback` never calls `Utils::ShopValidator.sanitize!` on `auth_query.shop` before using it to build `Auth::Session.new(shop: auth_query.shop)` and later `Session.from(shop: auth_query.shop, ...)` [3](#0-2) .

### Finding Description
The binding under test is: `HMAC-covers(shop) == shop-trusted-downstream`. The first half is true — `shop` is part of the signed string in `AuthQuery#to_signable_string` [4](#0-3) , so any post-signing mutation of `shop` breaks the HMAC and `HmacValidator.validate` returns `false`. This means the attacker cannot forge a callback for an arbitrary victim shop by tampering with a signed request meant for their own dev shop — that specific attack fails.

The real problem, as the question anticipates, is a *different* invariant: "a validly-signed `shop` value is a genuine `*.myshopify.com` domain." Shopify's own OAuth flow signs whatever `shop` value was present in the authorize redirect. `Auth::Oauth.begin_auth` builds the authorize URL using the raw, unsanitized `shop` argument supplied by the calling app (`auth_base_uri(shop)`, `https://#{shop}/admin/oauth/authorize?...`) [5](#0-4) , and nothing in this gem forces the host app to have validated `shop` with `ShopValidator.sanitize!` before calling `begin_auth`. `validate_auth_callback` then only checks: `HmacValidator.validate(auth_query)` (signature integrity, not domain shape), `Context.private?`, and CSRF `state` equality [6](#0-5) . It never calls `Utils::ShopValidator.sanitize!(auth_query.shop)`. The gem does define `ShopValidator.sanitize!` for exactly this purpose [7](#0-6) , but `validate_auth_callback` doesn't invoke it, so `auth_query.shop` — whatever string was echoed back by the signing party — is used directly to construct `Auth::Session.new(shop: auth_query.shop)` and the final `Session` returned to the host app, becoming the session key and (in typical host-app usage) the admin/API host for all subsequent requests.

Attack surface: this requires the app itself to accept an attacker-controlled `shop` param into `begin_auth` without pre-validating it (a common integration pattern, since the gem exposes `sanitize!` as an opt-in utility rather than enforcing it internally in `begin_auth`/`validate_auth_callback`). If the host app does that, the attacker can drive `begin_auth` with `shop=notashop` or `shop=169.254.169.254`, Shopify (or a shim in dev mode) or the app's own OAuth authorize endpoint completes the round trip, and the resulting signed callback is accepted by `validate_auth_callback` with no myshopify-format check.

### Impact Explanation
If exploitable in a given host app, the effect is that a non-myshopify `shop` string becomes a trusted session key / admin host, which can enable session collisions across tenants or requests being directed at attacker-chosen hosts (SSRF-adjacent) downstream, e.g. if the app uses `session.shop` to build API base URIs without its own re-validation. This matches the reported gap: not "Critical - authentication bypass via forged HMAC" (that path is blocked, confirmed above), but a missing input-validation control (`ShopValidator.sanitize!`) that this gem itself provides but never calls automatically in the OAuth callback path.

### Likelihood Explanation
This is contingent on the host application's own handling of the `shop` parameter before calling `begin_auth` — if the app already validates/normalizes `shop` (as Shopify's own documentation for this gem recommends, and as `ShopValidator.sanitize!` is designed for), the gap is not reachable. The gem does not enforce this invariant internally, and `validate_auth_callback` provides no defense-in-depth check on `auth_query.shop`'s format.

### Recommendation
Call `Utils::ShopValidator.sanitize!(auth_query.shop)` (or equivalent format validation) inside `Auth::Oauth.validate_auth_callback` before constructing `Auth::Session`/`Session.from`, and likewise validate/sanitize `shop` at the top of `begin_auth`, so that only genuine `*.myshopify.com` (or otherwise trusted) domains are ever accepted regardless of what the calling app passes in.

### Proof of Concept
Not provided — per the rules, this finding does not meet the required bar for a demonstrable, in-gem exploit: `HmacValidator.validate` correctly blocks the signature-tampering scenario, and the missing `sanitize!` call in `validate_auth_callback` is a missing-defense-in-depth issue whose actual exploitability depends entirely on the host application's own (out-of-scope) handling of the `shop` parameter before calling `begin_auth`, not on any bypass of this gem's own guarantees.

### Citations

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
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
