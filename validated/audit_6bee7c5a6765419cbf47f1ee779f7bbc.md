### Title
`TokenExchange.exchange_token` sends the app's `client_secret` to a host built from an unsanitized JWT `dest` claim - (File: `lib/shopify_api/auth/token_exchange.rb`)

### Summary
`ShopifyAPI::Auth::TokenExchange.exchange_token` builds the outbound request host directly from the session token's `dest` claim, unlike every sibling OAuth-grant flow in this gem, which routes the caller-supplied `shop` through `Utils::ShopValidator.sanitize!` before it is used to build the request host.

### Finding Description
`exchange_token` decodes the JWT with `ShopifyAPI::Auth::JwtPayload.new(session_token)` and takes `dest_shop = jwt_payload.shop`, which is simply `@dest.gsub("https://", "")` with no format/domain validation [1](#0-0) . That raw string is used to construct `shop_session = ShopifyAPI::Auth::Session.new(shop: dest_shop)`, which is passed straight into `Clients::HttpClient.new(session: shop_session, base_path: "/admin/oauth")` and used as the outbound host: `@base_uri = "https://#{api_host || session.shop}"` [2](#0-1) . The POST body sent to that host includes `client_id` and the app's `client_secret` in plaintext [3](#0-2) .

Every other credential-bearing OAuth flow in this same file/module treats the `shop` value as untrusted and explicitly calls `Utils::ShopValidator.sanitize!(shop)` before building the session/host: `migrate_to_expiring_token` [4](#0-3) , `RefreshToken.refresh_access_token` [5](#0-4) , and `ClientCredentials.client_credentials` [6](#0-5) . `exchange_token` is the one grant path that skips this check entirely — the equality that should hold is `host receiving client_secret == ShopValidator.sanitize!(shop)`, but here it is `host receiving client_secret == raw JWT dest claim`.

The `JwtPayload` constructor does verify the HMAC-SHA256 signature of the JWT and the `aud` claim against `Context.api_key` [7](#0-6) , so a token cannot be *forged* without the app's `client_secret`. However, the gem never re-validates that the resulting `dest`/`shop` string is actually a well-formed, single-label myshopify/spin/shop.dev host (no path, no extra characters, no unexpected scheme) the way `ShopValidator.sanitize_shop_domain` does for every other entry point (checking against `TRUSTED_SHOPIFY_DOMAINS`, rejecting `no_shop_name_in_subdomain`, handling `unified_admin?` rewriting, etc.) [8](#0-7) .

### Impact Explanation
If `dest` is not constrained to a safe host format (i.e., the exploitability of this depends entirely on whether Shopify's session-token issuance process guarantees `dest` is always a clean `*.myshopify.com`/`*.myshopify.io` string with no embedded path/host-injection characters — something this gem's own code does not itself enforce or trust for any other flow), a crafted `dest` value could redirect the `client_secret`-bearing POST to an attacker-influenced host, which would be High/Critical (client_secret exfiltration). I could not verify from this gem's code whether Shopify's token issuer imposes that guarantee externally; the gem's own defense-in-depth check (`ShopValidator.sanitize!`) that is applied everywhere else is simply missing here.

### Likelihood Explanation
Low-to-moderate confidence as a directly exploitable bug by an unprivileged internet user, because minting a validly-signed session token requires knowledge of `Context.api_secret_key`, which only Shopify and the app hold. The concrete exploit path (an attacker independently controlling the `dest` claim's exact bytes) requires either a bug in Shopify's own token issuance or some other component in the app that can influence what an already-signed token's `dest` says — I was not able to prove either from this gem's code alone. What is provable is the code-level inconsistency: this is the one place among four structurally identical `client_secret`-sending flows that omits `ShopValidator.sanitize!`.

### Recommendation
Apply `Utils::ShopValidator.sanitize!` to `jwt_payload.shop` (or `dest_shop`) before constructing `shop_session`/before it is used to build `HttpClient`'s base URI, exactly as done in `migrate_to_expiring_token`, `refresh_access_token`, and `client_credentials`, so the request host is always constrained to `ShopValidator::TRUSTED_SHOPIFY_DOMAINS` regardless of what the JWT's `dest` claim contains.

### Proof of Concept
Not reproducible purely within this gem's test surface: constructing a validly HMAC-signed session token with an attacker-chosen malicious `dest` requires the app's `client_secret`, which an unprivileged external attacker does not have. This finding is reported as a code-level defense-in-depth gap/inconsistency (missing `ShopValidator.sanitize!` call unique to `exchange_token`) rather than a demonstrated end-to-end exploit; a full PoC would require establishing that some external component can influence the `dest` claim value in a signed token, which is outside this gem's code and could not be confirmed with the tools available.

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

**File:** lib/shopify_api/auth/jwt_payload.rb (L47-50)
```ruby
      sig { returns(String) }
      def shop
        @dest.gsub("https://", "")
      end
```

**File:** lib/shopify_api/clients/http_client.rb (L16-19)
```ruby
        api_host = Context.api_host

        @base_uri = T.let("https://#{api_host || session.shop}", String)
        @base_uri_and_path = T.let("#{@base_uri}#{base_path}", String)
```

**File:** lib/shopify_api/auth/token_exchange.rb (L51-59)
```ruby
          shop_session = ShopifyAPI::Auth::Session.new(shop: dest_shop)
          body = {
            client_id: ShopifyAPI::Context.api_key,
            client_secret: ShopifyAPI::Context.api_secret_key,
            grant_type: TOKEN_EXCHANGE_GRANT_TYPE,
            subject_token: session_token,
            subject_token_type: ID_TOKEN_TYPE,
            requested_token_type: requested_token_type.serialize,
          }
```

**File:** lib/shopify_api/auth/token_exchange.rb (L103-104)
```ruby
          validated_shop = Utils::ShopValidator.sanitize!(shop)
          shop_session = ShopifyAPI::Auth::Session.new(shop: validated_shop)
```

**File:** lib/shopify_api/auth/refresh_token.rb (L24-25)
```ruby
          validated_shop = Utils::ShopValidator.sanitize!(shop)
          shop_session = ShopifyAPI::Auth::Session.new(shop: validated_shop)
```

**File:** lib/shopify_api/auth/client_credentials.rb (L25-26)
```ruby
          validated_shop = Utils::ShopValidator.sanitize!(shop)
          shop_session = ShopifyAPI::Auth::Session.new(shop: validated_shop)
```

**File:** lib/shopify_api/utils/shop_validator.rb (L9-48)
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

      class << self
        extend T::Sig

        sig do
          params(
            shop_domain: String,
            myshopify_domain: T.nilable(String),
          ).returns(T.nilable(String))
        end
        def sanitize_shop_domain(shop_domain, myshopify_domain: nil)
          uri = uri_from_shop_domain(shop_domain, myshopify_domain)
          return nil if uri.nil? || uri.host.nil? || uri.host.empty?

          trusted_domains(myshopify_domain).each do |trusted_domain|
            host = T.cast(uri.host, String)
            uri_domain = uri.domain
            next if uri_domain.nil?

            no_shop_name_in_subdomain = host == trusted_domain
            from_trusted_domain = trusted_domain == uri_domain

            if unified_admin?(uri) && from_trusted_domain
              return myshopify_domain_from_unified_admin(uri)
            end
            return nil if no_shop_name_in_subdomain || host.empty?
            return host if from_trusted_domain
          end
          nil
        end
```
