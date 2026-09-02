This is confirmed and worth reporting: `TokenExchange.exchange_token` derives the target shop directly from the JWT `dest` claim via `JwtPayload#shop` (`@dest.gsub("https://", "")`) without ever passing it through `Utils::ShopValidator.sanitize!`, unlike every sibling OAuth flow (`ClientCredentials.client_credentials`, `RefreshToken.refresh_access_token`, and `TokenExchange.migrate_to_expiring_token`), which all validate the shop with `ShopValidator.sanitize!` before using it as the request host.

### Title
Unvalidated JWT `dest` claim used as request host for `client_secret` delivery in Token Exchange - (File: lib/shopify_api/auth/token_exchange.rb)

### Summary
`ShopifyAPI::Auth::TokenExchange.exchange_token` takes the `dest` claim straight out of the caller-supplied session token and uses it, unsanitized, as the host that receives the app's `client_id`/`client_secret` in the token-exchange POST body — breaking the equality `host validated == host that receives client_secret`.

### Finding Description
`JwtPayload#shop` does nothing more than `@dest.gsub("https://", "")` [1](#0-0) . It performs no allow-list check against Shopify domains (no call to `Utils::ShopValidator`), unlike the rest of the auth module.

`TokenExchange.exchange_token` takes this unsanitized value (`dest_shop`) and uses it directly to build the `Session` that determines the HTTP request host, then sends `client_id`/`client_secret` to that host: [2](#0-1) 

Compare this with `TokenExchange.migrate_to_expiring_token`, `ClientCredentials.client_credentials`, and `RefreshToken.refresh_access_token`, all of which call `Utils::ShopValidator.sanitize!(shop)` before constructing the session/host that will receive `client_secret`: [3](#0-2) [4](#0-3) [5](#0-4) 

`ShopValidator.sanitize!` exists specifically to guard against exactly this class of bug — untrusted domain strings being used as request hosts — and rejects anything outside `TRUSTED_SHOPIFY_DOMAINS` (`shopify.com`, `myshopify.io`, `myshopify.com`, `spin.dev`, `shop.dev`) [6](#0-5) . `exchange_token` bypasses this entirely.

The JWT signature itself is verified against `Context.api_secret_key`/`old_api_secret_key` [7](#0-6) , so an attacker without the app's secret cannot forge an arbitrary token. This constrains the practical exploitability of the `dest`-as-host trust gap to cases where a validly-signed token with an attacker-influenced `dest` can be produced (e.g., surfaces that mint/relay session tokens, or trust boundaries between the identity provider and this consuming code) — the gem itself provides no defense-in-depth here, whereas its own sibling methods do.

### Impact Explanation
If an untrusted/malformed `dest` value ever reaches `exchange_token` bound to a validly-signed JWT (or via any relay/misconfiguration upstream of this gem that this gem does not defend against), `client_id` and `client_secret` are POSTed to a host derived from that value with no domain allow-listing — this is credential leakage of the app's `client_secret` to a non-Shopify host, i.e., High severity per the SSRF/credential-leak criteria (SSRF carrying the app's credentials).

### Likelihood Explanation
Low-to-moderate: exploitation requires a validly HS256-signed session token whose `dest` claim is not constrained to a genuine Shopify domain, since forging the signature outright requires the shared secret. However, this is a real regression/inconsistency relative to the rest of the codebase — the library just added `ShopValidator` (v16.3.0) precisely to close this class of gap in three other OAuth entry points but missed the highest-traffic one (`exchange_token`), leaving the binding "trusted domain == host receiving client_secret" unenforced in this specific path.

### Recommendation
In `ShopifyAPI::Auth::TokenExchange.exchange_token`, validate `dest_shop` through `Utils::ShopValidator.sanitize!` (as already done in `migrate_to_expiring_token`, `client_credentials`, and `refresh_access_token`) before constructing `shop_session` and issuing the request, e.g.:
```ruby
jwt_payload = ShopifyAPI::Auth::JwtPayload.new(session_token)
dest_shop = Utils::ShopValidator.sanitize!(jwt_payload.shop)
```
Additionally, harden `JwtPayload#shop` to strip both `https://` and `http://` schemes, or better, route all consumers of `dest` through `ShopValidator` rather than the raw `gsub`.

### Proof of Concept
1. Construct (or obtain) a session token whose payload has a valid signature (per `Context.api_secret_key`) but a `dest` claim such as `"https://attacker-controlled-host.example"` (rather than a `*.myshopify.com` host) — this requires either compromise/misuse of the signing path or a token issued by a relay that does not itself constrain `dest` to Shopify domains.
2. Call:
```ruby
ShopifyAPI::Auth::TokenExchange.exchange_token(
  session_token: forged_or_relayed_token,
  requested_token_type: ShopifyAPI::Auth::TokenExchange::RequestedTokenType::OFFLINE_ACCESS_TOKEN,
)
```
3. `JwtPayload#shop` returns `"attacker-controlled-host.example"` unchanged [8](#0-7) .
4. `exchange_token` builds `shop_session` with that shop and POSTs a body containing `client_id`/`client_secret` to `https://attacker-controlled-host.example/admin/oauth/access_token` [9](#0-8) , exfiltrating the app's `client_secret` to a non-Shopify host — contrast with `migrate_to_expiring_token`, which would reject such a shop via `ShopValidator.sanitize!` and raise `Errors::InvalidShopError` [3](#0-2) .

### Citations

**File:** lib/shopify_api/auth/jwt_payload.rb (L24-45)
```ruby
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

**File:** lib/shopify_api/auth/token_exchange.rb (L103-104)
```ruby
          validated_shop = Utils::ShopValidator.sanitize!(shop)
          shop_session = ShopifyAPI::Auth::Session.new(shop: validated_shop)
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
