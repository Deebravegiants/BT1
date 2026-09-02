### Title
OAuth callback sends the app's `client_secret` to an unvalidated `shop` host - ([File: lib/shopify_api/auth/oauth.rb])

### Summary
`ShopifyAPI::Auth::Oauth.validate_auth_callback` builds the access-token request host directly from the caller-supplied `AuthQuery#shop` field without ever passing it through `Utils::ShopValidator.sanitize!`, unlike every other code path in the gem that turns a `shop` string into a request host.

### Finding Description
`validate_auth_callback` constructs a `null_session` straight from `auth_query.shop` and hands it to `Clients::HttpClient`, which derives the POST destination as `https://#{session.shop}` and sends a body containing `client_id`/`client_secret` to that host: [1](#0-0) 

Compare this with `ClientCredentials.client_credentials` and `RefreshToken.refresh_access_token`, both of which call `Utils::ShopValidator.sanitize!(shop)` before building the session/host that will receive the `client_secret`: [2](#0-1) [3](#0-2) 

`HttpClient#initialize` turns `session.shop` directly into the request's base URI: [4](#0-3) 

`ShopValidator` exists precisely to bind the `shop` string used for building a request host to the set of trusted Shopify domains (`myshopify.com`, `shopify.com`, `myshopify.io`, `spin.dev`, `shop.dev`), rejecting anything else: [5](#0-4) 

The identity binding that should hold is: *the host that receives the app's `client_secret`* == *a Shopify-trusted domain validated by `ShopValidator`*. In `validate_auth_callback` this binding is broken — the host is instead equal to whatever string arrives in the `shop` field of the `AuthQuery` object, which is populated by the host application directly from the callback's query-string parameters (see the documented usage pattern): [6](#0-5) 

The `shop` value is one of the fields covered by HMAC verification (`Utils::HmacValidator.validate`), but that only proves the tuple `(code, host, shop, state, timestamp)` was signed by Shopify with the app's own `api_secret_key` for whatever `shop` Shopify's authorization server put in the redirect — it does not constrain `shop` to a Shopify-owned domain the way `ShopValidator` does: [7](#0-6) [8](#0-7) 

Because this code path is the sole one lacking the sanitize call that the other equivalent flows (`ClientCredentials`, `RefreshToken`) enforce, it is a genuine regression in the identity-binding invariant the gem otherwise upholds, even if I could not fully verify in this pass whether Shopify's own authorization server can ever be induced to sign a callback for a non-myshopify `shop` value (e.g., via custom-domain or transfer edge cases) — that is the one open question limiting a full proof of remote exploitability.

### Impact Explanation
If a value can reach `validate_auth_callback` for a `shop` that is not a Shopify-trusted host (whether through an edge case in Shopify's redirect generation, a proxy/CDN in front of the callback endpoint that permits header/param smuggling, or a caller that doesn't itself re-validate `shop` before constructing `AuthQuery`), the app's `client_id`/`client_secret` are sent to an attacker-controlled host. That is High-impact SSRF carrying the app's credentials to a third-party endpoint, and could enable theft of the app's `client_secret` (Critical-tier credential per the rules) if such a request ever gets routed to attacker infrastructure.

### Likelihood Explanation
Likelihood is constrained because the `shop` field is inside the HMAC-signed callback payload, so a network attacker without knowledge of `api_secret_key` cannot unilaterally choose an arbitrary `shop`. Exploitability depends on whether Shopify (or an intermediary) can be made to sign a callback containing a non-myshopify `shop`, which I was not able to confirm or rule out from this codebase alone.

### Recommendation
Add `Utils::ShopValidator.sanitize!(auth_query.shop)` in `validate_auth_callback` before constructing `null_session`/`Session.from`, mirroring the pattern already used in `ClientCredentials.client_credentials` and `RefreshToken.refresh_access_token`, so the host that ultimately receives `client_id`/`client_secret` is always constrained to a Shopify-trusted domain regardless of what value arrives in the callback query string.

### Proof of Concept
Not fully constructible from this gem alone: reproducing the exploit requires demonstrating that Shopify's OAuth authorization server (or an intermediary) can be coerced into producing a validly-HMAC-signed callback whose `shop` parameter is a non-`myshopify.com` domain, which is outside this repository's code. Within the repo, the missing-validation defect itself can be shown by unit-testing `ShopifyAPI::Auth::Oauth.validate_auth_callback` with a crafted `AuthQuery` (`shop: "attacker.example"`, with a matching valid HMAC computed using the test's own `api_secret_key`) and observing that, unlike `ClientCredentialsTest#test_client_credentials_rejects_non_shopify_domain`, no `Errors::InvalidShopError` is raised and the request is attempted against `https://attacker.example/admin/oauth/access_token`.

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

**File:** lib/shopify_api/utils/shop_validator.rb (L1-64)
```ruby
# typed: strict
# frozen_string_literal: true

require "addressable/uri"

module ShopifyAPI
  module Utils
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

**File:** docs/usage/oauth.md (L241-251)
```markdown
```ruby
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

**File:** lib/shopify_api/auth/oauth/auth_query.rb (L24-43)
```ruby
        def initialize(code:, shop:, timestamp:, state:, host:, hmac:)
          @code = code
          @shop = shop
          @timestamp = timestamp
          @state = state
          @host = host
          @hmac = hmac
        end

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
