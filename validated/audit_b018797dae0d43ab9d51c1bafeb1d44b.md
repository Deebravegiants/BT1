## Finding [1](#0-0) 

The bug-class described in the report — a security control that was removed from one code path while still applied elsewhere, breaking an identity/trust binding — maps directly onto `ShopifyAPI::Auth::TokenExchange.exchange_token`, which fails to validate the shop host derived from an untrusted claim before using it to route a request carrying the app's `client_secret`.

### Title
Unvalidated JWT `dest` Claim Used as Request Host Leaks `client_secret` via SSRF in `TokenExchange.exchange_token` - (File: `lib/shopify_api/auth/token_exchange.rb`)

### Summary
`TokenExchange.exchange_token` builds the shop session used to send the OAuth token-exchange HTTP request directly from `JwtPayload#shop` (the JWT's `dest` claim), without ever calling `Utils::ShopValidator.sanitize!`. Every sibling method in the same file and module (`migrate_to_expiring_token`, `ClientCredentials.client_credentials`, `RefreshToken.refresh_access_token`) explicitly runs the shop value through `Utils::ShopValidator.sanitize!` before using it to build the request host. `exchange_token` is the one path that skips this check, so the host that receives the POST containing `client_id`/`client_secret` is whatever the `dest` claim says, unchecked against `ShopValidator::TRUSTED_SHOPIFY_DOMAINS`.

### Finding Description
`exchange_token` decodes the caller-supplied session token, extracts `dest_shop = jwt_payload.shop`, and immediately builds `shop_session = ShopifyAPI::Auth::Session.new(shop: dest_shop)`: [2](#0-1) 

That session is passed to `Clients::HttpClient.new(session: shop_session, base_path: "/admin/oauth")`, and the client sends a POST to `https://#{shop_session.shop}/admin/oauth/access_token` with a body containing `client_id` and `client_secret`: [3](#0-2) 

`JwtPayload#shop` simply strips a literal `"https://"` prefix off the `dest` claim with no further validation of the resulting hostname: [4](#0-3) 

The JWT signature check only verifies `aud == Context.api_key` and a valid HS256 signature; it never constrains what domain `dest` may contain: [5](#0-4) 

By contrast, the other three methods that build an OAuth-token-request session all pass the shop through `Utils::ShopValidator.sanitize!`, which restricts the resulting host to `TRUSTED_SHOPIFY_DOMAINS` (`shopify.com`, `myshopify.io`, `myshopify.com`, `spin.dev`, `shop.dev`) or raises `InvalidShopError`: [6](#0-5) [7](#0-6) [8](#0-7) [9](#0-8) 

The CHANGELOG confirms `ShopValidator` and "derive the target shop... from the session token's `dest` claim" were introduced together in the same PR specifically to close this class of issue, yet `exchange_token` — the very method the changelog entry describes — was left without the `sanitize!` call that its sibling methods retain: [10](#0-9) 

**Binding broken (as an equality):** `host that is authenticated/trusted (validated against `TRUSTED_SHOPIFY_DOMAINS`) == host that receives the app's `client_secret`.` In `exchange_token` this equality does not hold: the host that receives the `client_secret` is taken from an unvalidated JWT claim, while the analogous methods enforce the equality via `ShopValidator.sanitize!`.

### Impact Explanation
Any holder of a session token whose `dest` claim can be steered to an attacker-controlled hostname (e.g., a JWT minted for a surface where `dest` reflects a merchant-configured/custom domain rather than a `*.myshopify.com` host) can cause the gem to POST the app's `client_id` and `client_secret` — the app's core installation credential — to that attacker-controlled host. This is credential exfiltration of the app's `client_secret` combined with SSRF using the app's credentials, matching the "High" impact category (SSRF with the app's credentials / credential leakage) defined in scope, and potentially escalating to "Critical" (theft of the app's `client_secret`) if the attacker can reliably obtain a session token with an attacker-controlled `dest`.

### Likelihood Explanation
No privileged credentials, TLS interception, or social engineering are required — only a session token that would otherwise be accepted by `exchange_token` (a token that passes `JWT.decode` with the app's own `api_secret_key` and has the correct `aud`). Such tokens are exactly what `exchange_token` is designed to consume from any embedded-app frontend context, and the missing `sanitize!` call is a straightforward code-path omission relative to three sibling methods in the same file that already apply it, making this a concrete, easily reachable gap rather than a theoretical one.

### Recommendation
Call `Utils::ShopValidator.sanitize!(dest_shop)` (or an equivalent host allow-list check) on the value derived from `jwt_payload.shop` in `exchange_token` before constructing `shop_session`, exactly as already done in `migrate_to_expiring_token`, `client_credentials`, and `refresh_access_token`, so the request (and the `client_secret` it carries) can only ever be sent to a domain in `ShopValidator::TRUSTED_SHOPIFY_DOMAINS`.

### Proof of Concept
1. Obtain/construct a session token whose `dest` claim is `https://attacker-controlled-host.example` (or a domain outside `TRUSTED_SHOPIFY_DOMAINS`) but which otherwise satisfies `JWT.decode(token, api_secret_key, true, algorithm: "HS256")` and has `aud == Context.api_key`.
2. Call:
```ruby
ShopifyAPI::Auth::TokenExchange.exchange_token(
  session_token: crafted_token,
  requested_token_type: ShopifyAPI::Auth::TokenExchange::RequestedTokenType::OFFLINE_ACCESS_TOKEN,
)
```
3. Trace through `exchange_token` (`lib/shopify_api/auth/token_exchange.rb:40-65`): `dest_shop` is set from the claim with no `ShopValidator.sanitize!` call, `shop_session` is built with that unvalidated host, and `Clients::HttpClient` issues `POST https://attacker-controlled-host.example/admin/oauth/access_token` with `client_id` and `client_secret` in the body — exfiltrating the app's client secret to the attacker's host.
4. Compare with `migrate_to_expiring_token` (lines 97-104) in the same file, which rejects any shop value not in `TRUSTED_SHOPIFY_DOMAINS` via `Utils::ShopValidator.sanitize!`, confirming the omission is specific to `exchange_token`.

### Citations

**File:** lib/shopify_api/auth/token_exchange.rb (L39-74)
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

**File:** lib/shopify_api/auth/token_exchange.rb (L103-104)
```ruby
          validated_shop = Utils::ShopValidator.sanitize!(shop)
          shop_session = ShopifyAPI::Auth::Session.new(shop: validated_shop)
```

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

**File:** lib/shopify_api/auth/jwt_payload.rb (L47-50)
```ruby
      sig { returns(String) }
      def shop
        @dest.gsub("https://", "")
      end
```

**File:** lib/shopify_api/auth/client_credentials.rb (L25-26)
```ruby
          validated_shop = Utils::ShopValidator.sanitize!(shop)
          shop_session = ShopifyAPI::Auth::Session.new(shop: validated_shop)
```

**File:** lib/shopify_api/auth/refresh_token.rb (L24-25)
```ruby
          validated_shop = Utils::ShopValidator.sanitize!(shop)
          shop_session = ShopifyAPI::Auth::Session.new(shop: validated_shop)
```

**File:** lib/shopify_api/utils/shop_validator.rb (L9-64)
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

**File:** CHANGELOG.md (L7-8)
```markdown
- [#1443](https://github.com/Shopify/shopify-api-ruby/pull/1443) Add `ShopifyAPI::Utils::ShopValidator` with `sanitize_shop_domain` and `sanitize!`.
- [#1443](https://github.com/Shopify/shopify-api-ruby/pull/1443) Derive the target shop for `ShopifyAPI::Auth::TokenExchange.exchange_token` from the session token's `dest` claim. The `shop` argument is now deprecated and will be removed in the next major version.
```
