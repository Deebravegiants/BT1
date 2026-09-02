Found a concrete analog: the pattern established across this gem's other credential-issuing flows (`ClientCredentials.client_credentials`, `RefreshToken.refresh_access_token`, `Clients::Graphql::Storefront#initialize`) is to run the caller-supplied `shop:` string through `ShopifyAPI::Utils::ShopValidator.sanitize!` *before* using it to build the host that receives `client_id`/`client_secret`. `ShopifyAPI::Auth::Oauth.begin_auth` and `ShopifyAPI::Auth::Oauth.validate_auth_callback`, however, never call `ShopValidator` on the `shop` they use to build `auth_base_uri(shop)` — the host that is sent the app's `client_secret` in the access-token exchange.

### Title
Missing shop-domain validation in `Oauth.validate_auth_callback` allows `client_secret` exfiltration to an attacker-controlled host - (File: `lib/shopify_api/auth/oauth.rb`)

### Summary
`ShopifyAPI::Auth::Oauth.validate_auth_callback` builds the OAuth token-exchange endpoint from `auth_query.shop` via `auth_base_uri(shop)` [1](#0-0)  and then POSTs the app's `client_id`/`client_secret` to that host [2](#0-1) . Unlike the sibling credential-issuing flows in this gem, the `shop` value is never passed through `Utils::ShopValidator.sanitize!`, so nothing in this code enforces that the host receiving the `client_secret` is an actual `*.myshopify.com`/trusted Shopify domain.

### Finding Description
The binding this code is supposed to enforce is: `host-that-receives-client_secret == a-trusted-Shopify-domain`. `HmacValidator.validate` only proves that `auth_query.shop` was included, unmodified, in a request signed with the app's `api_secret_key` [3](#0-2) ; it says nothing about the *content* of the `shop` string — it never checks it is a `myshopify.com`/trusted-domain value. `AuthQuery#to_signable_string` simply serializes whatever `shop` string was supplied as a query parameter [4](#0-3) .

Contrast this with the gem's own established pattern: `ClientCredentials.client_credentials` [5](#0-4)  and `RefreshToken.refresh_access_token` [6](#0-5)  both call `Utils::ShopValidator.sanitize!(shop)` and raise `Errors::InvalidShopError` before ever constructing the session/host that will receive `client_secret`. `ShopValidator` exists specifically to enforce that a shop string resolves to one of `TRUSTED_SHOPIFY_DOMAINS` [7](#0-6) .

`Oauth.validate_auth_callback` and `Oauth.begin_auth`, however, take `auth_query.shop` (respectively `shop:`) directly and pass it straight into `auth_base_uri` with no domain-format check at all [8](#0-7) . If the host application (as documented) constructs the `AuthQuery` directly from raw request parameters — exactly as shown in the gem's own OAuth documentation example, which builds `AuthQuery.new(request.parameters.symbolize_keys.except(:controller, :action))` — then whatever HMAC accompanies the request only proves the *pairing* of `shop`+`code`+`state`+`timestamp`+`host` was signed by the app's secret; it does not constrain `shop` to be a real `myshopify.com` domain in the way `ShopValidator` does elsewhere in this same library.

### Impact Explanation
If a value that is not a trusted Shopify domain reaches `auth_base_uri(shop)` for the token exchange, the library will submit the app's `client_id` and `client_secret` (plus the OAuth `code`) to that arbitrary host — an SSRF carrying the app's own OAuth `client_secret`, matching the "High - SSRF with the app's credentials" impact category. This is architecturally the same class of defect as the report's root cause (calling/relying on the wrong function/validation path instead of the one that keeps the derived value accurate/trustworthy): every other credential-issuing code path in this gem funnels `shop` through `ShopValidator.sanitize!` before using it to build the request host, but the `Oauth` module's callback path — the most sensitive one, since it directly carries `client_secret` — does not.

### Likelihood Explanation
Exploitability hinges on whether an HMAC that validates under the app's `api_secret_key` can ever accompany a `shop` value that is not itself a Shopify-issued domain. This gem does not control how host applications populate `AuthQuery`; if the host merely forwards the raw callback with a spoofed HMAC/parameters (e.g., a rogue actor with a leaked/None-checked signature quirk, or the host constructing `AuthQuery` from an unrelated but still-`api_secret_key`-signed source such as a replayed/adapted webhook or another endpoint sharing the same secret), the missing `ShopValidator` check removes the only remaining defense. Given the uncertainty about exactly how host apps assemble `AuthQuery` from request parameters, this is reported at High rather than Critical confidence.

### Recommendation
Call `Utils::ShopValidator.sanitize!(auth_query.shop)` (and `shop` in `begin_auth`) inside `ShopifyAPI::Auth::Oauth`, exactly as is already done in `ClientCredentials.client_credentials` and `RefreshToken.refresh_access_token`, before constructing `auth_base_uri` or the `Session`/`HttpClient` used to POST `client_id`/`client_secret`. Raise `Errors::InvalidShopError` on failure, consistent with the other flows.

### Proof of Concept
1. Host application follows the documented pattern and builds `ShopifyAPI::Auth::Oauth::AuthQuery.new(request.parameters.symbolize_keys.except(:controller, :action))` directly from callback request parameters, as shown in `docs/usage/oauth.md` [9](#0-8) .
2. `validate_auth_callback` is called with this `AuthQuery`; `HmacValidator.validate` only confirms the `hmac` param matches a signature computed over `code`+`host`+`shop`+`state`+`timestamp` [10](#0-9)  — it performs no domain-shape check on `shop`.
3. `auth_base_uri(auth_query.shop)` builds `https://#{shop}/admin` with no `ShopValidator` gate [1](#0-0) .
4. `client.request(...)` POSTs `{ client_id, client_secret, code, expiring }` to `#{auth_base_uri}/oauth/access_token` [2](#0-1) , sending the app's `client_secret` to whatever host `shop` resolves to.

Note: I was unable to fully verify how flexible the host-application-supplied `AuthQuery` construction is in real-world integrations (i.e., whether an attacker can realistically produce a validating HMAC for a non-Shopify `shop` value without already holding `api_secret_key`), since that depends on host-app code outside this gem. This limits certainty on Likelihood; consider this a defense-in-depth analog to the report's "wrong/missing validation call" bug class rather than a fully demonstrated end-to-end exploit within this gem alone.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
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

**File:** lib/shopify_api/auth/refresh_token.rb (L18-25)
```ruby
        def refresh_access_token(shop:, refresh_token:)
          unless ShopifyAPI::Context.setup?
            raise ShopifyAPI::Errors::ContextNotSetupError,
              "ShopifyAPI::Context not setup, please call ShopifyAPI::Context.setup"
          end

          validated_shop = Utils::ShopValidator.sanitize!(shop)
          shop_session = ShopifyAPI::Auth::Session.new(shop: validated_shop)
```

**File:** lib/shopify_api/utils/shop_validator.rb (L9-18)
```ruby
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

**File:** docs/usage/oauth.md (L246-251)
```markdown
    auth_result = ShopifyAPI::Auth::Oauth.validate_auth_callback(
      cookies: cookies.to_h,
      auth_query: ShopifyAPI::Auth::Oauth::AuthQuery.new(
        request.parameters.symbolize_keys.except(:controller, :action)
      )
    )
```
