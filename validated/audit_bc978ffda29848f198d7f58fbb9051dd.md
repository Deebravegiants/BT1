## Title
OAuth callback sends the app's `client_secret` to an unvalidated `shop` host - ([File: lib/shopify_api/auth/oauth.rb])

### Summary
`ShopifyAPI::Auth::Oauth.validate_auth_callback` builds the access-token-exchange request using `auth_query.shop` directly, without ever passing it through `Utils::ShopValidator.sanitize!`, unlike every other credential-issuing flow in this gem (`ClientCredentials.client_credentials` and `TokenExchange.exchange_token` both explicitly call `ShopValidator.sanitize!`/derive the shop from a verified JWT `dest` claim before using it as a request host).

### Finding Description
The binding that should hold is: *the host that receives `Context.api_secret_key` == a validated `*.myshopify.com`/trusted Shopify domain*. In `validate_auth_callback`: [1](#0-0) 

the code only checks `Utils::HmacValidator.validate(auth_query)` and the `state` cookie match — it never calls `Utils::ShopValidator.sanitize!(auth_query.shop)`. The unvalidated `auth_query.shop` is used to build `null_session = Auth::Session.new(shop: auth_query.shop)`, which is fed into `Clients::HttpClient.new(session: null_session, base_path: "/admin/oauth")`. Inside `HttpClient#initialize`: [2](#0-1) 

the request base URI is derived directly from `session.shop` (`"https://#{api_host || session.shop}"`), and the subsequent POST body sent to that host contains `client_id`, `code`, and **`client_secret: Context.api_secret_key`**: [3](#0-2) 

By contrast, `ClientCredentials.client_credentials` sanitizes the shop before it's ever used as a request host: [4](#0-3) 

and `TokenExchange.exchange_token` derives the shop from the `dest` claim of a cryptographically-verified JWT (`JwtPayload.new(session_token)`), not from raw untrusted query input: [5](#0-4) 

`validate_auth_callback` is the only one of these three token-issuing flows that skips `ShopValidator` entirely, even though `AuthQuery.shop` is populated straight from the callback query string by the host application (typically `params[:shop]` in the app's Rack/Rails controller) before being passed into this method — the HMAC only proves that the whole (`code, host, shop, state, timestamp`) tuple was signed with the app's own secret; it does **not** itself constrain `shop` to be a `myshopify.com`/trusted domain, that constraint has to be enforced separately, and CHANGELOG 4.0.2 documents that this project previously added exactly this check ("Verify that the shop domain is a subdomain of .myshopify.com which creating the session") for this reason: [6](#0-5) 

### Impact Explanation
If it can be triggered, this breaks the "host receiving `client_secret` must be a trusted Shopify domain" invariant and results in exfiltration of the app's `client_secret` to an attacker-controlled host — a Critical-class impact per the given rubric (theft of the app's `client_secret`) and/or SSRF carrying the app's credentials (High). This directly mirrors the report's requested analog: "a host validated versus the host that receives the access token or `client_secret`."

### Likelihood Explanation
This is Low-to-uncertain likelihood/exploitability, and I cannot fully confirm it is exploitable purely from this gem's own code:
- `AuthQuery.to_signable_string` includes `shop` inside the HMAC-signed payload, and `HmacValidator.validate` verifies that signature with `Context.api_secret_key` (or `old_api_secret_key`). Legitimate callback query strings with a valid HMAC are produced by Shopify's own OAuth service, which itself constrains `shop` to a real store domain — an external attacker who does not know `api_secret_key` cannot independently mint a `(shop, hmac)` pair with an attacker-chosen `shop`.
- I could not find, within `lib/shopify_api/**`, any code path that lets an unprivileged internet user supply an arbitrary `shop` value alongside a valid HMAC without already possessing the secret.
- The realistic risk is that this gem provides no defense-in-depth here (unlike its sibling methods), so it depends entirely on the *host application* correctly trusting only genuine Shopify-signed redirects and not, e.g., allowing HMAC bypass or reusing stale/leaked signed callback tuples across shop domains. That dependency on host-app behavior pushes this toward the excluded "depends on host app ignoring documented API" category, though the missing internal validation is a genuine inconsistency versus this gem's own `ClientCredentials`/`TokenExchange` implementations.

### Recommendation
Add `Utils::ShopValidator.sanitize!(auth_query.shop)` (or equivalent trusted-domain check) inside `validate_auth_callback` before constructing `null_session`/`Session.from`, mirroring `ClientCredentials.client_credentials`, so that `client_secret` can never be sent to a host that fails the trusted-domain check, independent of what the HMAC alone guarantees.

### Proof of Concept
Not independently reproducible with unprivileged-internet-user access alone using only this gem's code: exploitation requires either (a) a way to obtain a validly-HMAC-signed callback tuple whose `shop` is not a genuine Shopify store domain, or (b) a host-application bug that skips/misuses `HmacValidator.validate`. Neither path was found within `lib/shopify_api/**` in this scan; this is reported as an internal validation-boundary inconsistency (missing `ShopValidator.sanitize!` call analogous to the pattern present in `ClientCredentials`/`TokenExchange`) rather than a confirmed end-to-end exploit.

### Citations

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

**File:** lib/shopify_api/clients/http_client.rb (L11-19)
```ruby
      sig { params(base_path: String, session: T.nilable(Auth::Session)).void }
      def initialize(base_path:, session: nil)
        session ||= Context.active_session
        raise Errors::NoActiveSessionError, "No passed or active session" unless session

        api_host = Context.api_host

        @base_uri = T.let("https://#{api_host || session.shop}", String)
        @base_uri_and_path = T.let("#{@base_uri}#{base_path}", String)
```

**File:** lib/shopify_api/auth/client_credentials.rb (L19-33)
```ruby
        def client_credentials(shop:)
          unless ShopifyAPI::Context.setup?
            raise ShopifyAPI::Errors::ContextNotSetupError,
              "ShopifyAPI::Context not setup, please call ShopifyAPI::Context.setup"
          end

          validated_shop = Utils::ShopValidator.sanitize!(shop)
          shop_session = ShopifyAPI::Auth::Session.new(shop: validated_shop)
          body = {
            client_id: ShopifyAPI::Context.api_key,
            client_secret: ShopifyAPI::Context.api_secret_key,
            grant_type: CLIENT_CREDENTIALS_GRANT_TYPE,
          }

          client = Clients::HttpClient.new(session: shop_session, base_path: "/admin/oauth")
```

**File:** lib/shopify_api/auth/token_exchange.rb (L39-51)
```ruby
          # Validate the session token and use the shop from the token's `dest` claim
          jwt_payload = ShopifyAPI::Auth::JwtPayload.new(session_token)
          dest_shop = jwt_payload.shop

          if shop
            ShopifyAPI::Logger.deprecated(
              "The `shop` parameter for `exchange_token` is deprecated and will be removed in v17. " \
                "The shop is now always taken from the session token's `dest` claim.",
              "17.0.0",
            )
          end

          shop_session = ShopifyAPI::Auth::Session.new(shop: dest_shop)
```

**File:** CHANGELOG.md (L559-562)
```markdown
## Version 4.0.2

- Verify that the shop domain is a subdomain of .myshopify.com which creating the session

```
