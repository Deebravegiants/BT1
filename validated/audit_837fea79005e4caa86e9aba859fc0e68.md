### Title
`Oauth.validate_auth_callback` sends the app's `client_secret` to a shop-supplied host without domain sanitization - (File: lib/shopify_api/auth/oauth.rb)

### Summary
`ShopifyAPI::Auth::Oauth.validate_auth_callback` builds the OAuth token-exchange request URL from `auth_query.shop` via `auth_base_uri(shop)` and POSTs a body containing `client_id`/`client_secret` to `https://#{shop}/admin/oauth/access_token` without ever calling `Utils::ShopValidator.sanitize!` on `shop`, unlike the sibling flows `ClientCredentials.client_credentials` and `RefreshToken.refresh_access_token`, which both call `Utils::ShopValidator.sanitize!(shop)` before constructing the request.

### Finding Description
`validate_auth_callback` only checks that `Utils::HmacValidator.validate(auth_query)` passes [1](#0-0) . The HMAC is computed over the exact fields the caller supplies to `AuthQuery.new` (`code, host, shop, state, timestamp`) [2](#0-1) , using `OpenSSL.secure_compare` against `Context.api_secret_key` (or the old key) [3](#0-2) .

The `shop` value that passes HMAC validation is then used directly, unsanitized, to build the destination host that receives the app's `client_secret`: [4](#0-3) [5](#0-4) 

Contrast this with `ClientCredentials.client_credentials` and `RefreshToken.refresh_access_token`, which explicitly call `Utils::ShopValidator.sanitize!(shop)` — raising `Errors::InvalidShopError` unless the domain is one of the `TRUSTED_SHOPIFY_DOMAINS` (`shopify.com`, `myshopify.io`, `myshopify.com`, `spin.dev`, `shop.dev`) — before ever putting `shop` into a URL that will carry the `client_secret` [6](#0-5) [7](#0-6) [8](#0-7) .

The equality this gem is supposed to enforce is: `host that is validated as a trusted Shopify domain == host that receives the client_secret`. In `oauth.rb`, that equality is broken: the host validated is merely "whatever byte string the caller passed as `shop`, provided the caller's own HMAC matches" — there is no independent check that the host is actually a `*.myshopify.com`/`myshopify.io`/etc domain.

### Impact Explanation
Because the host embedded in the outgoing OAuth token-exchange request is never checked against `ShopValidator::TRUSTED_SHOPIFY_DOMAINS`, any code path in the host application that constructs an `AuthQuery` with a caller-influenced `shop` value (e.g., built from `request.parameters` as literally documented in `docs/usage/oauth.md`) risks sending the app's `client_id`/`client_secret` to an attacker-chosen host if that host string also satisfies the HMAC check — this is an SSRF-with-credentials pattern (the exact class called out as High severity: "SSRF with the app's credentials"). It also means this module is inconsistent with the rest of the gem's own defense-in-depth (`ClientCredentials`, `RefreshToken` both sanitize), so it cannot claim the trusted-domain invariant holds for the OAuth authorization-code flow.

### Likelihood Explanation
Exploitation requires an attacker to produce a `shop` value with a valid HMAC computed by the app's own `api_secret_key`/`old_api_secret_key`. In the intended flow this signature is generated exclusively by Shopify's servers upon redirecting back from the real OAuth consent screen, and an unprivileged internet user cannot forge it without knowledge of the secret. I could not find any additional gem-side call that constrains `shop` to a trusted domain before or after HMAC validation in this file, so if the assumption that the HMAC signer is always trustworthy about domain shape does not hold in some deployment (e.g., an app using `old_api_secret_key` rotation, or any caller mistakenly reusing a previously valid HMAC/shop pair), the missing sanitize step is the only thing standing in the way. This is lower likelihood than a directly attacker-forgeable bug, since it depends on the secret-holder (Shopify) misbehaving or a rotation/reuse edge case, which I was not able to fully verify within this codebase.

### Recommendation
Call `Utils::ShopValidator.sanitize!(auth_query.shop)` in `validate_auth_callback` before using the value to build `auth_base_uri` and before constructing `null_session`/the returned `Session`, mirroring the pattern already used in `ClientCredentials.client_credentials` and `RefreshToken.refresh_access_token`.

### Proof of Concept
Not independently reproducible from static analysis alone: constructing a passing HMAC requires the app's `api_secret_key`, which is out of scope for an unprivileged attacker per the rules. The finding is a structural inconsistency (missing `ShopValidator.sanitize!` call in `oauth.rb` relative to `client_credentials.rb`/`refresh_token.rb`), not a demonstrated end-to-end exploit; I flag this explicitly as unverified beyond the code-level comparison shown above.

### Citations

**File:** lib/shopify_api/auth/oauth.rb (L60-65)
```ruby
        def validate_auth_callback(cookies:, auth_query:)
          unless Context.setup?
            raise Errors::ContextNotSetupError, "ShopifyAPI::Context not setup, please call ShopifyAPI::Context.setup"
          end
          raise Errors::InvalidOauthError, "Invalid OAuth callback." unless Utils::HmacValidator.validate(auth_query)
          raise Errors::UnsupportedOauthError, "Cannot perform OAuth for private apps." if Context.private?
```

**File:** lib/shopify_api/auth/oauth.rb (L73-81)
```ruby
          null_session = Auth::Session.new(shop: auth_query.shop)
          body = {
            client_id: Context.api_key,
            client_secret: Context.api_secret_key,
            code: auth_query.code,
            expiring: Context.expiring_offline_access_tokens ? 1 : 0, # Only applicable for offline tokens
          }

          client = Clients::HttpClient.new(session: null_session, base_path: "/admin/oauth")
```

**File:** lib/shopify_api/auth/oauth.rb (L117-119)
```ruby
        sig { params(shop: String).returns(String) }
        def auth_base_uri(shop)
          return "https://#{shop}/admin" unless defined?(DevServer) && shop.include?(".my.shop.dev")
```

**File:** lib/shopify_api/auth/oauth/auth_query.rb (L33-43)
```ruby
        sig { override.returns(String) }
        def to_signable_string
          params = {
            code: code,
            host: host,
            shop: shop,
            state: state,
            timestamp: timestamp,
          }
          URI.encode_www_form(params)
        end
```

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-22)
```ruby
        sig { params(verifiable_query: VerifiableQuery).returns(T::Boolean) }
        def validate(verifiable_query)
          return false unless verifiable_query.hmac

          result = validate_signature(verifiable_query, Context.api_secret_key)
          if result || Context.old_api_secret_key.nil? || T.must(Context.old_api_secret_key).empty?
            result
          else
            validate_signature(verifiable_query, T.must(Context.old_api_secret_key))
          end
        end
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

**File:** lib/shopify_api/auth/refresh_token.rb (L18-33)
```ruby
        def refresh_access_token(shop:, refresh_token:)
          unless ShopifyAPI::Context.setup?
            raise ShopifyAPI::Errors::ContextNotSetupError,
              "ShopifyAPI::Context not setup, please call ShopifyAPI::Context.setup"
          end

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
