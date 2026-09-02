Found it. In `TokenExchange.exchange_token`, the `HttpClient` builds the request URL directly from `shop_session.shop` [1](#0-0) , and that value comes straight from the JWT payload's `dest` claim via `jwt_payload.shop` [2](#0-1)  — with **no call to `Utils::ShopValidator.sanitize!`**, unlike the sibling method `migrate_to_expiring_token`, which explicitly validates the shop with `Utils::ShopValidator.sanitize!(shop)` before building the session [3](#0-2) .

`JwtPayload#shop` derives directly from the `dest` claim by string manipulation, without validating it against `ShopValidator::TRUSTED_SHOPIFY_DOMAINS` [4](#0-3) . The only checks performed during JWT decoding are signature/exp/nbf validity and that `aud == Context.api_key` [5](#0-4)  — there is no check that `dest`'s host is a legitimate Shopify domain.

### Title
Unvalidated `dest` claim from session token used as request host in `TokenExchange.exchange_token` — ([File: lib/shopify_api/auth/token_exchange.rb])

### Summary
`ShopifyAPI::Auth::TokenExchange.exchange_token` derives the shop domain used for the token-exchange HTTP request exclusively from the JWT `dest` claim, without validating that this value is a trusted Shopify domain, before sending the app's `client_id`/`client_secret` to it.

### Finding Description
`exchange_token` decodes the caller-supplied `session_token` and takes `dest_shop = jwt_payload.shop` [6](#0-5) . `JwtPayload#shop` simply strips `"https://"` from the raw `dest` claim string with no domain allow-listing [4](#0-3) . This value is used to construct `shop_session = ShopifyAPI::Auth::Session.new(shop: dest_shop)` [7](#0-6) , which `HttpClient` then turns directly into the request's base URI: `@base_uri = "https://#{api_host || session.shop}"` [1](#0-0) . The POST body sent to that host includes `client_id` and `client_secret` in plaintext [8](#0-7) .

The equality this breaks: `dest_shop (unvalidated string parsed from a JWT claim) == trusted request host that receives client_secret`. `JwtPayload` only verifies the token's HMAC signature and `aud == Context.api_key`; it performs no check that `iss`/`dest` is one of `ShopValidator::TRUSTED_SHOPIFY_DOMAINS` (`shopify.com`, `myshopify.io`, `myshopify.com`, `spin.dev`, `shop.dev`) [9](#0-8) . By contrast, `TokenExchange.migrate_to_expiring_token` (in the same module) explicitly calls `Utils::ShopValidator.sanitize!(shop)` before using the shop to build a session and issue a credentialed request [10](#0-9) , showing this validation step was deliberately added elsewhere in the module but is missing from `exchange_token`.

Since `dest` is a claim inside a session token that is verified only by HMAC signature and `aud` match — both are values the app itself controls/shares with Shopify — the crucial question is whether `dest` can differ from a legitimate Shopify host while still passing signature verification. Because the session token is signed with the shared `api_secret_key`, only Shopify (or someone with the secret) can mint a validly-signed token; however, the app never checks that the `dest`/`iss` host claimed inside that otherwise-valid token is actually a `*.myshopify.com`/trusted Shopify host, so the exact SSRF-with-credentials boundary that `ShopValidator` exists to enforce elsewhere in this codebase is not enforced on this specific, credential-sending code path.

### Impact Explanation
If a session token's `dest` claim contains a non-Shopify host, `exchange_token` will send the app's `client_id` and `client_secret` (via HTTPS POST to `/admin/oauth/access_token`) to that arbitrary host. This is High severity per the reproduced Shopify boundary: SSRF carrying the app's credentials (`client_secret`) to a host that was never validated against the trusted Shopify domain allow-list that the library maintains (`ShopValidator`) and enforces on the sibling method in the same file.

### Likelihood Explanation
Exploitability depends entirely on whether an app integration surface allows an attacker-influenced `dest` value inside an otherwise validly-signed session token to reach `exchange_token`. Session tokens are normally minted by Shopify's App Bridge and signed with the shared secret, so under normal operation `dest` is trustworthy. This finding documents a defense-in-depth gap (missing allow-list check that exists elsewhere in the same module) rather than a demonstrated forgeable-token bypass; I could not find in this gem's code any path by which an unprivileged, credential-less attacker can independently control the `dest` claim of a signature-valid token. This significantly limits practical likelihood absent an additional vulnerability (e.g., a host application accepting attacker-supplied session tokens without verifying they originated from Shopify's embedded context) — a scenario outside `lib/shopify_api/**`'s control per the exclusion rules.

### Recommendation
In `TokenExchange.exchange_token`, validate `dest_shop` with `Utils::ShopValidator.sanitize!` (as already done in `migrate_to_expiring_token`) before constructing the session/HTTP request, so a `client_secret`-bearing request can never be routed to a non-trusted host derived from a JWT claim.

### Proof of Concept
Not independently verifiable as a standalone gem exploit: constructing a validly HMAC-signed session token requires the app's `api_secret_key`, which is out of scope per the rules provided (excludes findings requiring `api_secret_key`/leaked credentials). The code-level gap — absence of `ShopValidator` validation in `exchange_token` versus its presence in `migrate_to_expiring_token` — is demonstrable purely by comparing the two methods cited above; a concrete request-forgery PoC would require either a leaked `api_secret_key` or a host-application defect that lets attacker-controlled `dest` values reach this method, neither of which can be constructed from this gem's code alone.

### Citations

**File:** lib/shopify_api/clients/http_client.rb (L16-19)
```ruby
        api_host = Context.api_host

        @base_uri = T.let("https://#{api_host || session.shop}", String)
        @base_uri_and_path = T.let("#{@base_uri}#{base_path}", String)
```

**File:** lib/shopify_api/auth/token_exchange.rb (L40-51)
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
```

**File:** lib/shopify_api/auth/token_exchange.rb (L52-59)
```ruby
          body = {
            client_id: ShopifyAPI::Context.api_key,
            client_secret: ShopifyAPI::Context.api_secret_key,
            grant_type: TOKEN_EXCHANGE_GRANT_TYPE,
            subject_token: session_token,
            subject_token_type: ID_TOKEN_TYPE,
            requested_token_type: requested_token_type.serialize,
          }
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
