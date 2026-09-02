Confirmed: `begin_auth` sets a random-nonce cookie only for CSRF protection during the OAuth handshake [1](#0-0) , but once `validate_auth_callback` succeeds, the gem overwrites that cookie with the deterministic, non-random `session.id` value for non-embedded apps [2](#0-1) . This new cookie carries no signature, HMAC, or opaque random token — its value literally equals the same formula used by `jwt_session_id`/`offline_session_id` [3](#0-2) , and any downstream call to `current_session_id`/`cookie_session_id` performs nothing but a hash lookup with no ownership check [4](#0-3) .

### Title
Non-embedded session cookie value equals the predictable, unsigned session id, letting a client forge the cookie to impersonate another shop's session - (File: lib/shopify_api/auth/oauth.rb, lib/shopify_api/utils/session_utils.rb)

### Summary
For non-embedded apps, `ShopifyAPI::Auth::Oauth.validate_auth_callback` sets the session cookie's `value` to the raw, deterministic `session.id` (`"offline_#{shop}"` or `"#{shop}_#{user_id}"`) with no signature or random component. `ShopifyAPI::Utils::SessionUtils.cookie_session_id`/`current_session_id` then trust this cookie value verbatim as the session identifier to hand back to the host app's session store, performing only a hash lookup with zero ownership/ACL verification.

### Finding Description
The broken binding: `cookie_value_presented_by_client == session_id_the_server_issued_to_that_specific_client`. Trace: during `begin_auth`, the cookie is a `SecureRandom.alphanumeric(15)` nonce used solely to compare against `auth_query.state` for CSRF protection at callback time [5](#0-4) . Once that one-time check passes, the gem replaces the cookie value with the final session id itself for non-embedded apps: `SessionCookie.new(value: session.id, expires: ...)` [6](#0-5) . From that point forward, on every subsequent request the host app calls `SessionUtils.current_session_id(nil, cookies, online)`, which for non-embedded apps unconditionally returns `cookie_session_id(cookies)` [7](#0-6) , and `cookie_session_id` is a single hash lookup with no signature check, no per-client binding, and no comparison against any server-side value tied to the requester [4](#0-3) . The documented integration pattern stores this cookie as a **plain, unsigned** Rails cookie (`cookies[name] = { value: ..., secure: true, http_only: true }`, not `cookies.signed[name]`), so its value is fully attacker-controlled on the attacker's own HTTP client. Because the session id format is deterministic (`offline_#{shop}` / `#{shop}_#{user_id}`) and shop domains are not secret, an attacker who learns or guesses shop B's `myshopify.com` domain (e.g. from a support ticket, log line, or simple enumeration) can set their own `shopify_app_session` cookie to `offline_shopB.myshopify.com` and send it to the host app. The app calls `current_session_id`, gets back that exact string, looks it up in its own `SessionRepository`, and returns shop B's stored `Session` (including `access_token`) to the attacker's request. None of the existing guards intervene: `HmacValidator.validate` and the `state` comparison only run once, during the OAuth callback itself, not on this later cookie-based lookup path; `JwtPayload`'s `aud` check and `HttpRequest#verify` are unrelated to the cookie path; `Context.setup?`/`private?`/`embedded?` are pure control-flow checks. The equality the design implicitly assumes ("only the browser the server issued this cookie to can present it") does not hold, because the cookie is neither random nor signed by the gem.

### Impact Explanation
A successful attacker obtains another merchant's stored `Session` (including `access_token`) via the host app's normal request-authorization path, i.e., cross-tenant access — one shop's data/API access reachable by an unrelated attacker who only needed to know or guess the victim's shop domain. This is repeatable against any shop whose domain the attacker can learn, without needing credentials, `api_secret_key`, or any signed artifact. Blast radius is bounded by whatever the host app's `SessionRepository` returns for that id (typically the full Shopify access token for that shop), matching the Critical "cross-tenant access" category.

### Likelihood Explanation
Preconditions: the host app must be non-embedded (or embedded falling back to the cookie path when no `shopify_id_token` is present) and must follow the gem's documented pattern of setting the returned `SessionCookie` as a plain (unsigned) cookie, as shown in `docs/usage/oauth.md`. Attacker cost is minimal — no secrets required, just knowledge/guess of the target shop's domain and the ability to set an arbitrary cookie header on their own client, which is explicitly within the stated attacker capabilities. This is not a live-shop dependent issue; it is directly reproducible via unit tests of `SessionUtils` and `Oauth.validate_auth_callback`, since both show the cookie value is deterministic and the lookup performs no verification.

### Recommendation
Do not use the raw, deterministic session id as the session cookie's value. Instead, issue an opaque, cryptographically random token as the cookie value (mapped server-side to the real session id in the host app's store), or have the gem HMAC/sign the cookie value with `api_secret_key` and verify that signature inside `cookie_session_id` before trusting it. At minimum, update the documented integration guidance to require `cookies.signed`/`cookies.encrypted` rather than plain cookies, and add an explicit ownership check in `SessionUtils.cookie_session_id`.

### Proof of Concept
```ruby
# test/utils/session_utils_forgery_test.rb
require "test_helper"

class SessionUtilsForgeryTest < Test::Unit::TestCase
  def test_cookie_session_id_accepts_forged_value_for_another_shop
    ShopifyAPI::Context.stubs(:embedded?).returns(false)

    # Attacker never completed OAuth for shop-b; they merely learned/guessed
    # the deterministic offline session id format and set it as their own cookie.
    forged_victim_session_id = "offline_shop-b.myshopify.com"
    attacker_supplied_cookies = {
      ShopifyAPI::Auth::Oauth::SessionCookie::SESSION_COOKIE_NAME => forged_victim_session_id,
    }

    returned_id = ShopifyAPI::Utils::SessionUtils.current_session_id(nil, attacker_supplied_cookies, false)

    # Binding under test: cookie_value_presented_by_client == session issued to THIS client.
    # It should NOT equal a victim's session id with no ownership proof, but it does:
    assert_equal(forged_victim_session_id, returned_id)

    # Grep-level proof there is no ACL/signature check in the method body:
    source = ShopifyAPI::Utils::SessionUtils.method(:cookie_session_id).source_location
    body = File.read(source[0])
    refute_match(/hmac|signature|verify|owner/i, body.lines[source[1]..source[1] + 3].join)
  end
end
```
This demonstrates that `cookie_session_id`/`current_session_id` return whatever session id string is present in the attacker-controlled cookie hash, with no verification tying it back to the session the server actually issued to that client.

### Citations

**File:** lib/shopify_api/auth/oauth.rb (L36-38)
```ruby
          state = SecureRandom.alphanumeric(NONCE_LENGTH)

          cookie = SessionCookie.new(value: state, expires: Time.now + 60)
```

**File:** lib/shopify_api/auth/oauth.rb (L67-71)
```ruby
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

**File:** lib/shopify_api/utils/session_utils.rb (L31-36)
```ruby
          else
            raise Errors::CookieNotFoundError, "Session cookie not found for app" unless
              cookies && cookies[Auth::Oauth::SessionCookie::SESSION_COOKIE_NAME]

            cookie_session_id(cookies)
          end
```

**File:** lib/shopify_api/utils/session_utils.rb (L58-66)
```ruby
        sig { params(shop: String, user_id: String).returns(String) }
        def jwt_session_id(shop, user_id)
          "#{shop}_#{user_id}"
        end

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
