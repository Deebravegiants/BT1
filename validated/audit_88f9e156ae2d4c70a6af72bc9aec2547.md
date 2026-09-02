### Title
OAuth callback sends `client_secret` and access-token requests to an unvalidated `shop` domain - ([File: lib/shopify_api/auth/oauth.rb])

### Summary
`ShopifyAPI::Auth::Oauth.validate_auth_callback` builds the access-token exchange request using `auth_query.shop` directly, without ever passing it through `Utils::ShopValidator.sanitize!`, unlike the other credential-issuing flows in the same library (`ClientCredentials.client_credentials` and `RefreshToken.refresh_access_token`), which both call `Utils::ShopValidator.sanitize!(shop)` before building a session/host.

### Finding Description
`validate_auth_callback` only checks two things about the incoming request: the HMAC over `code/host/shop/state/timestamp` [1](#0-0)  and that the `state` cookie matches `auth_query.state` [2](#0-1) . It then builds a `null_session` directly from `auth_query.shop` and immediately performs the token exchange, sending the app's `client_id`/`client_secret` to that host: [3](#0-2) 

`Clients::HttpClient` derives the request's target host directly from `session.shop`: [4](#0-3) 

The identity binding that should hold is: *`shop` value that determines the network destination of the `client_secret`-bearing POST == a value proven to be a genuine `*.myshopify.com` (or other trusted Shopify) domain*. That binding is enforced everywhere else credentials are constructed — `ClientCredentials.client_credentials` [5](#0-4)  and `RefreshToken.refresh_access_token` [6](#0-5)  both call `Utils::ShopValidator.sanitize!(shop)`, which rejects any domain not under `TRUSTED_SHOPIFY_DOMAINS` (`shopify.com`, `myshopify.io`, `myshopify.com`, `spin.dev`, `shop.dev`) [7](#0-6) . `Oauth.validate_auth_callback` is missing this same call — it uses `auth_query.shop` unsanitized both for the `null_session` used to send the token-exchange request and for the final `Session.from(shop: auth_query.shop, ...)`.

The HMAC does cover `shop`, meaning an attacker who does not know `api_secret_key` cannot forge an arbitrary `shop` value on a request they craft from scratch. However, HMAC coverage only proves the *bytes* were signed by Shopify for some request Shopify itself issued — it does not prove those bytes are constrained to a trusted Shopify domain (that check is a separate, application-level responsibility that this gem enforces in two of three OAuth-adjacent code paths but omits in the third). Because the host application is expected to hand `request.parameters` straight into `AuthQuery` (as shown in the gem's own documented example) [8](#0-7) , the responsibility for shop-domain trust enforcement rests with this gem's own `validate_auth_callback`, and this is exactly the domain-confusion class of bug `Utils::ShopValidator` exists to prevent (see its dedicated attacker-domain rejection tests) [9](#0-8) .

### Impact Explanation
If any request path can cause `Oauth.validate_auth_callback` to be invoked with a `shop` value under attacker control while still carrying a valid signature (e.g., a callback that Shopify legitimately issues but whose `shop` value is not constrained to be a `*.myshopify.com` host, or any future/alternate caller of this method that does not itself pre-validate `shop`), the app's `client_id` and `client_secret` are POSTed to that host, and the resulting "access token" response is trusted to build a `Session`. This matches the report's High-impact category: SSRF/credential exfiltration carrying the app's `client_secret`, and it stems from the same class of bug as the external report — an operation is performed on a value (`shop`-derived host) that is not validated the same way equivalent code paths validate it, an inconsistent identity-binding check across otherwise-parallel code (`ClientCredentials`, `RefreshToken` vs. `Oauth`).

### Likelihood Explanation
Exploitability is bounded by the fact that Shopify's HMAC does cover `shop`, so a fully external/anonymous attacker cannot forge the signature without the `api_secret_key`. The residual risk is that `validate_auth_callback` unconditionally trusts an HMAC-valid `shop` string as a safe network destination even though this gem enforces domain trust via `ShopValidator` in its sibling methods, making this an inconsistency/defense-in-depth gap rather than a directly demonstrated bypass with a crafted external request.

### Recommendation
Call `Utils::ShopValidator.sanitize!(auth_query.shop)` (mirroring `ClientCredentials` and `RefreshToken`) inside `Oauth.validate_auth_callback` before constructing `null_session` and before calling `Session.from`, so the token-exchange request and resulting session are only ever bound to a value proven to be a trusted Shopify domain, consistent with the rest of the library.

### Proof of Concept
Not independently reproducible as a fully unprivileged, credential-free attack from the information available: exploitation requires either (a) a caller of `Oauth.validate_auth_callback` that supplies an HMAC-valid `AuthQuery` whose `shop` is not itself pre-validated as `*.myshopify.com`, or (b) a code path where the `shop` bound into the HMAC is not restricted by Shopify to trusted domains. This cannot be confirmed purely from `lib/shopify_api/**`; verifying whether Shopify's real OAuth callback ever allows `shop` values outside `myshopify.com` at the wire level is outside this gem's code and outside what the index/tools here can confirm.

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

**File:** lib/shopify_api/auth/oauth.rb (L64-71)
```ruby
          raise Errors::InvalidOauthError, "Invalid OAuth callback." unless Utils::HmacValidator.validate(auth_query)
          raise Errors::UnsupportedOauthError, "Cannot perform OAuth for private apps." if Context.private?

          state = cookies[SessionCookie::SESSION_COOKIE_NAME]
          raise Errors::NoSessionCookieError unless state

          raise Errors::InvalidOauthError,
            "Invalid state in OAuth callback." unless state == auth_query.state
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

**File:** lib/shopify_api/clients/http_client.rb (L16-19)
```ruby
        api_host = Context.api_host

        @base_uri = T.let("https://#{api_host || session.shop}", String)
        @base_uri_and_path = T.let("#{@base_uri}#{base_path}", String)
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

**File:** docs/usage/oauth.md (L242-251)
```markdown
def callback
  begin
    # Create an AuthQuery object from the request parameters,
    # and pass the list of cookies to `validate_auth_callback`
    auth_result = ShopifyAPI::Auth::Oauth.validate_auth_callback(
      cookies: cookies.to_h,
      auth_query: ShopifyAPI::Auth::Oauth::AuthQuery.new(
        request.parameters.symbolize_keys.except(:controller, :action)
      )
    )
```

**File:** test/utils/shop_validator_test.rb (L38-66)
```ruby
      def test_rejects_attacker_controlled_domain
        assert_raises(ShopifyAPI::Errors::InvalidShopError) do
          ShopifyAPI::Utils::ShopValidator.sanitize!("attacker.example")
        end
      end

      def test_rejects_empty_string
        assert_raises(ShopifyAPI::Errors::InvalidShopError) do
          ShopifyAPI::Utils::ShopValidator.sanitize!("")
        end
      end

      def test_rejects_non_shopify_domain
        assert_raises(ShopifyAPI::Errors::InvalidShopError) do
          ShopifyAPI::Utils::ShopValidator.sanitize!("evil.com")
        end
      end

      def test_rejects_shopify_suffix_as_subdomain_of_attacker
        assert_raises(ShopifyAPI::Errors::InvalidShopError) do
          ShopifyAPI::Utils::ShopValidator.sanitize!("myshopify.com.evil.com")
        end
      end

      def test_rejects_similar_looking_domain
        assert_raises(ShopifyAPI::Errors::InvalidShopError) do
          ShopifyAPI::Utils::ShopValidator.sanitize!("test-shop.notmyshopify.com")
        end
      end
```
