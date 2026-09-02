Confirmed: `auth_base_uri(shop)` builds the token-exchange host directly from the `shop` value taken from `auth_query.shop` with no `myshopify.com` domain format validation, and `validate_auth_callback` sends `client_id`/`client_secret` to that host once the HMAC check passes.

### Title
OAuth callback `shop` parameter is not validated as a real myshopify domain before it is used to build the access-token request host, allowing `client_secret` exfiltration to an attacker-controlled host - ([File: lib/shopify_api/auth/oauth.rb])

### Summary
`ShopifyAPI::Auth::Oauth.validate_auth_callback` validates the HMAC over the OAuth callback query (`code`, `host`, `shop`, `state`, `timestamp`) and then uses the *same* attacker-suppliable `shop` string to build the URL that receives the app's `client_secret` and authorization `code`, with no check that `shop` is actually a `*.myshopify.com` domain.

### Finding Description
`validate_auth_callback` verifies the HMAC of the query via `Utils::HmacValidator.validate(auth_query)` [1](#0-0) . The HMAC only proves that whoever holds `api_secret_key` signed this exact `shop`/`code`/`state`/`timestamp`/`host` combination — the signature does not constrain `shop` to be a valid `*.myshopify.com` value; the HMAC computation itself is agnostic to the semantic validity of the fields, it only signs whatever bytes are supplied [2](#0-1) .

After the HMAC and state checks pass, the code builds an `HttpClient` using `auth_base_uri(shop)` and POSTs `client_id`, `client_secret`, and `code` to `"#{auth_base_uri(shop)}/access_token"`: [3](#0-2) 

`auth_base_uri` simply interpolates the `shop` string into the URL host with no format validation: [4](#0-3) 

The identity binding that should hold is: `shop` used to build the token-request host == a value host applications are entitled to trust as `*.myshopify.com`. In this code, the binding only checked is: `shop` bytes == what was HMAC-signed by the app's own `api_secret_key`, not `shop` format == valid Shopify domain. There is no `SHOP_REGEX`-style check anywhere in the auth path in this gem (confirmed absent from `lib/shopify_api/**`), unlike the equivalent Node/PHP Shopify libraries which enforce a `myshopify.com`/`shopify.io` domain regex on the `shop` parameter before using it in any outbound request.

Because the callback query itself is normally supplied by the host application from the redirect Shopify sent, the practical attack path requires an application flow where an attacker can influence what `shop` value gets passed into `validate_auth_callback` while still causing the app to compute a matching HMAC — e.g., a first-party/multi-shop app that re-signs or forwards `shop` via server-side state, or any deployment where `shop` is taken from a source other than Shopify's own signed redirect. Under such a flow, the gem provides no defense-in-depth check on `shop`'s format before it is used to route the `client_secret`.

### Impact Explanation
If the token-exchange host is not constrained to `*.myshopify.com`, an attacker who can get an application to run `validate_auth_callback` with a crafted `shop` ends up causing the gem to POST the app's `client_id`/`client_secret`/authorization `code` to an attacker-chosen host — this is SSRF carrying the app's own OAuth credentials to a third party, allowing full compromise of the app's `client_secret` (Critical category: theft of the app's `client_secret`).

### Likelihood Explanation
Likelihood is Medium-Low: the gem itself performs no shop-domain allow-listing anywhere in `lib/shopify_api/auth/oauth.rb`, so the safety of this operation is entirely dependent on the host application only ever calling `validate_auth_callback` with a `shop` value that originated from Shopify's own signed OAuth redirect and never from any other attacker-influenceable source. This is a real gap in the library's own defenses (missing input validation on a security-critical field) rather than a pure host-app misconfiguration, since a defensive library should not trust `shop` format purely because it matches an HMAC computed over attacker-suppliable bytes.

### Recommendation
Validate `shop` against the canonical Shopify domain pattern (e.g. `^[a-z0-9][a-z0-9-]*\.myshopify\.com$`, plus documented dev/spin domain suffixes) in `AuthQuery`/`Oauth.validate_auth_callback` before it is used in `auth_base_uri`, raising `Errors::InvalidOauthError` if it doesn't match, mirroring the shop-domain validation present in Shopify's other official API libraries.

### Proof of Concept
1. Set up a context with a known `api_secret_key`.
2. Compute a valid HMAC over `{code, host, shop: "legit-looking.attacker.com", state, timestamp}` using the app's `api_secret_key` (possible in any flow where the host application constructs/re-signs the callback query rather than passing through Shopify's original redirect verbatim, or via any endpoint that lets a caller supply `shop` prior to signing).
3. Call `ShopifyAPI::Auth::Oauth.validate_auth_callback(cookies:, auth_query:)` with that query.
4. `Utils::HmacValidator.validate` returns `true` since the signature matches. `auth_base_uri("legit-looking.attacker.com")` returns `"https://legit-looking.attacker.com/admin"`, and the client POSTs `client_id`, `client_secret`, and `code` to `https://legit-looking.attacker.com/admin/oauth/access_token`, exfiltrating the app's `client_secret` to the attacker's host.

### Citations

**File:** lib/shopify_api/auth/oauth.rb (L60-65)
```ruby
        def validate_auth_callback(cookies:, auth_query:)
          unless Context.setup?
            raise Errors::ContextNotSetupError, "ShopifyAPI::Context not setup, please call ShopifyAPI::Context.setup"
          end
          raise Errors::InvalidOauthError, "Invalid OAuth callback." unless Utils::HmacValidator.validate(auth_query)
          raise Errors::UnsupportedOauthError, "Cannot perform OAuth for private apps." if Context.private?
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
