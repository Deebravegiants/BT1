### Title
Unvalidated JWT `dest` Claim Used to Route `client_secret` in `TokenExchange.exchange_token` - (File: `lib/shopify_api/auth/token_exchange.rb`)

### Summary
`ShopifyAPI::Auth::TokenExchange.exchange_token` extracts the shop from the `dest` claim of an untrusted-format-checked JWT and uses that raw value to build the HTTP host that receives the app's `client_id`/`client_secret` — unlike the sibling method `migrate_to_expiring_token` in the same file, which explicitly sanitizes the shop with `ShopValidator.sanitize!` before doing the same thing.

### Finding Description
`JwtPayload` verifies only the JWT signature and the `aud` claim; it never validates that the `dest`/`shop` value is a trusted Shopify domain: [1](#0-0) 

`exchange_token` then takes this unvalidated `shop` value straight from the token and builds a `Session` from it, which is fed into `Clients::HttpClient`: [2](#0-1) 

`HttpClient#initialize` derives the request host directly from `session.shop` with no domain check of its own: [3](#0-2) 

so the POST body containing `client_id` and `client_secret` (line 53-54 of `token_exchange.rb`) is sent to `https://#{dest_shop}/admin/oauth/access_token`, where `dest_shop` came unchecked from the JWT.

By contrast, `migrate_to_expiring_token` in the very same file performs the intended binding check before doing an identical client_secret-bearing request: [4](#0-3) 

This is exactly the identity-binding break called out by the report's bug class: the host that is *validated* (checked against `ShopValidator::TRUSTED_SHOPIFY_DOMAINS`) is not the same host that actually *receives* the `client_secret` in `exchange_token`. The equality that should hold — `validated_shop == host_receiving_client_secret` — is broken for this specific code path, while it is correctly enforced one function below it.

### Impact Explanation
If the `dest` claim in a validly-signed session token can ever be a value outside the trusted Shopify domain set (e.g., through a custom app-bridge host configuration, non-standard admin embedding, or any future change in how `dest` is populated that this gem cannot control), `exchange_token` will silently POST the app's `client_id` and `client_secret` to that host — SSRF with the app's credentials and possible full compromise of the app's OAuth client secret. This matches the report's High-severity bucket ("SSRF with the app's credentials ... or credential leakage into logs or error output").

### Likelihood Explanation
Exploitability depends entirely on whether `dest` can be attacker-influenced while the JWT signature still validates — the gem itself provides no defense-in-depth once the token verifies. Given the codebase's own author explicitly added `ShopValidator.sanitize!` to the neighboring `migrate_to_expiring_token` method for the identical `client_secret` POST, this indicates the missing check in `exchange_token` is an unintentional omission of a defense that the maintainers themselves consider necessary — a real gap in binding "trusted domain" verification to "host that receives client_secret," even though the direct exploit path requires an as-yet-unconfirmed way to control `dest` in a signature-valid token.

### Recommendation
In `TokenExchange.exchange_token`, validate `dest_shop` with `Utils::ShopValidator.sanitize!(dest_shop)` (mirroring `migrate_to_expiring_token`) before constructing `shop_session`, so the same trusted-domain check that gates every other `client_secret`-bearing request also gates the token-exchange flow.

### Proof of Concept
1. Obtain (or otherwise cause to be issued) a validly-signed session token whose `dest` claim is not a Shopify-trusted domain.
2. Call `ShopifyAPI::Auth::TokenExchange.exchange_token(session_token: token, requested_token_type: ...)`.
3. Observe that `Clients::HttpClient` builds `@base_uri` from the unvalidated `dest` value [3](#0-2)  and the request body containing `client_id`/`client_secret` [5](#0-4)  is POSTed to that host — contrast with `migrate_to_expiring_token`, which would have rejected the same value via `ShopValidator.sanitize!` [6](#0-5) .

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
