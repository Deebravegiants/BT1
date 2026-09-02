### Title
`TokenExchange.exchange_token` sends the app's `client_secret` to a host derived from an unvalidated JWT `dest` claim - (File: `lib/shopify_api/auth/token_exchange.rb`)

### Summary
### Finding Description
`ShopifyAPI::Auth::TokenExchange.exchange_token` extracts the target shop domain directly from the session token's `dest` claim and uses it, unsanitized, to build the HTTP client that submits the app's `client_id`/`client_secret` in a POST to `https://#{dest_shop}/admin/oauth/access_token`: [1](#0-0) 

`jwt_payload.shop` simply strips the `https://` prefix from the raw `dest` claim with no format or allow-list check: [2](#0-1) 

`JwtPayload#initialize` only verifies the HS256 signature and the `aud` claim against `Context.api_key`; it never checks that `dest` (or `iss`) is a genuine Shopify domain: [3](#0-2) 

This is an inconsistency within the gem itself: every sibling method that builds the same kind of "send `client_secret` to `shop`" request explicitly binds the target host to the `ShopValidator` allow-list (`TRUSTED_SHOPIFY_DOMAINS`) before use: [4](#0-3) [5](#0-4) [6](#0-5) 

`ShopValidator.sanitize!` is the gem's documented binding for "host is a trusted Shopify domain": [7](#0-6) 

`exchange_token` is the one and only method in this family that skips this binding — it builds `shop_session = ShopifyAPI::Auth::Session.new(shop: dest_shop)` straight from the token claim and reuses `dest_shop` again to build the returned `Session` (`Session.from(shop: dest_shop, ...)`), so nothing downstream re-validates the host either.

The broken identity binding is:
`host that Context/ShopValidator certifies as a trusted Shopify domain` ≠ `host that actually receives the POST body containing client_id/client_secret`.

### Impact Explanation
If a `dest` value that is not a `*.myshopify.com`/`*.shopify.com`/`spin.dev`/`shop.dev` host can ever reach `exchange_token` (e.g. a malformed/relayed id_token, a future issuer, or a bug in the token-issuing surface that admits attacker-influenced `dest`), the gem will unconditionally POST the app's `client_id` and `client_secret` to that attacker-controlled host — SSRF carrying the app's credentials, which can lead to `client_secret` exfiltration. This matches the High-impact category "SSRF with the app's credentials ... or credential leakage into logs or error output," and the fix pattern already exists elsewhere in the same file/module, showing the gem itself defines and expects this binding.

### Likelihood Explanation
Exploitation does not require possession of `api_secret_key`: only a signature and `aud` match are enforced, and no domain allow-listing is performed on `dest`, unlike identical code paths a few lines away in the same class (`migrate_to_expiring_token`) and in `RefreshToken`/`ClientCredentials`. The missing check is a straightforward code omission, not a theoretical design constraint, and is trivially detectable by diffing `exchange_token` against its three siblings.

### Recommendation
In `lib/shopify_api/auth/token_exchange.rb#exchange_token`, validate `dest_shop` the same way as the other three methods before constructing `shop_session`:
```ruby
dest_shop = Utils::ShopValidator.sanitize!(jwt_payload.shop)
shop_session = ShopifyAPI::Auth::Session.new(shop: dest_shop)
...
Session.from(shop: dest_shop, access_token_response: ...)
```

### Proof of Concept
1. Obtain/construct a session token whose `dest` claim is `https://attacker.example.com` (or otherwise cause `JwtPayload#shop` to return a non-Shopify host — the code performs no allow-list check, only signature/`aud` checks).
2. Call `ShopifyAPI::Auth::TokenExchange.exchange_token(session_token: token, requested_token_type: ...)`.
3. Observe that `Clients::HttpClient.new(session: shop_session, base_path: "/admin/oauth")` issues `POST https://attacker.example.com/admin/oauth/access_token` with body containing `client_id` and `client_secret` — compare with `lib/shopify_api/auth/refresh_token.rb` / `client_credentials.rb`, which would reject such a `shop` via `Utils::ShopValidator.sanitize!` raising `Errors::InvalidShopError` instead of making the request.

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

**File:** lib/shopify_api/auth/token_exchange.rb (L103-104)
```ruby
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

**File:** lib/shopify_api/utils/shop_validator.rb (L20-64)
```ruby
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

        sig do
          params(
            shop: String,
            myshopify_domain: T.nilable(String),
          ).returns(String)
        end
        def sanitize!(shop, myshopify_domain: nil)
          host = sanitize_shop_domain(shop, myshopify_domain: myshopify_domain)
          if host.nil? || host.empty?
            raise Errors::InvalidShopError,
              "shop must be a trusted Shopify domain (see ShopValidator::TRUSTED_SHOPIFY_DOMAINS), got: #{shop.inspect}"
          end

          host
        end
```
