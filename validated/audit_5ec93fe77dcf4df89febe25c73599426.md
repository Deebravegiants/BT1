### Title
Predictable offline session identifier (`offline_#{shop}`) accepted as trusted session key without HMAC/entropy - ([File: lib/shopify_api/utils/session_utils.rb])

### Summary
For non-embedded apps, `ShopifyAPI::Utils::SessionUtils.current_session_id` returns the raw `shopify_app_session` cookie value unchanged and unauthenticated, and this gem itself sets that cookie's value to the fully deterministic string `"offline_#{shop}"` (zero entropy beyond the public `.myshopify.com` domain) during `Oauth.validate_auth_callback`. Combined with this gem's own documented session-storage reference pattern (lookup by raw `id`), any unprivileged attacker who knows a victim shop's domain can forge this "session id" and retrieve that shop's stored offline session/access token.

### Finding Description
The broken binding: `SessionStorage key used to retrieve session == bytes authenticated under Context.api_secret_key`. In this codebase that binding is never enforced for the cookie-derived path.

Trace:
1. `SessionUtils.current_session_id(shopify_id_token, cookies, online)` — when `Context.embedded?` is `false` (or embedded but no `shopify_id_token`) — goes straight to `cookie_session_id(cookies)`, which is just `cookies[SessionCookie::SESSION_COOKIE_NAME]` [1](#0-0) [2](#0-1) . No `HmacValidator.validate` or `OpenSSL.secure_compare` call exists anywhere in this method or `cookie_session_id`.
2. The only place this gem populates that cookie is `Oauth.validate_auth_callback`, which for non-embedded, offline sessions sets `SessionCookie.new(value: session.id, ...)`, and `session.id` for offline sessions is produced by `offline_session_id(shop)` = `"offline_#{shop}"` [3](#0-2) [4](#0-3) . This value carries no secret material and no random nonce — it is fully derived from the shop's public `.myshopify.com` domain.
3. HMAC validation (`Utils::HmacValidator.validate`) is only exercised once, during the OAuth callback itself, against the `auth_query` (code/state/timestamp/hmac from Shopify), not against the cookie value produced from that flow [5](#0-4) . After that point, the cookie is a bare, unsigned string that any client can also present directly in an HTTP `Cookie:` header — cookies are not cryptographically bound to a browser or origin by the HTTP protocol itself, only by browser-enforced same-origin cookie jar rules, which an attacker crafting a raw request from their own client bypasses entirely.
4. This gem's own `BREAKING_CHANGES_FOR_V16.md` documents the sanctioned session-storage reference implementation (from `shopify_app`), which retrieves sessions with a naive `find_by(id: id)` keyed exactly on this string [6](#0-5) . `docs/getting_started.md` explicitly instructs developers to feed raw cookies into `current_session_id` for non-embedded apps to retrieve the session id used for storage lookups [7](#0-6) .

Attacker request: knowing (or trivially discovering, since `.myshopify.com` domains are effectively public/enumerable) a victim shop's domain `victim-shop.myshopify.com`, the attacker sends a bare HTTP request to the target app with header `Cookie: shopify_app_session=offline_victim-shop.myshopify.com`. The app calls `current_session_id(nil, cookies, false)` → `cookie_session_id` → returns `"offline_victim-shop.myshopify.com"` verbatim → the app's session storage (built per this gem's documented pattern) loads and returns the victim's stored offline session, including `access_token`, with no HMAC or secret check ever performed against `Context.api_secret_key`.

Existing guards do not intervene: `HmacValidator.validate` is not called anywhere in this path; `ShopValidator.sanitize!`, `state` comparison, and `JwtPayload` checks apply only to the OAuth-callback and JWT/id-token paths, not the cookie path; `Context.embedded?` being `false` is precisely what routes execution into the unguarded cookie branch.

### Impact Explanation
A successful request yields cross-tenant access: the attacker obtains the victim shop's stored offline `access_token` (and any online session tokens if `#{shop}_#{user_id}` user ids are guessed/enumerated), which can be used to call the Shopify Admin API as that shop. This is repeatable against any victim shop whose domain is known, with no per-victim secret required, matching the "Critical - cross-tenant access, theft of merchant access token" category.

### Likelihood Explanation
Preconditions: the app must be non-embedded (`Context.embedded? == false`), use cookie-based sessions per this gem's documented flow, and use the gem's own recommended reference session-storage pattern (keyed retrieval by `session.id`/cookie value, as documented in this gem's `BREAKING_CHANGES_FOR_V16.md`). Attacker cost is minimal: no credentials, no secret, just knowledge of the target's `.myshopify.com` domain and the fixed, gem-defined format string `"offline_#{shop}"`. This is fully repeatable against arbitrary victim shops.

### Recommendation
Do not use a deterministic, secret-free string as the sole session-storage key/cookie value for non-embedded offline sessions. Bind the session cookie/id to a cryptographically random, unguessable value (or an HMAC/signed token keyed on `Context.api_secret_key`) that is verified on every lookup, rather than trusting `cookies[SESSION_COOKIE_NAME]` as-is in `SessionUtils.cookie_session_id`.

### Proof of Concept
Minitest + Mocha plan in `test/utils/session_utils_test.rb` style:
```ruby
def test_offline_cookie_session_id_has_no_hmac_and_is_shop_derived
  ShopifyAPI::Context.stubs(:embedded?).returns(false)
  victim_shop = "victim-shop.myshopify.com"
  forged_cookie_value = "offline_#{victim_shop}"
  cookies = { ShopifyAPI::Auth::Oauth::SessionCookie::SESSION_COOKIE_NAME => forged_cookie_value }

  ShopifyAPI::Utils::HmacValidator.expects(:validate).never

  session_id = ShopifyAPI::Utils::SessionUtils.current_session_id(nil, cookies, false)

  assert_equal(forged_cookie_value, session_id)
  assert_equal(ShopifyAPI::Utils::SessionUtils.offline_session_id(victim_shop), session_id)
end
```
This demonstrates the equality `attacker-forged cookie bytes == SessionStorage lookup key` holds without any call to `HmacValidator.validate` or `OpenSSL.secure_compare`, confirming the SESSION_DERIVATION violation.

### Citations

**File:** lib/shopify_api/utils/session_utils.rb (L19-36)
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

**File:** docs/getting_started.md (L47-52)
```markdown
#### Cookie
Cookie based authentication is not supported for embedded apps due to browsers dropping support for third party cookies due to security concerns. Non-embedded apps are able to use cookies for session storage/retrieval.

For *non-embedded* apps, you can pass the cookies into:
 - `ShopifyAPI::Utils::SessionUtils.current_session_id(nil, cookies, true)` for online (user) sessions or
 - `ShopifyAPI::Utils::SessionUtils.current_session_id(nil, cookies, false)` for offline (store) sessions.
```
