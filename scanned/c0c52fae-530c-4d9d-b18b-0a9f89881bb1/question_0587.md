# Q587: online_token? — identity shape from the response via associated_user presence

## Question
Is there a reachable state in which an unprivileged attacker, controlling presence or absence of `associated_user`, which flips the session between online and offline and therefore flips the session id at `online_token?`, which decides online vs offline purely by `!associated_user.nil?`, makes `Oauth::AccessTokenResponse#online_token?` return a result the caller treats as authenticated, given that whether the session is online or offline - and therefore which storage key it occupies - is decided by response content? Test SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host and quantify Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`).

## Target
- File/function: `lib/shopify_api/auth/oauth/access_token_response.rb` -> `Oauth::AccessTokenResponse#online_token?`
- Entrypoint: `online_token?`, which decides online vs offline purely by `!associated_user.nil?`
- Attacker controls: presence or absence of `associated_user`, which flips the session between online and offline and therefore flips the session id
- Exploit idea: whether the session is online or offline - and therefore which storage key it occupies - is decided by response content
- Invariant to test: SHOP BINDING: shop authenticated by the signature/JWT == shop interpolated into the session id == shop used as the request host
- Expected Immunefi impact: Critical - theft of a merchant's Admin API access token (`X-Shopify-Access-Token`) (this repo is covered by Shopify's HackerOne program per SECURITY.md; severity mapped to the equivalent Critical/High class)
- Fast validation: flip `associated_user` presence and assert the resulting session id cannot collide with an existing offline key
