### Title
Non-embedded session cookie carries a fully predictable session ID (`offline_#{shop}` / `#{shop}_#{user_id}`) with no HMAC binding to `Context.api_secret_key` - (File: `lib/shopify_api/auth/oauth.rb`, `lib/shopify_api/auth/session.rb`, `lib/shopify_api/utils/session_utils.rb`)

### Summary
For non-embedded apps, `Oauth.validate_auth_callback` sets the session cookie's value directly to `session.id` [1](#0-0) , and `Session.from` computes that id deterministically as `"offline_#{shop}"` or `"#{shop}_#{associated_user.id}"` from public inputs [2](#0-1) . `SessionUtils.current_session_id`/`cookie_session_id` then trust this cookie value verbatim as the session lookup key with no cryptographic verification [3](#0-2) [4](#0-3) . Since the value is derivable from a public shop domain alone, an attacker can forge the cookie header for any victim shop without ever possessing `Context.api_secret_key`.

### Finding Description
The claimed binding is: `SessionUtils.current_session_id(nil, cookies, online) == id` should only hold if `id` was derived from bytes authenticated under `Context.api_secret_key` (i.e., produced only via a genuine OAuth callback verified by `Utils::HmacValidator.validate`). In reality:

- `offline_session_id(shop)` is `"offline_#{shop}"` [5](#0-4)  and `jwt_session_id(shop, user_id)` is `"#{shop}_#{user_id}"` [6](#0-5)  — both fully computable from the public `shop` domain (and, for online, a `user_id` an attacker can obtain by installing the app themselves).
- `Session.from` uses these exact same formulas to assign `Session#id` after the real OAuth exchange [2](#0-1) .
- For non-embedded apps, `validate_auth_callback` sets the session cookie's `value` to this predictable `session.id`, unsigned and unencrypted, as a bare `SessionCookie` struct [1](#0-0) .
- For non-embedded apps, `current_session_id` accepts *only* the cookie value and returns it unmodified as the identity to be used for session-storage lookup — there is no HMAC/JWT check whatsoever in this branch [3](#0-2) .

Because the returned "session id" is identical to a value the attacker can compute purely from the target's public shop domain, an attacker who knows (or guesses) a victim's `*.myshopify.com` domain can simply send `Cookie: shopify_app_session=offline_victim.myshopify.com` to the host app. The gem hands back `"offline_victim.myshopify.com"` as a validated session identifier with no cryptographic check that this string was ever actually issued by the server or tied to a request authenticated under `Context.api_secret_key`. If the host app's session storage (as documented, e.g. `CustomSessionStorage`) looks up a session record keyed by this id — which is the intended and documented usage pattern for this gem — the attacker's forged cookie resolves to the victim merchant's real stored `Session`, exposing `access_token` and `refresh_token`.

None of the existing guards intervene: `HmacValidator.validate` only runs during the OAuth callback (`validate_auth_callback`), not during `current_session_id` cookie consumption [7](#0-6) ; `Context.embedded?` merely selects the cookie-only branch instead of adding protection [8](#0-7) ; and `SessionCookie` performs no signing at all [9](#0-8) .

### Impact Explanation
An attacker who knows a victim merchant's shop domain can forge a cookie value that is byte-identical to the legitimate session id, causing the host app's session storage lookup to serve the victim's stored `Session`, including `access_token` and `refresh_token`. This is theft of a merchant's tokens (Critical), enabling durable access even after token rotation since the refresh token can mint new access tokens. The attack is fully repeatable against any shop whose domain is known (myshopify domains are frequently public/guessable via storefronts, webhooks, or app-store listings), and requires no privileged credential — only the public shop name.

### Likelihood Explanation
Preconditions: the host app must run with `is_embedded: false` (this is an explicit, documented configuration this gem supports) and must use the cookie value as the trust anchor for session lookup, which is exactly what `SessionUtils.current_session_id` is designed to be used for. The attacker's cost is trivial — knowledge of a target shop's domain, which is not secret. No interaction with the victim or the app developer is required, no secret material is needed, and the exploit generalizes to any shop, making this highly feasible and broadly repeatable.

### Recommendation
Never use a raw, guessable identity string as a bearer-equivalent cookie value. Either (a) sign the cookie value (e.g., HMAC it under `Context.api_secret_key`) and verify that HMAC in `SessionUtils.cookie_session_id` before treating it as an identity, or (b) use an unguessable, randomly generated token (e.g., `SecureRandom.uuid`, already used as the default `Session#id` when no deterministic id is supplied) as the cookie value distinct from the storage-key `session.id`, mapping one to the other server-side only after verifying the cookie's authenticity.

### Proof of Concept
```ruby
# test/utils/session_utils_test.rb (new test)
def test_forged_offline_cookie_is_accepted_as_identity
  ShopifyAPI::Context.setup(
    api_key: "key", api_secret_key: "secret", api_version: "2022-01",
    is_private: false, is_embedded: false, scope: [], host_name: "app.com"
  )

  victim_shop = "victim-shop.myshopify.com"
  # Attacker never performed OAuth, never holds api_secret_key,
  # but derives the exact predictable id from the public shop domain:
  forged_id = ShopifyAPI::Utils::SessionUtils.offline_session_id(victim_shop)
  assert_equal "offline_victim-shop.myshopify.com", forged_id

  cookies = { ShopifyAPI::Auth::Oauth::SessionCookie::SESSION_COOKIE_NAME => forged_id }

  returned_id = ShopifyAPI::Utils::SessionUtils.current_session_id(nil, cookies, false)

  # BROKEN BINDING: returned_id is accepted as a valid identity even though
  # it was never produced from bytes authenticated under Context.api_secret_key —
  # it's just string interpolation of public data.
  assert_equal forged_id, returned_id
end
```
This demonstrates that `current_session_id` returns, unchecked, an identity value the attacker computed purely from public information, with no dependency on `Context.api_secret_key` — violating the SESSION DERIVATION invariant and enabling session-storage impersonation of the victim merchant when the host app looks up sessions by this id, as it is documented to do.

### Citations

**File:** lib/shopify_api/auth/oauth.rb (L60-71)
```ruby
        def validate_auth_callback(cookies:, auth_query:)
          unless Context.setup?
            raise Errors::ContextNotSetupError, "ShopifyAPI::Context not setup, please call ShopifyAPI::Context.setup"
          end
          raise Errors::InvalidOauthError, "Invalid OAuth callback." unless Utils::HmacValidator.validate(auth_query)
          raise Errors::UnsupportedOauthError, "Cannot perform OAuth for private apps." if Context.private?

          state = cookies[SessionCookie::SESSION_COOKIE_NAME]
          raise Errors::NoSessionCookieError unless state

          raise Errors::InvalidOauthError,
            "Invalid state in OAuth callback." unless state == auth_query.state
```

**File:** lib/shopify_api/auth/oauth.rb (L105-110)
```ruby
          else
            SessionCookie.new(
              value: session.id,
              expires: session.expires ? session.expires : nil,
            )
          end
```

**File:** lib/shopify_api/auth/session.rb (L111-117)
```ruby
          if is_online
            associated_user = T.must(access_token_response.associated_user)
            associated_user_scope = access_token_response.associated_user_scope
            id = "#{shop}_#{associated_user.id}"
          else
            id = "offline_#{shop}"
          end
```

**File:** lib/shopify_api/utils/session_utils.rb (L20-37)
```ruby
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

**File:** lib/shopify_api/utils/session_utils.rb (L58-61)
```ruby
        sig { params(shop: String, user_id: String).returns(String) }
        def jwt_session_id(shop, user_id)
          "#{shop}_#{user_id}"
        end
```

**File:** lib/shopify_api/utils/session_utils.rb (L63-66)
```ruby
        sig { params(shop: String).returns(String) }
        def offline_session_id(shop)
          "offline_#{shop}"
        end
```

**File:** lib/shopify_api/utils/session_utils.rb (L68-71)
```ruby
        sig { params(cookies: T::Hash[String, String]).returns(T.nilable(String)) }
        def cookie_session_id(cookies)
          cookies[Auth::Oauth::SessionCookie::SESSION_COOKIE_NAME]
        end
```

**File:** lib/shopify_api/auth/oauth/session_cookie.rb (L7-25)
```ruby
      class SessionCookie < T::Struct
        extend T::Sig

        SESSION_COOKIE_NAME = "shopify_app_session"

        const :name, String, default: SESSION_COOKIE_NAME
        const :value, String
        const :expires, T.nilable(Time)

        alias_method :eql?, :==
        sig { params(other: T.nilable(SessionCookie)).returns(T::Boolean) }
        def ==(other)
          return false unless other

          name == other.name &&
            value == other.value &&
            expires == other.expires
        end
      end
```
