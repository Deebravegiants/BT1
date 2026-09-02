## Title
Predictable, non-random session identifiers used as the unauthenticated session cookie value enable session hijacking / cross-tenant access — (File: `lib/shopify_api/auth/session.rb`, `lib/shopify_api/auth/oauth.rb`)

### Summary
For non-embedded apps, `ShopifyAPI::Auth::Oauth.validate_auth_callback` sets the browser session cookie's *value* directly to `session.id` [1](#0-0) . That `id` is not a cryptographically random token — it is deterministically derived from public/guessable data: `"#{shop}_#{associated_user.id}"` for online sessions or `"offline_#{shop}"` for offline sessions [2](#0-1) . Because the cookie is the *sole unauthenticated bearer credential* the host app is documented to use as a lookup key into its session store (`MyApp::SessionRepository.store_session(auth_result[:session])`, later retrieved by `SessionUtils.current_session_id`) [3](#0-2) , an attacker who can guess or enumerate a target `shop` domain and Shopify `associated_user.id` can forge that exact cookie value and be treated as that merchant/user, gaining the merchant's stored access token.

### Finding Description
The binding that should hold is:
`cookie_value (attacker-suppliable bytes) == unguessable_secret(session)`

Instead the gem implements:
`cookie_value == f(shop, associated_user.id)` where `f` is a public, non-secret, deterministic string concatenation — no HMAC, no random component, no server-side secret is mixed in [2](#0-1) .

`shop` (the myshopify.com domain) is not secret — it is transmitted in plaintext throughout OAuth and webhook flows. `associated_user.id` is the merchant's staff Shopify user ID, a small enumerable integer returned in the OAuth token response and is not treated as secret anywhere else in the library (it appears, for instance, unencrypted in the `AssociatedUser` struct) [4](#0-3) .

The `SessionCookie` created for non-embedded apps carries this deterministic ID as its literal value:
```ruby
cookie = if Context.embedded?
  SessionCookie.new(value: "", expires: Time.now)
else
  SessionCookie.new(value: session.id, expires: session.expires ? session.expires : nil)
end
``` [1](#0-0) 

The documented integration pattern instructs the host app to store the returned `Session` (keyed by `session.id`) and to set this exact `cookie.value` into the browser cookie jar [5](#0-4) . Later, `SessionUtils.current_session_id` simply reads this cookie value back with no additional cryptographic verification and returns it to be used as the session-store lookup key [3](#0-2) . There is no signature, MAC, or nonce over the cookie value anywhere in this gem — `http_only`/`secure` flags (set by the host per the documented example) only stop browser-side JavaScript from reading the cookie; they do nothing to stop a raw unauthenticated HTTP client from sending a *forged* `Cookie` header containing the guessed value.

This is exactly the "session id derived from unauthenticated bytes" bug class: the identity binding "bytes that unlock a session" vs "bytes that are cryptographically tied to that session's issuance" is broken, because the unlocking bytes are just a public string concatenation reproducible by anyone.

### Impact Explanation
An attacker who knows (or enumerates) a target shop's domain and a valid staff user ID for that shop can construct the exact online-session cookie value `"#{shop}_#{user_id}"` and present it as their own `Cookie` header to the host application. If the host application's session store (built per this gem's documented pattern) contains a live session for that ID — which it will, for any merchant who has completed OAuth — the attacker is treated as that authenticated merchant/user and is handed cross-tenant access, including the merchant's OAuth `access_token`. This matches the "Critical: cross-tenant access / theft of a merchant access token" impact bucket, since the root cause is entirely within this gem's session-id generation and cookie-value assignment logic, not a host-app misuse.

### Likelihood Explanation
- `shop` domains are routinely known/public (they appear in URLs, marketing pages, `myshopify.com` subdomains are often derivable from a store's public storefront name).
- `associated_user.id` values are small integers assigned sequentially by Shopify and are not treated as secrets elsewhere in the codebase or Shopify's public API surface.
- No rate limiting or lockout is required to be bypassed — this is a single guess/request per candidate ID, and many host apps store sessions indefinitely.
- The only mitigating factor is that the attacker needs the host app's session store to have a previously created record for the guessed ID, which happens naturally for any actively-installed merchant.

### Recommendation
Do not use a deterministic, information-derived string as the literal session cookie value. Instead:
- Generate a cryptographically random, unguessable session identifier (e.g., `SecureRandom.uuid` or better, `SecureRandom.hex(32)`) to use as the cookie value, and store the mapping from that random token to the deterministic `Session` record server-side, or
- HMAC-sign the cookie value (bind it to `Context.api_secret_key`) so forging it requires knowledge of the app secret, not just public shop/user IDs.

### Proof of Concept
1. Merchant `victim-shop.myshopify.com` installs the app as a non-embedded app; staff user with Shopify ID `4242` completes OAuth. Per the documented flow, the host app stores `Session#id == "victim-shop.myshopify.com_4242"` and sets a cookie with that exact value [6](#0-5) .
2. Attacker (any unauthenticated internet user), knowing/guessing the shop domain and enumerating small staff-user IDs, issues:
```
GET /some/authenticated/app/route HTTP/1.1
Host: app.example.com
Cookie: shopify_app_session=victim-shop.myshopify.com_4242
```
3. `SessionUtils.current_session_id` extracts `"victim-shop.myshopify.com_4242"` from the cookie with no further verification [3](#0-2)  and the host app's session repository (built per this gem's documented contract) returns the victim's stored `Session`, including `access_token`, granting the attacker full cross-tenant access to the victim's Shopify store data.

### Citations

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

**File:** lib/shopify_api/auth/session.rb (L107-140)
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

          if access_token_response.expires_in
            expires = Time.now + access_token_response.expires_in.to_i
          end

          if access_token_response.refresh_token_expires_in
            refresh_token_expires = Time.now + access_token_response.refresh_token_expires_in.to_i
          end

          new(
            id: id,
            shop: shop,
            access_token: access_token_response.access_token,
            scope: access_token_response.scope,
            is_online: is_online,
            associated_user_scope: associated_user_scope,
            associated_user: associated_user,
            expires: expires,
            shopify_session_id: access_token_response.session,
            refresh_token: access_token_response.refresh_token,
            refresh_token_expires: refresh_token_expires,
          )
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

**File:** docs/usage/oauth.md (L230-270)
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

    puts("OAuth complete! New access token: #{auth_result[:session].access_token}")

    head 307
    response.set_header("Location", "<some-redirect-url>")
  rescue => e
    puts(e.message)
```
