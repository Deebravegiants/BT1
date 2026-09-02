### Title
OAuth callback sends `client_secret` to an unvalidated `shop` host, bypassing the `ShopValidator` trust boundary enforced elsewhere in the gem - (File: `lib/shopify_api/auth/oauth.rb`)

### Summary
`ShopifyAPI::Auth::Oauth.validate_auth_callback` builds the access-token request host directly from `auth_query.shop` and never routes it through `ShopifyAPI::Utils::ShopValidator.sanitize!`, unlike every other code path in the gem that turns a caller/attacker-influenced `shop` value into a request host (`RefreshToken.refresh_access_token`, `TokenExchange.exchange_token`'s `dest`-derived shop is bound to the signed JWT, `ClientCredentials`, and the storefront GraphQL client).

### Finding Description
`validate_auth_callback` only checks that the callback's HMAC is valid over `code, host, shop, state, timestamp` [1](#0-0) , then immediately uses `auth_query.shop` to construct the session that targets the token endpoint:

```ruby
null_session = Auth::Session.new(shop: auth_query.shop)
...
client = Clients::HttpClient.new(session: null_session, base_path: "/admin/oauth")
``` [2](#0-1) 

`HmacValidator.validate` only proves the bytes were signed with the app's secret — it does not constrain `shop` to a `myshopify.com`/trusted admin domain. The gem's own newer `ShopValidator` module (added in 16.3.0, per `CHANGELOG.md`) exists precisely to close this gap by resolving/whitelisting `shop` against `TRUSTED_SHOPIFY_DOMAINS` (`shopify.com`, `myshopify.io`, `myshopify.com`, `spin.dev`, `shop.dev`) before it is used to build a request host [3](#0-2) . `RefreshToken.refresh_access_token` correctly calls `Utils::ShopValidator.sanitize!(shop)` before constructing the session that sends `client_id`/`client_secret` [4](#0-3) , but `Oauth.validate_auth_callback` never performs this sanitization — it trusts the HMAC-covered `shop` field as if it were already a validated host, and uses it to route the app's `client_id`/`client_secret` (see `body` at lines 74-79).

This breaks the equality that should hold: `shop value HMAC-signed by Shopify == shop value validated as a legitimate Shopify admin host`. The HMAC only proves *integrity/origin of the byte string*, not that the string is a well-formed, in-scope Shopify domain. Because `HttpClient` builds the destination URL straight from `session.domain` (`https://#{shop}/admin/oauth/access_token`), any string in the `shop` HMAC field is used verbatim as a network destination for a request carrying the app's `client_secret`.

### Impact Explanation
If Shopify's OAuth authorize/callback flow (or a `/admin/oauth` redirect construction anywhere in the ecosystem) can be induced to sign a `shop` value that is not a trusted Shopify domain — e.g., through host/domain confusion, unusual OAuth relay setups, or first-party/dev-server flows the gem already special-cases in `auth_base_uri` (`.my.shop.dev`) — the resulting `access_token` request, which includes `client_id` and `client_secret` in the POST body, would be sent to that attacker-influenced host instead of Shopify. This is exactly the class of credential-exfiltration/SSRF-with-app-credentials risk the report highlights by analogy (an unvalidated/asymmetric input silently accepted and forwarded downstream with a security-relevant effect), and matches the gem's own precedent of requiring `ShopValidator.sanitize!` before using `shop` as a request host.

### Likelihood Explanation
Likelihood is constrained: exploitation requires that the HMAC-covered `shop` value can be made something other than the exact domain Shopify's `/admin/oauth/authorize` step redirects to, which is out of this gem's control in the normal SaaS OAuth flow. The vulnerability is a defense-in-depth gap in the gem itself (a validated boundary present elsewhere in the same file/module is absent here), not a demonstrated end-to-end forgeable request without any secret. I was not able to fully verify (given index/tool limits) whether any caller can supply an attacker-chosen `shop` to `validate_auth_callback` that still passes HMAC validation without secret knowledge, or whether Shopify's platform-side redirect strictly canonicalizes `shop` before signing it, so likelihood should be treated as uncertain rather than confirmed high.

### Recommendation
Call `Utils::ShopValidator.sanitize!(auth_query.shop)` (as already done in `RefreshToken.refresh_access_token`) in `validate_auth_callback` before constructing `null_session` and before using the value for `Session.from(shop: ...)`, so the value used to route the `client_secret`-bearing token request is provably a trusted Shopify domain, not merely an HMAC-signed byte string.

### Proof of Concept
Conceptual, since it requires a byte string that both (a) is HMAC-signable only by Shopify/holder of `client_secret`, and (b) fails `ShopValidator.sanitize!`:
1. Compare `Oauth.validate_auth_callback` (`lib/shopify_api/auth/oauth.rb:64-98`, no `ShopValidator` call) against `RefreshToken.refresh_access_token` (`lib/shopify_api/auth/refresh_token.rb:24`, explicit `Utils::ShopValidator.sanitize!(shop)` call) in the same codebase to show the inconsistent trust boundary.
2. `HmacValidator.validate` (`lib/shopify_api/utils/hmac_validator.rb:12-22`) only performs `OpenSSL.secure_compare` over the signable string; it never inspects `shop`'s domain shape.
3. `ShopValidator.sanitize_shop_domain` (`lib/shopify_api/utils/shop_validator.rb:29-48`) shows the domain checks that are being skipped in the OAuth callback path (must resolve to one of `TRUSTED_SHOPIFY_DOMAINS` or a caller-provided `myshopify_domain`). [5](#0-4) [6](#0-5) [7](#0-6)

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

**File:** lib/shopify_api/utils/shop_validator.rb (L8-48)
```ruby
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

      class << self
        extend T::Sig

        sig do
          params(
            shop_domain: String,
            myshopify_domain: T.nilable(String),
          ).returns(T.nilable(String))
        end
        def sanitize_shop_domain(shop_domain, myshopify_domain: nil)
          uri = uri_from_shop_domain(shop_domain, myshopify_domain)
          return nil if uri.nil? || uri.host.nil? || uri.host.empty?

          trusted_domains(myshopify_domain).each do |trusted_domain|
            host = T.cast(uri.host, String)
            uri_domain = uri.domain
            next if uri_domain.nil?

            no_shop_name_in_subdomain = host == trusted_domain
            from_trusted_domain = trusted_domain == uri_domain

            if unified_admin?(uri) && from_trusted_domain
              return myshopify_domain_from_unified_admin(uri)
            end
            return nil if no_shop_name_in_subdomain || host.empty?
            return host if from_trusted_domain
          end
          nil
        end
```

**File:** lib/shopify_api/auth/refresh_token.rb (L18-33)
```ruby
        def refresh_access_token(shop:, refresh_token:)
          unless ShopifyAPI::Context.setup?
            raise ShopifyAPI::Errors::ContextNotSetupError,
              "ShopifyAPI::Context not setup, please call ShopifyAPI::Context.setup"
          end

          validated_shop = Utils::ShopValidator.sanitize!(shop)
          shop_session = ShopifyAPI::Auth::Session.new(shop: validated_shop)
          body = {
            client_id: ShopifyAPI::Context.api_key,
            client_secret: ShopifyAPI::Context.api_secret_key,
            grant_type: "refresh_token",
            refresh_token:,
          }

          client = Clients::HttpClient.new(session: shop_session, base_path: "/admin/oauth")
```
