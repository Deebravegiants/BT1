## Title
SSRF / `client_secret` exfiltration via unsanitized JWT `dest` claim in `TokenExchange.exchange_token` - (File: `lib/shopify_api/auth/token_exchange.rb`)

### Summary
`ShopifyAPI::Auth::TokenExchange.exchange_token` derives the target host for its outbound OAuth token-exchange request directly from the session token's `dest` claim via `JwtPayload#shop`, which only strips a `"https://"` prefix and performs no domain validation. Every other method in the gem that builds a request host from caller/token-derived shop input runs it through `ShopifyAPI::Utils::ShopValidator.sanitize!` first — `exchange_token` is the one path that skips this check, so the "shop" field that determines where the app's `client_id`/`client_secret` are POSTed is not bound to a validated Shopify domain.

### Finding Description
`JwtPayload#shop` is defined as: [1](#0-0) 

It performs no validation that the resulting string is a genuine `*.myshopify.com` (or otherwise trusted) domain — it is a bare string transform on the `dest` claim.

`TokenExchange.exchange_token` takes this unsanitized value and uses it directly to build the session/host that receives the token-exchange request, which carries the app's `client_id` and `client_secret` in the body: [2](#0-1) 

That session is passed into `Clients::HttpClient`, which builds the request's base URI straight from `session.shop`: [3](#0-2) 

By contrast, the sibling method `TokenExchange.migrate_to_expiring_token`, which builds the exact same kind of client-secret-carrying request, explicitly sanitizes the shop value first: [4](#0-3) 

`Utils::ShopValidator.sanitize!`/`sanitize_shop_domain` is the gem's dedicated mechanism (added specifically to close this class of issue, per the changelog entry for `ShopifyAPI::Utils::ShopValidator`) for ensuring a shop-domain string is actually one of `TRUSTED_SHOPIFY_DOMAINS` before it's used to target a request: [5](#0-4) 

This is the same reported bug *class* as the analog report (a value is trusted and acted upon for a security-relevant purpose without being routed through the validation that the codebase itself defines for that exact purpose): the report's `usdt.transfer()` return value is assumed-safe without checking; here, the `dest`/`shop` value is assumed-safe (a valid Shopify host) without checking, even though the checking utility exists and is used one function away.

### Impact Explanation
`exchange_token` sends the app's `client_id` and `client_secret` in an HTTP POST body to `https://#{shop_session.shop}/admin/oauth/access_token`. Because `shop_session.shop` is taken from the JWT `dest` claim with no allow-listing of trusted Shopify domains, any path that results in a `dest` value outside `*.myshopify.com`/trusted dev domains will cause the app's `client_secret` to be sent to that host — this is SSRF carrying the app's own credentials, matching the report's Impact criteria for High severity ("SSRF with the app's credentials" / "credential leakage").

### Likelihood Explanation
The `session_token` argument is fully attacker/caller-supplied input to `exchange_token` (it is whatever bearer token the host application forwards from the client-side request) and its `dest` claim only needs to verify against `Context.api_secret_key`/`Context.old_api_secret_key`; nothing in `JwtPayload` or `TokenExchange.exchange_token` restricts the token to an admin-issued, `myshopify.com`-scoped session token (the `admin_session_token?` check exists in `JwtPayload` but is only used for `shopify_user_id`, not for `shop`/`exchange_token`). Given the gem's own security fix (`ShopValidator`) was introduced specifically to close this gap and applied inconsistently, the missing check in `exchange_token` is a concrete, provable regression rather than a theoretical one.

### Recommendation
In `TokenExchange.exchange_token`, sanitize `dest_shop` through `Utils::ShopValidator.sanitize!(dest_shop)` before constructing `shop_session`/`Clients::HttpClient`, mirroring what `migrate_to_expiring_token` already does.

### Proof of Concept
1. Obtain/construct a session token whose `dest` claim is not a `*.myshopify.com` domain but is nonetheless correctly HMAC-signed under the app's `api_secret_key` (e.g., a non-admin-scoped Shopify-issued token type whose `dest` is not host-restricted, or any token flow where `dest` isn't guaranteed to be `myshopify.com`-scoped).
2. Call `ShopifyAPI::Auth::TokenExchange.exchange_token(session_token: token, requested_token_type: ...)`.
3. Observe that `Clients::HttpClient` issues `POST https://<dest-value>/admin/oauth/access_token` with `client_id`/`client_secret` in the body, per `lib/shopify_api/clients/http_client.rb` line 18 and `lib/shopify_api/auth/token_exchange.rb` lines 51-65 — contrast with `migrate_to_expiring_token`, which would reject a non-trusted `shop` value at line 103 via `Utils::ShopValidator.sanitize!`.

### Citations

**File:** lib/shopify_api/auth/jwt_payload.rb (L47-51)
```ruby
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

**File:** lib/shopify_api/utils/shop_validator.rb (L9-18)
```ruby
      TRUSTED_SHOPIFY_DOMAINS = T.let(
        [
          "shopify.com",
          "myshopify.io",
          "myshopify.com",
          "spin.dev",
          "shop.dev",
        ].freeze,
        T::Array[String],
      )
```
