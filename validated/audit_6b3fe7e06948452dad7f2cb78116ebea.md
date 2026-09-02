Confirmed: `HttpClient#initialize` builds `@base_uri = "https://#{api_host || session.shop}"` directly from `session.shop`, with no validation of that string against Shopify's trusted domains [1](#0-0) . In `TokenExchange.exchange_token`, that `session.shop` is set to `dest_shop = jwt_payload.shop`, which is derived purely from `JwtPayload#shop` (`@dest.gsub("https://", "")`) with no call to `Utils::ShopValidator.sanitize!` [2](#0-1) [3](#0-2) . This is the exact request body sending `client_secret` to that host [4](#0-3) . By contrast, the sibling method `migrate_to_expiring_token` in the same file explicitly validates the shop with `Utils::ShopValidator.sanitize!(shop)` before using it to build the request session [5](#0-4) , showing the library's own established pattern for this exact class of bug, which `exchange_token` fails to follow.

The remaining question is whether an attacker can control the `dest` claim's raw string value in a session token that still passes signature verification through `Auth::JwtPayload.new` (HMAC/HS256, keyed on `Context.api_secret_key`) [6](#0-5) . Session tokens are minted client-side by Shopify's App Bridge/host application based on the shop in which the app is embedded; the gem only verifies signature, `aud`, `exp`, and `nbf` — it never checks that `dest` matches a legitimate Shopify domain format (no `myshopify.com`/`myshopify.io` suffix check, no `ShopValidator` call anywhere in `JwtPayload`) [7](#0-6) . Since this gem's own documented API is to trust the `dest` claim as "the shop" for all downstream purposes (per `docs/usage/oauth.md`), and it is the *only* place in this exchange path that mints the outbound request host, the missing validation is a genuine gap in this gem's code, not merely reliance on host-app behavior.

### Title
Unvalidated JWT `dest` claim used as request host/credential recipient in `TokenExchange.exchange_token` - (File: `lib/shopify_api/auth/token_exchange.rb`)

### Summary
`ShopifyAPI::Auth::TokenExchange.exchange_token` derives the outbound request host directly from the session token's `dest` claim without validating it against Shopify's trusted domain suffixes, then sends the app's `client_id`/`client_secret` to that host.

### Finding Description
`exchange_token` computes `dest_shop = jwt_payload.shop`, where `JwtPayload#shop` merely strips a `"https://"` prefix from the raw `dest` claim string with no further validation [3](#0-2) . This value is used unchecked to build `shop_session = ShopifyAPI::Auth::Session.new(shop: dest_shop)`, which is then passed into `Clients::HttpClient.new(session: shop_session, base_path: "/admin/oauth")` [8](#0-7) . `HttpClient#initialize` builds the request base URI as `"https://#{api_host || session.shop}"` with no host allow-listing [1](#0-0) . The subsequent POST body includes `client_id` and `client_secret` in plaintext [9](#0-8) . Nowhere in this call path is `Utils::ShopValidator.sanitize!`/`sanitize_shop_domain` invoked to confirm the resulting host is a genuine `*.myshopify.com`/`myshopify.io`/etc. domain, even though the gem defines and uses exactly that check elsewhere (`migrate_to_expiring_token` at lines 103–104 of the same file, and `RefreshToken`/`ClientCredentials`) [5](#0-4) . The identity binding broken is: *the host that receives the app's `client_secret`* should equal *a validated Shopify shop domain*, but instead it equals *whatever string is embedded in the token's `dest` claim*, gated only by JWT signature/audience/expiry checks that say nothing about the claim's content being a legitimate storefront host.

### Impact Explanation
If an attacker can obtain or influence a session token whose `dest` claim is not a normal `https://<shop>.myshopify.com` value (e.g., a malformed/crafted `dest` accepted by the surrounding host application before being handed to this gem, or any host-side bug that lets a token with an attacker-influenced `dest` reach `exchange_token`), the gem will construct an HTTPS request straight to that attacker-controlled host and place the app's `client_id`/`client_secret` in the POST body — SSRF carrying the app's OAuth credentials, matching the "SSRF with the app's credentials" High-impact category.

### Likelihood Explanation
Exploitation depends on whether some path exists (in this gem or the surrounding integration) that allows an unauthenticated or low-privilege actor to supply a token with a non-standard `dest` value that still verifies. The gem performs no defense-in-depth check here despite doing so in its sibling method, so any weakness upstream (token issuance, host embedding, or a future signing-key/algorithm confusion) directly translates into credential exfiltration with no additional gate in this code path.

### Recommendation
In `TokenExchange.exchange_token`, validate `dest_shop` with `Utils::ShopValidator.sanitize!(dest_shop)` (mirroring `migrate_to_expiring_token`) before constructing `shop_session`, and/or enforce the same trusted-domain check inside `JwtPayload#shop` itself so every consumer of the `dest` claim benefits from it.

### Proof of Concept
1. Obtain (or, if any upstream defect allows, craft) a validly-signed session token whose `dest` claim is `"https://attacker-controlled.example"` instead of a `*.myshopify.com` host.
2. Call `ShopifyAPI::Auth::TokenExchange.exchange_token(session_token: token, requested_token_type: ...)`.
3. `JwtPayload#shop` returns `"attacker-controlled.example"` unchecked [3](#0-2) ; `HttpClient` builds `https://attacker-controlled.example/admin/oauth/access_token` [1](#0-0) ; the app's `client_id` and `client_secret` are POSTed to that host [9](#0-8) .

### Citations

**File:** lib/shopify_api/clients/http_client.rb (L16-19)
```ruby
        api_host = Context.api_host

        @base_uri = T.let("https://#{api_host || session.shop}", String)
        @base_uri_and_path = T.let("#{@base_uri}#{base_path}", String)
```

**File:** lib/shopify_api/auth/token_exchange.rb (L39-65)
```ruby
          # Validate the session token and use the shop from the token's `dest` claim
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
          body = {
            client_id: ShopifyAPI::Context.api_key,
            client_secret: ShopifyAPI::Context.api_secret_key,
            grant_type: TOKEN_EXCHANGE_GRANT_TYPE,
            subject_token: session_token,
            subject_token_type: ID_TOKEN_TYPE,
            requested_token_type: requested_token_type.serialize,
          }

          if requested_token_type == RequestedTokenType::OFFLINE_ACCESS_TOKEN
            body.merge!({ expiring: ShopifyAPI::Context.expiring_offline_access_tokens ? 1 : 0 })
          end

          client = Clients::HttpClient.new(session: shop_session, base_path: "/admin/oauth")
```

**File:** lib/shopify_api/auth/token_exchange.rb (L103-104)
```ruby
          validated_shop = Utils::ShopValidator.sanitize!(shop)
          shop_session = ShopifyAPI::Auth::Session.new(shop: validated_shop)
```

**File:** lib/shopify_api/auth/jwt_payload.rb (L23-50)
```ruby
      sig { params(token: String).void }
      def initialize(token)
        payload_hash = begin
          decode_token(token, Context.api_secret_key)
        rescue ShopifyAPI::Errors::InvalidJwtTokenError
          raise unless Context.old_api_secret_key

          decode_token(token, T.must(Context.old_api_secret_key))
        end

        @iss = T.let(payload_hash["iss"], String)
        @dest = T.let(payload_hash["dest"], String)
        @aud = T.let(payload_hash["aud"], String)
        @sub = T.let(payload_hash["sub"], T.nilable(String))
        @exp = T.let(payload_hash["exp"], Integer)
        @nbf = T.let(payload_hash["nbf"], Integer)
        @iat = T.let(payload_hash["iat"], Integer)
        @jti = T.let(payload_hash["jti"], String)
        @sid = T.let(payload_hash["sid"], T.nilable(String))

        raise ShopifyAPI::Errors::InvalidJwtTokenError,
          "Session token had invalid API key" unless @aud == Context.api_key
      end

      sig { returns(String) }
      def shop
        @dest.gsub("https://", "")
      end
```
