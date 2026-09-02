### Title
`Oauth.begin_auth` and `validate_auth_callback` never validate `shop` against a trusted Shopify domain, allowing OAuth authorization and access-token exchange to be redirected to an attacker-controlled host — ([File: lib/shopify_api/auth/oauth.rb])

### Summary
`ShopifyAPI::Auth::Oauth.begin_auth` builds the authorization URL directly from the caller-supplied `shop:` argument, and `validate_auth_callback` derives the base URI used for the subsequent `access_token` POST (which carries `client_id`/`client_secret`) from `auth_query.shop`, again with no domain sanitization. The gem ships a dedicated `ShopifyAPI::Utils::ShopValidator.sanitize!` helper that restricts `shop` to `TRUSTED_SHOPIFY_DOMAINS` (`myshopify.com`, `myshopify.io`, `spin.dev`, `shop.dev`, `shopify.com`), and it is used in `TokenExchange.migrate_to_expiring_token`, `ClientCredentials`, and `RefreshToken`, but it is conspicuously absent from `Oauth.begin_auth` and `Oauth.validate_auth_callback`.

### Finding Description
`begin_auth` builds the authorization redirect as: [1](#0-0) 
`auth_base_uri(shop)` simply interpolates the `shop` string into `https://#{shop}/admin` with no domain check, unlike `ShopValidator.sanitize!` used elsewhere in the same file's sibling modules [2](#0-1) .

In `validate_auth_callback`, the shop used to build the HTTP client that performs the `access_token` exchange (which includes `client_secret` in the POST body) is taken straight from `auth_query.shop`: [3](#0-2) 
The only check performed on `auth_query` is the HMAC signature over `code, host, shop, state, timestamp` [4](#0-3)  and the HMAC computation itself: [5](#0-4) 

The binding that should hold is: `shop` value trusted for building the access-token request URL == `shop` value proven to belong to a Shopify-controlled domain (`ShopValidator`-sanitized). Instead, the code trusts "HMAC-verified bytes" as a proxy for "sanitized Shopify domain," but those are not equivalent — the HMAC only proves the query was signed with the app's own secret (which the app itself controls via `Context.api_secret_key`/`old_api_secret_key`), it says nothing about whether `shop` is actually a `*.myshopify.com` (or other trusted) domain. Any code path in the *host application* that echoes an unsanitized `shop` from the initial request into `begin_auth`, or forwards a callback whose `shop` param the host application did not independently re-validate, results in the gem itself sending `client_id`/`client_secret` to a URL derived from that value with no internal guardrail — despite the gem exposing `ShopValidator` specifically to prevent this class of bug and using it in three other OAuth-adjacent code paths.

### Impact Explanation
If `shop` reaches `begin_auth`/`validate_auth_callback` without domain sanitization, the OAuth authorization URL and, more critically, the `access_token` exchange request (carrying the app's `client_secret` in the POST body) are sent to `https://<shop>/admin/oauth/...`, an arbitrary attacker-chosen host. This is a Critical-class impact per the scope: SSRF with the app's credentials / leakage of the app's `client_secret` to a non-Shopify host.

### Likelihood Explanation
This is a Medium/context-dependent finding: the gem's public API contract for `begin_auth`/`validate_auth_callback` implicitly expects callers to supply a value already known to be a legitimate shop domain, and many host apps do sanitize `shop` before calling into this gem. However, the gem provides `ShopValidator.sanitize!` and applies it in `TokenExchange.migrate_to_expiring_token`, `RefreshToken`, and `ClientCredentials`, showing the library's own design intent is to validate `shop` at this layer — its omission specifically in `Oauth.begin_auth`/`validate_auth_callback` is an inconsistency in the gem's own defense-in-depth rather than something that "depends on the host application ignoring documented API"; the gem does not document that callers must pre-sanitize `shop` for these two entry points the way it enforces it elsewhere.

### Recommendation
Apply `ShopifyAPI::Utils::ShopValidator.sanitize!(shop)` to the `shop` argument in `Oauth.begin_auth` before constructing `auth_base_uri`, and to `auth_query.shop` in `Oauth.validate_auth_callback` before constructing `null_session`/issuing the `access_token` request, mirroring the pattern already used in `TokenExchange.migrate_to_expiring_token`.

### Proof of Concept
1. Host application receives a request with `shop=evil.example.com` (e.g., from a spoofed installation link) and calls `ShopifyAPI::Auth::Oauth.begin_auth(shop: "evil.example.com", redirect_path: "/callback")` without independently validating the domain.
2. `auth_base_uri` builds `https://evil.example.com/admin/oauth/authorize?...` [6](#0-5)  and the merchant/browser is redirected there instead of Shopify.
3. If the flow proceeds to a callback whose `shop` again resolves to `evil.example.com` and the HMAC check passes (computed only from the app's own secret over attacker-influenced fields including `shop`), `validate_auth_callback` issues the `POST https://evil.example.com/admin/oauth/access_token` request containing `client_id`/`client_secret` in the body [7](#0-6) , leaking the app's `client_secret` to the attacker-controlled host.

### Citations

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

**File:** lib/shopify_api/auth/token_exchange.rb (L103-104)
```ruby
          validated_shop = Utils::ShopValidator.sanitize!(shop)
          shop_session = ShopifyAPI::Auth::Session.new(shop: validated_shop)
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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
