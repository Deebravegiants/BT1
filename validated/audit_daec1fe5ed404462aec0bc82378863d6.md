### Title
Non-embedded session cookie value equals the deterministic, secret-free `offline_session_id(shop)`, letting any attacker forge a session cookie to hijack another shop's offline session - (File: `lib/shopify_api/utils/session_utils.rb`, `lib/shopify_api/auth/oauth.rb`)

### Summary
For non-embedded apps, `ShopifyAPI::Auth::Oauth.validate_auth_callback` sets the `shopify_app_session` cookie's value to `session.id`, which for offline sessions is exactly `SessionUtils.offline_session_id(shop) == "offline_#{shop}"` — a pure, secret-free string interpolation of the public shop domain. `SessionUtils.current_session_id` then, for non-embedded requests, simply returns whatever value is present in that cookie (`cookie_session_id`) with no signature, HMAC, or freshness check. Since any attacker can compute `"offline_#{shop}"` for any public `*.myshopify.com` name, they can set that exact string as their own `Cookie` header on a direct HTTP request to the app and have the app resolve/load that shop's stored offline session (and its access token) as if they were an authenticated party for that shop.

### Finding Description
The binding the app relies on is: `current_session_id(shopify_id_token, cookies, online=false) == session.id` should imply "the caller previously completed OAuth and received this exact cookie from the server for this shop." In code:

- `SessionCookie` value is set directly to `session.id` on OAuth callback for non-embedded flows: [1](#0-0) 
- `offline_session_id` is a pure deterministic function of `shop`, with no secret or salt: [2](#0-1) 
- For non-embedded apps, `current_session_id` trusts the raw cookie value verbatim, with no HMAC/signature check on the value itself: [3](#0-2) 
- `cookie_session_id` returns the cookie's contents unmodified: [4](#0-3) 

Root cause: the "session id" doubles as both a storage key and, via this cookie mechanism, an implicit bearer credential — but it carries no unpredictability or cryptographic binding to the fact that OAuth for that specific shop actually completed on that specific client. Because `shop` names are public/enumerable, and `"offline_#{shop}"` requires no secret to compute, an attacker's own HTTP client (not a victim's browser, not a MITM) can simply send `Cookie: shopify_app_session=offline_<target>.myshopify.com` directly to the app. If `<target>` has installed the app (i.e., an offline session already exists in the host's `SessionStorage`), the app resolves that session id, loads the stored session (including its `access_token`), and treats the attacker's request as authenticated for that tenant.

None of the existing guards intercept this path: `HmacValidator.validate` only checks the OAuth *callback* query params against `client_secret`, not the later cookie-driven session restoration; `ShopValidator.sanitize!` only validates shop string format; the OAuth `state` comparison only protects the callback step (`lib/shopify_api/auth/oauth.rb` lines 67-71); `JwtPayload`'s `aud` check applies only to the embedded/JWT branch (`Context.embedded?` is false here); and `Context.setup?/private?/embedded?` do not add any authentication to the raw cookie value. There is no code path in `session_utils.rb` or `oauth.rb` that binds the cookie value to a non-guessable secret for non-embedded sessions.

### Impact Explanation
An attacker who merely knows (or brute-forces) a target's `*.myshopify.com` domain can present a forged `shopify_app_session` cookie and have the host app resolve and use that shop's stored offline `access_token` on their behalf — this is cross-tenant access to another merchant's access token via a purely predictable identifier, matching the Critical category ("cross-tenant access", "theft ... of a merchant access token"). It is fully repeatable: the attacker can iterate over any list of shop names (Shopify shop names are commonly discoverable/guessable) and mount a scripted sweep, since each candidate id is a deterministic, zero-cost string computation with no rate-limited secret to guess.

### Likelihood Explanation
Preconditions: the app is non-embedded (or falls back to cookie auth), uses this gem's documented `current_session_id`/`SessionCookie` mechanism, and the host's `SessionStorage` performs a keyed lookup by session id (the standard, documented usage). The attacker needs no credentials, no MITM, and no access to `api_secret_key` — only the ability to send an HTTP request with a custom `Cookie` header, which is trivially within the stated attacker capabilities. The only "cost" is that the target shop must already have an offline session stored (i.e., have installed the app), which is the normal state for any live installed shop.

### Recommendation
Do not use the raw, deterministic session id as the cookie's bearer value. Instead, either (a) sign/MAC the cookie value (e.g., HMAC with `Context.api_secret_key`) and verify the MAC in `current_session_id`/`cookie_session_id` before trusting it, or (b) use an opaque, cryptographically random session cookie value that is separately mapped to the deterministic session id server-side, so that possession of the cookie — not knowledge of the shop name — is what grants access.

### Proof of Concept
```ruby
# test/utils/session_utils_forgery_test.rb
require "test_helper"

class SessionUtilsForgeryTest < Minitest::Test
  def test_offline_session_id_is_pure_deterministic_function_of_shop
    shops = (1..50).map { |i| "attacker-guessed-shop-#{i}.myshopify.com" }
    ids = shops.map { |s| ShopifyAPI::Utils::SessionUtils.offline_session_id(s) }

    # Equality claimed broken: attacker-computed id == server-issued cookie value
    shops.each_with_index do |shop, i|
      assert_equal "offline_#{shop}", ids[i]
    end
    assert_equal ids.uniq.length, ids.length # fully predictable & distinct per shop
  end

  def test_non_embedded_current_session_id_trusts_forged_cookie_verbatim
    ShopifyAPI::Context.setup(
      api_key: "key", api_secret_key: "secret", host_name: "app.example.com",
      scope: "read_products", is_embedded: false, is_private: false, api_version: "2023-01",
    )

    target_shop = "victim-shop.myshopify.com"
    forged_id = ShopifyAPI::Utils::SessionUtils.offline_session_id(target_shop)

    # Attacker never received this cookie from the server; computed it purely from public shop name
    forged_cookies = { ShopifyAPI::Auth::Oauth::SessionCookie::SESSION_COOKIE_NAME => forged_id }

    resolved_id = ShopifyAPI::Utils::SessionUtils.current_session_id(nil, forged_cookies, false)

    assert_equal forged_id, resolved_id
    assert_equal "offline_#{target_shop}", resolved_id
    # If the host's SessionStorage has an entry keyed by resolved_id (i.e., victim shop installed
    # the app), the app will load victim's session/access_token for this attacker-controlled request.
  end
end
```
This demonstrates both halves of the broken binding: `offline_session_id(shop)` is a pure, secret-free function of a public value, and `current_session_id` for non-embedded apps returns the untrusted cookie value verbatim with no cryptographic check, so an attacker-forged cookie is indistinguishable from a legitimately issued one.

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

**File:** lib/shopify_api/utils/session_utils.rb (L31-36)
```ruby
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
