### Title
Unsanitized JWT `dest` claim used as request host and to receive `client_secret` in `TokenExchange.exchange_token` - ([File: lib/shopify_api/auth/token_exchange.rb])

### Summary
`ShopifyAPI::Auth::TokenExchange.exchange_token` derives the request host for the token-exchange call directly from the session token's `dest` claim without validating that the value is a trusted `*.myshopify.com`/`*.myshopify.io` domain. The sibling method in the same module, `migrate_to_expiring_token`, sanitizes its `shop` parameter through `Utils::ShopValidator.sanitize!` before using it as a host, but `exchange_token` does not apply the same check to the value it extracts from the JWT.

### Finding Description
`JwtPayload#shop` (`lib/shopify_api/auth/jwt_payload.rb:47-51`) simply strips `"https://"` from the token's `dest` claim with no domain allow-listing: [1](#0-0) 

`TokenExchange.exchange_token` (`lib/shopify_api/auth/token_exchange.rb:39-51`) takes this unvalidated value (`dest_shop`) and constructs a `Session` with `shop: dest_shop`, which `Clients::HttpClient` then turns directly into the request host — `@base_uri = "https://#{api_host || session.shop}"` — and POSTs a body containing `client_secret` (`lib/shopify_api/clients/http_client.rb:16-19`, `lib/shopify_api/auth/token_exchange.rb:51-65`). [2](#0-1) [3](#0-2) 

Contrast this with the module's own `migrate_to_expiring_token`, which explicitly calls `Utils::ShopValidator.sanitize!(shop)` before building the session/host used for the same kind of request: [4](#0-3) 

The `ShopValidator` module exists specifically to enforce that a shop value resolves to a trusted Shopify domain (`myshopify.com`, `myshopify.io`, `spin.dev`, `shop.dev`, `shopify.com`) before it is trusted as a request host: [5](#0-4) 

The broken identity binding is: `host validated (JWT signature over aud/exp/etc.) == host that receives client_secret`. The JWT's HMAC signature only proves the token payload was signed by the app's shared secret and that `aud == Context.api_key`; it makes no guarantee that `dest` is restricted to a `ShopValidator`-trusted domain. `exchange_token` treats "signature valid" as equivalent to "dest is a safe request host," which is the same class of gap the underlying Trail of Bits report describes (a value trusted for one purpose — sync-committee membership / here, "signed by us" — being reused for a different purpose — "controls which host receives the client_secret" — without an explicit binding check).

### Impact Explanation
If `dest` in a validly-signed session token is ever not confined to a myshopify domain (e.g. non-standard issuance paths, custom/whitelabel domains, or future Shopify surface changes that populate `dest` from a wider set of values than the admin/myshopify host), `exchange_token` will send the app's `client_secret` and `subject_token` (the session token) as an HTTP POST body to that attacker-influenced host — an SSRF that exfiltrates the app's `client_secret` and the presented access/session material to a third party. This matches the "High - SSRF with the app's credentials" impact category, since `client_secret` is placed directly in the outgoing request body to the derived host.

### Likelihood Explanation
Likelihood is constrained by the fact that the session token must carry a valid HMAC signature over `Context.api_secret_key`, which in the currently understood Shopify-issued flow means `dest` is populated by Shopify itself. Under normal operation, Shopify sets `dest` to the shop's canonical admin/myshopify host, so this is not trivially exploitable by an anonymous internet user today. However, the code contains no defensive check enforcing that invariant — the exact protection that the neighboring `migrate_to_expiring_token` method applies is silently missing here — leaving the SSRF-with-credentials primitive latent and reachable the moment any code path (current or future) can cause `dest` to diverge from a myshopify-trusted host.

### Recommendation
Apply the same `Utils::ShopValidator.sanitize!` (or equivalent) check to `jwt_payload.shop`/`dest_shop` in `TokenExchange.exchange_token` before it is used to build the `Session`/request host, mirroring the pattern already used in `TokenExchange.migrate_to_expiring_token`. This ensures the host that receives `client_secret` is always independently verified against the trusted-domain allow-list rather than solely inferred from the JWT's `dest` claim.

### Proof of Concept
1. Obtain (or, in a hypothetical future issuance path, cause) a validly HMAC-signed session token whose `dest` claim is not a `ShopValidator`-trusted domain.
2. Call `ShopifyAPI::Auth::TokenExchange.exchange_token(session_token: token, requested_token_type: ...)`.
3. `JwtPayload#shop` returns the unsanitized `dest` host; `Clients::HttpClient` builds `@base_uri = "https://#{dest_host}"` and POSTs a JSON body including `client_id` and `client_secret` to `https://#{dest_host}/admin/oauth/access_token`, exfiltrating the app's `client_secret` to the attacker-controlled host — compare with `migrate_to_expiring_token`, where an equivalent untrusted `shop` value is rejected by `Utils::ShopValidator.sanitize!` raising `Errors::InvalidShopError`.

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

**File:** lib/shopify_api/auth/token_exchange.rb (L97-115)
```ruby
        def migrate_to_expiring_token(shop:, non_expiring_offline_token:)
          unless ShopifyAPI::Context.setup?
            raise ShopifyAPI::Errors::ContextNotSetupError,
              "ShopifyAPI::Context not setup, please call ShopifyAPI::Context.setup"
          end

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
