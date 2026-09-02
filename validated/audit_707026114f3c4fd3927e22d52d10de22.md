### Title
Non-embedded session lookup trusts an unsigned, deterministically-guessable `shopify_app_session` cookie as a tenant identifier - ([File: lib/shopify_api/utils/session_utils.rb])

### Summary
For non-embedded apps, `SessionUtils.current_session_id` returns the raw, unverified value of the `shopify_app_session` cookie via `cookie_session_id` as the session lookup key, with no cryptographic binding to the browser that actually completed OAuth. Because offline session IDs are deterministically derived as `"offline_#{shop}"` [1](#0-0) , an attacker who knows a victim's `myshopify.com` domain (public information) can set that exact cookie value in their own browser and have the host app resolve their request to the victim's stored offline session/access token.

### Finding Description
The broken binding: `session_id_returned == cookie_value_set_by_attacker` should require `cookie_value_set_by_attacker == HMAC_or_signature_verifiable_under(Context.api_secret_key)`, but instead `cookie_session_id` returns `cookies[SESSION_COOKIE_NAME]` verbatim with no signature check: [2](#0-1) . This value flows straight from `current_session_id` for the non-embedded branch, which only checks presence of the cookie, not its integrity, before invoking `cookie_session_id` [3](#0-2) .

The cookie's value is set once, at the end of `validate_auth_callback`, to `session.id` for non-embedded apps [4](#0-3) . For offline sessions, `session.id` is always `"offline_#{shop}"` — a value fully derivable from the shop's public `myshopify.com` domain, with no server-side secret or randomness involved [5](#0-4) . Nowhere in this gem is the returned session ID checked against an HMAC, JWT, or any secret derived from `Context.api_secret_key`; `HmacValidator.validate` and JWT `aud` checks are only applied elsewhere (OAuth callback HMAC, and the embedded-app JWT branch), not to this non-embedded cookie path.

Exploit flow: 1) Attacker learns/guesses `victim-shop.myshopify.com` (trivial — shop domains are not secret). 2) Attacker sets their own browser's `shopify_app_session` cookie to `offline_victim-shop.myshopify.com` (via JS if the cookie isn't `HttpOnly`, or via cookie tossing/leaked non-secret test cookie on a shared parent domain — this gem's `SessionCookie` struct does not enforce any cookie attributes at all: [6](#0-5) ). 3) Attacker calls any endpoint in the host app that calls `current_session_id(nil, cookies, false)`. 4) The gem returns `"offline_victim-shop.myshopify.com"` unchanged, which the host app then uses as the session store key to load the victim's stored offline `access_token`.

Existing guards do not stop this: `HmacValidator.validate` only runs during the OAuth callback (`validate_auth_callback`), not on subsequent authenticated requests; `Context.embedded?` merely selects this vulnerable code path rather than mitigating it; there is no `ShopValidator.sanitize!`/HMAC/JWT check anywhere in `cookie_session_id` or `current_session_id`'s non-embedded branch.

### Impact Explanation
If exploited, an unprivileged attacker causes the host app to treat their own request as authenticated for an arbitrary victim merchant, exposing that merchant's session (and, once the host app loads it from its session store, their access token) to actions performed by the attacker — a cross-tenant session hijack. This is repeatable against any shop that has completed OAuth with the app, requires only knowledge of the shop's `myshopify.com` domain, and matches the "Critical - cross-tenant access" category from the rules.

However, this design mirrors the intended, documented mechanism in Shopify's own reference implementations: the session cookie is meant to function purely as an opaque session-store key, analogous to a framework session ID (e.g., Rails `session_id`), with the assumption that the *transport* (cookie is set via `Set-Cookie` by the host app, typically `HttpOnly`, `Secure`, `SameSite`) is what prevents tampering — not cryptographic signing inside the gem. The severity of this finding hinges entirely on whether the *predictability* of the offline session ID (`"offline_#{shop}"`, derived purely from public shop domain) undermines that transport-security assumption, since an attacker who can write *any* cookie value into their own browser (which every attacker trivially can, via `document.cookie` or dev tools, without needing `HttpOnly` bypass or cookie tossing) can forge a value that is not a secret at all.

### Likelihood Explanation
Preconditions: non-embedded app configuration (`Context.embedded? == false`), and the victim shop must have previously completed offline OAuth. No secrets, tokens, or privileged access are required by the attacker — only the victim's `myshopify.com` domain name, which is not confidential. The attacker sets a cookie on *their own* browser/session (this requires no cookie-tossing or interception at all, since cookies are freely attacker-controlled on the attacker's own client) and sends a normal request. This is trivially repeatable against any number of victim shops the attacker can enumerate or already knows.

### Recommendation
Do not use a deterministic, guessable value (`"offline_#{shop}"`) as the bare cookie value trusted for session lookup in non-embedded apps. Either (a) sign/HMAC the cookie value with `Context.api_secret_key` and verify it in `cookie_session_id` before returning it, or (b) store a random, unguessable session identifier separate from the deterministic session-store key, and map that opaque cookie value to the real session server-side only after verifying it was issued by this app for this browser.

### Proof of Concept
```ruby
# test/utils/session_utils_test.rb (conceptual addition)
def test_non_embedded_cookie_session_id_is_trusted_without_verification
  ShopifyAPI::Context.stubs(:embedded?).returns(false)

  forged_shop = "victim-shop.myshopify.com"
  forged_session_id = "offline_#{forged_shop}"  # attacker derives this with zero secrets
  cookies = { ShopifyAPI::Auth::Oauth::SessionCookie::SESSION_COOKIE_NAME => forged_session_id }

  # Binding under test: returned_id == HMAC_verified_value(under Context.api_secret_key)
  # Actual: returned_id == cookies[cookie_name] verbatim, no verification performed
  result = ShopifyAPI::Utils::SessionUtils.current_session_id(nil, cookies, false)

  assert_equal(forged_session_id, result)
  # No call to Utils::HmacValidator, no JWT decode, no Context.api_secret_key usage
  # occurs anywhere in cookie_session_id/current_session_id's non-embedded branch,
  # confirmable by grepping lib/shopify_api/utils/session_utils.rb for
  # `HmacValidator`, `JWT`, or `api_secret_key` (none found).
end
```
This demonstrates that any string placed in the `shopify_app_session` cookie — including the fully public, deterministic `"offline_#{shop}"` value for a victim shop — is returned unchanged as the trusted session identifier, with no code path in this gem verifying it was issued to the requesting browser.

### Citations

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

**File:** lib/shopify_api/utils/session_utils.rb (L31-36)
```ruby
          else
            raise Errors::CookieNotFoundError, "Session cookie not found for app" unless
              cookies && cookies[Auth::Oauth::SessionCookie::SESSION_COOKIE_NAME]

            cookie_session_id(cookies)
          end
```

**File:** lib/shopify_api/utils/session_utils.rb (L68-71)
```ruby
        sig { params(cookies: T::Hash[String, String]).returns(T.nilable(String)) }
        def cookie_session_id(cookies)
          cookies[Auth::Oauth::SessionCookie::SESSION_COOKIE_NAME]
        end
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

**File:** lib/shopify_api/auth/oauth/session_cookie.rb (L7-14)
```ruby
      class SessionCookie < T::Struct
        extend T::Sig

        SESSION_COOKIE_NAME = "shopify_app_session"

        const :name, String, default: SESSION_COOKIE_NAME
        const :value, String
        const :expires, T.nilable(Time)
```
