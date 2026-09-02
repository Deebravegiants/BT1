### Title
`TokenExchange.exchange_token` sends `client_secret` to an unsanitized host derived from the JWT `dest` claim - (File: `lib/shopify_api/auth/token_exchange.rb`)

### Summary
`ShopifyAPI::Auth::TokenExchange.exchange_token` derives the destination host for the token-exchange HTTP request directly from the session token's `dest` claim without ever passing it through `ShopifyAPI::Utils::ShopValidator`, unlike every other credential-sending code path in the gem.

### Finding Description
`exchange_token` decodes the caller-supplied session token, takes `jwt_payload.shop` (the raw `dest` claim with `https://` stripped) as `dest_shop`, and uses it unmodified to build the session/host that receives the OAuth token-exchange request, including `client_secret`: [1](#0-0) 

The resulting `shop_session` is passed straight into `Clients::HttpClient.new`, whose constructor uses `session.shop` as the literal request host (`@base_uri = "https://#{api_host || session.shop}"`) unless a fixed `api_host` override is configured: [2](#0-1) 

`JwtPayload` only verifies the HMAC signature and that `aud == Context.api_key`; it performs no validation that `dest` is a trusted `*.myshopify.com`/`myshopify.io`/`spin.dev`/`shop.dev` domain: [3](#0-2) 

By contrast, every other place in the gem that turns a caller/claim-supplied "shop" string into the HTTP host for a credentialed request explicitly calls `Utils::ShopValidator.sanitize!` first: `ClientCredentials.client_credentials`, `TokenExchange.migrate_to_expiring_token`, and `RefreshToken`: [4](#0-3) [5](#0-4) 

The library's own changelog documents that this "derive shop from `dest`" behavior in `exchange_token` was recently introduced and that the previously-validated `shop` parameter is now ignored: [6](#0-5) 

This is exactly the "host validated vs. host that receives the `client_secret`" identity-binding gap called out in scope: the binding the code should enforce is `host(request) == sanitize(dest)`, but the code actually enforces `host(request) == dest` (unsanitized), i.e. any string decodable from the `dest` claim, not just a trusted Shopify domain.

### Impact Explanation
If the raw `dest` value is ever attacker-influenced or fails to match Shopify's expected `*.myshopify.com` format (e.g., a malformed/legacy/embedded-extension token, a future token format, or an app misconfiguration where `dest` is not a canonical `myshopify.com` host), `exchange_token` will POST the app's `client_id`, `client_secret`, and the raw `subject_token` (the session token itself) to that unvalidated host — an SSRF that exfiltrates the app's `client_secret` to a third party. This matches the "Critical: theft/exfiltration of the app's `client_secret`" / "High: SSRF with the app's credentials" impact tiers in scope.

### Likelihood Explanation
Exploitation requires a syntactically valid JWT whose signature verifies (i.e., signed with the app's own `api_secret_key`/`old_api_secret_key`) but whose `dest` claim is not a sanitized Shopify domain. Because `JwtPayload` never independently validates `dest`'s domain, the security of this path relies entirely on Shopify's token-issuance guarantees rather than defense-in-depth within the gem — this is precisely the class of code the rest of the library defends against by calling `ShopValidator.sanitize!` everywhere else. I could not identify a way for an unprivileged internet user to forge or influence the `dest` claim of a signature-valid token without already possessing `api_secret_key`, so I cannot confirm an end-to-end exploit reachable purely from an unauthenticated network position; this is a missing defense-in-depth control (inconsistent with the rest of the codebase) rather than a demonstrated authentication bypass.

### Recommendation
In `TokenExchange.exchange_token`, sanitize `dest_shop` the same way `migrate_to_expiring_token`, `client_credentials`, and `RefreshToken` do, before constructing `shop_session`:
```ruby
dest_shop = Utils::ShopValidator.sanitize!(jwt_payload.shop)
```
This restores a consistent invariant across all token-issuing code paths: the HTTP host that ultimately receives `client_secret` must always be a value that has passed `ShopValidator`, never a raw, unvalidated claim/parameter.

### Proof of Concept
Not independently reproducible from the internet without a signature-valid JWT carrying a non-canonical `dest`; per the gem's own `JwtPayload` implementation, no domain-format check is performed on `dest` before it becomes the request host in `exchange_token`, in contrast to the validated `client_credentials`/`migrate_to_expiring_token` paths shown above.

### Citations

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

**File:** lib/shopify_api/auth/token_exchange.rb (L97-104)
```ruby
        def migrate_to_expiring_token(shop:, non_expiring_offline_token:)
          unless ShopifyAPI::Context.setup?
            raise ShopifyAPI::Errors::ContextNotSetupError,
              "ShopifyAPI::Context not setup, please call ShopifyAPI::Context.setup"
          end

          validated_shop = Utils::ShopValidator.sanitize!(shop)
          shop_session = ShopifyAPI::Auth::Session.new(shop: validated_shop)
```

**File:** lib/shopify_api/clients/http_client.rb (L16-19)
```ruby
        api_host = Context.api_host

        @base_uri = T.let("https://#{api_host || session.shop}", String)
        @base_uri_and_path = T.let("#{@base_uri}#{base_path}", String)
```

**File:** lib/shopify_api/auth/jwt_payload.rb (L33-50)
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

        raise ShopifyAPI::Errors::InvalidJwtTokenError,
          "Session token had invalid API key" unless @aud == Context.api_key
      end

      sig { returns(String) }
      def shop
        @dest.gsub("https://", "")
      end
```

**File:** lib/shopify_api/auth/client_credentials.rb (L19-26)
```ruby
        def client_credentials(shop:)
          unless ShopifyAPI::Context.setup?
            raise ShopifyAPI::Errors::ContextNotSetupError,
              "ShopifyAPI::Context not setup, please call ShopifyAPI::Context.setup"
          end

          validated_shop = Utils::ShopValidator.sanitize!(shop)
          shop_session = ShopifyAPI::Auth::Session.new(shop: validated_shop)
```

**File:** CHANGELOG.md (L7-8)
```markdown
- [#1443](https://github.com/Shopify/shopify-api-ruby/pull/1443) Add `ShopifyAPI::Utils::ShopValidator` with `sanitize_shop_domain` and `sanitize!`.
- [#1443](https://github.com/Shopify/shopify-api-ruby/pull/1443) Derive the target shop for `ShopifyAPI::Auth::TokenExchange.exchange_token` from the session token's `dest` claim. The `shop` argument is now deprecated and will be removed in the next major version.
```
