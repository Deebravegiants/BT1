### Title
Missing shop-domain validation on JWT `dest` claim before sending `client_secret` in Token Exchange - ([File: lib/shopify_api/auth/token_exchange.rb])

### Summary
`ShopifyAPI::Auth::TokenExchange.exchange_token` derives the destination host for the OAuth token-exchange request directly from the unvalidated `dest` claim of the session token, then uses that raw string as the HTTP host that receives the app's `client_id`/`client_secret`. Every sibling credential-issuing method in the same module (`client_credentials`, `refresh_access_token`, `migrate_to_expiring_token`) explicitly calls `Utils::ShopValidator.sanitize!` on the shop value before building the request host, but `exchange_token` does not.

### Finding Description
`ShopifyAPI::Auth::JwtPayload#shop` performs no domain validation — it just strips a literal prefix: [1](#0-0) 

`TokenExchange.exchange_token` takes this raw value and uses it verbatim as the session's `shop`, which becomes the request host: [2](#0-1) 

`Clients::HttpClient` builds the outbound request host directly from `session.shop`, with no additional validation layer of its own: [3](#0-2) 

The request body posted to that host contains the app's `client_id` and `client_secret`: [4](#0-3) 

Contrast this with the other three OAuth-credential paths in the same module/file group, which all call `Utils::ShopValidator.sanitize!(shop)` — which restricts the host to `myshopify.com`/`myshopify.io`/`shopify.com`/`spin.dev`/`shop.dev` subdomains before it is ever used to build the destination host for a request carrying `client_secret`: [5](#0-4) [6](#0-5) [7](#0-6) 

The identity binding that should hold — analogous to the report's "scaling factor must match the value it is applied to" — is:

```
host_that_receives(client_id, client_secret) == ShopValidator.sanitize!(shop)
```

In `exchange_token` this instead reduces to:

```
host_that_receives(client_id, client_secret) == JwtPayload#shop (raw "dest" claim, string-stripped only)
```

`JwtPayload` only verifies the JWT signature (HS256 with `Context.api_secret_key`) and the `aud` claim; it never checks that `dest` is actually a trusted `*.myshopify.com`-style host, unlike `ShopValidator.sanitize!` used everywhere else credentials are transmitted.

### Impact Explanation
If the `dest` claim value ever differs from a well-formed, trusted Shopify host (e.g., unexpected formatting, injected characters, or any future change in how the claim is populated/consumed), `exchange_token` will unconditionally send the app's `client_id` and `client_secret` to that unverified host — an SSRF carrying the app's own OAuth credentials, matching the "High" severity category (SSRF with the app's credentials). This is a direct violation of the defense-in-depth invariant the library itself established for every other credential-issuing code path in `lib/shopify_api/auth/`.

### Likelihood Explanation
Exploitability is bounded by the fact that the session token must carry a valid signature under `Context.api_secret_key`, which an external, unprivileged attacker does not possess — this limits blast radius compared to a fully attacker-forgeable field. However, the `session_token` itself is explicitly documented as reachable via a URL query parameter (`id_token=`) rather than only a trusted transport, and the resulting `dest` value is consumed with zero format/domain validation before being used as an outbound request host for the app's own secret — an inconsistency not present anywhere else in the codebase. Because the enforcement gap is concrete and code-verifiable (missing `ShopValidator.sanitize!` call that exists in three sibling methods), and the only other independent variable is the trustworthiness of the byte content Shopify puts in `dest`, this is a real, fixable defect rather than a purely theoretical one.

### Recommendation
Apply `Utils::ShopValidator.sanitize!` to `jwt_payload.shop` (the `dest` claim) in `TokenExchange.exchange_token`, exactly as is already done in `client_credentials`, `refresh_access_token`, and `migrate_to_expiring_token`, before constructing `shop_session`/building the request host:

```ruby
dest_shop = ShopifyAPI::Utils::ShopValidator.sanitize!(jwt_payload.shop)
```

### Proof of Concept
1. Set up `ShopifyAPI::Context` normally with a real `api_secret_key`.
2. Craft (or, in a real deployment, capture) a session token whose `dest` claim is not a clean `*.myshopify.com` host string — e.g. any value that passes JWT signature/`aud` checks in `JwtPayload` but is not filtered through `ShopValidator` (e.g., a value containing extra path/host components beyond a bare domain).
3. Call:
```ruby
ShopifyAPI::Auth::TokenExchange.exchange_token(
  session_token: crafted_token,
  requested_token_type: ShopifyAPI::Auth::TokenExchange::RequestedTokenType::OFFLINE_ACCESS_TOKEN,
)
```
4. Observe that `Clients::HttpClient` builds `@base_uri = "https://#{dest_shop}"` and POSTs a JSON body containing `client_id` and `client_secret` to that host, with no `ShopValidator` check ever performed — unlike the identical flow in `client_credentials.rb`/`refresh_token.rb`, where the same crafted `shop` value would be rejected with `ShopifyAPI::Errors::InvalidShopError` before any request is made.

### Citations

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

**File:** lib/shopify_api/auth/token_exchange.rb (L103-115)
```ruby
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

**File:** lib/shopify_api/clients/http_client.rb (L16-19)
```ruby
        api_host = Context.api_host

        @base_uri = T.let("https://#{api_host || session.shop}", String)
        @base_uri_and_path = T.let("#{@base_uri}#{base_path}", String)
```

**File:** lib/shopify_api/auth/client_credentials.rb (L25-33)
```ruby
          validated_shop = Utils::ShopValidator.sanitize!(shop)
          shop_session = ShopifyAPI::Auth::Session.new(shop: validated_shop)
          body = {
            client_id: ShopifyAPI::Context.api_key,
            client_secret: ShopifyAPI::Context.api_secret_key,
            grant_type: CLIENT_CREDENTIALS_GRANT_TYPE,
          }

          client = Clients::HttpClient.new(session: shop_session, base_path: "/admin/oauth")
```

**File:** lib/shopify_api/auth/refresh_token.rb (L24-33)
```ruby
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
