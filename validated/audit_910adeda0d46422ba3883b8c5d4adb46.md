I found a concrete SSRF/credential-leak analog: `TokenExchange.exchange_token` sends the app's `client_secret` to a host derived from an unvalidated JWT claim, unlike every other flow in the gem (`ClientCredentials`, `RefreshToken`, `TokenExchange.migrate_to_expiring_token`) that all call `Utils::ShopValidator.sanitize!` before building the request host.

### Title
`client_secret` sent to unvalidated host derived from JWT `dest` claim in token exchange - (File: `lib/shopify_api/auth/token_exchange.rb`)

### Summary
`TokenExchange.exchange_token` extracts the destination shop from the `dest` claim of a session token via `ShopifyAPI::Auth::JwtPayload#shop` and uses it, unsanitized, as the request host for the token-exchange POST that carries the app's `client_id`/`client_secret`. Every sibling credential-issuing method in the gem (`ClientCredentials.client_credentials`, `RefreshToken.refresh_access_token`, `TokenExchange.migrate_to_expiring_token`) explicitly calls `Utils::ShopValidator.sanitize!(shop)` before constructing the outbound request, but `exchange_token` does not apply this check to `dest_shop`.

### Finding Description
`JwtPayload#initialize` only verifies the JWT signature (HS256, keyed by `Context.api_secret_key`) and that `aud == Context.api_key`: [1](#0-0) 
It never validates that `dest` (and therefore `shop`) is a trusted `*.myshopify.com`/`spin.dev`/`shop.dev` host: [2](#0-1) 

`exchange_token` takes that unvalidated value and uses it directly to build the outbound session/host: [3](#0-2) 

`Clients::HttpClient#initialize` then builds the request base URI straight from `session.shop` with no allow-list check at all: [4](#0-3) 

Compare this to the three other credential-exchange call sites, which all sanitize the shop before it reaches `HttpClient`: [5](#0-4) [6](#0-5) [7](#0-6) 

The binding that should hold is: **`host that receives the client_secret` == `a value validated by `Utils::ShopValidator` against `TRUSTED_SHOPIFY_DOMAINS``**. In `exchange_token`, the host instead equals `JWT `dest` claim, stripped of `https://`, with no domain allow-listing` — the equality is broken specifically for this one flow.

The mitigating factor (and source of uncertainty) is that the JWT is HS256-signed with `Context.api_secret_key`, which an unprivileged internet user does not know, so they cannot themselves mint a token with an attacker-chosen `dest`. Exploitability therefore hinges on whether `dest` can be influenced through a channel that doesn't require forging the signature (e.g., if `dest` is ever attacker-influenced upstream, or if Shopify itself relaxes what it allows in `dest`, or via a token obtained through a compromised/malicious embedded surface). Within the code of this gem alone, I could not find a way for an unprivileged attacker to control `dest` without already possessing the signing secret, so I cannot fully confirm end-to-end exploitability purely from this repository's code — the missing `ShopValidator.sanitize!` call is a genuine, demonstrable **inconsistency and defense-in-depth gap** relative to the rest of the gem, but proving it is independently attacker-triggerable would require confirming how/whether `dest` can ever diverge from a trusted domain in a validly-signed token issued by Shopify's App Bridge, which is outside this gem's code.

### Impact Explanation
If `dest` can ever be a non-myshopify value in an otherwise validly-signed token (e.g., future Shopify domain formats, spin/dev environments not covered by `TRUSTED_SHOPIFY_DOMAINS`, or any issuance path Shopify may use that this gem's allow-list doesn't yet include), `exchange_token` would POST the app's `client_id` and `client_secret` to that host — an SSRF carrying the app's credentials, matching the High severity category ("SSRF with the app's credentials"). This is the same class of bug as the analog rule: a value trusted for routing sensitive credentials is not validated against the intended trust boundary that all sibling functions enforce.

### Likelihood Explanation
Low-to-Medium. Exploitation by a fully unprivileged attacker with no secret and no ability to influence `dest` in a validly-signed token is not demonstrated by this gem's code alone. The likelihood is driven entirely by whether `dest` can diverge from `TRUSTED_SHOPIFY_DOMAINS` in tokens that legitimately pass signature verification — something this codebase does not itself constrain, unlike its sibling flows which enforce it defensively regardless of the token's signature status.

### Recommendation
Apply the same defense-in-depth validation used everywhere else: sanitize `dest_shop` through `Utils::ShopValidator.sanitize!` before constructing `shop_session` in `exchange_token`, e.g.:
```ruby
dest_shop = Utils::ShopValidator.sanitize!(jwt_payload.shop)
shop_session = ShopifyAPI::Auth::Session.new(shop: dest_shop)
```
This closes the inconsistency and ensures the host receiving `client_secret` is always constrained to the trusted domain allow-list, independent of what the JWT `dest` claim contains.

### Proof of Concept
Not independently reproducible from this gem's code alone without possessing `Context.api_secret_key` (required to mint a validly-signed session token with a `dest` claim outside `Utils::ShopValidator::TRUSTED_SHOPIFY_DOMAINS`). The demonstrable part is the code-level inconsistency:
```ruby
# lib/shopify_api/auth/token_exchange.rb:39-51 -- no sanitize! call
jwt_payload = ShopifyAPI::Auth::JwtPayload.new(session_token)
dest_shop = jwt_payload.shop
shop_session = ShopifyAPI::Auth::Session.new(shop: dest_shop)

# vs. lib/shopify_api/auth/client_credentials.rb:25-26 -- sanitize! enforced
validated_shop = Utils::ShopValidator.sanitize!(shop)
shop_session = ShopifyAPI::Auth::Session.new(shop: validated_shop)
```

### Citations

**File:** lib/shopify_api/auth/jwt_payload.rb (L33-45)
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

**File:** lib/shopify_api/auth/refresh_token.rb (L18-33)
```ruby
        def refresh_access_token(shop:, refresh_token:)
          unless ShopifyAPI::Context.setup?
            raise ShopifyAPI::Errors::ContextNotSetupError,
              "ShopifyAPI::Context not setup, please call ShopifyAPI::Context.setup"
          end

          validated_shop = Utils::ShopValidator.sanitize!(shop)
          shop_session = ShopifyAPI::Auth::Session.new(shop: validated_shop)
          body = {
            client_id: ShopifyAPI::Context.api_key,
            client_secret: ShopifyAPI::Context.api_secret_key,
            grant_type: "refresh_token",
            refresh_token:,
          }

          client = Clients::HttpClient.new(session: shop_session, base_path: "/admin/oauth")
```
