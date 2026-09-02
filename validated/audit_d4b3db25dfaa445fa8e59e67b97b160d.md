This is the key finding: in `TokenExchange.exchange_token`, the shop used to construct the HTTP request destination comes directly from the unauthenticated *shape* of the JWT `dest` claim, with no validation that it is a genuine `*.myshopify.com` domain before being used as the literal request host.

### Title
Unvalidated `dest` claim from session token used directly as HTTP request host in Token Exchange - (File: `lib/shopify_api/auth/token_exchange.rb`)

### Summary
`TokenExchange.exchange_token` decodes the caller-supplied session token, takes the `dest` claim from the payload, and uses it verbatim as the `shop` for the `Session` that determines the destination host of the subsequent `client.request` call that transmits `client_secret` and `client_id` in the POST body.

### Finding Description
`JwtPayload#shop` merely strips `"https://"` from the `dest` claim and returns the remainder, with no format/domain validation: [1](#0-0) . `TokenExchange.exchange_token` then uses this value as `dest_shop`, builds a `Session` with `shop: dest_shop`, and passes that session into `Clients::HttpClient.new(session: shop_session, base_path: "/admin/oauth")` before POSTing a body containing `client_secret` and `client_id`: [2](#0-1) . `HttpClient#initialize` builds the request's base URI directly from `session.shop` (`@base_uri = "https://#{api_host || session.shop}"`), with no allow-list check limiting it to `*.myshopify.com`: [3](#0-2) .

Only `aud` is checked against `Context.api_key`; the signature check confirms the token was issued for this app's client ID, but places no constraint on the `dest` value's domain shape (e.g., that it ends in `.myshopify.com` or a valid Shopify-controlled domain): [4](#0-3) .

The identity binding that should hold is: **the host that receives the `client_secret` == a genuine Shopify-controlled domain**. Since the code trusts `dest` for host construction without validating its shape, this binding is not enforced by the library itself.

### Impact Explanation
If the `session_token` string passed into `exchange_token` originates from anything other than App Bridge's genuine token flow (e.g., is attacker-influenced, replayed, or otherwise not independently re-verified for shop domain shape by the host app), the resulting HTTP request — which carries the app's `client_secret` in its body — is sent to a host derived from the token's `dest` claim. This is an SSRF-with-credentials pattern (the analog of the AuctionCrowdfund bug's "attacker controls the price/target without the code re-checking who legitimately controls it").

### Likelihood Explanation
Low-to-moderate. Session tokens are normally minted and signed only by Shopify, and the JWT signature check with `Context.api_secret_key` prevents a fully unauthenticated attacker from forging an arbitrary `dest` from scratch. However, the library itself performs no additional sanity check that `dest` is a well-formed `*.myshopify.com`/Shopify domain before using it as a literal request host, which is a defense-in-depth gap relative to the "host validated versus host that receives the client_secret" binding class described in the prompt. I could not fully verify within remaining iterations whether any additional shop-domain format check exists elsewhere in the exchange path (e.g., `AuthScopes`, `Context`, or REST client base_path helpers) that might mitigate this.

### Recommendation
Validate that `dest_shop` matches the expected Shopify domain pattern (e.g., matches `/\A[a-zA-Z0-9][a-zA-Z0-9-]*\.myshopify\.(com|io)\z/` or the configured `custom_shop_domains`) before constructing the `Session`/`HttpClient` used to send `client_secret`, mirroring the existing `.my.shop.dev` special-case logic already present in `Oauth.auth_base_uri`.

### Proof of Concept
Not independently verified with a runnable exploit; this write-up is based on static code-path tracing of `exchange_token` → `Session.new(shop: dest_shop)` → `HttpClient#initialize` → `@base_uri = "https://#{session.shop}"`. I was unable to confirm within the available iterations whether the JWT signature check alone is sufficient to fully block attacker-controlled `dest` values in all deployment configurations (e.g., custom shop domain allowances), so this should be treated as a hardening gap rather than a confirmed exploitable bypass.

### Citations

**File:** lib/shopify_api/auth/jwt_payload.rb (L43-45)
```ruby
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

**File:** lib/shopify_api/clients/http_client.rb (L16-19)
```ruby
        api_host = Context.api_host

        @base_uri = T.let("https://#{api_host || session.shop}", String)
        @base_uri_and_path = T.let("#{@base_uri}#{base_path}", String)
```
