## Title
Online session ID is derived from an unvalidated JWT `sub` claim, bypassing the admin-token binding check - (`lib/shopify_api/utils/session_utils.rb`)

### Summary
`ShopifyAPI::Utils::SessionUtils.session_id_from_shopify_id_token` computes the online session lookup key (`"#{shop}_#{sub}"`) directly from the `sub` claim of any JWT that satisfies only `aud == api_key` and a valid HS256 signature — without checking that the token is actually an *admin* session token. The library itself defines a stricter check for this exact purpose (`admin_session_token?` + `user_id_sub?`) but only applies it in `JwtPayload#shopify_user_id`, not in the session-id derivation path that host apps are documented to use for session lookups.

### Finding Description
`ShopifyAPI::Auth::JwtPayload` decodes and verifies any JWT signed with the app's `api_secret_key` whose `aud` equals `Context.api_key`: [1](#0-0) 

It exposes two different ways to derive an identity from the token:
- `shopify_user_id`, which only returns a value when the token is an *admin session token* (`iss` ends with `/admin`) **and** `sub` looks like a numeric admin user id: [2](#0-1) [3](#0-2) 

- the raw `sub` attribute, with no such restriction: [4](#0-3) 

`ShopifyAPI::Utils::SessionUtils`, however, builds the *online session id* — the key host apps use to look up a stored `Session` (containing the merchant's OAuth access token) — using the unrestricted `sub`, not `shopify_user_id`: [5](#0-4) 

This is the documented, intended entry point for embedded apps to resolve the "current session" from a bearer/session token: [6](#0-5) 

The intended binding is: `online_session_id == "#{shop}_#{admin_user_id}"`, where `admin_user_id` is only meaningful when `iss` denotes an admin session (`.../admin`). The actual code computes `online_session_id == "#{shop}_#{sub}"` for **any** JWT signed by the app's secret with matching `aud`, regardless of `iss`. Shopify issues JWTs with this same shape (`iss`, `dest`, `aud`, `sub`, `exp`, ...) for other embedded surfaces signed with the same app credentials, e.g. checkout/customer-account UI extension tokens, as reflected in this library's own test fixtures: [7](#0-6) 

If a non-admin token's `sub` value happens to match (or is caused to match) the numeric id of a real admin/online user for the same shop, `current_session_id`/`session_id_from_shopify_id_token` returns the exact same session key as the legitimate admin session, so `MyApp::SessionRepository.load_session(id)` in the host app (built exactly per this gem's documented flow) resolves to that admin user's stored access token — an identity binding that the token itself never actually asserted.

### Impact Explanation
This breaks the equality `session_id == identity of the token presenter`, allowing a holder of a differently-scoped, non-admin JWT (signed by the same app secret for a different Shopify surface) to obtain a session key that maps to another user's/merchant's stored access token in the host app's session store. That is an authentication-bypass / cross-tenant access risk classified as Critical under the given rules, since it lets one authenticated identity resolve to another principal's stored OAuth access token via this gem's own documented API, not through host-app misuse.

### Likelihood Explanation
Exploitability depends on an attacker being able to obtain or influence a valid, differently-scoped JWT signed by the app's secret whose `sub` collides with a targeted admin user id for the same shop, which requires Shopify to have issued such a token (e.g., a customer/checkout extension token) with a colliding `sub`. This narrows practical likelihood, but the root cause is a genuine binding gap in the library's own code — `jwt_session_id` never checks `admin_session_token?`/`user_id_sub?`, unlike `shopify_user_id`, which exists specifically to enforce that check but is not used on this path.

### Recommendation
In `ShopifyAPI::Utils::SessionUtils.session_id_from_shopify_id_token`, when `online: true`, derive the user id via `JwtPayload#shopify_user_id` (which enforces `admin_session_token?` and `user_id_sub?`) instead of the raw `sub`, and raise an appropriate error (e.g. `InvalidJwtTokenError`) when the token is not an admin session token.

### Proof of Concept
1. App is configured as embedded with `api_key`/`api_secret_key`.
2. An admin online session exists for `shop = "victim.myshopify.com"`, user id `42`, session id `"victim.myshopify.com_42"`, holding a real access token, stored via `MyApp::SessionRepository.store_session`.
3. Attacker obtains any Shopify-issued JWT signed with the same `api_secret_key`/`aud` for a non-admin surface (e.g. `iss: "https://victim.myshopify.io/checkouts"`) whose `sub` is `"42"`.
4. Attacker calls `ShopifyAPI::Utils::SessionUtils.current_session_id(attacker_token, nil, true)` (or `session_id_from_shopify_id_token`) exactly as documented in `docs/getting_started.md`.
5. Method returns `"victim.myshopify.com_42"` — identical to the legitimate admin session id — because `jwt_session_id` uses `payload.sub` directly without checking `admin_session_token?`: [5](#0-4) 
6. Host app's `SessionRepository.load_session("victim.myshopify.com_42")` returns the victim's stored session/access token to the attacker's request context.

### Citations

**File:** lib/shopify_api/auth/jwt_payload.rb (L18-19)
```ruby
      sig { returns(T.nilable(String)) }
      attr_reader :sub, :sid
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

**File:** lib/shopify_api/auth/jwt_payload.rb (L53-56)
```ruby
      sig { returns(T.nilable(Integer)) }
      def shopify_user_id
        @sub.to_i if user_id_sub? && admin_session_token?
      end
```

**File:** lib/shopify_api/auth/jwt_payload.rb (L83-91)
```ruby
      sig { returns(T::Boolean) }
      def admin_session_token?
        @iss.end_with?("/admin")
      end

      sig { returns(T::Boolean) }
      def user_id_sub?
        @sub&.match?(/\A\d+\z/) || false
      end
```

**File:** lib/shopify_api/utils/session_utils.rb (L45-61)
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

        sig { params(shop: String, user_id: String).returns(String) }
        def jwt_session_id(shop, user_id)
          "#{shop}_#{user_id}"
        end
```

**File:** docs/getting_started.md (L58-70)
```markdown
For *embedded* apps:

If you have an `HTTP_AUTHORIZATION` header or `id_token` from the request URL params , you can pass that as `shopify_id_token` into:
- `ShopifyAPI::Utils::SessionUtils.current_session_id(shopify_id_token, nil, true)` for online (user) sessions or
- `ShopifyAPI::Utils::SessionUtils.current_session_id(shopify_id_token, nil, false)` for offline (store) sessions.

`current_session_id` accepts shopify_id_token in the format of `Bearer this_token` or just `this_token`.

You can also use this method to get session ID:
- `ShopifyAPI::Utils::SessionUtils::session_id_from_shopify_id_token(id_token: id_token, online: true)` for online (user) sessions or
- `ShopifyAPI::Utils::SessionUtils::session_id_from_shopify_id_token(id_token: id_token, online: false)` for offline (store) sessions.

`session_id_from_shopify_id_token` does **NOT** accept shopify_id_token in the format of `Bearer this_token`, you must pass in `this_token`.
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
