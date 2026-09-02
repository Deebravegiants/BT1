Confirmed: `HttpClient#initialize` sets `@base_uri = "https://#{api_host || session.shop}"` [1](#0-0)  — the raw `session.shop` value directly becomes the request host that receives `client_id`/`client_secret` in the OAuth body when no `api_host` override is set.

### Title
Unsanitized JWT `dest` claim used as OAuth token-exchange request host, allowing `client_secret` exfiltration - (File: lib/shopify_api/auth/token_exchange.rb)

### Summary
`TokenExchange.exchange_token` takes the shop hostname straight from the caller-supplied session token's `dest` claim and uses it, unsanitized, as the destination host for the token-exchange HTTP request that carries the app's `client_id` and `client_secret` in the body.

### Finding Description
Every other OAuth entry point in this library that builds a request host from a shop string first calls `Utils::ShopValidator.sanitize!`, which restricts the resulting host to `TRUSTED_SHOPIFY_DOMAINS` (`shopify.com`, `myshopify.io`, `myshopify.com`, `spin.dev`, `shop.dev`) or an explicitly configured `myshopify_domain`: `ClientCredentials.client_credentials` [2](#0-1) , `RefreshToken.refresh_access_token` [3](#0-2) , and even `TokenExchange.migrate_to_expiring_token` in the very same file [4](#0-3) .

`TokenExchange.exchange_token`, however, extracts `dest_shop = jwt_payload.shop` and passes it directly into `Session.new(shop: dest_shop)` with no call to `ShopValidator.sanitize!`: [5](#0-4) . `JwtPayload#shop` itself performs no domain validation — it merely strips the `https://` prefix from the `dest` claim: [6](#0-5) . The `JwtPayload` constructor only verifies the `aud` claim matches `Context.api_key`; it never checks that `dest`/`iss` are Shopify-owned hosts [7](#0-6) .

That unsanitized `dest_shop` is then handed to `Clients::HttpClient.new(session: shop_session, base_path: "/admin/oauth")`, whose constructor sets `@base_uri = "https://#{api_host || session.shop}"` — i.e. the outbound request's host is derived directly from `session.shop` when no `api_host` override is configured [1](#0-0) . The request body sent to that host includes `client_id` and `client_secret` in plaintext [8](#0-7) .

The binding this breaks: `session.shop` used to build the outbound request host `==` a value drawn from `TRUSTED_SHOPIFY_DOMAINS`. In every other OAuth flow this equality is enforced by `ShopValidator.sanitize!`; in `exchange_token` it is not — the host is instead whatever string appears in the `dest` claim of the session token supplied to `exchange_token`.

Whether this claim is trustworthy is bounded by how the host application obtains and vets the `session_token` parameter it passes to `exchange_token` — the gem's own signature check (`aud == Context.api_key`) confirms the token was signed with the correct secret, but it does not verify `dest` is a `*.myshopify.com`/trusted host, unlike the sibling functions in this same file.

### Impact Explanation
If reached with a `dest` value pointing to an attacker-controlled host, the gem would POST the app's `client_id` and `client_secret` (and the `session_token` itself as `subject_token`) to that host, i.e. SSRF carrying the app's OAuth credentials — matching the "High: SSRF with the app's credentials" impact category.

### Likelihood Explanation
Exploitability hinges entirely on whether a session token with an attacker-influenced `dest` claim can reach `exchange_token` while still passing the `aud == Context.api_key` check. Because valid session tokens must be signed with `Context.api_secret_key` (a secret this gem does not expose to callers), I could not find, within library code alone, a path by which an unprivileged internet user forges or otherwise supplies such a token without already possessing `api_secret_key` or a legitimately-issued token whose `dest` is attacker-influenced. I could not confirm within this codebase whether Shopify-issued session tokens ever contain a non-myshopify `dest` reachable by an external actor, or whether host applications are expected to pass user-supplied tokens straight through — this needs verification beyond what static reading of `lib/shopify_api/**` can establish.

### Recommendation
In `TokenExchange.exchange_token`, sanitize `dest_shop` the same way the other OAuth flows do:
```ruby
dest_shop = Utils::ShopValidator.sanitize!(jwt_payload.shop)
```
This makes the binding `session.shop == trusted Shopify domain` consistently enforced across every OAuth code path in the library, closing the gap between `exchange_token` and its sibling `migrate_to_expiring_token`.

### Proof of Concept
Not independently verifiable from this codebase alone (see Likelihood Explanation) — the code-level gap is demonstrable by comparing the two functions in `lib/shopify_api/auth/token_exchange.rb`:
```ruby
# exchange_token (VULNERABLE): no sanitize!
dest_shop = jwt_payload.shop
shop_session = ShopifyAPI::Auth::Session.new(shop: dest_shop)

# migrate_to_expiring_token (SAFE): sanitize! enforced
validated_shop = Utils::ShopValidator.sanitize!(shop)
shop_session = ShopifyAPI::Auth::Session.new(shop: validated_shop)
```
Both feed into the same `Clients::HttpClient` that builds the request host from `session.shop` [1](#0-0) , and both requests carry `client_secret` in the body.

### Citations

**File:** lib/shopify_api/clients/http_client.rb (L16-19)
```ruby
        api_host = Context.api_host

        @base_uri = T.let("https://#{api_host || session.shop}", String)
        @base_uri_and_path = T.let("#{@base_uri}#{base_path}", String)
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

**File:** lib/shopify_api/auth/refresh_token.rb (L18-25)
```ruby
        def refresh_access_token(shop:, refresh_token:)
          unless ShopifyAPI::Context.setup?
            raise ShopifyAPI::Errors::ContextNotSetupError,
              "ShopifyAPI::Context not setup, please call ShopifyAPI::Context.setup"
          end

          validated_shop = Utils::ShopValidator.sanitize!(shop)
          shop_session = ShopifyAPI::Auth::Session.new(shop: validated_shop)
```

**File:** lib/shopify_api/auth/token_exchange.rb (L39-51)
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
```

**File:** lib/shopify_api/auth/token_exchange.rb (L52-59)
```ruby
          body = {
            client_id: ShopifyAPI::Context.api_key,
            client_secret: ShopifyAPI::Context.api_secret_key,
            grant_type: TOKEN_EXCHANGE_GRANT_TYPE,
            subject_token: session_token,
            subject_token_type: ID_TOKEN_TYPE,
            requested_token_type: requested_token_type.serialize,
          }
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
