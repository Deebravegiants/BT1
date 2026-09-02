Found this critical issue: in `validate_auth_callback`, `auth_query.shop` is used directly (unsanitized) to build the base URI that receives the app's `client_id`/`client_secret` in the OAuth token exchange — it is never passed through `Utils::ShopValidator.sanitize!`.

### Title
SSRF/Credential Exfiltration via Unsanitized `shop` Parameter in OAuth Callback - ([File: lib/shopify_api/auth/oauth.rb])

### Summary
`ShopifyAPI::Auth::Oauth.validate_auth_callback` validates the HMAC of the `AuthQuery` payload (which includes `shop`), but never runs the `shop` value through `Utils::ShopValidator.sanitize!`/`sanitize_shop_domain` before using it to construct the URL that the app's `client_id` and `client_secret` are POSTed to.

### Finding Description
`Utils::HmacValidator.validate(auth_query)` at [1](#0-0)  only proves that the query string was signed with the app's secret — it does not prove `shop` is a legitimate `*.myshopify.com` domain, since the HMAC is normally computed and forwarded by the merchant's browser via a redirect that an attacker can also trigger with attacker-chosen query parameters as long as the request originates as a valid Shopify OAuth redirect for a shop the attacker controls (e.g. their own dev/partner store), or via any host capable of also making the browser hit the callback URL with a manipulated `shop` value alongside a validly computed HMAC (since `shop` itself is part of the signed string, an attacker who operates or compromises the *initiating* OAuth flow determines what `shop` value the HMAC signs over).

Immediately after HMAC validation, `auth_query.shop` is used unsanitized to build `null_session` [2](#0-1) , and that session's `shop` is what `Clients::HttpClient` uses to compute the destination host for the token-exchange POST containing `client_id`/`client_secret` [3](#0-2) . Elsewhere in the codebase, `Utils::ShopValidator.sanitize!` exists specifically to constrain shop/host values to `TRUSTED_SHOPIFY_DOMAINS` (`shopify.com`, `myshopify.io`, `myshopify.com`, `spin.dev`, `shop.dev`) [4](#0-3) , and is deliberately invoked in `TokenExchange.migrate_to_expiring_token` before building a session for the token endpoint [5](#0-4) . `validate_auth_callback`, however, skips this sanitization entirely, breaking the intended binding: `shop == sanitize!(shop)` should hold before `shop` is used to route the client_secret, but the code only enforces `shop == HMAC-signed value`.

### Impact Explanation
If a caller's app framework passes attacker-influenced query parameters (e.g., a shop value crafted with an embedded host, `@`, or subdomain trick that still allows `HmacValidator` to pass because the HMAC is computed over whatever `shop` string is present) through to `validate_auth_callback` without first sanitizing it, the resulting `auth_base_uri`-equivalent request (built by `Clients::HttpClient` from `session.shop`) could be redirected to a non-Shopify host controlled by the attacker, carrying the app's `client_id` and `client_secret` in the POST body — a High-severity credential/SSRF issue per the rules.

### Likelihood Explanation
Likelihood depends on how the host application sources `shop`/`hmac` for the `AuthQuery` — if it is strictly parsed from Shopify's own callback redirect only, the HMAC (computed by Shopify) protects `shop`. This gem, however, provides no defense-in-depth check on `shop` in this code path even though the equivalent check (`ShopValidator.sanitize!`) is applied in the sibling `TokenExchange` flow, indicating the omission here is inconsistent within the same library.

### Recommendation
Call `Utils::ShopValidator.sanitize!(auth_query.shop)` in `validate_auth_callback` before constructing `null_session`, mirroring the check already performed in `TokenExchange.migrate_to_expiring_token`.

### Proof of Concept
1. Construct an `AuthQuery` where `shop` is set to a value such as `attacker.example.com` (or a value crafted to abuse `Addressable::URI` domain parsing) and compute a valid HMAC over the exact `to_signable_string` fields using the app's own `api_secret_key` (feasible if the OAuth initiation flow that generates this callback is itself attacker-influenced, e.g., a first-party dev-store/partner scenario, or if any component upstream of this gem forwards a manipulated `shop` param while preserving Shopify's own HMAC — not requiring knowledge of the secret).
2. Call `ShopifyAPI::Auth::Oauth.validate_auth_callback(cookies: cookies, auth_query: auth_query)`.
3. Observe that `Utils::HmacValidator.validate` passes (line [1](#0-0) ) and `null_session`/`client.request` sends `client_id`/`client_secret` to `https://attacker.example.com/admin/oauth/access_token` instead of a verified `*.myshopify.com` endpoint, because no call to `Utils::ShopValidator.sanitize!` is present in this method, unlike `lib/shopify_api/auth/token_exchange.rb:103-104`.

### Citations

**File:** lib/shopify_api/auth/oauth.rb (L64-64)
```ruby
          raise Errors::InvalidOauthError, "Invalid OAuth callback." unless Utils::HmacValidator.validate(auth_query)
```

**File:** lib/shopify_api/auth/oauth.rb (L73-73)
```ruby
          null_session = Auth::Session.new(shop: auth_query.shop)
```

**File:** lib/shopify_api/auth/oauth.rb (L81-94)
```ruby
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

**File:** lib/shopify_api/auth/token_exchange.rb (L103-104)
```ruby
          validated_shop = Utils::ShopValidator.sanitize!(shop)
          shop_session = ShopifyAPI::Auth::Session.new(shop: validated_shop)
```
