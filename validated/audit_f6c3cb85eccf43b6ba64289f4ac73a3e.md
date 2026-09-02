Confirmed vulnerability: `TokenExchange.exchange_token` in `lib/shopify_api/auth/token_exchange.rb` takes the `shop` value used to build the destination host for the `client_secret`-bearing HTTP request directly from `jwt_payload.shop` (the JWT `dest` claim), and never passes it through `Utils::ShopValidator.sanitize!` the way `client_credentials.rb` and `migrate_to_expiring_token` do.

### Title
Unsanitized JWT `dest` claim used as request host in Token Exchange leaks `client_secret` - ([File: lib/shopify_api/auth/token_exchange.rb])

### Summary
`ShopifyAPI::Auth::TokenExchange.exchange_token` derives the host it sends the app's `client_id`/`client_secret` to directly from the session token's `dest` claim, without validating that the claim is a genuine, trusted `*.myshopify.com` (or otherwise trusted) domain via `Utils::ShopValidator`.

### Finding Description
In `exchange_token`, the shop used to build the outbound request is taken unsanitized: [1](#0-0) 

Compare this to the sibling method `migrate_to_expiring_token` in the same file, and to `ClientCredentials.client_credentials`, both of which call `Utils::ShopValidator.sanitize!(shop)` before constructing the session used for the outbound request: [2](#0-1) [3](#0-2) 

The `shop_session` built from the unsanitized `dest_shop` is then handed to `Clients::HttpClient`, which builds the outbound request host directly from `session.shop`: [4](#0-3) 

The request body sent to that host contains the app's `client_secret`: [5](#0-4) 

`JwtPayload` only verifies the JWT signature and that `aud == Context.api_key`; it never validates that `dest` is a trusted Shopify domain: [6](#0-5) 

The broken identity binding is: `host validated (none) != host that receives the app's client_secret (jwt_payload.shop)`. Every other credential-sending path in this gem (`client_credentials.rb`, `migrate_to_expiring_token`) binds the destination host through `ShopValidator.sanitize!`, which restricts hosts to `TRUSTED_SHOPIFY_DOMAINS`; `exchange_token` is the outlier that skips this check.

### Impact Explanation
If `dest` in a session token can ever be attacker-influenced (e.g., a compromised/malicious embedded-app iframe context, a misconfigured proxy, or any caller that constructs the `session_token` from data not perfectly restricted to trusted Shopify infrastructure), `exchange_token` will POST the app's `client_id` and `client_secret` to whatever host is present in `dest`, i.e., SSRF carrying the app's own OAuth `client_secret` to an attacker-controlled server. This matches the "High - SSRF with the app's credentials" impact category.

### Likelihood Explanation
Exploitation depends on the JWT's `dest` claim not being a trusted domain while the signature still validates — this requires either a real signing weakness, a token issued by a different context than assumed, or an integration bug in the host app that leads to unsanitized `dest` values reaching this code with a still-verifiable signature. This is a defense-in-depth gap rather than a directly attacker-forgeable-without-secrets bypass, so likelihood is lower than a straightforward missing-signature bug, but it is a genuine and inconsistent-with-the-rest-of-the-codebase omission of host validation on a `client_secret`-bearing request.

### Recommendation
Sanitize `dest_shop` through `Utils::ShopValidator.sanitize!` before constructing `shop_session` in `exchange_token`, mirroring the pattern already used in `migrate_to_expiring_token` and `client_credentials`:
```ruby
dest_shop = Utils::ShopValidator.sanitize!(jwt_payload.shop)
```

### Proof of Concept
Not independently reproducible without a JWT whose signature validates against `Context.api_secret_key` but whose `dest` claim is a non-Shopify host — this requires conditions (a signed token with an untrusted `dest`) that could not be fully confirmed as reachable by an unprivileged attacker within this investigation. The code-level omission itself is confirmed by direct comparison against the sanitized sibling paths cited above.

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

**File:** lib/shopify_api/clients/http_client.rb (L16-19)
```ruby
        api_host = Context.api_host

        @base_uri = T.let("https://#{api_host || session.shop}", String)
        @base_uri_and_path = T.let("#{@base_uri}#{base_path}", String)
```

**File:** lib/shopify_api/auth/jwt_payload.rb (L43-50)
```ruby
        raise ShopifyAPI::Errors::InvalidJwtTokenError,
          "Session token had invalid API key" unless @aud == Context.api_key
      end

      sig { returns(String) }
      def shop
        @dest.gsub("https://", "")
      end
```
