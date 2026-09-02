### Title
Non-embedded session cookie value is a fully predictable, unauthenticated session-store key that `SessionUtils.current_session_id` trusts without verification - ([File: lib/shopify_api/auth/oauth.rb], [File: lib/shopify_api/utils/session_utils.rb])

### Summary
`Oauth.validate_auth_callback` sets the `shopify_app_session` cookie to `session.id`, which for offline sessions is exactly `"offline_#{shop}"` and for online sessions is `"#{shop}_#{associated_user.id}"` [1](#0-0) , [2](#0-1) . On every subsequent request, `Utils::SessionUtils.current_session_id`/`cookie_session_id` reads that cookie value and returns it verbatim as the session-store lookup key, with no HMAC, signature, or origin check whatsoever [3](#0-2) [4](#0-3) . Because the id-derivation formulas (`offline_session_id`/`jwt_session_id`) are also exposed as gem code and require only a publicly-known shop domain, an attacker can compute a victim's session id and present it as their own cookie to make the host app resolve to the victim's stored session.

### Finding Description
Binding claimed: `session.id` should equal a value derived only from bytes authenticated under `Context.api_secret_key` for the *specific request being served*. In `validate_auth_callback`, this holds at creation time - `auth_query.shop` is only used after `Utils::HmacValidator.validate(auth_query)` succeeds, and `shop` is part of the HMAC-signed string (`AuthQuery#to_signable_string` includes `shop`) [5](#0-4) [6](#0-5) . So an attacker cannot forge an arbitrary `auth_query.shop` to make the *gem itself* mint a cookie for a shop they don't control - that half of the question's claim is not exploitable, since forging the HMAC requires `Context.api_secret_key`, which the attacker never holds.

However, the binding is violated on the *read* side, which is also implemented in this gem: `SessionUtils.current_session_id` (non-embedded branch, and the embedded-JWT-fallback branch) calls `cookie_session_id(cookies)`, which does nothing but `cookies[SessionCookie::SESSION_COOKIE_NAME]` [7](#0-6) [8](#0-7) . This value is handed to the host app as "the" session id to use for storage lookup, with no re-derivation from an authenticated source and no comparison against any signed value. Combined with the fact that `offline_session_id(shop) == "offline_#{shop}"` and `jwt_session_id(shop, user_id) == "#{shop}_#{user_id}"` are pure, public functions of the shop domain (and, for online sessions, a user id an attacker installing the app on their own store can observe the format of) [9](#0-8) , any unprivileged attacker who knows a victim's `*.myshopify.com` domain (public information) can compute the exact string the app expects as an offline session id and submit it as their own `Cookie: shopify_app_session=offline_<victim-shop>` on a request to the app.

Existing guards evaluated:
- `HmacValidator.validate` only protects the OAuth callback request itself; it is never invoked again when the cookie is later read by `SessionUtils.current_session_id`.
- `ShopValidator.sanitize!` / `state` comparison are only used during `begin_auth`/`validate_auth_callback`, not on the cookie-read path.
- `JwtPayload`'s `aud`/`sub` checks only apply to the embedded, token-based branch (`shopify_id_token` present); they do not protect the plain-cookie fallback path used in non-embedded apps, which is exactly the path in the question.
- `Context.embedded?` only decides whether the cookie is set at all (embedded apps get an empty/expired cookie) - it provides no protection for non-embedded apps, which is the case the question specifies.

None of these guards re-validate the cookie's contents against any HMAC-authenticated value at read time, so the divergence (`session.id` trusted as-is vs. `session.id` actually being unauthenticated attacker input) is real within this gem's own `SessionUtils` code.

### Impact Explanation
Whether this is exploitable end-to-end depends on what the host app does with the id returned by `SessionUtils.current_session_id` (typically: `SessionStorage.load_session(id)` or equivalent, per this gem's documented usage). Since the gem documents and implements `current_session_id` specifically so host apps can look up sessions by cookie, and this function performs no authentication of the cookie value, a host app following documented usage will fetch whatever session object is stored under the attacker-supplied id. If the victim shop has already completed OAuth (a legitimate merchant installing the app), an attacker who merely knows/guesses the victim's shop domain can set their browser's `shopify_app_session` cookie to `offline_<victim-shop>` and have the app treat their request as authenticated for the victim's shop - obtaining access to the victim's stored access token / API access via the app's own logic. This is cross-tenant access to another merchant's authenticated context without ever completing OAuth for that shop, matching the Critical "cross-tenant access" category.

### Likelihood Explanation
Preconditions: (1) host app is non-embedded (or embedded app falling back to cookie auth without an id token) so the plain `shopify_app_session` cookie path is used; (2) the victim shop has already completed OAuth and has a session stored under the deterministic id; (3) attacker knows the victim's `*.myshopify.com` domain, which is normally public/discoverable. No secrets, no HMAC forgery, and no interaction with the victim are required - the attacker only sets a cookie on their own outbound request. This is inexpensive and repeatable against any shop whose domain is known and who has installed the app.

### Recommendation
Do not trust the raw `shopify_app_session` cookie value as a storage key. Either (a) sign/encrypt the cookie value (e.g., HMAC it with `Context.api_secret_key` and verify that HMAC in `SessionUtils.cookie_session_id` before returning it), or (b) store a random, unguessable session identifier server-side and only put that opaque token in the cookie, never the deterministic `offline_#{shop}` / `#{shop}_#{user_id}` id directly.

### Proof of Concept
```ruby
# test/utils/session_utils_cookie_forgery_test.rb
require "test_helper"

class SessionUtilsCookieForgeryTest < Minitest::Test
  def setup
    ShopifyAPI::Context.setup(
      api_key: "key", api_secret_key: "secret", host_name: "app.com",
      scope: "read_products", is_embedded: false, is_private: false,
      api_version: ShopifyAPI::LatestApiVersion,
    )
  end

  def test_attacker_can_predict_and_replay_offline_session_id_without_secret
    victim_shop = "victim-shop.myshopify.com"

    # Attacker computes this with zero knowledge of api_secret_key.
    predicted_id = ShopifyAPI::Utils::SessionUtils.offline_session_id(victim_shop)
    assert_equal "offline_#{victim_shop}", predicted_id

    # Attacker sends this as their own cookie value.
    forged_cookies = { ShopifyAPI::Auth::Oauth::SessionCookie::SESSION_COOKIE_NAME => predicted_id }

    # current_session_id trusts the cookie verbatim, no HMAC re-validation.
    resolved_id = ShopifyAPI::Utils::SessionUtils.current_session_id(nil, forged_cookies, false)

    assert_equal predicted_id, resolved_id
    # Demonstrates: resolved_id is fully attacker-controlled/predictable,
    # never checked against any value authenticated under Context.api_secret_key.
  end
end
```
This shows both sides of the claimed binding diverge: `resolved_id` (what the host app will use to fetch a stored session) equals a value the attacker derived purely from public shop-domain knowledge, with no step in `SessionUtils.current_session_id` or `cookie_session_id` requiring possession of `Context.api_secret_key` or any authenticated bytes tied to the current request.

### Citations

**File:** lib/shopify_api/auth/oauth.rb (L60-65)
```ruby
        def validate_auth_callback(cookies:, auth_query:)
          unless Context.setup?
            raise Errors::ContextNotSetupError, "ShopifyAPI::Context not setup, please call ShopifyAPI::Context.setup"
          end
          raise Errors::InvalidOauthError, "Invalid OAuth callback." unless Utils::HmacValidator.validate(auth_query)
          raise Errors::UnsupportedOauthError, "Cannot perform OAuth for private apps." if Context.private?
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

**File:** lib/shopify_api/utils/session_utils.rb (L58-71)
```ruby
        sig { params(shop: String, user_id: String).returns(String) }
        def jwt_session_id(shop, user_id)
          "#{shop}_#{user_id}"
        end

        sig { params(shop: String).returns(String) }
        def offline_session_id(shop)
          "offline_#{shop}"
        end

        sig { params(cookies: T::Hash[String, String]).returns(T.nilable(String)) }
        def cookie_session_id(cookies)
          cookies[Auth::Oauth::SessionCookie::SESSION_COOKIE_NAME]
        end
```

**File:** lib/shopify_api/auth/oauth/auth_query.rb (L33-43)
```ruby
        sig { override.returns(String) }
        def to_signable_string
          params = {
            code: code,
            host: host,
            shop: shop,
            state: state,
            timestamp: timestamp,
          }
          URI.encode_www_form(params)
        end
```
