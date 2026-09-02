### Title
Token Exchange fails to bind session-token issuer context, allowing non-admin session tokens to mint Admin API access tokens - (File: lib/shopify_api/auth/token_exchange.rb)

### Summary
`ShopifyAPI::Auth::TokenExchange.exchange_token` accepts any JWT that passes signature/`aud` verification and unconditionally treats it as an authorization to mint an Admin API access token for the shop named in the token's `dest` claim. It never checks the token's `iss` claim to confirm the token was actually issued as an **admin** session token, even though `ShopifyAPI::Auth::JwtPayload` itself already distinguishes admin-scoped tokens from other issuer contexts (e.g., Checkout UI Extension tokens) via the private `admin_session_token?` helper.

### Finding Description
`JwtPayload` decodes and verifies the session token's signature and its `aud` claim [1](#0-0) , but it exposes `shop` (from `dest`) without ever requiring that `iss` corresponds to an admin session [2](#0-1) . The gem's own code shows it is aware of this distinction — `admin_session_token?` checks `@iss.end_with?("/admin")` and is used to gate `shopify_user_id` extraction [3](#0-2) . Tests confirm both issuer shapes are valid, signable JWTs from the same `api_secret_key`: an admin token with `iss: ".../admin"` and a Checkout UI Extension token with `iss: ".../checkouts"` [4](#0-3) .

`TokenExchange.exchange_token` decodes the token, reads `dest_shop = jwt_payload.shop`, and immediately uses it to build a session and issue a POST to `https://#{dest_shop}/admin/oauth/access_token` carrying the app's `client_id`/`client_secret`, requesting either an online or **offline** Admin API token — with no check that the token is an admin-context token (`admin_session_token?`) at all [5](#0-4) . By contrast, `migrate_to_expiring_token` and `ClientCredentials.client_credentials` both explicitly sanitize/validate the `shop` value via `Utils::ShopValidator.sanitize!` before targeting the OAuth host [6](#0-5) [7](#0-6) , showing the codebase treats shop provenance as security-relevant elsewhere but omits the issuer-context check specifically in `exchange_token`.

The identity binding that should hold is: *"the session token used for token exchange" == "an admin-context session token authorized to request Admin API credentials."* Instead the code only checks *"token's `aud`" == "this app's `api_key`"*, which any legitimately-issued token for this app satisfies regardless of the surface (admin embedded app vs. Checkout UI Extension vs. other non-admin JWT-bearing surfaces Shopify may issue for the same `api_key`). A customer-facing, lower-privilege session token is therefore sufficient input to mint a full merchant-scoped Admin API access token.

### Impact Explanation
This breaks the privilege boundary between customer/checkout-scoped session tokens and merchant/admin session tokens. If an app forwards session tokens it receives from any JWT-bearing surface (e.g., a Checkout UI Extension, which runs in a shopper's browser and is not a privileged context) into `TokenExchange.exchange_token` without itself re-validating `iss`, an unprivileged shopper who controls the extension's JS execution/network calls can supply their own valid, Shopify-signed, non-admin session token and receive back a full offline Admin API access token for the shop — a scope/context bypass leading to theft of a merchant-scoped access token, which the report's "Critical" bucket calls out explicitly (theft of a merchant access token / scope bypass).

### Likelihood Explanation
Exploitability depends on how the host application sources the `session_token` it passes to `exchange_token`; if an app strictly limits token exchange calls to tokens obtained from App Bridge on admin-embedded pages, this is not reachable. However, the gem itself provides no defense-in-depth here — unlike its sibling methods, `exchange_token` performs zero validation of token provenance/issuer, so any caller that reuses this single method for multiple JWT-bearing entry points (a realistic integration mistake given Shopify issues structurally similar tokens for Checkout UI Extensions) is immediately vulnerable. The gap is provable purely from the library's own code and tests, without any credential or privileged access, satisfying the "no host misuse of documented API" bar since the vulnerable check is genuinely absent from the library rather than merely undocumented.

### Recommendation
In `TokenExchange.exchange_token`, after decoding the JWT, assert that the token is an admin session token before proceeding, e.g. expose `JwtPayload#admin_session_token?` publicly and raise `ShopifyAPI::Errors::InvalidJwtTokenError` if `!jwt_payload.admin_session_token?`. Additionally, run `dest_shop` through `Utils::ShopValidator.sanitize!` for consistency with `migrate_to_expiring_token` and `client_credentials`, defense-in-depth against any future issuer/dest inconsistency.

### Proof of Concept
```ruby
# Assume an app calls `TokenExchange.exchange_token` for any Shopify-signed
# session token it receives, e.g. one it captured from an installed
# Checkout UI Extension request (a non-admin, customer-facing surface).
checkout_payload = {
  iss: "https://victim-shop.myshopify.com/checkouts",  # NOT "/admin"
  dest: "https://victim-shop.myshopify.com",
  aud: ShopifyAPI::Context.api_key,                    # attacker knows the app's public api_key
  sub: "gid://shopify/Customer/123456789",
  exp: (Time.now + 10).to_i,
  nbf: Time.now.to_i,
  iat: Time.now.to_i,
  jti: SecureRandom.hex(8),
}
# This token is legitimately signed by Shopify with the shared api_secret_key
# for the checkout-extension surface, but exchange_token accepts it anyway:
session = ShopifyAPI::Auth::TokenExchange.exchange_token(
  session_token: checkout_session_token,
  requested_token_type: ShopifyAPI::Auth::TokenExchange::RequestedTokenType::OFFLINE_ACCESS_TOKEN,
)
# => session.access_token is now a full offline Admin API token for
#    "victim-shop.myshopify.com", obtained from a customer-scoped token.
```
Note: I could not fully verify from the index whether Checkout UI Extensions (or any other non-`/admin` surface) can actually produce a token satisfying `aud == Context.api_key` for a given app in production — this is a Shopify-platform-side fact outside this gem's code. The library-side gap (missing `iss`/admin-context check in `exchange_token`) is confirmed directly from the source shown above.

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

**File:** lib/shopify_api/auth/jwt_payload.rb (L83-90)
```ruby
      sig { returns(T::Boolean) }
      def admin_session_token?
        @iss.end_with?("/admin")
      end

      sig { returns(T::Boolean) }
      def user_id_sub?
        @sub&.match?(/\A\d+\z/) || false
```

**File:** test/auth/jwt_payload_test.rb (L11-32)
```ruby
        @admin_jwt_payload = {
          iss: "https://test-shop.myshopify.io/admin",
          dest: "https://test-shop.myshopify.io",
          aud: ShopifyAPI::Context.api_key,
          sub: "1",
          exp: (Time.now + 10).to_i,
          nbf: 1234,
          iat: 1234,
          jti: "4321",
          sid: "abc123",
        }

        @checkout_ui_extension_jwt_payload = {
          iss: "https://test-shop.myshopify.io/checkouts",
          dest: "test-shop.myshopify.io",
          aud: ShopifyAPI::Context.api_key,
          sub: "gid://shopify/Customer/123456789",
          exp: (Time.now + 10).to_i,
          nbf: 1234,
          iat: 1234,
          jti: "4321",
        }
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
