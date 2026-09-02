### Title
Missing shop-domain validation in `TokenExchange.exchange_token` leaks `client_secret` to an unvalidated host - (File: `lib/shopify_api/auth/token_exchange.rb`)

### Summary
`ShopifyAPI::Auth::TokenExchange.exchange_token` derives the destination host for the OAuth `access_token` request directly from the session token's `dest` claim without ever passing it through `ShopifyAPI::Utils::ShopValidator.sanitize!`, unlike every other method in this library that builds a similar request. This breaks the binding "host that receives `client_id`/`client_secret`" == "host that has been verified to be a trusted Shopify domain".

### Finding Description
`ShopifyAPI::Auth::JwtPayload#shop` simply does: [1](#0-0) 

It only strips the literal string `"https://"` from the `dest` claim; it performs no check that the resulting host is a `*.myshopify.com`/`myshopify.io`/`spin.dev`/`shop.dev` domain. `JwtPayload#initialize` only validates the HMAC signature and the `aud` claim against `Context.api_key`: [2](#0-1) 

`TokenExchange.exchange_token` then takes this unsanitized value and uses it verbatim to build the session that the `HttpClient` uses to compute the outgoing request host, sending the app's `client_id` and `client_secret` to it: [3](#0-2) 

`Clients::HttpClient#initialize` builds `@base_uri` straight from `session.shop`: [4](#0-3) 

Every other credential-bearing flow in this same module set enforces the missing check via `Utils::ShopValidator.sanitize!`, which restricts the host to `TRUSTED_SHOPIFY_DOMAINS` before it is used to build the outbound request: [5](#0-4) [6](#0-5) [7](#0-6) [8](#0-7) 

So the library has an established, tested pattern (`sanitize!`, with a dedicated `TRUSTED_SHOPIFY_DOMAINS` allow-list and dedicated `InvalidShopError`) for exactly this purpose, but `exchange_token` — the primary, documented flow for embedded apps — is the one path that omits it. The equality that should hold is:

`host used to send client_id/client_secret == ShopValidator.sanitize!(host)`

but for `exchange_token` it is instead:

`host used to send client_id/client_secret == raw JwtPayload#dest (minus "https://")`

### Impact Explanation
Any code path that reaches `TokenExchange.exchange_token` with a session token whose `dest` claim is not constrained to a `myshopify.com`-family host will cause the app's `client_id` and `client_secret` to be POSTed to that host. Because `JwtPayload` accepts any token signed with the app's own secret and only checks `aud`, it does not distinguish between an admin session token (`iss` ending in `/admin`) and other Shopify-issued token types (e.g. checkout/extension tokens, seen accepted by the very same `JwtPayload` class in the checkout UI extension tests), nor does it independently confirm that `dest` is restricted to Shopify's own infrastructure the way `ShopValidator` does. This is the same failure mode as the reported bug class: a security-sensitive value (the destination host for the client secret) is trusted based on a check (JWT signature/`aud`) that does not actually bind it to the invariant the code relies on (host is a genuine Shopify domain), while a stricter, already-implemented check exists elsewhere in the codebase and is simply not applied here.

### Likelihood Explanation
This code path is directly reachable through the gem's primary documented API (`TokenExchange.exchange_token`) with only a Shopify-issued session token — no `api_secret_key` guessing or leakage is required to trigger the call, only to have the library process whatever token is handed to it. The absence of `ShopValidator.sanitize!` here — while present in the three structurally identical sibling methods in the same file/directory — is a clear, provable inconsistency rather than a theoretical concern.

### Recommendation
In `TokenExchange.exchange_token`, validate `dest_shop` with `Utils::ShopValidator.sanitize!(dest_shop)` (mirroring `migrate_to_expiring_token`, `client_credentials`, and `refresh_access_token`) before constructing `shop_session`, and raise `Errors::InvalidShopError` if the `dest` claim does not resolve to a trusted Shopify domain.

### Proof of Concept
1. Obtain (or have a client-side flow deliver) a session token that is validly signed with the app's `api_secret_key` and has `aud` equal to the app's `api_key`, but whose `dest` claim is not a `*.myshopify.com` host (e.g., any Shopify-issued token type whose `dest`/equivalent field is not constrained the way `ShopValidator`'s allow-list constrains it).
2. Call `ShopifyAPI::Auth::TokenExchange.exchange_token(session_token: token, requested_token_type: ...)`.
3. Observe that `dest_shop = jwt_payload.shop` is used unchanged to build `shop_session`, and `Clients::HttpClient` sends an HTTP POST containing `client_id` and `client_secret` to `https://#{dest_shop}/admin/oauth/access_token` with no domain allow-list check, unlike the sibling `migrate_to_expiring_token` call which would reject the same input via `Utils::ShopValidator.sanitize!`.

### Citations

**File:** lib/shopify_api/auth/jwt_payload.rb (L23-45)
```ruby
      sig { params(token: String).void }
      def initialize(token)
        payload_hash = begin
          decode_token(token, Context.api_secret_key)
        rescue ShopifyAPI::Errors::InvalidJwtTokenError
          raise unless Context.old_api_secret_key

          decode_token(token, T.must(Context.old_api_secret_key))
        end

        @iss = T.let(payload_hash["iss"], String)
        @dest = T.let(payload_hash["dest"], String)
        @aud = T.let(payload_hash["aud"], String)
        @sub = T.let(payload_hash["sub"], T.nilable(String))
        @exp = T.let(payload_hash["exp"], Integer)
        @nbf = T.let(payload_hash["nbf"], Integer)
        @iat = T.let(payload_hash["iat"], Integer)
        @jti = T.let(payload_hash["jti"], String)
        @sid = T.let(payload_hash["sid"], T.nilable(String))

        raise ShopifyAPI::Errors::InvalidJwtTokenError,
          "Session token had invalid API key" unless @aud == Context.api_key
      end
```

**File:** lib/shopify_api/auth/jwt_payload.rb (L47-51)
```ruby
      sig { returns(String) }
      def shop
        @dest.gsub("https://", "")
      end
      alias_method :shopify_domain, :shop
```

**File:** lib/shopify_api/auth/token_exchange.rb (L39-65)
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

**File:** lib/shopify_api/auth/token_exchange.rb (L97-115)
```ruby
        def migrate_to_expiring_token(shop:, non_expiring_offline_token:)
          unless ShopifyAPI::Context.setup?
            raise ShopifyAPI::Errors::ContextNotSetupError,
              "ShopifyAPI::Context not setup, please call ShopifyAPI::Context.setup"
          end

          validated_shop = Utils::ShopValidator.sanitize!(shop)
          shop_session = ShopifyAPI::Auth::Session.new(shop: validated_shop)
          body = {
            client_id: ShopifyAPI::Context.api_key,
            client_secret: ShopifyAPI::Context.api_secret_key,
            grant_type: TOKEN_EXCHANGE_GRANT_TYPE,
            subject_token: non_expiring_offline_token,
            subject_token_type: RequestedTokenType::OFFLINE_ACCESS_TOKEN.serialize,
            requested_token_type: RequestedTokenType::OFFLINE_ACCESS_TOKEN.serialize,
            expiring: "1",
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

**File:** lib/shopify_api/utils/shop_validator.rb (L6-65)
```ruby
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
