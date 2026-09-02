### Title
`SessionUtils.current_session_id` trusts the raw `shopify_app_session` cookie as a session-store lookup key with no cryptographic binding, and offline session IDs are deterministically guessable (`offline_#{shop}`) - ([File: lib/shopify_api/utils/session_utils.rb])

### Summary
For non-embedded apps, `ShopifyAPI::Utils::SessionUtils.current_session_id` returns `cookies["shopify_app_session"]` verbatim as the session-store lookup key, with no HMAC or signature verification anywhere in this gem. Combined with `Auth::Session.from` / `Session#initialize` producing fully deterministic offline session IDs (`"offline_#{shop}"`), an attacker who knows a victim's shop domain (public information) can construct that exact cookie value and, if the host app's session store returns the corresponding `Auth::Session`, obtain that merchant's `access_token` via `HttpClient`.

### Finding Description
The claimed binding is: `current_session_id(shopify_id_token, cookies, online) == cookies["shopify_app_session"]` **with no check that this value was issued by, or is cryptographically tied to, this gem's OAuth flow** — i.e. there is no equality check of the form `hmac(secret, cookie_value) == received_hmac` anywhere before this value is used as a trust anchor.

Tracing the non-embedded branch in `lib/shopify_api/utils/session_utils.rb:31-36`:
```
else
  raise Errors::CookieNotFoundError, ... unless cookies && cookies[SESSION_COOKIE_NAME]
  cookie_session_id(cookies)
end
```
`cookie_session_id` (line 68-71) does nothing but `cookies[SESSION_COOKIE_NAME]` — a direct pass-through of attacker-controlled bytes. [1](#0-0) [2](#0-1) 

The cookie itself is created in `Auth::Oauth.validate_auth_callback`, where for non-embedded apps the cookie's *value* is set directly to `session.id` (not a random nonce, not signed): [3](#0-2) . The docs instruct developers to store this with `cookies[name] = { secure: true, http_only: true, value: ... }` — an unsigned Rails cookie; `http_only`/`secure` prevent JS access and require TLS but do **not** prevent an attacker from directly sending a hand-crafted `Cookie:` header in their own HTTP request. [4](#0-3) 

Critically, `session.id` for the common offline-token case is fully deterministic: `Session.from` sets `id = "offline_#{shop}"` [5](#0-4) , and `Session#initialize` only falls back to `SecureRandom.uuid` if no `id` is explicitly supplied [6](#0-5) . Since shop domains (`{shop}.myshopify.com`) are public/guessable, an attacker never needs to steal a cookie — they can compute `offline_#{victim_shop}` outright and send `Cookie: shopify_app_session=offline_victim-shop.myshopify.com` to any endpoint of the app that calls `current_session_id`.

None of the gem's existing guards intervene here: `HmacValidator.validate` only applies to OAuth callback query-string HMACs (`auth_query`), not to this cookie; `Context.embedded?` merely routes into the same unguarded `cookie_session_id` call; there is no JWT/`aud` check in this branch since no ID token is involved. The divergence is real: the "session id" the gem trusts as an authenticated lookup key is, in the non-embedded path, just user-controlled/guessable request data.

Whether this leads to actual access-token exposure depends on the host app's session store returning the corresponding `Auth::Session` for that guessed ID and the host wiring that into `HttpClient#initialize`, which is outside this gem — but the gem's own contract (`current_session_id` is documented and used specifically as *the* session-store lookup key) makes this the proximate root cause inside this repository.

### Impact Explanation
If exploited, the attacker's request is treated by the host app as belonging to the victim merchant's session, and — if the host's session store keys sessions by this exact id — the returned `Auth::Session#access_token` would be attached to outbound Shopify Admin API requests the attacker triggers through the app, i.e. cross-tenant access to another merchant's data/access token. This matches the Critical severity bar (cross-tenant access / access-token theft). It is repeatable against any victim shop whose domain the attacker knows, with no rate limiting on cookie guesses since `offline_#{shop}` requires zero brute force once the shop domain is known.

### Likelihood Explanation
Preconditions: the app must be non-embedded (`Context.embedded? == false`), configured to use the authorization-code-grant cookie flow as documented, and the host must map `current_session_id`'s return value directly to a session-store lookup (this is the gem's intended/documented usage pattern). The attacker needs only the victim's `myshopify.com` domain — no secret, no token, no prior compromise — and can send the crafted `Cookie` header with a single unauthenticated HTTP request. This is low-cost and fully repeatable across arbitrary victim shops.

### Recommendation
Never use the raw cookie value as a trust-bearing lookup key. The session cookie should either (a) store a cryptographically random opaque token that is itself looked up in a server-side session store without independently reconstructing an "offline_#{shop}" style ID from attacker input, or (b) be HMAC-signed by the gem (analogous to `HmacValidator`) so `cookie_session_id` can verify `hmac(api_secret_key, session_id) == signature` before returning it. At minimum, the gem's documentation/implementation should mandate Rails' signed/encrypted cookie jar (`cookies.signed`/`cookies.encrypted`) rather than plain `cookies[]=`, and `Session.from`/`Session#initialize` should avoid predictable, attacker-computable IDs for offline sessions.

### Proof of Concept
```ruby
# test/utils/session_utils_test.rb (new test)
def test_current_session_id_trusts_arbitrary_cookie_non_embedded
  ShopifyAPI::Context.setup(
    api_key: "key", api_secret_key: "secret", host_name: "host",
    api_version: "unstable", is_embedded: false, is_private: false, scope: []
  )

  victim_shop = "victim-shop.myshopify.com"
  forged_cookie_value = "offline_#{victim_shop}" # attacker-computable, no secret needed

  cookies = { ShopifyAPI::Auth::Oauth::SessionCookie::SESSION_COOKIE_NAME => forged_cookie_value }

  result = ShopifyAPI::Utils::SessionUtils.current_session_id(nil, cookies, false)

  # Binding under test: returned id equals attacker-supplied bytes verbatim,
  # with no HMAC/signature check performed anywhere in the call path.
  assert_equal forged_cookie_value, result
  assert_equal "offline_#{victim_shop}", result
end
```
This demonstrates that `current_session_id` returns the attacker-chosen (and, for offline sessions, attacker-derivable) cookie value byte-for-byte, confirming the missing HMAC/signature binding in the non-embedded branch.

### Citations

**File:** lib/shopify_api/utils/session_utils.rb (L19-37)
```ruby
        def current_session_id(shopify_id_token, cookies, online)
          if Context.embedded?
            if shopify_id_token
              id_token = shopify_id_token.gsub("Bearer ", "")
              session_id_from_shopify_id_token(id_token: id_token, online: online)
            else
              # falling back to session cookie
              raise Errors::CookieNotFoundError, "JWT token or Session cookie not found for app" unless
                cookies && cookies[Auth::Oauth::SessionCookie::SESSION_COOKIE_NAME]

              cookie_session_id(cookies)
            end
          else
            raise Errors::CookieNotFoundError, "Session cookie not found for app" unless
              cookies && cookies[Auth::Oauth::SessionCookie::SESSION_COOKIE_NAME]

            cookie_session_id(cookies)
          end
        end
```

**File:** lib/shopify_api/utils/session_utils.rb (L68-71)
```ruby
        sig { params(cookies: T::Hash[String, String]).returns(T.nilable(String)) }
        def cookie_session_id(cookies)
          cookies[Auth::Oauth::SessionCookie::SESSION_COOKIE_NAME]
        end
```

**File:** lib/shopify_api/auth/oauth.rb (L100-112)
```ruby
          cookie = if Context.embedded?
            SessionCookie.new(
              value: "",
              expires: Time.now,
            )
          else
            SessionCookie.new(
              value: session.id,
              expires: session.expires ? session.expires : nil,
            )
          end

          { session: session, cookie: cookie }
```

**File:** docs/usage/oauth.md (L252-259)
```markdown

    # Update cookies with the authorized access token from result
    cookies[auth_result[:cookie].name] = {
      expires: auth_result[:cookie].expires,
      secure: true,
      http_only: true,
      value: auth_result[:cookie].value
    }
```

**File:** lib/shopify_api/auth/session.rb (L70-72)
```ruby
      def initialize(shop:, id: nil, state: nil, access_token: "", scope: [], associated_user_scope: nil, expires: nil,
        is_online: nil, associated_user: nil, shopify_session_id: nil, refresh_token: nil, refresh_token_expires: nil)
        @id = T.let(id || SecureRandom.uuid, String)
```

**File:** lib/shopify_api/auth/session.rb (L107-117)
```ruby
        sig { params(shop: String, access_token_response: Oauth::AccessTokenResponse).returns(Session) }
        def from(shop:, access_token_response:)
          is_online = access_token_response.online_token?

          if is_online
            associated_user = T.must(access_token_response.associated_user)
            associated_user_scope = access_token_response.associated_user_scope
            id = "#{shop}_#{associated_user.id}"
          else
            id = "offline_#{shop}"
          end
```
