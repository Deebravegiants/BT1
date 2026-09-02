### Title
Predictable, Unauthenticated Session-ID Cookie Enables Cross-Tenant Offline Session Hijacking - ([File: lib/shopify_api/utils/session_utils.rb], [File: lib/shopify_api/auth/session.rb])

### Summary
For non-embedded apps (and as an embedded fallback), this gem's documented session-retrieval flow trusts a raw, unauthenticated browser cookie value as the session identifier used to look up a shop's stored access token. The gem itself generates that identifier deterministically from public information — `"offline_#{shop}"` for offline sessions and `"#{shop}_#{associated_user.id}"` for online sessions — rather than from any secret or cryptographically verified value. An attacker who can supply an arbitrary `Cookie` header to the app (a normal HTTP capability, no XSS or credential theft required) can set `shopify_app_session` to a guessed identifier for a victim shop and, following the documented API, this gem will hand that exact string back as "the current session id" (`ShopifyAPI::Utils::SessionUtils.current_session_id`) for the host application to use to load the victim's session/access-token from storage.

### Finding Description
The intended, documented binding is: *cookie value == identifier of a session that this specific browser was actually issued after completing OAuth for a specific shop*. In practice, the code breaks this binding because the "session id" bytes returned by `cookie_session_id` are never validated as having been issued to the requester — they are simply read verbatim off the incoming cookie hash: [1](#0-0) 

```ruby
def cookie_session_id(cookies)
  cookies[Auth::Oauth::SessionCookie::SESSION_COOKIE_NAME]
end
```

This value is returned directly by `current_session_id` for both embedded (as a fallback) and non-embedded flows: [2](#0-1) 

Per the gem's own getting-started documentation, host applications are told to pass raw cookies from the request straight into this method and use the resulting string to load the persisted `Session`/access token: [3](#0-2) 

Crucially, the identifier that gets stored in that cookie is not random or secret — it is deterministically derived from the shop's public `myshopify.com` domain (and, for online sessions, the merchant's numeric associated-user id, which is also often discoverable): [4](#0-3) 

```ruby
if is_online
  associated_user = T.must(access_token_response.associated_user)
  associated_user_scope = access_token_response.associated_user_scope
  id = "#{shop}_#{associated_user.id}"
else
  id = "offline_#{shop}"
end
```

The cookie itself is set with `httponly`/`secure` flags in the documented examples, but those flags only prevent JavaScript from reading the cookie and require TLS — they do nothing to prevent an attacker from directly crafting an HTTP request to the app's own server with an arbitrary `Cookie: shopify_app_session=offline_victim-shop.myshopify.com` header, since the cookie is not signed, HMAC'd, or otherwise bound to a prior authenticated OAuth completion for that requester.

This is precisely the "session id derived from unauthenticated bytes" identity-binding failure class: the equality that should hold —
`session_id_presented_by_client == session_id_that_this_gem/host previously issued to this specific authenticated browser for this specific shop`
— is never checked. Any string satisfying the known, public `"offline_#{shop}"` or `"#{shop}_#{user_id}"` format is accepted as a valid session identifier.

### Impact Explanation
If the host application follows this gem's documented pattern literally (`SessionRepository.store_session`/`retrieve_session(id)` keyed by `session.id`, as shown in the gem's own OAuth docs), an attacker can:
1. Know or guess a victim's `myshopify.com` domain (public — shown in every Shopify storefront URL).
2. Send a request to the vulnerable app with `Cookie: shopify_app_session=offline_<victim>.myshopify.com`.
3. Have the gem's `current_session_id` return that exact attacker-chosen string, which the host app then uses to fetch the victim's persisted `Session` object — including the victim's stored offline `access_token`.
4. Use the returned access token to make Admin API calls as the victim shop.

This results in cross-tenant access and merchant access-token exfiltration, meeting the Critical impact bar. No credentials, secrets, or prior privileged access are required — only the ability to send an HTTP request to the app with a controlled `Cookie` header, which is a standard unprivileged internet capability.

### Likelihood Explanation
Likelihood is High for offline sessions specifically: the identifier space is a single deterministic string per shop domain, with no randomness at all (`"offline_#{shop}"`), so there is nothing to brute-force — the attacker computes it directly from the target's public storefront domain. Online session ids additionally require knowing an `associated_user.id`, which is lower effort than guessing a secret but non-trivial to enumerate; the offline case is the primary, most exploitable path. The vulnerability is triggered by exactly following this gem's own documented integration pattern (`docs/getting_started.md`), not by any host-app deviation from that guidance, so it is squarely a defect of this gem's design rather than of a third party's misuse.

### Recommendation
Do not use a deterministic, publicly-derivable string as the value trusted from an unauthenticated cookie. Options:
- Generate `Session#id` as a cryptographically random, unguessable value (e.g., `SecureRandom.uuid`) independent of `shop`/`user_id`, and use `shop`/`user_id` only as separate, non-identifying metadata fields on the stored record.
- If a deterministic id is required for lookups, require the session cookie value to be signed/HMAC'd (bound to `api_secret_key` or a per-app signing key) so that `cookie_session_id` can validate the signature before returning the id, mirroring the binding already enforced for `HmacValidator`/`JwtPayload`.
- Update `docs/getting_started.md` and `SessionUtils.current_session_id` to make clear that raw cookie values must never be used directly as trusted lookup keys without such verification.

### Proof of Concept
Given a non-embedded app built exactly per `docs/getting_started.md`:

```ruby
# Attacker knows the victim's public storefront domain, e.g. "victim-shop.myshopify.com"

# 1. Attacker crafts a raw HTTP request to the vulnerable app with a forged cookie:
# GET /some/authenticated/endpoint
# Cookie: shopify_app_session=offline_victim-shop.myshopify.com

# 2. Inside the app controller (following the gem's documented pattern):
session_id = ShopifyAPI::Utils::SessionUtils.current_session_id(nil, cookies.to_h, false)
# => "offline_victim-shop.myshopify.com"   (exactly the attacker-supplied value, unverified)

session = MyApp::SessionRepository.retrieve_session(session_id)
# => returns the victim shop's persisted Session, including its real access_token

# 3. Attacker's request is now processed using the victim's access_token,
#    granting cross-tenant access to the victim's Shopify Admin API data.
```

Because `Session.from` deterministically sets `id = "offline_#{shop}"` [5](#0-4)  and `cookie_session_id` performs no verification of the cookie's origin [1](#0-0) , this PoC requires no XSS, no leaked secrets, and no privileged access — only the ability to send a crafted `Cookie` header, which is available to any unprivileged internet user.

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

**File:** docs/getting_started.md (L41-52)
```markdown
### Sessions

Sessions are required to make requests with the REST or GraphQL clients. This Library provides helpers for creating sessions via OAuth. Helpers are provided to retrieve session ID from a HTTP request from an embedded Shopify app or cookies from non-embedded apps.

Session persistence is handled by the [ShopifyApp](https://github.com/Shopify/shopify_app) gem and is recommended for use in the Rails context. See that gem for documentation on how to use it.

#### Cookie
Cookie based authentication is not supported for embedded apps due to browsers dropping support for third party cookies due to security concerns. Non-embedded apps are able to use cookies for session storage/retrieval.

For *non-embedded* apps, you can pass the cookies into:
 - `ShopifyAPI::Utils::SessionUtils.current_session_id(nil, cookies, true)` for online (user) sessions or
 - `ShopifyAPI::Utils::SessionUtils.current_session_id(nil, cookies, false)` for offline (store) sessions.
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
