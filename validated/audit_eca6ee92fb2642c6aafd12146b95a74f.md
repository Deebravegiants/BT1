### Title
Token Exchange trusts any JWT signed with the app secret as an admin session token, allowing a checkout/customer-scoped session token to be exchanged for a merchant access token - (File: `lib/shopify_api/auth/token_exchange.rb`)

### Summary
`TokenExchange.exchange_token` derives the target shop and authorizes a token exchange request purely from the `dest` claim of a caller-supplied JWT, without ever checking the `iss` claim. `ShopifyAPI::Auth::JwtPayload` computes `shop` from `dest` alone [1](#0-0)  and only uses `iss.end_with?("/admin")` internally to gate the unrelated `shopify_user_id` helper [2](#0-1)  — it is never enforced as a precondition for treating the token as a legitimate admin session token.

### Finding Description
The gem's own tests demonstrate two distinct JWT "flavors" signed with the same `Context.api_secret_key`: an admin session token with `iss` ending in `/admin` [3](#0-2)  and a checkout UI extension token with `iss` ending in `/checkouts`, representing a customer's identity in a storefront checkout session rather than a merchant/admin session [4](#0-3) .

`TokenExchange.exchange_token` accepts a `session_token:` argument, constructs a `JwtPayload`, and uses `jwt_payload.shop` (i.e., the `dest` claim) as the shop to exchange with — with no check that `jwt_payload` actually is an admin-issued token (`iss` ending in `/admin`): [5](#0-4) 

Because `JWT_LEEWAY`/`decode_token` only validates signature, expiry and the `aud` (api_key) claim [6](#0-5) , any token minted by Shopify for the app — including a checkout-extension identity token scoped to an unauthenticated/low-privilege buyer session — passes validation and is treated as equivalent to an admin session token. The `exchange_token` flow then requests an `OFFLINE_ACCESS_TOKEN` (a merchant-level, long-lived offline access token) for `dest_shop`, using the app's `client_id`/`client_secret` [7](#0-6) .

This breaks the intended identity binding: `iss` (token issuance context/audience — "checkout extension" vs. "admin") must equal "admin" before the token is used to authorize an offline/merchant-scoped grant. The equality that should be enforced and is not:
`jwt_payload.iss.end_with?("/admin") == true` before allowing `TokenExchange.exchange_token` to proceed, especially for `OFFLINE_ACCESS_TOKEN` requests.

### Impact Explanation
If Shopify's token-exchange endpoint honors the `subject_token`'s scope/issuer distinction server-side, this finding may be non-exploitable end-to-end (defense may live entirely on Shopify's server). However, from a library-correctness standpoint, this gem — which is the only enforcement point on the app side — performs no client-side validation that the presented token is actually an admin session token before spending the app's `client_secret` to request an offline access token for that shop. This matches the "Scope or expiry check bypass" impact category: the library answers permissively, trusting a JWT claim (`dest`) without binding it to another claim (`iss`) that establishes the token's authorization scope. If any customer-facing or lower-privileged Shopify JWT issuance context is ever accepted server-side for token exchange (or if server-side validation is weaker than assumed), this client-side gap directly enables a customer/checkout-scoped identity to obtain merchant-level offline access on behalf of the app.

### Likelihood Explanation
Requires an attacker to obtain a checkout/customer-scoped session token for a shop (these are issued during storefront checkout flows and could be more accessible to lower-privileged parties than merchant admin sessions) and pass it to the app's `exchange_token` call. Likelihood depends on host-app integration details and Shopify's own server-side enforcement, which cannot be verified from this gem's code alone.

### Recommendation
In `TokenExchange.exchange_token`, validate that `jwt_payload.iss` ends with `/admin` (i.e., reuse/expose the existing private `admin_session_token?` check in `JwtPayload`) before proceeding, and raise `ShopifyAPI::Errors::InvalidJwtTokenError` otherwise — mirroring the existing `aud` check already performed in `JwtPayload#initialize` [8](#0-7) .

### Proof of Concept
1. Obtain (or have App Bridge issue) a valid checkout UI extension token with shape `{ iss: "https://shop.myshopify.io/checkouts", dest: "shop.myshopify.io", aud: <api_key>, sub: "gid://shopify/Customer/123", exp: ..., ... }`, signed with the app's `api_secret_key` (as shown in the test fixture) [4](#0-3) .
2. Call `ShopifyAPI::Auth::TokenExchange.exchange_token(session_token: checkout_token, requested_token_type: RequestedTokenType::OFFLINE_ACCESS_TOKEN)`.
3. Observe that `JwtPayload.new(session_token)` succeeds (no `iss` check) and `dest_shop = jwt_payload.shop` resolves to `"shop.myshopify.io"` [9](#0-8) , and the gem proceeds to request an offline (merchant) access token for that shop using the app's `client_secret` [10](#0-9) .

Note: full exploitability depends on whether Shopify's token-exchange endpoint itself rejects non-admin `subject_token`s for `OFFLINE_ACCESS_TOKEN`/`ONLINE_ACCESS_TOKEN` requests — this cannot be confirmed from the gem's code alone, since that enforcement (if any) is server-side.

### Citations

**File:** lib/shopify_api/auth/jwt_payload.rb (L43-45)
```ruby
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

**File:** lib/shopify_api/auth/jwt_payload.rb (L53-56)
```ruby
      sig { returns(T.nilable(Integer)) }
      def shopify_user_id
        @sub.to_i if user_id_sub? && admin_session_token?
      end
```

**File:** lib/shopify_api/auth/jwt_payload.rb (L76-81)
```ruby
      sig { params(token: String, api_secret_key: String).returns(T::Hash[String, T.untyped]) }
      def decode_token(token, api_secret_key)
        JWT.decode(token, api_secret_key, true, leeway: JWT_LEEWAY, algorithm: "HS256")[0]
      rescue JWT::DecodeError => err
        raise ShopifyAPI::Errors::InvalidJwtTokenError, "Error decoding session token: #{err.message}"
      end
```

**File:** test/auth/jwt_payload_test.rb (L11-21)
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
```

**File:** test/auth/jwt_payload_test.rb (L23-32)
```ruby
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
