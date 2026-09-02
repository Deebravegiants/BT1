I found a concrete instance of the identity-binding pattern the report describes: `exchange_token` in `token_exchange.rb` derives the shop it talks to (and sends the app's `client_secret` to) from the JWT's `dest` claim without ever passing it through `Utils::ShopValidator`, unlike every other credential-issuing path in this gem (`migrate_to_expiring_token`, `client_credentials.rb`, `refresh_token.rb`, `graphql/storefront.rb`), which all call `ShopValidator.sanitize!`.

### Title
Unsanitized JWT `dest` claim used as request host for client_secret-bearing token exchange - (File: lib/shopify_api/auth/token_exchange.rb)

### Summary
`TokenExchange.exchange_token` builds the host it sends the app's `client_id`/`client_secret` to directly from the `dest` claim of an attacker-suppliable JWT, without validating that the resulting domain is a trusted Shopify domain. Every sibling method in the same file, and every other OAuth entry point in this gem, funnels the shop value through `Utils::ShopValidator.sanitize!` before using it to build a request host — this one path skips that check.

### Finding Description
`exchange_token` decodes the session token into a `JwtPayload`, whose `shop` accessor simply strips `"https://"` from the `dest` claim with no additional formatting or domain-trust check: [1](#0-0) 

`exchange_token` then takes that raw value and uses it, unsanitized, to build the `Session`/`HttpClient` that receives the `client_secret`: [2](#0-1) 

`Clients::HttpClient` resolves the request host from `session.shop`, so whatever string comes out of `dest_shop` becomes part of the URL that receives the POST body containing `client_id`/`client_secret`.

Contrast this with the sibling method in the very same file, `migrate_to_expiring_token`, which passes `shop` through `Utils::ShopValidator.sanitize!` before building the session/host: [3](#0-2) 

and the same pattern is followed by `client_credentials.rb`, `refresh_token.rb`, and `graphql/storefront.rb` (all matched by the earlier `ShopValidator` grep). `ShopValidator.sanitize!` exists specifically to reject domains that are not `myshopify.com`/`myshopify.io`/`spin.dev`/`shop.dev`/`shopify.com` subdomains, guarding exactly the "host that receives the `client_secret`" boundary described in the rules: [4](#0-3) [5](#0-4) 

The binding that should hold is:
`host that receives client_secret == a ShopValidator-trusted Shopify domain`

In `exchange_token` this equality is never enforced — the right-hand side is simply "whatever string is in the JWT's `dest` claim," and the JWT's own validation (`JwtPayload#initialize`) only checks `aud == Context.api_key`, `exp`/`nbf`, and signature; it never checks that `dest`/`iss` is a Shopify domain: [6](#0-5) 

### Impact Explanation
This matches the High-severity category "SSRF with the app's credentials." If a session token whose `dest` claim is attacker-influenced can be presented to `exchange_token` (e.g., an app accepting a `shopify_id_token`/session token that is not itself independently confirmed to originate for a specific, expected shop before calling `exchange_token`), the gem will send the app's `client_id` and `client_secret` to a host derived from that unchecked claim, whereas every other similar flow in the codebase explicitly guards against exactly this by calling `ShopValidator.sanitize!`.

### Likelihood Explanation
Exploitation requires a validly-signed JWT (HS256 with `Context.api_secret_key`) whose `aud` matches the app's `api_key` but whose `dest`/`iss` is not a genuine Shopify domain. In the normal flow, only Shopify issues such tokens for real shops, so this is not trivially exploitable without also controlling how the token is produced/relayed to the host app. This is why it's flagged as an inconsistency/gap relative to the gem's own established pattern rather than a fully self-contained exploit chain purely within this gem — I could not find, within `lib/shopify_api/**` (excluding rest resources), a path that lets an unprivileged internet user mint or relay an arbitrary-`dest` token without already possessing the app's secret. I want to be explicit about this uncertainty rather than overstate exploitability.

### Recommendation
In `TokenExchange.exchange_token`, sanitize `dest_shop` through `Utils::ShopValidator.sanitize!(dest_shop)` before constructing `shop_session`/`Session.from`, mirroring `migrate_to_expiring_token` and the other OAuth credential-exchange paths, so the host that receives `client_id`/`client_secret` is always constrained to a trusted Shopify domain rather than trusting the raw JWT `dest` claim.

### Proof of Concept
Not fully constructible within this gem alone: it requires a validly HMAC/HS256-signed JWT for the app (`aud == Context.api_key`) whose `dest` value is a non-Shopify domain. Given such a token:
```ruby
ShopifyAPI::Auth::TokenExchange.exchange_token(
  session_token: token_with_dest_set_to_non_shopify_host,
  requested_token_type: ShopifyAPI::Auth::TokenExchange::RequestedTokenType::ONLINE_ACCESS_TOKEN,
)
```
would cause `Clients::HttpClient` to POST the body containing `client_id`/`client_secret` to `https://#{dest_shop}/admin/oauth/access_token`, i.e., to the attacker-controlled host, unlike `migrate_to_expiring_token`, which would reject such a shop via `ShopValidator.sanitize!`.

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

**File:** lib/shopify_api/utils/shop_validator.rb (L56-64)
```ruby
        def sanitize!(shop, myshopify_domain: nil)
          host = sanitize_shop_domain(shop, myshopify_domain: myshopify_domain)
          if host.nil? || host.empty?
            raise Errors::InvalidShopError,
              "shop must be a trusted Shopify domain (see ShopValidator::TRUSTED_SHOPIFY_DOMAINS), got: #{shop.inspect}"
          end

          host
        end
```
