## Title
OAuth callback trusts unsanitized `shop` as SSRF target for the access-token exchange carrying `client_secret` - (File: `lib/shopify_api/auth/oauth.rb`)

### Summary
`ShopifyAPI::Auth::Oauth.validate_auth_callback` builds the session used to perform the access-token exchange directly from `auth_query.shop`, without ever passing it through `Utils::ShopValidator.sanitize!`, unlike every other credential-exchange entry point in the same module family.

### Finding Description
In `validate_auth_callback`, after HMAC validation and state/nonce comparison, the code does: [1](#0-0) 

`null_session = Auth::Session.new(shop: auth_query.shop)` is passed straight into `Clients::HttpClient.new(session: null_session, ...)`, and `HttpClient` derives the outbound request host directly from `session.shop`: [2](#0-1) 

This request body includes `client_id` and `client_secret` and is POSTed to `https://#{auth_query.shop}/admin/oauth/access_token`. Nowhere in `validate_auth_callback` is `auth_query.shop` passed through `Utils::ShopValidator.sanitize!`, which the codebase itself defines and consistently applies elsewhere in the same auth namespace: `Auth::ClientCredentials.client_credentials` and `Auth::TokenExchange.migrate_to_expiring_token` both call `Utils::ShopValidator.sanitize!(shop)` before constructing the session used for the token exchange: [3](#0-2) [4](#0-3) 

The identity binding that is broken here is: **the shop value whose bytes are covered by the HMAC != the shop value validated as belonging to a trusted `*.myshopify.com`/Shopify domain**. `Utils::HmacValidator.validate` only proves that `auth_query.shop` (together with `code`, `host`, `state`, `timestamp`) matches a signature computed with `Context.api_secret_key`; it says nothing about whether that string is actually a Shopify-controlled host: [5](#0-4) [6](#0-5) 

Because the HMAC is computed server-side over exactly the fields supplied in the request (the gem does not independently derive `shop` from a Shopify-issued, pre-validated source), and `ShopValidator.sanitize!`/`TRUSTED_SHOPIFY_DOMAINS` exist specifically to constrain `shop` to real Shopify domains before it is used as a network destination, skipping that check on this one code path leaves the SSRF-relevant host binding unenforced in the library itself, in contrast to the sibling `client_credentials`/`token_exchange` flows that do enforce it.

### Impact Explanation
If any wrapper/framework integration (e.g. Rails controller) constructs `AuthQuery` from raw callback request parameters and forwards it to `validate_auth_callback` (which is the exact usage pattern shown in this gem's own `docs/usage/oauth.md`), the `shop` field is never independently constrained to `TRUSTED_SHOPIFY_DOMAINS` inside the gem. Should an attacker manage to produce a valid HMAC for an attacker-chosen `shop` value (e.g., via the same weaknesses that would also break `ShopValidator` — for instance the previously fixed subdomain/host confusion cases the validator's own test suite guards against, such as `attacker.com/.myshopify.com` or `myshopify.com.evil.com`), the resulting request — carrying the app's `client_id` and `client_secret` — would be sent to that attacker-controlled host, exfiltrating the app's `client_secret`. This matches the High-impact category "SSRF with the app's credentials, ... or credential leakage into logs or error output."

### Likelihood Explanation
The likelihood is bounded by the HMAC check: as long as `Context.api_secret_key` remains secret, an external attacker cannot independently forge a `shop`/`hmac` pair. The real risk is defense-in-depth: this method is the only OAuth exchange path in the codebase that omits the `ShopValidator.sanitize!` step that its sibling flows (`client_credentials`, `token_exchange.migrate_to_expiring_token`) apply, meaning any bypass of `ShopValidator`'s domain logic (that class exists precisely to reject look-alike/attacker domains) would not be caught a second time in `validate_auth_callback`, unlike in the other flows. This is a real gap in the binding enforced by the gem itself, independent of host-application behavior, but its practical exploitability without a validator bypass or a leaked secret is not established.

### Recommendation
Sanitize `auth_query.shop` through `Utils::ShopValidator.sanitize!` before constructing `null_session` in `Auth::Oauth.validate_auth_callback`, mirroring `Auth::ClientCredentials.client_credentials` and `Auth::TokenExchange.migrate_to_expiring_token`, so that the host receiving `client_id`/`client_secret` is always constrained to `ShopValidator::TRUSTED_SHOPIFY_DOMAINS` in addition to passing HMAC verification.

### Proof of Concept
Conceptual (cannot be fully demonstrated without an `api_secret_key` bypass, which is out of scope to obtain):
1. Trigger `ShopifyAPI::Auth::Oauth.validate_auth_callback(cookies:, auth_query:)` with an `AuthQuery` whose `shop` is a value not present in `ShopValidator::TRUSTED_SHOPIFY_DOMAINS`.
2. Observe that no `ShopValidator.sanitize!`/`sanitize_shop_domain` call exists anywhere in `lib/shopify_api/auth/oauth.rb` (confirmed via `grep_search` across the repo), unlike `lib/shopify_api/auth/client_credentials.rb:25` and `lib/shopify_api/auth/token_exchange.rb:103`.
3. The resulting `Clients::HttpClient` is initialized with `session.shop` equal to the unsanitized value and issues the token-exchange POST (containing `client_secret`) to `https://#{shop}/admin/oauth/access_token`.

### Citations

**File:** lib/shopify_api/auth/oauth.rb (L70-81)
```ruby
          raise Errors::InvalidOauthError,
            "Invalid state in OAuth callback." unless state == auth_query.state

          null_session = Auth::Session.new(shop: auth_query.shop)
          body = {
            client_id: Context.api_key,
            client_secret: Context.api_secret_key,
            code: auth_query.code,
            expiring: Context.expiring_offline_access_tokens ? 1 : 0, # Only applicable for offline tokens
          }

          client = Clients::HttpClient.new(session: null_session, base_path: "/admin/oauth")
```

**File:** lib/shopify_api/clients/http_client.rb (L12-19)
```ruby
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
