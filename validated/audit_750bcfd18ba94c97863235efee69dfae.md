Found it. `TokenExchange.exchange_token` in [1](#0-0)  derives `dest_shop` from the session token's `dest` claim and uses it, unvalidated, both as the `Session#shop` (sent as the `X-Shopify-Shop-Domain`/host for the outbound token-exchange request that carries the app's `client_id`/`client_secret`) and as the `shop` persisted on the returned `Session`. Unlike every sibling grant helper — `ClientCredentials.client_credentials`, `RefreshToken.refresh_access_token`, and `TokenExchange.migrate_to_expiring_token` — which all call `Utils::ShopValidator.sanitize!(shop)` before building the `Session` and HTTP client ( [2](#0-1) , [3](#0-2) , [4](#0-3) ), `exchange_token` skips `ShopValidator` entirely.

### Title
Unvalidated JWT `dest` claim used as request host in `TokenExchange.exchange_token`, bypassing the shop-domain trust boundary enforced elsewhere in the gem - (File: lib/shopify_api/auth/token_exchange.rb)

### Summary
`ShopifyAPI::Auth::TokenExchange.exchange_token` takes the `dest` claim from a session token (`JwtPayload#shop`) and uses it directly, without passing it through `Utils::ShopValidator.sanitize!`, both to build the `Session` object that determines the outbound HTTP host and to label the returned, cached `Session`. Every other credential-issuing helper in the same file and module (`migrate_to_expiring_token`, `client_credentials`, `refresh_access_token`) explicitly validates the shop string against `ShopValidator::TRUSTED_SHOPIFY_DOMAINS` before using it the same way.

### Finding Description
`JwtPayload#shop` returns `@dest.gsub("https://", "")`, i.e. a raw string taken from the JWT `dest` claim, only checked for HS256 signature validity/expiry/`aud` match (`lib/shopify_api/auth/jwt_payload.rb`, lines 33-50). Nothing in `JwtPayload` or `TokenExchange.exchange_token` checks that this string is actually a `*.myshopify.com` / trusted Shopify domain the way `Utils::ShopValidator.sanitize!` does (`lib/shopify_api/utils/shop_validator.rb`, lines 9-64), which whitelists only `shopify.com`, `myshopify.io`, `myshopify.com`, `spin.dev`, `shop.dev` and rejects userinfo/path tricks. `exchange_token` builds `shop_session = ShopifyAPI::Auth::Session.new(shop: dest_shop)` and passes it straight into `Clients::HttpClient.new(session: shop_session, base_path: "/admin/oauth")`, which derives the request host from `session.shop`; the request body includes `client_id` and `client_secret` (`lib/shopify_api/auth/token_exchange.rb`, lines 41-74). The identity binding that should hold — "the host contacted with the app's `client_secret` == a domain in `ShopValidator::TRUSTED_SHOPIFY_DOMAINS`" — is not enforced for this code path, whereas the gem enforces it everywhere else a `shop` string reaches `Clients::HttpClient`.

Because the app developer is documented to trust `dest_shop` ("the shop is now always taken from the session token's `dest` claim" — see the deprecation notice at lines 43-49), and because token exchange is specifically the flow used by embedded apps receiving `session_token` values that ultimately originate from the client-side App Bridge / browser context, this is the one place in the gem's OAuth surface where a shop-derived hostname skips the shared validator that the rest of the module relies on as its defense-in-depth boundary.

### Impact Explanation
If the `dest` claim can be made to contain anything other than a genuine `*.myshopify.com`-family host (e.g. via a JWT issued for a non-standard `iss`/`dest` pair, or any future relaxation of what values `dest` can hold), `exchange_token` would POST the app's `client_id` and `client_secret` to an attacker-influenced host — SSRF carrying the app's credentials, which is explicitly a High-severity class in scope. Even absent a concrete forgery primitive we could confirm from static review alone, this is a broken security invariant: the gem itself treats "validate shop via `ShopValidator` before using it as a request host" as mandatory (enforced in three sibling methods) but omits it here, so the code does not defend the boundary it clearly intends to defend.

### Likelihood Explanation
Medium. Exploitation requires a session token whose `dest` claim is not a trusted Shopify domain but that still verifies under the app's `api_secret_key`/`old_api_secret_key` and matches `aud` — i.e., a token that is properly signed by Shopify but scoped to an unexpected `dest`. We could not fully verify from this gem alone what values Shopify's token issuer permits in `dest`, so this should be treated as a missing defense-in-depth control confirmed by direct code comparison within this repository, not a fully demonstrated end-to-end forgery.

### Recommendation
In `TokenExchange.exchange_token`, validate `dest_shop` with `Utils::ShopValidator.sanitize!(dest_shop)` (mirroring `migrate_to_expiring_token`, `client_credentials`, and `refresh_access_token`) before constructing `shop_session` and before returning it in `Session.from`, so the shop domain used to route the credential-bearing HTTP request is always constrained to `ShopValidator::TRUSTED_SHOPIFY_DOMAINS`.

### Proof of Concept
Static comparison (no dynamic exploit executed):
1. `lib/shopify_api/auth/token_exchange.rb:40-51` — `dest_shop = jwt_payload.shop; shop_session = ShopifyAPI::Auth::Session.new(shop: dest_shop)` — no `ShopValidator` call.
2. `lib/shopify_api/auth/token_exchange.rb:103-104` — `migrate_to_expiring_token`, same file, same module: `validated_shop = Utils::ShopValidator.sanitize!(shop)` — validator present.
3. `lib/shopify_api/auth/client_credentials.rb:25` and `lib/shopify_api/auth/refresh_token.rb:24` — same pattern, validator present.
4. `lib/shopify_api/auth/jwt_payload.rb:48-50` — `shop` is derived purely from the `dest` claim string with no domain allow-list check.

This asymmetry within the same module is the concrete, file-level evidence supporting the finding; a full proof of forged-`dest` exploitation would require confirming what `dest` values Shopify's real token issuer can produce, which is outside this gem's code.

### Citations

**File:** lib/shopify_api/auth/token_exchange.rb (L40-65)
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

**File:** lib/shopify_api/auth/client_credentials.rb (L25-26)
```ruby
          validated_shop = Utils::ShopValidator.sanitize!(shop)
          shop_session = ShopifyAPI::Auth::Session.new(shop: validated_shop)
```

**File:** lib/shopify_api/auth/refresh_token.rb (L24-25)
```ruby
          validated_shop = Utils::ShopValidator.sanitize!(shop)
          shop_session = ShopifyAPI::Auth::Session.new(shop: validated_shop)
```
