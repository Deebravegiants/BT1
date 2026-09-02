### Title
OAuth callback sends `client_secret` to an unsanitized `shop` domain from the HMAC-signed query, bypassing the app's trusted-domain check - ([File: lib/shopify_api/auth/oauth.rb])

### Summary
`ShopifyAPI::Auth::Oauth.validate_auth_callback` builds the session used to exchange the OAuth `code` for an access token directly from `auth_query.shop`, without ever passing it through `ShopifyAPI::Utils::ShopValidator.sanitize!`, unlike every other credential-exchange path in the gem (`ClientCredentials.client_credentials`, `RefreshToken.refresh_access_token`, `TokenExchange.migrate_to_expiring_token`) which all call `Utils::ShopValidator.sanitize!(shop)` before constructing the session that receives the `client_secret`.

### Finding Description
`validate_auth_callback` verifies the callback query string's HMAC via `Utils::HmacValidator.validate(auth_query)` [1](#0-0) . The HMAC covers `code`, `host`, `shop`, `state`, and `timestamp` as defined by `AuthQuery#to_signable_string` [2](#0-1) . However, once the HMAC check passes, the code takes `auth_query.shop` as a raw string and builds a `null_session` directly from it: `Auth::Session.new(shop: auth_query.shop)`, then constructs an HTTP client whose target host is derived from `session.shop` and posts the app's `client_id`/`client_secret`/`code` to `https://#{shop}/admin/oauth/access_token` [3](#0-2) [4](#0-3) .

Every other place in the gem that turns a caller-supplied `shop` string into a destination for the `client_secret` explicitly calls `Utils::ShopValidator.sanitize!`, which restricts the resulting host to `TRUSTED_SHOPIFY_DOMAINS` (`shopify.com`, `myshopify.io`, `myshopify.com`, `spin.dev`, `shop.dev`) and raises `Errors::InvalidShopError` otherwise [5](#0-4) :
- `ClientCredentials.client_credentials` [6](#0-5) 
- `RefreshToken.refresh_access_token` [7](#0-6) 
- `TokenExchange.migrate_to_expiring_token` [8](#0-7) 

`validate_auth_callback` is the outlier: it never sanitizes `auth_query.shop` against `TRUSTED_SHOPIFY_DOMAINS`, so the identity binding "the HMAC-verified `shop` field == a Shopify-trusted domain that may receive `client_secret`" is not enforced here, even though it is enforced everywhere else the gem sends the secret to a `shop`-derived host.

The HMAC does guarantee the `shop`/`code`/`host`/`state`/`timestamp` bytes were produced by whoever holds `api_secret_key` (normally Shopify), so under normal operation this cannot be forged by a third party who does not know the secret. But it also means the *only* safety net for this particular flow is the HMAC check plus whatever value Shopify's redirect actually contains — there is no defense-in-depth domain allow-list as in the sibling flows, and no code-level guarantee that `shop` is confined to a trusted Shopify TLD before the app's `client_secret` is transmitted to `https://#{shop}/...`. This is precisely the kind of drift the report's call for a signature specification is meant to prevent: the spec would need to state explicitly which fields of a signed message are treated as trusted identifiers for routing credentials, and this code path silently diverges from the pattern used elsewhere in the same gem.

### Impact Explanation
If `auth_query.shop` is not constrained to a Shopify-owned domain, an attacker able to influence the value that ends up in this parameter (e.g. via a compromised/rotated secret with `old_api_secret_key`, or via an app that constructs its own `AuthQuery` from unsanitized input rather than from an untouched Shopify redirect) causes the app's `client_id`/`client_secret` and the merchant's OAuth `code` to be POSTed to an attacker-controlled host — an SSRF-with-credentials scenario resulting in `client_secret`/authorization-code exfiltration, matching the High-impact category (SSRF with the app's credentials / credential leakage).

### Likelihood Explanation
Under the intended usage — `AuthQuery` built strictly from an unmodified Shopify redirect and validated via a never-rotated, never-leaked `api_secret_key` — this is not directly exploitable, since the HMAC check ties `shop` to Shopify's own signing key. The likelihood is elevated by the fact that this is the one credential-exchange call site in the gem that omits the `ShopValidator.sanitize!` defense-in-depth check present in all sibling flows, so any host-side misuse of `AuthQuery` (e.g., constructing it from data that wasn't itself freshly HMAC-verified by Shopify, or during key rotation windows where `old_api_secret_key` is honored) removes the only remaining check on the destination host.

### Recommendation
Apply `Utils::ShopValidator.sanitize!(auth_query.shop)` in `Oauth.validate_auth_callback` before constructing `null_session`, mirroring `ClientCredentials`, `RefreshToken`, and `TokenExchange.migrate_to_expiring_token`, so the `client_secret` is never sent to a host outside `TRUSTED_SHOPIFY_DOMAINS` regardless of how `shop` reached this method. As the underlying report recommends, document as part of the signature specification which claims of a verified message are also required to satisfy domain/tenant allow-listing before being used to route credentials.

### Proof of Concept
1. Construct (or otherwise obtain) an `AuthQuery` whose `shop` field is not restricted to `TRUSTED_SHOPIFY_DOMAINS` but whose HMAC nonetheless validates against `Context.api_secret_key` or `Context.old_api_secret_key` (e.g., during a key-rotation window, or wherever `AuthQuery` is built from data not itself under Shopify's direct redirect control).
2. Call `ShopifyAPI::Auth::Oauth.validate_auth_callback(cookies:, auth_query:)`.
3. Observe that `Clients::HttpClient` is instantiated with `session.shop` equal to the attacker-influenced value and that the POST containing `client_id`, `client_secret`, and `code` is sent to `https://#{shop}/admin/oauth/access_token` with no `ShopValidator` check, in contrast to `ClientCredentials.client_credentials`, which would reject the same `shop` value with `Errors::InvalidShopError`.

### Citations

**File:** lib/shopify_api/auth/oauth.rb (L60-64)
```ruby
        def validate_auth_callback(cookies:, auth_query:)
          unless Context.setup?
            raise Errors::ContextNotSetupError, "ShopifyAPI::Context not setup, please call ShopifyAPI::Context.setup"
          end
          raise Errors::InvalidOauthError, "Invalid OAuth callback." unless Utils::HmacValidator.validate(auth_query)
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

**File:** lib/shopify_api/auth/client_credentials.rb (L19-26)
```ruby
        def client_credentials(shop:)
          unless ShopifyAPI::Context.setup?
            raise ShopifyAPI::Errors::ContextNotSetupError,
              "ShopifyAPI::Context not setup, please call ShopifyAPI::Context.setup"
          end

          validated_shop = Utils::ShopValidator.sanitize!(shop)
          shop_session = ShopifyAPI::Auth::Session.new(shop: validated_shop)
```

**File:** lib/shopify_api/auth/refresh_token.rb (L18-25)
```ruby
        def refresh_access_token(shop:, refresh_token:)
          unless ShopifyAPI::Context.setup?
            raise ShopifyAPI::Errors::ContextNotSetupError,
              "ShopifyAPI::Context not setup, please call ShopifyAPI::Context.setup"
          end

          validated_shop = Utils::ShopValidator.sanitize!(shop)
          shop_session = ShopifyAPI::Auth::Session.new(shop: validated_shop)
```

**File:** lib/shopify_api/auth/token_exchange.rb (L97-104)
```ruby
        def migrate_to_expiring_token(shop:, non_expiring_offline_token:)
          unless ShopifyAPI::Context.setup?
            raise ShopifyAPI::Errors::ContextNotSetupError,
              "ShopifyAPI::Context not setup, please call ShopifyAPI::Context.setup"
          end

          validated_shop = Utils::ShopValidator.sanitize!(shop)
          shop_session = ShopifyAPI::Auth::Session.new(shop: validated_shop)
```
