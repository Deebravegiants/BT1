### Title
Predictable, non-random session identifiers enable session fixation / cross-tenant session hijack - (File: `lib/shopify_api/auth/session.rb`, `lib/shopify_api/auth/oauth.rb`)

### Summary
The identity binding that should hold is: `session_cookie_value == a value that only Shopify OAuth (or a valid JWT signed with the app's client secret) could have produced for that specific shop/user`. Instead, for offline sessions the library computes the session id — which is also used verbatim as the browser session cookie value — as `"offline_#{shop}"`, a deterministic string built solely from the shop's public `.myshopify.com` domain, with no random or secret component. Anyone who merely knows a target shop's domain (public information) can compute the exact same identifier without ever completing OAuth or possessing an HMAC/JWT signed by the app's `client_secret`.

### Finding Description
`ShopifyAPI::Auth::Session.from` derives the session `id` deterministically: [1](#0-0) 

For offline (non-user, app-level) tokens, `id = "offline_#{shop}"` — a pure function of the shop domain, with no nonce, secret, or random component.

This `id` is then used directly as the value of the browser-facing session cookie for non-embedded apps in `ShopifyAPI::Auth::Oauth.validate_auth_callback`: [2](#0-1) 

The cookie carries no HMAC, signature, or other integrity check of its own (`SessionCookie` is a plain struct): [3](#0-2) 

The library's own documentation instructs consuming apps to persist and retrieve `ShopifyAPI::Auth::Session` objects keyed by this same `id`/cookie value, and to trust that lookup as "the session" for making authenticated API calls: [4](#0-3) 

Because the offline session id contains no secret material, the equality that should distinguish "a shop that completed OAuth" from "a shop whose domain is merely known" collapses: `id(shop) = f(shop)` is trivially computable by anyone. An unprivileged internet user who knows (or guesses) a target merchant's `myshopify.com` domain — which is routinely public (storefront URL, app-store listing, embedded-app `host` param, etc.) — can compute `"offline_#{victim_shop}"` and set it as their own browser's `shopify_app_session` cookie, exactly as the documented flow does, without ever running through `begin_auth`/`validate_auth_callback` or presenting a valid HMAC/JWT.

The online-session id (`"#{shop}_#{associated_user.id}"`) has the same weakness, differing only by the additional (often small/sequential) numeric user id.

### Impact Explanation
If the host application follows this gem's documented session-storage pattern (look up `Session` by cookie/id and treat a hit as "authenticated"), an attacker who knows a victim shop's domain can fixate/forge that shop's session identifier in their own browser and have the application retrieve and act on the victim shop's stored `Session`, including its `access_token`. This constitutes cross-tenant access and potential access-token exposure/misuse without ever completing OAuth or possessing the app's `client_secret` — matching the "session fixation" / cross-tenant access impact class.

### Likelihood Explanation
Exploitability only requires knowledge of a target shop's `.myshopify.com` domain, which is not secret. No TLS interception, credential theft, or privileged access is needed — only the ability to set a cookie value in one's own browser and rely on the host app's documented, straightforward session-retrieval logic.

### Recommendation
Do not derive session identifiers solely from public shop/user identifiers. Include a per-session random/secret component (e.g., `SecureRandom.uuid`, as already used as the default `id` when not explicitly supplied) in the identifier that is actually exposed via the cookie, and avoid encouraging host apps to trust a bare, guessable string as proof of an authenticated session. If a deterministic key is still needed for storage lookups, separate it from the value placed in the browser cookie, and ensure the cookie value itself is unpredictable/signed.

### Proof of Concept
1. Attacker learns victim's shop domain, e.g. `victim-shop.myshopify.com` (public).
2. Attacker computes offline session id per `Session.from`: `"offline_victim-shop.myshopify.com"` [5](#0-4) .
3. Attacker sets this exact string as the `shopify_app_session` cookie in their own browser (mirroring how `validate_auth_callback` sets `cookie.value = session.id`) [6](#0-5) .
4. Visiting the app, the host application (following the documented pattern) retrieves the stored `Session` for that id/shop and treats the attacker as authenticated for `victim-shop`, exposing the victim's stored access token / API access.

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

**File:** lib/shopify_api/auth/oauth.rb (L100-112)
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

          { session: session, cookie: cookie }
```

**File:** lib/shopify_api/auth/oauth/session_cookie.rb (L1-26)
```ruby
# typed: strict
# frozen_string_literal: true

module ShopifyAPI
  module Auth
    module Oauth
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
      end
    end
```

**File:** docs/usage/oauth.md (L253-266)
```markdown
    # Update cookies with the authorized access token from result
    cookies[auth_result[:cookie].name] = {
      expires: auth_result[:cookie].expires,
      secure: true,
      http_only: true,
      value: auth_result[:cookie].value
    }

    # Store the Session object if your app has a DB/file storage for session persistence
    # This session object could be retrieved later to make authenticated API requests to Shopify
    MyApp::SessionRepository.store_session(auth_result[:session])

    puts("OAuth complete! New access token: #{auth_result[:session].access_token}")

```
