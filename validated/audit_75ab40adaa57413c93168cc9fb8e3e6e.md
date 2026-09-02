Found a concrete SSRF finding: `validate_auth_callback` and `begin_auth` in `lib/shopify_api/auth/oauth.rb` build the OAuth token/authorize endpoint host directly from the attacker-influenced `shop`/`auth_query.shop` value, without ever calling `ShopValidator.sanitize!`, even though that validator exists in the same gem and is used elsewhere.

### Title
SSRF with app's `client_secret` via unsanitized `shop` in OAuth callback host construction - (File: lib/shopify_api/auth/oauth.rb)

### Summary
`ShopifyAPI::Auth::Oauth.validate_auth_callback` builds the URL host used to POST `client_id`/`client_secret`/authorization `code` from `auth_query.shop`, and `begin_auth` builds the authorize redirect host from the caller-supplied `shop`. Neither path runs the value through `ShopifyAPI::Utils::ShopValidator.sanitize!`, which the gem itself defines specifically to constrain shop values to trusted Shopify domains.

### Finding Description
`Utils::HmacValidator.validate(auth_query)` checks that the `shop` field is byte-for-byte what the app's secret signed [1](#0-0) , but that only proves the callback request wasn't tampered with in flight from whatever endpoint sent it — it never restricts `shop` to a real `*.myshopify.com` value. `validate_auth_callback` then passes `auth_query.shop` straight into `Auth::Session.new(shop: ...)` and, via `Clients::HttpClient.new(session: null_session, base_path: "/admin/oauth")`, that shop string becomes the request host receiving `client_id`, `client_secret`, and the authorization `code` [2](#0-1) . Similarly `begin_auth`'s `auth_base_uri(shop)` embeds the raw `shop` parameter into `https://#{shop}/admin` used for the OAuth authorize redirect [3](#0-2) .

The gem already ships `ShopifyAPI::Utils::ShopValidator.sanitize!`, whose explicit purpose is to reject any shop string that doesn't resolve to a trusted Shopify domain (`myshopify.com`, `myshopify.io`, `shopify.com`, `spin.dev`, `shop.dev`) [4](#0-3) , but this validator is never invoked inside `oauth.rb`. This is the binding break described by the report's bug class: the equality actually enforced is "bytes verified by HMAC == bytes parsed as `shop`", not "host contacted with the client secret == a trusted Shopify domain". An attacker who controls the value that ends up as `auth_query.shop`/`shop` (e.g. because the host application forwards a query parameter from the OAuth redirect without independently validating it, since the docs' own callback example builds `AuthQuery` directly from `request.parameters` [5](#0-4) ) can point the token-exchange POST at an attacker-controlled host.

### Impact Explanation
If `shop` is not independently constrained by the host app, this results in SSRF that leaks the app's `client_secret` and the OAuth authorization `code` to an attacker-controlled host — meeting the "High: SSRF with the app's credentials" bar.

### Likelihood Explanation
Exploitability strictly depends on the host application not validating/sanitizing `shop` before constructing `AuthQuery` — the gem's own documented example does exactly this pattern (`request.parameters.symbolize_keys.except(:controller, :action)` fed straight into `AuthQuery.new`) [5](#0-4) , and the gem itself does not call `ShopValidator` in this code path despite owning that utility. This is a real gap in defense-in-depth inside the gem, though its exploitability is amplified by (not solely dependent on) host behavior that the gem's own docs recommend.

### Recommendation
Call `ShopifyAPI::Utils::ShopValidator.sanitize!(shop)` (or `sanitize!(auth_query.shop)`) at the top of `begin_auth` and `validate_auth_callback` in `lib/shopify_api/auth/oauth.rb`, raising `Errors::InvalidShopError` before any host is derived from the value, mirroring how `ShopValidator` is already used elsewhere in the codebase (e.g. `test/utils/shop_validator_test.rb`).

### Proof of Concept
1. Host app's callback controller builds `AuthQuery` directly from request params (as shown in the gem's own docs), setting `shop` to `attacker.evil.com` while `code`/`state`/`timestamp`/`host` are otherwise valid and HMAC is computed by the attacker using knowledge of the URL structure is not needed — the attacker only needs the app to reach the callback with a crafted `shop`; if the app does no additional shop-domain check (as the docs example doesn't), `Utils::HmacValidator.validate` would fail only if `shop` mismatches what was actually signed by Shopify — so the realistic path is when the *initial* `begin_auth(shop: attacker_supplied)` is invoked with attacker input, causing the whole flow, including the final token POST in `validate_auth_callback`, to target `https://attacker.evil.com/admin/oauth/access_token` with `client_id`, `client_secret`, and `code` in the body [6](#0-5) .
2. `client_secret` and the authorization `code` are exfiltrated to the attacker's server.

**Uncertainty note:** I could not find, within the in-scope files searched, any call site where `begin_auth`/`validate_auth_callback` receives `shop` from a request without prior sanitization inside this gem itself — that responsibility is left to the host app in every documented flow. This weakens the case that this is a *gem-level* auth-bypass rather than a missing best-practice safeguard, and it is reasonable to conclude this may not clear the bar of "no host application ignoring the gem's documented API" exclusion, since the docs never claim the gem sanitizes `shop`. I flag this as the weakest link in the analog and would recommend validating with a background Devin session against the full call graph (including `shopify_app` integration patterns) before treating this as confirmed exploitable purely within this gem's boundary.

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

**File:** lib/shopify_api/utils/shop_validator.rb (L6-18)
```ruby
module ShopifyAPI
  module Utils
    module ShopValidator
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

**File:** docs/usage/oauth.md (L242-251)
```markdown
def callback
  begin
    # Create an AuthQuery object from the request parameters,
    # and pass the list of cookies to `validate_auth_callback`
    auth_result = ShopifyAPI::Auth::Oauth.validate_auth_callback(
      cookies: cookies.to_h,
      auth_query: ShopifyAPI::Auth::Oauth::AuthQuery.new(
        request.parameters.symbolize_keys.except(:controller, :action)
      )
    )
```
