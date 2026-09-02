## Title
Unvalidated `dest` claim from session token used to route the app's `client_secret` in `TokenExchange.exchange_token` - ([File: lib/shopify_api/auth/token_exchange.rb])

### Summary
`ShopifyAPI::Auth::TokenExchange.exchange_token` derives the destination shop directly from the JWT session token's `dest` claim and uses it, unsanitized, to build the HTTP host that receives the app's `client_id`/`client_secret` during the OAuth token-exchange POST. This is inconsistent with the sibling method `TokenExchange.migrate_to_expiring_token` in the same file, which explicitly runs the shop through `Utils::ShopValidator.sanitize!` before using it to build the same kind of credentialed request.

### Finding Description
`JwtPayload#shop` only strips the `"https://"` prefix from the `dest` claim and returns it verbatim, with no check against `Utils::ShopValidator::TRUSTED_SHOPIFY_DOMAINS`: [1](#0-0) 

`JwtPayload#initialize` only verifies the JWT signature and that `aud == Context.api_key`; it never validates that `dest`/`iss` resolve to a trusted Shopify domain: [2](#0-1) 

`TokenExchange.exchange_token` takes this unvalidated `dest_shop` and uses it directly to build the session that drives the credentialed request: [3](#0-2) 

`Clients::HttpClient#initialize` builds the request host straight from `session.shop`, and the POST body for the token-exchange call includes `client_id` and `client_secret`: [4](#0-3) [5](#0-4) 

By contrast, the neighboring `migrate_to_expiring_token` method — which builds and sends the exact same kind of credentialed request (`client_secret` in the body, host from `session.shop`) — explicitly binds the shop to the trusted-domain allowlist before use: [6](#0-5) 

This is the identity-binding gap: the equality that should hold is `host that receives client_secret == host validated as a trusted Shopify domain`. `migrate_to_expiring_token` enforces this via `Utils::ShopValidator.sanitize!`; `exchange_token` does not enforce it at all, trusting the JWT's `dest` claim to double as a validated, request-routing host without ever being bound to `Utils::ShopValidator::TRUSTED_SHOPIFY_DOMAINS`.

### Impact Explanation
If the `dest` claim of an id token processed by `JwtPayload` ever contains a value that isn't itself already constrained to `*.myshopify.com`/`*.myshopify.io`/`spin.dev`/`shop.dev` (e.g., a malformed or attacker-influenced destination reaching this code path through app integration code that forwards a token without the same guarantees the Admin embedding provides), `exchange_token` will send the app's `client_id` and `client_secret` to that unrestrained host — a credential-leaking SSRF using the app's own OAuth secret. This matches the High-impact "SSRF with the app's credentials" category, since it is the exact same request shape (`client_secret` in body, host taken from an unvalidated shop value) that the library's own `migrate_to_expiring_token` treats as needing sanitization.

### Likelihood Explanation
Medium: exploitation depends on how permissive the actual `dest` value can be when it reaches `JwtPayload`; under the documented, App Bridge-issued session-token flow, Shopify itself controls `dest`, but nothing in this library enforces that invariant at the `JwtPayload`/`exchange_token` layer the way `migrate_to_expiring_token` does for its `shop` argument. The missing symmetric check is a concrete, in-scope code defect (not merely a documentation gap), and the asymmetry between the two token-exchange code paths in the same file/module indicates the validation was known to be required but omitted here.

### Recommendation
In `TokenExchange.exchange_token`, validate `dest_shop` with `Utils::ShopValidator.sanitize!(dest_shop)` (mirroring `migrate_to_expiring_token`) before constructing `shop_session`/`HttpClient`, and/or enforce the same trusted-domain check inside `JwtPayload#shop` so that every consumer of the `dest` claim gets a shop value bound to `TRUSTED_SHOPIFY_DOMAINS` by construction.

### Proof of Concept
1. Obtain/construct a session token whose `dest` claim value is not constrained to a myshopify-family domain (any code path that feeds a token into `JwtPayload` without Shopify's own admin-embedding guarantees).
2. Call `ShopifyAPI::Auth::TokenExchange.exchange_token(session_token: token, requested_token_type: ...)`.
3. Observe `Clients::HttpClient.new(session: shop_session, base_path: "/admin/oauth")` build its base URI from the unsanitized `dest_shop` value: [7](#0-6) 
4. The POST to `.../admin/oauth/access_token`, carrying `client_id`/`client_secret` in the body, is sent to that host instead of a verified Shopify domain — compare directly against `migrate_to_expiring_token`, which would have rejected such a shop value via `Utils::ShopValidator.sanitize!`.

### Citations

**File:** lib/shopify_api/auth/jwt_payload.rb (L23-45)
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
```

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

**File:** lib/shopify_api/clients/http_client.rb (L11-19)
```ruby
      sig { params(base_path: String, session: T.nilable(Auth::Session)).void }
      def initialize(base_path:, session: nil)
        session ||= Context.active_session
        raise Errors::NoActiveSessionError, "No passed or active session" unless session

        api_host = Context.api_host

        @base_uri = T.let("https://#{api_host || session.shop}", String)
        @base_uri_and_path = T.let("#{@base_uri}#{base_path}", String)
```
