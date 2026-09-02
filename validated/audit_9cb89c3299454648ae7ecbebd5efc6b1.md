## Title
Missing shop-domain validation in `TokenExchange.exchange_token` sends `client_secret` to an unvalidated host derived from the JWT `dest` claim - (File: lib/shopify_api/auth/token_exchange.rb)

### Summary
`ShopifyAPI::Auth::TokenExchange.exchange_token` derives the shop host it POSTs the app's `client_id`/`client_secret` to directly from `ShopifyAPI::Auth::JwtPayload#shop` (the `dest` claim of the session token), with no call to `Utils::ShopValidator.sanitize!`. Every sibling method that builds an outbound request host (`migrate_to_expiring_token` in the same file, `ClientCredentials`, `RefreshToken`, `Clients::Graphql::Storefront`) explicitly validates the shop string with `ShopValidator.sanitize!` before using it to build a URL. `exchange_token` is the one path that skips this validation.

### Finding Description
`exchange_token` does: [1](#0-0) 
It takes `jwt_payload.shop` (i.e. `@dest.gsub("https://", "")` from `lib/shopify_api/auth/jwt_payload.rb`) and passes it unsanitized into `Auth::Session.new(shop: dest_shop)`, which is then used to build the outbound host in `Clients::HttpClient.new(session: shop_session, base_path: "/admin/oauth")`.

By contrast, `migrate_to_expiring_token` (same file) explicitly sanitizes: [2](#0-1) 

The binding this breaks (mapped from the "M-13" bug class of an unvalidated field being trusted for a security-relevant operation) is:
`host that receives the app's client_secret == host validated by ShopValidator`
For `exchange_token` this equality does not hold — the host used equals `jwt_payload.shop` (raw `dest` claim), not a value that has passed through `ShopValidator.sanitize!`.

`JwtPayload` only checks `aud == Context.api_key` and standard `exp`/`nbf` claims; it does not constrain `dest` to a `*.myshopify.com` (or configured internal/spin) shape: [3](#0-2) 

### Impact Explanation
This is categorized as High under the rules ("SSRF with the app's credentials") *if* the `dest` claim can ever contain attacker-influenced content reaching this code path without being re-validated downstream (e.g., a host application that passes a raw, not-yet-fully-verified token through, or any future/alternate token issuance path whose `dest` is not guaranteed to be a Shopify-owned domain). Given the missing defense-in-depth check that every other credential-sending path in this library enforces, the same class of host-confusion bug documented in the analog report (an identity/shape check applied inconsistently across otherwise-equivalent code paths) is present here: the shape of the destination host is asserted in `migrate_to_expiring_token`, `ClientCredentials`, `RefreshToken`, and `Clients::Graphql::Storefront`, but not in `exchange_token`.

### Likelihood Explanation
Low-to-Moderate. Under normal operation, the session token is HS256-signed with `Context.api_secret_key`, so a token with an attacker-chosen `dest` cannot be forged without knowledge of the app's secret. This significantly limits direct exploitability by an unprivileged internet user. However, the missing `ShopValidator.sanitize!` call is a genuine inconsistency versus the rest of the library's credential-sending code paths, and the security guarantee for `dest_shop`'s format rests entirely on trusting the JWT signature/claim shape rather than on an explicit domain-shape check, unlike every comparable method in this codebase.

### Recommendation
Add the same `Utils::ShopValidator.sanitize!(jwt_payload.shop)` call in `exchange_token` that is used in `migrate_to_expiring_token`, so the destination host for the `client_secret`-bearing request is validated consistently, regardless of the trust placed in JWT signature verification.

### Proof of Concept
Not independently reproducible as a live exploit without possession of the app's `api_secret_key` (required to mint a session token with an attacker-chosen `dest`), so this finding is reported as a code-consistency/defense-in-depth gap rather than a demonstrated live compromise:
1. Compare `lib/shopify_api/auth/token_exchange.rb` `exchange_token` (no `ShopValidator` call, uses `jwt_payload.shop` directly) against `migrate_to_expiring_token` in the same file (calls `Utils::ShopValidator.sanitize!(shop)` before use). [4](#0-3) [5](#0-4) 
2. If any code path can supply a `session_token` whose `dest` claim is not itself already constrained to a legitimate Shopify domain shape (e.g. a future integration point, a relaxed signature-verification mode, or reuse of `JwtPayload` outside the exact Shopify Admin session-token issuance flow), `exchange_token` will POST `client_id`/`client_secret` to `https://#{dest_shop}/admin/oauth/access_token` without any shape check, unlike its sibling method.

### Citations

**File:** lib/shopify_api/auth/token_exchange.rb (L39-51)
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

**File:** lib/shopify_api/auth/jwt_payload.rb (L33-51)
```ruby
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

      sig { returns(String) }
      def shop
        @dest.gsub("https://", "")
      end
      alias_method :shopify_domain, :shop
```
