### Title
`TokenExchange.exchange_token` fails to validate the JWT `iss` claim, allowing a non-admin session token to be exchanged for a merchant access token — ([File: lib/shopify_api/auth/token_exchange.rb])

### Summary
`ShopifyAPI::Auth::JwtPayload` decodes and cryptographically verifies session tokens (`aud`, `exp`, `nbf`, signature), but it exposes an internal notion of token provenance — `admin_session_token?`, derived from the `iss` claim — that is **never enforced** by any of the public consumers of `JwtPayload`. In particular, `ShopifyAPI::Auth::TokenExchange.exchange_token` takes any successfully-decoded JWT and unconditionally treats its `dest` claim as the shop to exchange an **admin, merchant-scoped access token** for, regardless of whether the token was actually issued for the admin context (`iss` ending in `/admin`) or for a completely different, lower-privilege context such as a Checkout UI Extension (`iss` ending in `/checkouts`).

### Finding Description
`JwtPayload#initialize` binds only `aud` (must equal `Context.api_key`) as an identity check: [1](#0-0) 

It separately computes `admin_session_token?` from the `iss` claim, and uses it internally only to gate `shopify_user_id`: [2](#0-1) [3](#0-2) 

The test suite confirms that Checkout UI Extension tokens are structurally different (`iss` ends with `/checkouts`, no `sid`) but are otherwise valid, well-formed, correctly-signed JWTs that pass `JwtPayload.new` without error: [4](#0-3) 

`TokenExchange.exchange_token` uses `jwt_payload.shop` (i.e., `dest`) directly as the shop identity for an admin OAuth token-exchange request that includes the app's `client_secret`, without ever checking `admin_session_token?`: [5](#0-4) 

Notably, the sibling method `migrate_to_expiring_token` in the same file *does* apply `Utils::ShopValidator.sanitize!` to its shop input, showing that domain/identity validation is an established pattern in this codebase that was simply omitted for the JWT-derived shop in `exchange_token`: [6](#0-5) 

`Utils::SessionUtils.session_id_from_shopify_id_token` has the same gap — it derives a session id from any decodable token without checking `admin_session_token?`: [7](#0-6) 

**The broken identity binding, expressed as an equality that should hold but doesn't:**
`token.iss(context bound to admin session)` == `token.iss(actually enforced by exchange_token before granting an admin access token)`

The `iss` claim exists precisely to distinguish the *context/privilege level* a session token was minted for (admin surface vs. checkout/customer surface), but nothing in `TokenExchange` or `SessionUtils` binds that claim to the privileged operation (issuing an OAuth admin access token, or generating a session id used for admin API authorization) being performed.

### Impact Explanation
This is a scope-check bypass (rules: "scope or expiry check bypass" — High). Checkout UI Extension tokens are issued to run in the buyer/checkout surface and are not intended to authorize merchant Admin API access. Because `exchange_token` performs no check that the presented token is an admin session token, a token that was only ever meant for the checkout extension context can be used to drive the library's token-exchange flow and cause the host app to be granted (and store) an Admin API access token for the shop identified in `dest`. Any host application that relies on this gem's `TokenExchange.exchange_token` as its sole authorization gate (as the docs recommend) inherits this bypass without further code of their own.

### Likelihood Explanation
Likelihood is moderate: it requires an attacker to obtain a legitimately-issued (Shopify-signed) session token from a lower-privilege surface (e.g. a checkout UI extension execution context, which by design runs partially in less trusted environments and can be more exposed than the admin embedded iframe) and submit it to the app's token-exchange endpoint that wraps `TokenExchange.exchange_token`. No possession of `api_secret_key` or other privileged credential is needed — only a token minted for a different, lower-trust surface of the same app.

### Recommendation
- In `JwtPayload`, make `admin_session_token?` a public, documented API, and require callers of privileged operations to check it.
- In `TokenExchange.exchange_token` (and `Utils::SessionUtils.session_id_from_shopify_id_token` when deriving admin session ids), raise `Errors::InvalidJwtTokenError` unless `jwt_payload.iss` indicates the token was issued for the admin session context, before using `dest`/`shop` to request or bind an access token.
- Apply the same `Utils::ShopValidator.sanitize!` pattern already used in `migrate_to_expiring_token` to the JWT-derived shop in `exchange_token`, so all methods that build an OAuth request host follow one consistent identity-binding rule.

### Proof of Concept
1. Obtain (or have a malicious actor supply via a checkout UI extension execution context) a validly-signed Shopify ID token whose payload matches the shape in `test/auth/jwt_payload_test.rb` lines 23-32 (`iss: ".../checkouts"`, `aud: <app's client_id>`).
2. Call `ShopifyAPI::Auth::TokenExchange.exchange_token(session_token: checkout_token, requested_token_type: ...)`.
3. Observe that `JwtPayload.new(checkout_token)` succeeds (no `iss`/context check performed), `dest_shop` is extracted, and the gem proceeds to POST the app's `client_id`/`client_secret` to `https://{dest_shop}/admin/oauth/access_token` on behalf of a token that was never intended to authorize merchant Admin API access — with no library-level rejection based on token provenance.

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

**File:** lib/shopify_api/auth/jwt_payload.rb (L53-56)
```ruby
      sig { returns(T.nilable(Integer)) }
      def shopify_user_id
        @sub.to_i if user_id_sub? && admin_session_token?
      end
```

**File:** lib/shopify_api/auth/jwt_payload.rb (L83-86)
```ruby
      sig { returns(T::Boolean) }
      def admin_session_token?
        @iss.end_with?("/admin")
      end
```

**File:** test/auth/jwt_payload_test.rb (L154-174)
```ruby
      def test_decode_jwt_payload_coming_from_checkout_ui_extension
        payload = @checkout_ui_extension_jwt_payload.dup
        jwt_token = JWT.encode(payload, ShopifyAPI::Context.api_secret_key, "HS256")
        decoded = ShopifyAPI::Auth::JwtPayload.new(jwt_token)
        assert_equal(payload,
          {
            iss: decoded.iss,
            dest: decoded.dest,
            aud: decoded.aud,
            sub: decoded.sub,
            exp: decoded.exp,
            nbf: decoded.nbf,
            iat: decoded.iat,
            jti: decoded.jti,
          })

        assert_equal(decoded.expire_at, @checkout_ui_extension_jwt_payload[:exp])
        assert_equal("test-shop.myshopify.io", decoded.shopify_domain)
        assert_equal("test-shop.myshopify.io", decoded.shop)
        assert_nil(decoded.shopify_user_id)
      end
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

**File:** lib/shopify_api/utils/session_utils.rb (L45-56)
```ruby
        def session_id_from_shopify_id_token(id_token:, online:)
          raise Errors::MissingJwtTokenError, "Missing Shopify ID Token" if id_token.nil? || id_token.empty?

          payload = Auth::JwtPayload.new(id_token)
          shop = payload.shop

          if online
            jwt_session_id(shop, T.must(payload.sub))
          else
            offline_session_id(shop)
          end
        end
```
