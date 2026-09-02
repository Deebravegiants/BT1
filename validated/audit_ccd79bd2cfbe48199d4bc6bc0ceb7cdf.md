### Title
Predictable, unsalted offline session ID used as bare session-cookie identifier enables cross-tenant session hijacking - ([File: lib/shopify_api/auth/session.rb])

### Summary

### Finding Description
For non-embedded (cookie-based) OAuth flows, `ShopifyAPI::Auth::Session.from` derives the session `id` deterministically from only the `shop` domain: `id = "offline_#{shop}"` for offline tokens, or `"#{shop}_#{associated_user.id}"` for online tokens. [1](#0-0) 

This `id` is placed, in cleartext, directly as the value of the browser session cookie by `Oauth.validate_auth_callback`: [2](#0-1) 

On subsequent requests, `Utils::SessionUtils.current_session_id` for non-embedded apps (or the embedded fallback path) returns this cookie value with **no verification whatsoever** — no HMAC, no signature, no binding to any secret or to the browser/session that originally completed OAuth: [3](#0-2) [4](#0-3) 

The host application is expected to use this returned `id` as the lookup key into its session store (which holds the real access token) — this is exactly the flow documented in `docs/usage/oauth.md` (`MyApp::SessionRepository.store_session`/lookup pattern).

The identity binding that should hold is: **cookie value == a value only derivable by someone who completed the real OAuth handshake for a specific shop**. Instead, for offline sessions the binding degenerates to: **cookie value == a string built purely from `shop`, which is public information** (shop domains are guessable/enumerable, e.g. `{name}.myshopify.com`). Any unprivileged internet user who knows or guesses a target shop's domain can compute `"offline_#{shop}"` themselves — no secret, no access token, and no prior authentication step is required to construct a value that is functionally indistinguishable from a legitimately-issued session cookie.

This is analogous to the reported `executeMigration()` bug: there, `successMigrated`/vote-count checks were insufficient to bind execution to a real quorum, letting anyone drive privileged state. Here, the "check" binding a cookie to a genuine authenticated session is effectively absent for the offline/non-embedded flow — the session identifier is derived from unauthenticated, public bytes (the shop name) rather than from any value that only the legitimate OAuth completion could produce.

### Impact Explanation
If a host application (following this gem's documented pattern) persists `Session` objects keyed by `session.id` and trusts the incoming cookie value to fetch the corresponding stored session/access token, an attacker who sets `Cookie: shopify_app_session=offline_target-shop.myshopify.com` in their own request is treated as the authenticated context for `target-shop`. Because the access token itself lives in the host's session store and is retrieved via this predictable key, this results in cross-tenant session hijacking / authentication bypass without ever needing the target's credentials, the app's `client_secret`, or any token — satisfying the Critical bar of "cross-tenant access" / "authentication bypass" via a "session id derived from unauthenticated bytes."

### Likelihood Explanation
Likelihood is high for any app that stores sessions by `id` and trusts the gem-provided `session.id`/cookie contract as documented, since:
- Shop domains are not secret (they're visible in URLs, App Store listings, redirect flows, etc.).
- No brute force or race condition is needed — the ID is a pure, static function of public data (`"offline_#{shop}"`), so it is exact, not merely guessable in a search space.
- The library performs zero validation on the incoming cookie value before treating it as a session identifier (`cookie_session_id` at `lib/shopify_api/utils/session_utils.rb:68-71` simply echoes it back).

The only mitigating factor is that this only manifests when the host's session storage keys sessions by this raw `id` and exposes cross-user lookup without further authentication of the cookie itself, which is exactly the pattern the gem's own documentation prescribes for the non-embedded flow (`docs/usage/oauth.md`, `MyApp::SessionRepository`).

### Recommendation
- Do not derive session IDs solely from public data (`shop`, `shop_user_id`); include a cryptographically random, unguessable component (e.g., `SecureRandom.uuid`, already used as the default in `Session.new` at `lib/shopify_api/auth/session.rb:72`) as the actual cookie/session key even for offline sessions, and store `"offline_#{shop}"` only as a secondary/lookup attribute, not as the externally-facing session cookie value.
- Alternatively, sign or encrypt the session cookie value (e.g., HMAC with `api_secret_key`) so that `cookie_session_id` can cryptographically verify the value was issued by the app rather than trusting it verbatim.
- Document explicitly that host applications must never use the deterministic `offline_#{shop}` / `#{shop}_#{user_id}` id as an authentication credential for looking up access tokens without an additional secret-bound check.

### Proof of Concept
1. App is installed on `victim-shop.myshopify.com` (any unprivileged actor can observe/guess this domain, e.g. via Shopify's public app-store install flow or naming conventions).
2. Attacker sends a request to the app with header:
   `Cookie: shopify_app_session=offline_victim-shop.myshopify.com`
3. The host app, following the gem's documented flow, calls `ShopifyAPI::Utils::SessionUtils.current_session_id(nil, cookies, false)`, which returns `"offline_victim-shop.myshopify.com"` unchanged (`lib/shopify_api/utils/session_utils.rb:31-37`, `68-71`), with no verification.
4. The host looks up its session store using this ID and retrieves `victim-shop`'s real `Session` (including `access_token`), because that is exactly the ID computed by `Session.from` at OAuth-completion time (`lib/shopify_api/auth/session.rb:108-117`).
5. Attacker now operates using `victim-shop`'s access token/session context without ever completing OAuth for that shop.

Note: Full exploitation depends on the exact session-storage implementation used by the host application (outside this gem), which could not be verified from the indexed files; the vulnerable, unauthenticated derivation and pass-through of the session identifier itself is confirmed within this gem's code as cited above.

### Citations

**File:** lib/shopify_api/auth/session.rb (L108-117)
```ruby
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

**File:** lib/shopify_api/utils/session_utils.rb (L31-37)
```ruby
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
