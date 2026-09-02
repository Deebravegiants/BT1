### Title
`TokenExchange.exchange_token` sends the app's `client_secret` to an unvalidated host derived from the JWT `dest` claim - ([File: lib/shopify_api/auth/token_exchange.rb])

### Summary

### Finding Description
`ShopifyAPI::Auth::TokenExchange.exchange_token` builds its outbound request host directly from the session token's `dest` claim, with no domain trust check: [1](#0-0) 

```ruby
jwt_payload = ShopifyAPI::Auth::JwtPayload.new(session_token)
dest_shop = jwt_payload.shop
...
shop_session = ShopifyAPI::Auth::Session.new(shop: dest_shop)
...
client = Clients::HttpClient.new(session: shop_session, base_path: "/admin/oauth")
```

`jwt_payload.shop` is simply `dest.gsub("https://", "")` with no restriction to a Shopify-owned domain: [2](#0-1) 

`JwtPayload#initialize` only checks the signature and that `aud == Context.api_key`; it never validates `iss`/`dest` against a trusted-domain allow-list: [3](#0-2) 

`HttpClient` then uses `session.shop` verbatim as the request host and puts the client secret in the POST body: [4](#0-3) [5](#0-4) 

This is the exact identity-binding gap called out in the rules: **the host validated ≠ the host that receives the `client_secret`**. Compare with the two sibling methods in this same module/family, which explicitly enforce that binding by routing the shop through `Utils::ShopValidator.sanitize!` before it is used to build the request host:

- `TokenExchange.migrate_to_expiring_token`: [6](#0-5) 

- `ClientCredentials.client_credentials`: [7](#0-6) 

`ShopValidator` exists precisely to enforce this invariant, restricting hosts to `shopify.com`, `myshopify.io`, `myshopify.com`, `spin.dev`, `shop.dev` (plus an optional custom `myshopify_domain`): [8](#0-7) 

`exchange_token` is the odd one out: it never calls `ShopValidator` on `dest_shop`, so any string that survives `dest.gsub("https://", "")` inside a validly-signed JWT becomes the host that the app's `client_id`/`client_secret` are POSTed to.

### Impact Explanation
If the `dest` claim in a session token is not itself constrained to Shopify-owned infrastructure (the code makes no such check — `JwtPayload` only checks `aud`, not `iss`/`dest`, and does not even require the token be an admin session token, as shown by the checkout-UI-extension token case which has a different `iss`), `exchange_token` will POST the app's `client_id` and `client_secret` to `https://#{dest_shop}/admin/oauth/access_token` for whatever `dest_shop` value is present. This is SSRF carrying the app's own credentials to a host that was never checked against the trusted-domain allow-list the library otherwise enforces (`ShopValidator`), matching the High-impact category "SSRF with the app's credentials … or credential leakage."

### Likelihood Explanation
The gap is a straightforward code inconsistency, not a hypothetical: two other methods in the same file/family (`migrate_to_expiring_token`, and `ClientCredentials.client_credentials`) deliberately guard the exact same operation with `ShopValidator.sanitize!`, showing the maintainers recognize the risk and consider it necessary — `exchange_token` simply omits the call for the value derived from the token's `dest` claim.

### Recommendation
In `TokenExchange.exchange_token`, validate `dest_shop` with `Utils::ShopValidator.sanitize!(dest_shop)` (or an equivalent trusted-domain check) before constructing `shop_session`/`HttpClient`, exactly as is already done in `migrate_to_expiring_token` and `ClientCredentials.client_credentials`. Additionally, consider having `JwtPayload` validate `dest`/`iss` against `ShopValidator`'s trusted domain list at decode time so all consumers of `JwtPayload#shop` get the guarantee automatically.

### Proof of Concept
1. Obtain (or coerce) a session token whose `dest` claim is not a Shopify-owned domain but still validates under `JwtPayload` (only `aud == Context.api_key` and signature/exp/nbf are checked; `iss`/`dest` are not restricted to trusted domains).
2. Call `ShopifyAPI::Auth::TokenExchange.exchange_token(session_token: token, requested_token_type: ...)`.
3. Observe (via `HttpClient#initialize`) that `@base_uri` becomes `"https://#{dest_shop}"`, i.e., the attacker-influenced value, and that the POST body containing `client_id`/`client_secret` is sent to that host — unlike `client_credentials`/`migrate_to_expiring_token`, which would raise `Errors::InvalidShopError` for the same `shop` value via `ShopValidator.sanitize!`.

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

**File:** lib/shopify_api/clients/http_client.rb (L11-33)
```ruby
      sig { params(base_path: String, session: T.nilable(Auth::Session)).void }
      def initialize(base_path:, session: nil)
        session ||= Context.active_session
        raise Errors::NoActiveSessionError, "No passed or active session" unless session

        api_host = Context.api_host

        @base_uri = T.let("https://#{api_host || session.shop}", String)
        @base_uri_and_path = T.let("#{@base_uri}#{base_path}", String)

        user_agent_prefix = Context.user_agent_prefix.nil? ? "" : "#{Context.user_agent_prefix} | "

        @headers = T.let({
          "User-Agent": "#{user_agent_prefix}Shopify API Library v#{VERSION} | Ruby #{RUBY_VERSION}",
          "Accept": "application/json",
        }, T::Hash[T.any(Symbol, String), T.untyped])

        @headers["Host"] = session.shop unless api_host.nil?

        unless session.access_token.nil? || T.must(session.access_token).empty?
          @headers["X-Shopify-Access-Token"] = T.cast(session.access_token, String)
        end
      end
```

**File:** lib/shopify_api/auth/client_credentials.rb (L19-33)
```ruby
        def client_credentials(shop:)
          unless ShopifyAPI::Context.setup?
            raise ShopifyAPI::Errors::ContextNotSetupError,
              "ShopifyAPI::Context not setup, please call ShopifyAPI::Context.setup"
          end

          validated_shop = Utils::ShopValidator.sanitize!(shop)
          shop_session = ShopifyAPI::Auth::Session.new(shop: validated_shop)
          body = {
            client_id: ShopifyAPI::Context.api_key,
            client_secret: ShopifyAPI::Context.api_secret_key,
            grant_type: CLIENT_CREDENTIALS_GRANT_TYPE,
          }

          client = Clients::HttpClient.new(session: shop_session, base_path: "/admin/oauth")
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
