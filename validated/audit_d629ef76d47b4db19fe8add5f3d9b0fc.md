## Finding

### Title
Predictable, non-secret `Session#id` used as bearer session-cookie value enables cross-tenant session hijacking - (File: `lib/shopify_api/auth/session.rb`, `lib/shopify_api/utils/session_utils.rb`)

### Summary
For non-embedded OAuth flows, `ShopifyAPI::Auth::Oauth.validate_auth_callback` sets the browser session cookie's value to the raw `Session#id`, and `ShopifyAPI::Utils::SessionUtils.current_session_id` later treats whatever value comes back in that cookie as a trusted, opaque lookup key for retrieving the stored session (and its access token) with no cryptographic binding to the browser that originally received it. The problem is that `Session#id` is not a random secret — it is deterministically derived from public information (`shop` domain and, for online sessions, the numeric `associated_user.id`).

### Finding Description
When `Context.embedded?` is false, `validate_auth_callback` builds the cookie like this: [1](#0-0) 

The `session.id` embedded in that cookie is computed deterministically: [2](#0-1) 

For offline access tokens the id is simply `"offline_#{shop}"`; for online tokens it is `"#{shop}_#{associated_user.id}"`. Neither `shop` (the myshopify domain, which is routinely public/discoverable) nor a Shopify staff `associated_user.id` (a small sequential integer, often observable from other JWTs, admin URLs, or by installing the app once as any staff member) is a secret.

Later, when identifying the caller's session, the library never re-verifies that the cookie was actually issued by the server for that browser — it just reads it back and uses it as the storage/lookup key: [3](#0-2) [4](#0-3) 

`SessionCookie` itself is a plain value struct with no signature/HMAC field at all: [5](#0-4) 

The library's own documented reference implementation confirms the intended usage pattern: the host app is expected to `retrieve(id)` the stored session (and thus the merchant's access token) directly by the id contained in the cookie, with no additional secret check: [6](#0-5) 

**Binding that should hold, expressed as an equality:**
`session_id_presented_in_cookie == session_id_only_derivable_by_the_party_the_server_actually_authenticated_via_OAuth`

**What actually holds:**
`session_id_presented_in_cookie == f(shop, user_id)` where `f` is a public, non-secret, guessable function — so any unprivileged party who knows (or guesses) a target `shop` domain and (for online sessions) a small integer user id can construct a valid cookie value themselves, without ever completing OAuth or possessing any credential.

### Impact Explanation
An unprivileged attacker who knows or guesses a victim's `myshopify.com` domain can set `Cookie: shopify_app_session=offline_<victim-shop>.myshopify.com` on a raw HTTP request to the host application built with this gem's documented pattern (`current_session_id` → `SessionRepository.retrieve(id)`), causing the app to activate the victim merchant's stored `Session`, including its `access_token`. This is cross-tenant access to another merchant's Shopify Admin access token purely through prediction of an identifier, with no XSS, no cookie theft, and no credentials required — matching the "Critical: cross-tenant access" / "theft of a merchant access token" categories.

### Likelihood Explanation
Likelihood is high for any host application that follows the gem's own documented reference session-storage pattern (id-keyed lookup, as shown in `BREAKING_CHANGES_FOR_V16.md`) for non-embedded apps using `SessionUtils.current_session_id`/cookie-based sessions. `shop` domains are frequently discoverable (public storefront, app-store listings, referrer headers, install links), and `associated_user.id` values are small sequential integers that are easy to enumerate. No special access, secret, or timing is required — only an HTTP client capable of sending an arbitrary `Cookie` header.

### Recommendation
Do not use a deterministic, publicly-derivable string as the bearer value of the session cookie. Generate a cryptographically random, unguessable session token (e.g., `SecureRandom` bytes, as already done for the OAuth `state` nonce) to be used as the cookie value, and keep the internal `shop_user`-derived `Session#id` purely as an internal storage key unrelated to what is exposed in the cookie. Alternatively, sign/HMAC the cookie value with `Context.api_secret_key` so that unauthenticated bytes presented by a client cannot be accepted as a valid session reference without proof of prior server issuance.

### Proof of Concept
```ruby
# Attacker knows/guesses a victim's shop domain: "victim-shop.myshopify.com"
# and, for online sessions, a small associated_user id (e.g. 1..1000).

# Offline session id is fully predictable:
predicted_id = "offline_victim-shop.myshopify.com"

# Attacker sends a raw HTTP request directly to the host app (built per
# this gem's documented pattern) with a forged cookie:
#
#   GET /some/authenticated/endpoint HTTP/1.1
#   Host: victim-app.example.com
#   Cookie: shopify_app_session=offline_victim-shop.myshopify.com
#
# ShopifyAPI::Utils::SessionUtils.current_session_id(nil, cookies, false)
# returns "offline_victim-shop.myshopify.com" verbatim (session_utils.rb:35-37),
# which the host app's SessionRepository.retrieve(id) (per BREAKING_CHANGES_FOR_V16.md
# reference implementation) uses to fetch the victim's stored Session, including
# its real access_token, activating it for the attacker's request.
```

### Citations

**File:** lib/shopify_api/auth/oauth.rb (L100-110)
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
```

**File:** lib/shopify_api/auth/session.rb (L107-118)
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

**File:** lib/shopify_api/auth/oauth/session_cookie.rb (L7-24)
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
```

**File:** BREAKING_CHANGES_FOR_V16.md (L66-75)
```markdown
# Reconstructs using Session.new()
def retrieve(id)
  shop = find_by(id: id)
  return unless shop

  ShopifyAPI::Auth::Session.new(
    shop: shop.shopify_domain,
    access_token: shop.shopify_token
  )
end
```
