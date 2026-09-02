### Title
Session-token type not bound before token exchange — `dest` claim trusted without validating `iss` is an admin session token - ([File: lib/shopify_api/auth/jwt_payload.rb])

### Summary
`ShopifyAPI::Auth::JwtPayload` verifies a session token's signature and its `aud` claim, but never checks that the `iss` claim identifies an **admin** session token before the token's `dest` claim is used to select the shop for `ShopifyAPI::Auth::TokenExchange.exchange_token`. The gem's own test fixtures show that JWTs with `iss` ending in `/checkouts` (buyer/checkout-extension tokens) decode successfully and expose `dest`/`shop` identically to an admin token, since only `aud == Context.api_key` is enforced.

### Finding Description
`JwtPayload#initialize` decodes any HS256 token signed with the app's own secret and only enforces: [1](#0-0) 
No check binds `iss` (the token's issuing context — `/admin` for App-Bridge admin session tokens vs. `/checkouts` for buyer checkout-extension tokens, as seen in the test fixtures) to the usage of `dest`: [2](#0-1) 
The only place `iss` is inspected at all is `admin_session_token?`, and it is used solely to gate `shopify_user_id`, not to gate whether the token is acceptable for token exchange: [3](#0-2) 

`TokenExchange.exchange_token` then takes *any* JWT that passes this decode and uses its `dest` claim directly to pick the shop and to build the token-exchange request body, without checking `iss.end_with?("/admin")`: [4](#0-3) 

The equality the gem should enforce is:
`accepted_token.iss ends with "/admin"` == `token used to request an admin (online/offline) access token`

Instead, the gem enforces only:
`accepted_token.aud == Context.api_key`

This means any Shopify-issued, correctly-signed JWT for the app's `client_id` — regardless of whether it was minted for the Admin embedded app context or for a buyer-facing context such as a checkout UI extension (`iss: ".../checkouts"`, `sub: "gid://shopify/Customer/..."`, as shown in the gem's own tests) — is accepted identically and its `dest` is trusted to select the shop for an **offline** or **online admin access-token exchange**.

### Impact Explanation
This breaks the binding between "the session token is an admin/merchant-scoped session token" and "the app performs an admin OAuth token exchange for that shop." If an app also issues checkout-extension or other buyer-scoped session tokens sharing the same `client_id`/`aud`, an unprivileged storefront customer (no merchant credentials required) could present their own legitimately-issued, but buyer-scoped, session token to the app's token-exchange endpoint. The gem itself performs no `iss`/scope binding to reject it, and will issue the request to Shopify's `/admin/oauth/access_token` asking for an **offline admin access token** for that shop using `subject_token: session_token`. Whether this ultimately succeeds depends on Shopify's server-side token-exchange enforcement (outside this gem), but the gem's client-side validation — the only defense this library provides — does not enforce the scope/session-type check at all, which is the class of "scope or expiry check answers permissively" called out in the rules.

### Likelihood Explanation
Any embedded app that also uses checkout UI extensions, or any context where the app's `client_id` signs multiple token audiences, is affected. Obtaining a legitimately signed, non-admin session token requires no privileges beyond being an ordinary shopper — this is the "unprivileged internet user" case. The only barrier to full exploitation is Shopify's backend also enforcing `iss`; this cannot be verified from the gem alone, so likelihood is assessed as Medium given the missing client-side check.

### Recommendation
In `ShopifyAPI::Auth::JwtPayload`, require and expose that the token is an admin session token (`iss.end_with?("/admin")`) as a hard precondition before it is used in `TokenExchange.exchange_token`, e.g. raise `InvalidJwtTokenError` in `exchange_token` (or in `JwtPayload#initialize`, via an explicit `token_type:` parameter) if `iss` does not match the expected `/admin` issuer for the shop in `dest`. This restores the equality between "claim trusted for `dest`" and "claim proves admin-session provenance."

### Proof of Concept
1. Attacker is an ordinary buyer on `victim-shop.myshopify.com` and loads a checkout UI extension that the target app also registers; App Bridge/Shopify issues them a validly-signed session token with:
   `iss: "https://victim-shop.myshopify.com/checkouts"`, `dest: "https://victim-shop.myshopify.com"`, `aud: <app's client_id>`, `sub: "gid://shopify/Customer/123"` — matching the shape validated in the gem's own test fixture [5](#0-4) .
2. Attacker submits this token to the app's authentication endpoint as if it were an admin session token.
3. The app calls `ShopifyAPI::Auth::TokenExchange.exchange_token(session_token: token, requested_token_type: OFFLINE_ACCESS_TOKEN)`.
4. `JwtPayload.new(token)` succeeds because only `aud` is checked [1](#0-0) ; `dest_shop` is extracted and used to request an offline admin access token for `victim-shop.myshopify.com` [6](#0-5) , with no check that the token actually came from an admin (`/admin`-issued) session.

Note: I could not verify from this repository alone whether Shopify's server-side `/admin/oauth/access_token` endpoint independently rejects non-admin `subject_token`s; that verification would require external/Shopify-side testing outside this gem's index.

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

**File:** lib/shopify_api/auth/jwt_payload.rb (L83-86)
```ruby
      sig { returns(T::Boolean) }
      def admin_session_token?
        @iss.end_with?("/admin")
      end
```

**File:** lib/shopify_api/auth/token_exchange.rb (L39-58)
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
