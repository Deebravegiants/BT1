### Title
`SessionUtils.current_session_id` accepts an unsigned, attacker-guessable cookie as the session identity for embedded apps whenever the `Authorization` header is absent - (File: `lib/shopify_api/utils/session_utils.rb`)

### Summary
`SessionUtils.current_session_id` is supposed to require a cryptographically verified Shopify ID token for embedded apps, falling back to a cookie only for non-embedded apps where the cookie is the sole trust anchor. Instead, when `Context.embedded?` is `true` but no `shopify_id_token` is supplied, the code silently takes the same unverified cookie path used by non-embedded apps, and because `SessionUtils.offline_session_id(shop)` is the bare, secret-free string `"offline_#{shop}"`, an attacker who merely knows a target's public shop domain can compute and forge that exact value in a `Cookie` header to be treated as an authenticated session for that shop.

### Finding Description
The binding that should hold is:

`current_session_id(header, cookies, online) == the shop identity cryptographically proven for *this* request` (via a Shopify-signed JWT `sub`/`shop` claim when embedded, or a value the app itself minted and bound to the browser's session when not embedded).

The actual code:
```ruby
def current_session_id(shopify_id_token, cookies, online)
  if Context.embedded?
    if shopify_id_token
      id_token = shopify_id_token.gsub("Bearer ", "")
      session_id_from_shopify_id_token(id_token: id_token, online: online)
    else
      # falling back to session cookie
      raise Errors::CookieNotFoundError, "..." unless cookies && cookies[Auth::Oauth::SessionCookie::SESSION_COOKIE_NAME]
      cookie_session_id(cookies)
    end
  else
    raise Errors::CookieNotFoundError, "..." unless cookies && cookies[Auth::Oauth::SessionCookie::SESSION_COOKIE_NAME]
    cookie_session_id(cookies)
  end
end
``` [1](#0-0) 

`cookie_session_id` performs zero verification — it just echoes back whatever the caller put in the `cookies` hash:
```ruby
def cookie_session_id(cookies)
  cookies[Auth::Oauth::SessionCookie::SESSION_COOKIE_NAME]
end
``` [2](#0-1) 

and `offline_session_id` is a pure, secret-free format string:
```ruby
def offline_session_id(shop)
  "offline_#{shop}"
end
``` [3](#0-2) 

Root cause: the `else` branch inside `if Context.embedded?` is byte-for-byte identical to the fully non-embedded branch — it performs no signature check, no HMAC check, and no correlation to the shop that the request claims to be from. It only checks that *some* cookie is present (`unless cookies && cookies[...]`), not that the cookie is authentic. Since `shop` (a `*.myshopify.com` domain) is public information and `offline_session_id` applies no secret transformation to it, the resulting identifier `"offline_#{shop}"` is fully predictable by anyone who knows the shop's domain — which is public/discoverable for any store.

Exploit flow: An attacker who is never installed on the victim's shop, and holds no secret, sends a raw HTTP request directly to an embedded app's endpoint that calls `SessionUtils.current_session_id`:
- Omit the `Authorization` header (or send no `shopify_id_token`).
- Set `Cookie: shopify_app_session=offline_victim-shop.myshopify.com`.

Because `Context.embedded?` is `true` but `shopify_id_token` is `nil`, the code takes the cookie fallback and returns `"offline_victim-shop.myshopify.com"` verbatim as the "current session id" — exactly the value `offline_session_id` would have produced for that shop. If the host app (as documented) uses this id to look up a persisted `Session` object and treats the result as the authenticated session for the request, the attacker causes the app to load and use the victim shop's stored offline `access_token` for that request, without ever having gone through the shop's OAuth/session-token flow.

None of the existing guards intervene: `Auth::JwtPayload`'s `aud`/`iss`/`sub` checks are never invoked because `shopify_id_token` is `nil`; `HmacValidator.validate` and `ShopValidator.sanitize!` are only used in the OAuth begin/callback flow, not in this runtime session-lookup path; and `Context.embedded?` being `true`, rather than blocking the fallback, is precisely the condition whose `else` branch performs the unverified read.

### Impact Explanation
This breaks the single-identity invariant: the shop identity used to select a persisted `Session`/`access_token` is not derived from the same authenticated source (a signed JWT) that the embedded model requires — it is taken from an attacker-supplied, unauthenticated HTTP header value that is trivially predictable. If exploited against a host app that follows the gem's documented pattern (`current_session_id` → look up stored session → make API calls with its `access_token`), this constitutes theft/misuse of a merchant's Admin API access token for an arbitrary victim shop, matching the Critical impact category. It is repeatable against any shop domain the attacker knows (shop domains are effectively public), with no per-shop secret required and no rate limit consideration.

### Likelihood Explanation
Preconditions: the app must be `is_embedded: true` (the common configuration for most Shopify apps) and must call `SessionUtils.current_session_id` (or equivalently rely on `cookie_session_id`) to resolve session identity, then trust the returned id for a session-store lookup — this is exactly the documented usage pattern in `docs/getting_started.md`. Attacker cost is a single unauthenticated HTTP request with a guessed cookie value; no credentials, no secrets, no timing attack, and no live-shop interaction are required to construct the forged identifier. This is fully feasible and repeatable against any target shop domain.

### Recommendation
Do not allow the cookie fallback to be reached for embedded apps at all — for embedded apps, require a valid `shopify_id_token`/`Authorization` header and never fall back silently to an unauthenticated cookie value. If a cookie fallback must remain for legacy reasons, bind the cookie value to a server-verifiable secret (e.g., HMAC-sign the cookie value with `api_secret_key` at issuance and verify the signature before trusting it), rather than trusting the raw session-id string supplied by the client.

### Proof of Concept
```ruby
# test/utils/session_utils_test.rb (new test)
def test_embedded_app_current_session_id_accepts_forged_offline_cookie_without_auth_header
  ShopifyAPI::Context.stubs(:embedded?).returns(true)

  victim_shop = "victim-shop.myshopify.com"
  forged_id = ShopifyAPI::Utils::SessionUtils.offline_session_id(victim_shop) # "offline_victim-shop.myshopify.com"

  # Attacker sends NO Authorization header, only a forged Cookie header they computed themselves
  cookies = { ShopifyAPI::Auth::Oauth::SessionCookie::SESSION_COOKIE_NAME => forged_id }

  # BUG: this should raise (embedded apps must present a signed id token), but instead
  # it returns the attacker-forged id, matching offline_session_id(victim_shop) exactly.
  result = ShopifyAPI::Utils::SessionUtils.current_session_id(nil, cookies, false)

  assert_equal(forged_id, result) # demonstrates the divergence: unauthenticated cookie == trusted session id
end
```
This test demonstrates that with no `Authorization`/`shopify_id_token` present, an embedded app configured per `Context.embedded? == true` still accepts an arbitrary, attacker-computed cookie value equal to `offline_session_id(shop)` as the resolved session id, contrary to the expected behavior of rejecting the request outright (as validated by the existing `test_embedded_app_current_session_id_raises_cookie_not_found_error` only for the *no-cookie* case, not the forged-cookie case). [4](#0-3)

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

**File:** test/utils/session_utils_test.rb (L91-104)
```ruby
      def test_embedded_app_current_session_id_raises_cookie_not_found_error
        ShopifyAPI::Context.stubs(:embedded?).returns(true)

        [
          nil,
          {},
          { "not-session-cookie-name": "not-this-cookie" },
        ].each do |cookies|
          error = assert_raises(ShopifyAPI::Errors::CookieNotFoundError) do
            ShopifyAPI::Utils::SessionUtils.current_session_id(nil, cookies, true)
          end
          assert_equal("JWT token or Session cookie not found for app", error.message)
        end
      end
```
