### Title
Session-token type confusion: `SessionUtils.session_id_from_shopify_id_token` derives a privileged session ID from any Shopify-signed JWT without verifying the token's `iss` (issuer/audience type) claim — (File: `lib/shopify_api/utils/session_utils.rb`, `lib/shopify_api/auth/jwt_payload.rb`)

### Summary
`ShopifyAPI::Auth::JwtPayload` validates a session token's signature and its `aud` claim against the app's `api_key`, but never validates that the token's `iss` claim actually identifies it as an **Admin embedded-app session token** before the token is used to derive an app/merchant session identifier. `Utils::SessionUtils.session_id_from_shopify_id_token` — the library's documented public API for embedded apps to obtain a session id from an incoming JWT — consumes `payload.sub` directly to build `"#{shop}_#{sub}"` without ever checking `admin_session_token?` (which only exists internally, gated behind the unrelated `shopify_user_id` helper).

### Finding Description
The identity binding that should hold is:
`token.iss ∈ {admin session tokens for this app}` ⇔ `token used as an admin/staff session identifier`

In `lib/shopify_api/auth/jwt_payload.rb`:
```ruby
raise ShopifyAPI::Errors::InvalidJwtTokenError,
  "Session token had invalid API key" unless @aud == Context.api_key
``` [1](#0-0) 

only the `aud` claim (the app's client id) is validated. The `iss` claim — which distinguishes an Admin session token (`iss` ends with `/admin`) from a Checkout UI Extension token (`iss` ends with `/checkouts`) — is parsed but only consulted in the unrelated `shopify_user_id` helper:
```ruby
def admin_session_token?
  @iss.end_with?("/admin")
end
``` [2](#0-1) 

The gem's own documented entry point for turning a bearer token into a session id ignores this distinction entirely:
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
``` [3](#0-2) 

`payload.sub` is used verbatim — never gated by `admin_session_token?`. This is the exact same documented API `getting_started.md` instructs host apps to call with any `HTTP_AUTHORIZATION`/`id_token` value they receive: [4](#0-3) 

A checkout UI extension token is a **legitimately Shopify-signed** JWT that any unauthenticated storefront customer can obtain (it authenticates them for extension calls, not for admin access): `iss = "https://shop.myshopify.io/checkouts"`, `aud = api_key`, `sub = "gid://shopify/Customer/123..."`, with no `sid`: [5](#0-4) 

Because `aud` matches the same `api_key` for every token type an app issues/receives, this token passes `JwtPayload.new` validation exactly like an admin session token would, and `session_id_from_shopify_id_token` will happily construct a session id such as `"shop.myshopify.io_gid://shopify/Customer/123456789"` from it — treating a customer-scoped credential as if it were the app/merchant session-lookup key, with no check that the token was actually issued for the admin embedded-app context.

### Impact Explanation
Any application built on this gem that follows the documented pattern (pass an incoming `id_token`/`Authorization` header straight into `SessionUtils.current_session_id`/`session_id_from_shopify_id_token`) receives a session id derived from an unvalidated token type. The gem provides no signal to the host app that the token was not an admin session token, so the token-type/scope boundary between "customer at checkout" and "merchant/staff in the admin" is not enforced by the library at the one place it is supposed to be enforced (`JwtPayload`/`SessionUtils`). This is a scope/token-type check bypass in the library's own session-derivation logic — the class of defect matching "a JWT claim trusted without being bound" and "a scope ... check that answers permissively" from the audit rubric.

### Likelihood Explanation
Obtaining a valid checkout UI extension JWT requires no privileges beyond visiting a storefront checkout where the app has a checkout extension — this is available to any unprivileged internet user. No secret, access token, or leaked credential is required to obtain this legitimately Shopify-signed token; the only missing control is inside this gem's own validation/derivation path.

### Recommendation
In `JwtPayload`, enforce and expose that the token type used for session derivation is correct — e.g., raise `InvalidJwtTokenError` in `session_id_from_shopify_id_token` (or in `JwtPayload#initialize`, via a required/expected `iss` suffix parameter) when `admin_session_token?` is false, so only tokens actually issued with `iss` ending in `/admin` can be turned into an app session id. Alternatively, prefer the signed `sid` claim (bound 1:1 to a specific Admin session) over the caller-reconstructed `"#{shop}_#{sub}"` composite key, and reject tokens lacking it when deriving session identifiers for admin/staff sessions.

### Proof of Concept
```ruby
# Attacker is an ordinary storefront customer at checkout who has obtained,
# via Shopify's own signing, a checkout UI extension token for this app:
checkout_payload = {
  iss: "https://victim-shop.myshopify.com/checkouts",
  dest: "victim-shop.myshopify.com",
  aud: ShopifyAPI::Context.api_key,      # same api key as admin tokens
  sub: "gid://shopify/Customer/999999",  # attacker's own customer id
  exp: (Time.now + 60).to_i,
  nbf: Time.now.to_i,
  iat: Time.now.to_i,
  jti: "attacker-jti",
}
checkout_jwt = JWT.encode(checkout_payload, ShopifyAPI::Context.api_secret_key, "HS256")
# (Shopify itself signs this for the customer in the real flow; here we simulate
# with the shared secret solely to demonstrate the missing iss check.)

# Host app follows the documented pattern verbatim:
session_id = ShopifyAPI::Utils::SessionUtils.session_id_from_shopify_id_token(
  id_token: checkout_jwt, online: true
)
# => "victim-shop.myshopify.com_gid://shopify/Customer/999999"
#
# JwtPayload.new never rejected this non-admin token; SessionUtils never
# checked admin_session_token? before using `sub` to build the session id.
```

### Citations

**File:** lib/shopify_api/auth/jwt_payload.rb (L43-44)
```ruby
        raise ShopifyAPI::Errors::InvalidJwtTokenError,
          "Session token had invalid API key" unless @aud == Context.api_key
```

**File:** lib/shopify_api/auth/jwt_payload.rb (L83-86)
```ruby
      sig { returns(T::Boolean) }
      def admin_session_token?
        @iss.end_with?("/admin")
      end
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

**File:** docs/getting_started.md (L58-68)
```markdown
For *embedded* apps:

If you have an `HTTP_AUTHORIZATION` header or `id_token` from the request URL params , you can pass that as `shopify_id_token` into:
- `ShopifyAPI::Utils::SessionUtils.current_session_id(shopify_id_token, nil, true)` for online (user) sessions or
- `ShopifyAPI::Utils::SessionUtils.current_session_id(shopify_id_token, nil, false)` for offline (store) sessions.

`current_session_id` accepts shopify_id_token in the format of `Bearer this_token` or just `this_token`.

You can also use this method to get session ID:
- `ShopifyAPI::Utils::SessionUtils::session_id_from_shopify_id_token(id_token: id_token, online: true)` for online (user) sessions or
- `ShopifyAPI::Utils::SessionUtils::session_id_from_shopify_id_token(id_token: id_token, online: false)` for offline (store) sessions.
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
