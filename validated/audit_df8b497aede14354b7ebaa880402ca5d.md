I have sufficient evidence to write the finding now.

### Title
Deterministic, unauthenticated session identifier enables session fixation for offline OAuth sessions - (File: `lib/shopify_api/auth/session.rb`)

### Summary
For the non-embedded Authorization Code Grant flow, the gem sets the browser's session cookie to the raw value of `Session#id`. For offline access tokens this ID is generated as `"offline_#{shop}"` — a value derived entirely from the publicly-known shop domain, with no random, secret, or HMAC-bound component. `SessionUtils.current_session_id` later trusts whatever value is present in that cookie as the lookup key for the stored session/access token, without ever re-validating it against the OAuth callback's HMAC-protected parameters.

### Finding Description
`Session.from` computes the session id for offline grants as `id = "offline_#{shop}"` [1](#0-0) , and `SessionUtils.offline_session_id` independently derives the exact same deterministic value from just the shop name [2](#0-1) . In `Oauth.validate_auth_callback`, when the app is not embedded, this `session.id` is placed directly into the `SessionCookie` value that gets set in the user's browser [3](#0-2) . The `SessionCookie` itself carries only `name`, `value`, and `expires` — it is not signed or HMAC-protected in any way [4](#0-3) .

Later, `SessionUtils.current_session_id` reads this cookie value verbatim and returns it as the authoritative session id used by the host application to look up the stored `Session` (including its `access_token`) — there is no cryptographic check binding the cookie's value back to a specific authenticated browser or OAuth transaction [5](#0-4) [6](#0-5) .

The identity binding broken here is: `session_cookie.value` (used to fetch the merchant's stored access token) **should equal** an unguessable, per-transaction secret bound to the completed OAuth flow, but instead equals `"offline_" + shop`, a value fully computable by anyone who knows the shop's `myshopify.com` domain — which is not a secret (it's visible in the app's install URL, in the `Shop` HTTP header the app itself reads at `login`, and in the merchant's own storefront URL).

### Impact Explanation
This satisfies the "session fixation" impact category: an attacker who knows (or guesses) a target shop's domain can pre-compute the exact session cookie value (`offline_<shop>.myshopify.com`) that will be assigned once that shop completes OAuth, and set it in a victim context (e.g. via cookie injection on a subdomain, or by simply using it as their own cookie value on a shared/non-isolated deployment). Because the identifier is deterministic and never re-derived from a secret, any client presenting that cookie value is treated as the legitimate owner of the corresponding stored session/access token by any host application that keys its session storage off this ID as documented (`ShopifyApp`-style `SessionRepository.store_session`) [7](#0-6) . This can lead to unauthorized use of the merchant's offline access token by anyone who knows the shop domain, without ever completing OAuth themselves.

### Likelihood Explanation
Likelihood is high for non-embedded apps using the Authorization Code Grant with offline tokens (a documented, supported flow) [8](#0-7) . No secret material is required to compute the target session id — only the public shop domain, which is trivially discoverable.

### Recommendation
Generate the session cookie value as an unguessable, randomly generated token (e.g. `SecureRandom` as already used elsewhere for `Session#id` when not explicitly passed) or a value that is HMAC-signed by `Context.api_secret_key`, rather than reusing the deterministic `"offline_#{shop}"` identifier as the externally-exposed cookie value. If the deterministic ID must remain for internal storage keys, decouple it from the cookie value so the browser-facing identifier cannot be derived by a third party.

### Proof of Concept
1. Attacker learns target shop domain `victim-shop.myshopify.com` (public information, e.g. from the app's own `Shop` login header flow, or general knowledge of the merchant's storefront).
2. Attacker computes the expected session id: `offline_victim-shop.myshopify.com`, matching `Session.from`'s deterministic formula [1](#0-0) .
3. Attacker sets a cookie `shopify_app_session=offline_victim-shop.myshopify.com` in their own browser before or independent of the merchant completing OAuth.
4. Once the merchant completes OAuth normally, the host app calls `SessionUtils.current_session_id`, which trusts the raw cookie value with no cryptographic validation [6](#0-5)  and looks up the stored session keyed on that id, returning the merchant's access token to the attacker's request.

### Citations

**File:** lib/shopify_api/auth/session.rb (L114-117)
```ruby
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

**File:** docs/usage/oauth.md (L38-41)
```markdown
2. [Authorization Code Grant](#authorization-code-grant)
    - OAuth flow that requires the app to redirect the user to Shopify for installation/authorization of the app to access the shop's data.
    - Suitable for non-embedded apps
    - Installations, and access scope changes are managed by the app
```

**File:** docs/usage/oauth.md (L252-266)
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
