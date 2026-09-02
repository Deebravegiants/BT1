### Title
Non-embedded OAuth session cookie value is a fully predictable, secret-free identifier (`offline_{shop}` / `{shop}_{user_id}`), enabling session fixation - ([File: lib/shopify_api/auth/oauth.rb])

### Summary
For non-embedded apps, `ShopifyAPI::Auth::Oauth.validate_auth_callback` sets the browser session cookie's `value` to `session.id`, and `ShopifyAPI::Auth::Session.from` derives that `id` deterministically as `"offline_#{shop}"` (offline tokens) or `"#{shop}_#{associated_user.id}"` (online tokens). Neither string contains any random, secret, or otherwise unguessable component. Because the gem's own docs instruct host apps to use this cookie value as the lookup key into their session store, the identity binding "cookie value presented by the browser == a value that could only be produced by completing a real, secret-backed OAuth handshake" is broken: the value can instead be computed by anyone who knows the target shop's `.myshopify.com` domain (public) and, for online sessions, the associated Shopify user id (often a small enumerable integer).

### Finding Description
The flow:

1. `Session.from` builds the session identifier purely from public/guessable inputs: [1](#0-0) 

2. `validate_auth_callback` then uses this exact identifier as the browser-facing session cookie value for non-embedded apps: [2](#0-1) 

3. `SessionUtils.offline_session_id` / `jwt_session_id` / `cookie_session_id` confirm that this same deterministic string is the canonical session lookup key used elsewhere in the gem: [3](#0-2) 

4. The gem's own documentation instructs integrators to persist `Session` under this id and to set the returned cookie value directly in the browser, confirming this is the intended, sanctioned usage pattern rather than a misuse by a downstream app: [4](#0-3) 

The broken equality is:

`identity_proven_by_cookie == HMAC/secret-derived proof of a completed OAuth grant`

but in this implementation it actually is:

`identity_proven_by_cookie == f(shop_domain, user_id)` — a function of public/guessable data with **no cryptographic randomness or secret binding**.

Because the `.myshopify.com` shop domain is not secret (it's often visible in the storefront URL, app listing, or simply guessable/brute-forceable for many shops), and because for offline sessions the id is *purely* `"offline_#{shop}"` with zero variable component beyond the shop name, any unprivileged internet user can pre-compute the exact cookie value that will eventually be assigned to a legitimate merchant's session.

### Impact Explanation
This is a session-fixation class vulnerability: an attacker who knows (or can guess) a target shop's domain can set `shopify_app_session=offline_{shop}` (or `{shop}_{user_id}` for online sessions) as their own cookie *before* the real merchant completes the OAuth install/authorize flow. Once the legitimate merchant finishes OAuth and the host application stores/updates a `Session` under that same deterministic id (per the gem's documented pattern), the attacker's pre-planted cookie now resolves to the merchant's session in the host app's session store, granting the attacker access to the merchant's authenticated app session and, transitively, to the app's use of the merchant's access token. This matches the "session fixation or forced OAuth completion" High-impact category, since it undermines the core guarantee that only the party who actually completed the Shopify-signed OAuth handshake can hold a valid app session for that shop.

### Likelihood Explanation
Likelihood is moderate-to-high in any deployment that follows the gem's documented pattern of using the returned `SessionCookie.value` (== `session.id`) as the durable session key, which is exactly what `docs/usage/oauth.md` recommends. No secret, access token, or privileged access is required by the attacker — only knowledge of the target shop domain (trivial to obtain) and, for online sessions, the numeric Shopify user id of the merchant staff member (often low-cardinality/enumerable). The offline-session case requires nothing beyond the shop domain.

### Recommendation
Do not use `session.id` (or any value derived solely from `shop`/`user_id`) as the cookie value that identifies a session to the browser. Generate a cryptographically random, unguessable session token at cookie-issuance time (e.g., `SecureRandom.uuid`/`SecureRandom.hex(32)`), store the mapping `random_token -> session.id` server-side, and only ever accept that random token from the cookie. Alternatively, bind the cookie value to a signed/HMAC'd wrapper (similar to how `SessionUtils` already trusts JWT-signed identifiers) rather than the raw deterministic `shop`/`user_id` composite string.

### Proof of Concept
1. Attacker learns/guesses target shop domain `victim-shop.myshopify.com` (public information, e.g. from the storefront URL).
2. Attacker computes `offline_victim-shop.myshopify.com` (per `Session.from`, `lib/shopify_api/auth/session.rb:116`) and sets `shopify_app_session=offline_victim-shop.myshopify.com` as their own browser cookie against the target app's domain.
3. The real merchant installs/authorizes the app; `validate_auth_callback` (`lib/shopify_api/auth/oauth.rb:96-110`) creates a `Session` with the same deterministic id and sets it as the merchant's session cookie value; the host app persists the session under this id, per the gem's documented storage pattern.
4. Attacker's browser, still holding the pre-set cookie value from step 2, is now recognized by the host application's session lookup (`SessionUtils.cookie_session_id`, `lib/shopify_api/utils/session_utils.rb:68-71`) as the merchant's valid session, granting the attacker access to app functionality performed with the merchant's access token.

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

**File:** lib/shopify_api/auth/oauth.rb (L96-110)
```ruby
          session_params = T.cast(response.body, T::Hash[String, T.untyped]).to_h
          session = Session.from(shop: auth_query.shop,
            access_token_response: Oauth::AccessTokenResponse.from_hash(session_params))

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

**File:** docs/usage/oauth.md (L230-264)
```markdown
##### Example
Your app should call `validate_auth_callback` to construct the `Session` object and cookie that will be used later for authenticated API requests.

1. Call `validate_auth_callback` to construct `Session` and `SessionCookie`.
2. Update browser cookies with the new value for the session.
3. Store the `Session` object to be used later when [making authenticated API calls](#using-oauth-session-to-make-authenticated-api-calls).
   - See [Make a GraphQL API call](https://github.com/Shopify/shopify-api-ruby/blob/main/docs/usage/graphql.md), or
   [Make a REST API call](https://github.com/Shopify/shopify-api-ruby/blob/main/docs/usage/rest.md) for examples on how to use the result `Session` object.

An example is shown below in a Rails app but these steps could be applied in any framework:

```ruby
def callback
  begin
    # Create an AuthQuery object from the request parameters,
    # and pass the list of cookies to `validate_auth_callback`
    auth_result = ShopifyAPI::Auth::Oauth.validate_auth_callback(
      cookies: cookies.to_h,
      auth_query: ShopifyAPI::Auth::Oauth::AuthQuery.new(
        request.parameters.symbolize_keys.except(:controller, :action)
      )
    )

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

```
