Found a valid analog. `ShopifyAPI::Auth::Oauth.validate_auth_callback` sends the app's `client_secret` (and requests the access token) to a host derived from `auth_query.shop`, but that `shop` value is only checked by equality against the HMAC-signed bytes of the callback query — it is never passed through `ShopifyAPI::Utils::ShopValidator.sanitize!`, unlike the sibling flows `ClientCredentials.client_credentials` and `TokenExchange.exchange_token`, which do call `ShopValidator.sanitize!`/rely on `dest` claim scoping before building the request host.

### Title
OAuth callback sends `client_id`/`client_secret` to an unsanitized `shop` host - (File: lib/shopify_api/auth/oauth.rb)

### Summary
`ShopifyAPI::Auth::Oauth.validate_auth_callback` builds the access-token-exchange request host directly from `auth_query.shop` without routing it through `Utils::ShopValidator.sanitize!`, unlike `ClientCredentials.client_credentials` [1](#0-0)  which explicitly validates the shop against `TRUSTED_SHOPIFY_DOMAINS` before using it to construct the request host and session.

### Finding Description
`validate_auth_callback` verifies the callback query's HMAC (which does cover the `shop` field as part of the signed string) and then immediately uses `auth_query.shop` to build a `null_session` and to derive the request base URI for the `POST /admin/oauth/access_token` call that carries `client_id` and `client_secret` in the body: [2](#0-1)  The HTTP client resolves the destination host from `session.shop` (via `Clients::HttpClient.new(session: null_session, ...)`), so the trust boundary being asserted is: "the host that receives `client_id`/`client_secret` equals a Shopify-controlled domain." However, that equality is never independently enforced here — it relies entirely on the HMAC being valid for whatever `shop` string was submitted, and no additional domain allow-listing (`ShopValidator.TRUSTED_SHOPIFY_DOMAINS`) is applied, unlike every other credential-bearing path in the auth module: `ClientCredentials.client_credentials` [3](#0-2)  validates the shop before use, and `RefreshToken`/`Storefront` clients reference `ShopValidator` as well.

Compare to the analog bug class: the gas-refund bug assumed a fixed, unverified relationship (overhead gas) held true and paid out based on that unverified assumption. Here, `validate_auth_callback` assumes the `shop` field, once HMAC-valid, is safe to use unchecked as the destination host for a credential-bearing request — an implicit binding of "HMAC-valid" to "trusted Shopify domain" that is not independently asserted by domain allow-listing the way parallel code paths do.

### Impact Explanation
If the `shop` value in a legitimately-signed OAuth callback could ever contain something other than a canonical `*.myshopify.com` host (for example, a value accepted by Shopify's HMAC-signing process but not constrained to the merchant's real store domain), the app's `client_secret` would be transmitted to that attacker-influenced host. This matches the Critical category: theft/exfiltration of the app's `client_secret` via SSRF-style credential leakage to an unverified host.

### Likelihood Explanation
Low-to-uncertain. The `auth_query` typically originates from a Shopify-redirect and its `hmac` is signed with `api_secret_key`, so in the normal flow `shop` is Shopify-controlled. This finding is primarily an inconsistency/defense-in-depth gap relative to the gem's own established pattern (`ShopValidator.sanitize!` used elsewhere) rather than a demonstrated bypass of Shopify's HMAC signing itself — I could not find a code path in-scope where an attacker can forge a valid HMAC over an arbitrary `shop` without knowing `api_secret_key`. I flag this because the codebase treats "HMAC-valid" and "trusted domain" as interchangeable here but not in sibling flows, and cannot fully verify from static analysis alone whether all upstream integrations guarantee `shop` is always a canonical domain before `hmac` is computed.

### Recommendation
Apply `Utils::ShopValidator.sanitize!(auth_query.shop)` in `validate_auth_callback` before constructing `null_session`/`auth_base_uri`, mirroring `ClientCredentials.client_credentials`, so that the destination host for the `client_secret`-bearing request is independently constrained to `ShopValidator::TRUSTED_SHOPIFY_DOMAINS` rather than relying solely on HMAC validity.

### Proof of Concept
Not independently reproducible with the tools/files available in this session (would require confirming whether any caller can supply an `auth_query.shop` value outside the canonical Shopify domain set while still producing a valid HMAC, which depends on `api_secret_key` secrecy that is out of scope to test here). This is flagged as a defense-in-depth / consistency gap relative to the gem's own `ShopValidator` usage pattern, not a confirmed bypass.

### Citations

**File:** lib/shopify_api/auth/client_credentials.rb (L20-26)
```ruby
          unless ShopifyAPI::Context.setup?
            raise ShopifyAPI::Errors::ContextNotSetupError,
              "ShopifyAPI::Context not setup, please call ShopifyAPI::Context.setup"
          end

          validated_shop = Utils::ShopValidator.sanitize!(shop)
          shop_session = ShopifyAPI::Auth::Session.new(shop: validated_shop)
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
