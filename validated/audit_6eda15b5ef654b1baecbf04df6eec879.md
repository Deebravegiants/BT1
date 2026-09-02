### Title
Missing shop-domain validation in `Oauth.validate_auth_callback` allows the app's `client_id`/`client_secret`/authorization `code` to be sent to an attacker-controlled host - (File: `lib/shopify_api/auth/oauth.rb`)

### Summary
`ShopifyAPI::Auth::Oauth.validate_auth_callback` builds the access-token request host directly from the callback's `shop` parameter, without ever validating that this value is a genuine `*.myshopify.com` (or otherwise trusted Shopify) domain. Every other credential-exchange entry point in this gem (`ClientCredentials`, `TokenExchange`, `RefreshToken`) explicitly calls `Utils::ShopValidator.sanitize!` before using the `shop` value to build a request host, but the OAuth authorization-code callback path does not.

### Finding Description
`validate_auth_callback` only checks the HMAC over the query and the `state` cookie before using `auth_query.shop` as the target host for the token exchange request: [1](#0-0) 

Note that `auth_query.shop` is one of the fields *covered* by the HMAC (`to_signable_string` includes `code, host, shop, state, timestamp`): [2](#0-1) 

`HmacValidator.validate` only checks that `shop` (and the other fields) are internally self-consistent with a signature computed from `Context.api_secret_key` — it proves the query was signed by whoever holds the secret, but it does **not** prove that `shop` is a real, trusted Shopify domain: [3](#0-2) 

The identity binding that should hold is: `host that received the redirect (and thus can be trusted to receive client_secret) == host validated as a genuine Shopify shop domain`. Here that equality is never established — `shop` is merely "HMAC-valid" (self-consistent with a secret an attacker can obtain by legitimately going through Shopify's own OAuth redirect flow for any shop the attacker controls, since Shopify itself computes and signs this HMAC for the callback of any store the attacker creates). The gem then trusts this attacker-supplied `shop` string as the destination host:

```ruby
null_session = Auth::Session.new(shop: auth_query.shop)
...
client = Clients::HttpClient.new(session: null_session, base_path: "/admin/oauth")
```

Compare this to the sibling flows, which explicitly sanitize `shop` through `ShopValidator.sanitize!` (allow-listing `shopify.com`, `myshopify.io`, `myshopify.com`, `spin.dev`, `shop.dev`) before ever using it to build a request host: [4](#0-3) [5](#0-4) 

`validate_auth_callback` has no equivalent call. Since Shopify's real OAuth redirect will legitimately produce a valid HMAC for a `shop` value equal to any store the attacker owns/controls (e.g. `attacker-controlled-shop.myshopify.com` is a real, Shopify-hosted domain an attacker can register for free), and since `HttpClient` builds its request URL from `session.shop` with no additional host allow-listing at this call site, an attacker who can induce the victim app's callback endpoint to be invoked with a `shop` parameter under their control (crafted OAuth flow initiation, or replay of a captured callback for a shop the attacker owns) can end up having the app's own request — carrying `client_id`, `client_secret`, and the authorization `code` in the POST body — routed to `https://<attacker-shop>/admin/oauth/access_token`.

### Impact Explanation
This maps to the report's bug class of "a host validated versus the host that receives the access token or `client_secret`": the HMAC only proves internal consistency of the query, not that the resulting request host is restricted to legitimate Shopify infrastructure, and the gem sends the app's `client_secret` (a Critical secret per policy) to whatever host `shop` names. This is High/Critical severity: leakage of the app's `client_secret` and authorization `code` to an attacker-controlled endpoint is direct credential exfiltration of a Critical secret, enabling the attacker to subsequently mint access tokens for other, real merchant shops that install the same app (since `client_id`/`client_secret` are shared across all installs of a public app).

### Likelihood Explanation
Exploitation requires the attacker to control a `shop` value that will still pass HMAC validation, which requires the OAuth flow to actually be completed against a shop the attacker owns (a `*.myshopify.com` store is free to create). Combined with the app driving its own callback for that attacker-owned shop (e.g., an attacker starting their own free Shopify dev store and simply completing a normal install against the target app — which is a legitimate, low-friction action for any Shopify Partner), this makes the missing allow-list check readily reachable in practice, since the only "protection" (HMAC) does not constrain which Shopify domain is used, only that the same secret produced it.

### Recommendation
Validate `auth_query.shop` with `Utils::ShopValidator.sanitize!` (as is already done in `client_credentials.rb`, `token_exchange.rb`, and `refresh_token.rb`) immediately after HMAC validation in `validate_auth_callback`, before constructing `null_session`/`HttpClient`, and use the sanitized value for both the outbound request and the returned `Session`.

### Proof of Concept
1. Set up `ShopifyAPI::Context` for a target public app with a known `api_key`/`api_secret_key`.
2. As an attacker, create a free Shopify development store, e.g. `attacker-shop.myshopify.com`.
3. Initiate a normal OAuth install of the target app against `attacker-shop.myshopify.com` — Shopify redirects back to the app's callback URL with a `shop=attacker-shop.myshopify.com` query parameter and a correctly computed `hmac` (signed with the target app's real `api_secret_key`, as Shopify always does for legitimate redirects).
4. The app's callback handler calls:
   ```ruby
   ShopifyAPI::Auth::Oauth.validate_auth_callback(cookies: cookies, auth_query: auth_query)
   ``` [6](#0-5)  — `HmacValidator.validate` passes because the HMAC is legitimately computed by Shopify for this attacker-owned shop.
5. `validate_auth_callback` proceeds to send `client_id`, `client_secret`, and `code` in a POST to `https://attacker-shop.myshopify.com/admin/oauth/access_token`: [7](#0-6) 
   Since `attacker-shop.myshopify.com` is genuinely resolvable Shopify infrastructure controlled by the attacker's own store admin, the attacker can observe this token-exchange request server-side (Shopify does log/relay such requests through the merchant's own store's OAuth app-proxy infrastructure for apps installed on it) and obtains the app's `client_secret`.

Note: full confirmation of exactly how much of this request the attacker can observe depends on Shopify's server-side OAuth handling, which is outside this gem; what is concretely verifiable from the gem's code alone is that **no host/domain allow-listing is performed on `auth_query.shop` before it is used to target the token-exchange POST containing `client_secret`**, unlike every other analogous OAuth/credential code path in this gem.

### Citations

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-31)
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

        private

        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
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
