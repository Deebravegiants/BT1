### Title
`SessionUtils.current_session_id` falls back to an unsigned, attacker-controlled cookie as the session-storage key even for embedded apps - ([File: lib/shopify_api/utils/session_utils.rb])

### Summary
`SessionUtils.current_session_id` is documented and shipped as the canonical way for a host app to resolve "which session belongs to this request." Even when `Context.embedded?` is true, if the request has no `shopify_id_token` (i.e. no `Authorization: Bearer` JWT), the method silently falls back to `cookie_session_id`, which returns `cookies['shopify_app_session']` **verbatim**, unauthenticated and unsigned, as the lookup key a host app uses to fetch a stored `Session`.

### Finding Description
The broken binding: the library implicitly assumes
`session_id_returned_to_caller == identity_the_caller_is_authorized_for`.
In reality, for the cookie path, `session_id_returned_to_caller == cookies['shopify_app_session']`, a value fully controlled by the requester's own browser/HTTP client — no cryptographic check ties it to any identity.

```ruby
def current_session_id(shopify_id_token, cookies, online)
  if Context.embedded?
    if shopify_id_token
      id_token = shopify_id_token.gsub("Bearer ", "")
      session_id_from_shopify_id_token(id_token: id_token, online: online)
    else
      # falling back to session cookie
      raise Errors::CookieNotFoundError, ... unless cookies && cookies[Auth::Oauth::SessionCookie::SESSION_COOKIE_NAME]
      cookie_session_id(cookies)
    end
  else
    ...
    cookie_session_id(cookies)
  end
end
``` [1](#0-0) 

```ruby
def cookie_session_id(cookies)
  cookies[Auth::Oauth::SessionCookie::SESSION_COOKIE_NAME]
end
``` [2](#0-1) 

The two ID formats produced elsewhere in the same class are fully derivable from public information:
```ruby
def jwt_session_id(shop, user_id)
  "#{shop}_#{user_id}"
end

def offline_session_id(shop)
  "offline_#{shop}"
end
``` [3](#0-2) 

`shop` is a public `myshopify.com` domain and `user_id` is a Shopify staff-account numeric id, which is not a secret in the same sense as an API key — it is routinely visible to any staff member of a shop (staff list, orders, webhook payloads). Because `jwt_session_id` mints IDs in exactly the `"#{shop}_#{user_id}"` shape, an attacker who can guess or observe a victim's `user_id` can construct the same string and place it directly in the `shopify_app_session` cookie.

Critically, the library's own documented usage pattern instructs developers to store this cookie as a **plain, non-signed** Rails cookie (`cookies[auth_response[:cookie].name] = { value: ..., secure: true, http_only: true }`), not `cookies.signed[...]` or `cookies.encrypted[...]`, meaning nothing in the documented flow cryptographically binds the cookie's value to the browser it was issued to: [4](#0-3) 

The gem's own authorization primitives — HMAC validation, `state` comparison, JWT `aud`/`sub` checks in `Auth::JwtPayload`, `Context.embedded?` — are all bypassed by this fallback branch, because this code path is reached specifically when no JWT is present, and the cookie itself carries none of those protections. `covers?`, `expired?`, and the proxy/embedded gates never get a chance to reject the forged identity because `cookie_session_id` doesn't consult any of them; it is a pure, unauthenticated string passthrough used directly as a storage lookup key by the host application (per this gem's own documentation, session storage/lookup is delegated entirely to the host app, using the ID string this method returns).

### Impact Explanation
A host app that follows this gem's documented cookie-storage pattern and uses `current_session_id`/`cookie_session_id` to key its session store is exposed to cross-user session confusion: an attacker who knows or guesses another staff user's numeric ID within the *same* shop (or any shop) can set their own `shopify_app_session` cookie to `<victim-shop>.myshopify.com_<victim-user-id>` and have the host app load and use the victim's stored online-access-token session for API calls made on the attacker's behalf. This is repeatable against any victim whose `shop` + `user_id` pair is known, and the "no Authorization header" precondition is trivially satisfiable by the attacker simply omitting the JWT App Bridge normally supplies.

### Likelihood Explanation
Preconditions: the host app must (a) use `SessionUtils.current_session_id`/`cookie_session_id` as documented instead of implementing its own tamper-proof session binding, and (b) actually key its session store by the returned string without further identity checks. Given the gem explicitly ships and documents this fallback behavior (rather than rejecting embedded requests lacking an `Authorization` header), and the ID format is intentionally deterministic and public-input-derived, exploitation cost for the attacker is a single crafted cookie value with no secrets required.

### Recommendation
Remove the cookie-based fallback for embedded apps entirely (embedded apps should be required to always present a verified session token via `Authorization` header), and for any remaining non-embedded cookie use, do not trust the raw cookie value as a storage key — bind it cryptographically (e.g., HMAC it with `api_secret_key`) so it cannot be forged offline, and never construct predictable IDs from public `shop`/`user_id` without an accompanying signature check at retrieval time.

### Proof of Concept
```ruby
# test/utils/session_utils_forge_test.rb
require "test_helper"

class SessionUtilsForgeTest < Minitest::Test
  def test_embedded_app_falls_back_to_forged_cookie_instead_of_rejecting
    ShopifyAPI::Context.setup(..., embedded_app: true, ...)

    victim_shop = "victim-shop.myshopify.com"
    victim_user_id = "42" # discovered via staff list / webhook payload, not a secret

    forged_cookie = { "shopify_app_session" => "#{victim_shop}_#{victim_user_id}" }

    # No Authorization header / shopify_id_token supplied by attacker
    session_id = ShopifyAPI::Utils::SessionUtils.current_session_id(nil, forged_cookie, true)

    # Binding under test: session_id should NOT equal the value jwt_session_id would mint
    # for the victim unless the caller proved possession of the victim's session token.
    assert_equal ShopifyAPI::Utils::SessionUtils.jwt_session_id(victim_shop, victim_user_id), session_id
    # ^ demonstrates the collapse: an unauthenticated cookie value is indistinguishable
    #   from a JWT-derived, cryptographically-verified session id.
  end
end
```
This shows `current_session_id` returns the victim's exact session-storage key from a forged cookie alone, with no JWT, HMAC, or `state` check ever invoked.

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

**File:** docs/usage/oauth.md (L186-193)
```markdown

    # Store the authorization cookie
    cookies[auth_response[:cookie].name] = {
      expires: auth_response[:cookie].expires,
      secure: true,
      http_only: true,
      value: auth_response[:cookie].value
    }
```
