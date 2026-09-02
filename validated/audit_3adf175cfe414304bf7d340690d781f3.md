## Finding

### Title
`TokenExchange.exchange_token` accepts non-admin (checkout) session tokens and exchanges them for full merchant Admin access tokens - ([File: lib/shopify_api/auth/token_exchange.rb])

### Summary
`ShopifyAPI::Auth::TokenExchange.exchange_token` decodes a caller-supplied session token via `JwtPayload` and, as long as the signature and `aud` claim check out, unconditionally forwards it to Shopify's token-exchange endpoint to mint a full Admin API access token for the shop found in the token's `dest` claim. The `iss` claim — which distinguishes an admin-embedded session token (`iss` ends in `/admin`) from a lower-privilege checkout UI extension token (`iss` ends in `/checkouts`) — is parsed but never checked before performing the exchange.

### Finding Description
`JwtPayload#initialize` decodes and verifies the JWT signature and only checks `@aud == Context.api_key`: [1](#0-0) 

It exposes `admin_session_token?` (`iss.end_with?("/admin")`), but that helper is only used internally for `shopify_user_id`, never to gate which flows may consume the token: [2](#0-1) 

The test suite confirms both admin session tokens (`iss: ".../admin"`) and checkout UI extension tokens (`iss: ".../checkouts"`) are valid, supported inputs to this same class, sharing the same `aud` (the app's `api_key`) and signature scheme: [3](#0-2) 

`TokenExchange.exchange_token` takes whatever `JwtPayload` produces — with **no check on `iss`/`admin_session_token?`** — derives `dest_shop`, and immediately uses it to request a full Admin access token, sending the app's `client_secret` along with the caller-supplied `session_token` as `subject_token`: [4](#0-3) 

This is exactly the "JWT claim trusted without being bound" pattern: the `dest`/`aud` claims are verified, but the claim that actually encodes *what kind of principal* issued the token (`iss`, buyer/checkout vs. merchant/admin) is decoded and available (`admin_session_token?`) yet is never bound to the operation being authorized. Every other Admin-privileged flow in this gem that builds a shop-scoped request carrying `client_secret` (`client_credentials.rb`, `refresh_token.rb`, `migrate_to_expiring_token`) additionally passes the shop through `Utils::ShopValidator.sanitize!` as a defense-in-depth check, but `exchange_token`'s only binding on its most sensitive input (the subject token) is signature + audience — not issuer/type.

### Impact Explanation
Checkout UI extension session tokens are handed out by Shopify to **anonymous, unauthenticated buyers** browsing checkout on any shop where the app's checkout extension is installed — this is about as "unprivileged internet user" as it gets. If such a token is captured/used with `exchange_token`, the gem will still attempt (and, absent server-side rejection, succeed in) obtaining a fully privileged merchant Admin API access token (online or offline) for that shop, using the app's `client_secret`. That is authentication bypass / theft of a merchant access token — a Critical-impact outcome per the scope's own definition — reachable purely because this gem's `TokenExchange.exchange_token` never verifies the caller's session token is actually an admin-embedded token before treating its `dest` as an authorization target.

### Likelihood Explanation
Reaching this code path requires only: (1) being any buyer at checkout on a shop with the app's checkout UI extension installed (to obtain a signed checkout session token — no account, no install privileges, no secrets needed), and (2) the host app forwarding a session token it receives to `ShopifyAPI::Auth::TokenExchange.exchange_token` without itself checking token type (which the gem does not require or even flag as necessary, since it exposes `admin_session_token?` but doesn't document that callers must check it before calling `exchange_token`). No leaked credentials, TLS interception, or privileged access are needed — only possession of a validly-signed, low-privilege token that this gem's method treats as fully authorizing an Admin token mint.

### Recommendation
In `TokenExchange.exchange_token`, reject the session token unless `jwt_payload` represents an admin-embedded session (i.e., enforce `admin_session_token?` — or equivalently validate `iss` ends with `/admin`) before deriving `dest_shop` and performing the exchange, mirroring the explicit validation Shopify's own documentation describes for `dest`. Additionally route `dest_shop` through `Utils::ShopValidator.sanitize!` for consistency with `client_credentials`, `refresh_token`, and `migrate_to_expiring_token`.

### Proof of Concept
1. Attacker (an anonymous shopper) loads checkout on `victim-shop.myshopify.com` where the app's checkout UI extension is enabled and obtains a Shopify-signed session token with:
   - `iss: "https://victim-shop.myshopify.com/checkouts"`
   - `dest: "https://victim-shop.myshopify.com"`
   - `aud: <app's api_key>`
   (matches the shape asserted in `test/auth/jwt_payload_test.rb` lines 23-32, `@checkout_ui_extension_jwt_payload`).
2. This token is passed (e.g. by a host app that reuses one "get a token, exchange it" code path for both admin and checkout contexts) to:
   ```ruby
   ShopifyAPI::Auth::TokenExchange.exchange_token(
     session_token: captured_checkout_token,
     requested_token_type: ShopifyAPI::Auth::TokenExchange::RequestedTokenType::OFFLINE_ACCESS_TOKEN,
   )
   ```
3. `JwtPayload.new(session_token)` succeeds (valid signature, valid `aud`); `exchange_token` never checks `iss`, extracts `dest_shop = "victim-shop.myshopify.com"`, and POSTs `{client_id, client_secret, subject_token: captured_checkout_token, grant_type: token-exchange, requested_token_type: offline-access-token}` to `https://victim-shop.myshopify.com/admin/oauth/access_token` (`lib/shopify_api/auth/token_exchange.rb` lines 51-74).
4. If Shopify's backend accepts the exchange (nothing in this gem prevents attempting it, and the gem provides no client-side check to stop it), the response is parsed into a full `ShopifyAPI::Auth::Session` with a merchant Admin access token, returned to the caller.

### Citations

**File:** lib/shopify_api/auth/jwt_payload.rb (L33-45)
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
```

**File:** lib/shopify_api/auth/jwt_payload.rb (L83-86)
```ruby
      sig { returns(T::Boolean) }
      def admin_session_token?
        @iss.end_with?("/admin")
      end
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

**File:** lib/shopify_api/auth/token_exchange.rb (L29-51)
```ruby
        def exchange_token(session_token:, requested_token_type:, shop: nil)
          unless ShopifyAPI::Context.setup?
            raise ShopifyAPI::Errors::ContextNotSetupError,
              "ShopifyAPI::Context not setup, please call ShopifyAPI::Context.setup"
          end
          raise ShopifyAPI::Errors::UnsupportedOauthError,
            "Cannot perform OAuth Token Exchange for private apps." if ShopifyAPI::Context.private?
          raise ShopifyAPI::Errors::UnsupportedOauthError,
            "Cannot perform OAuth Token Exchange for non embedded apps." unless ShopifyAPI::Context.embedded?

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
