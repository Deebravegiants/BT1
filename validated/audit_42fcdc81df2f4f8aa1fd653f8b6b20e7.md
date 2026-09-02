## Analysis

The reported bug class ("a field acted on but not covered by the HMAC") maps directly onto this gem's webhook-processing code. I first ruled out the OAuth callback (`ShopifyAPI::Auth::Oauth.validate_auth_callback`) and the token/refresh flows because there `shop` is always covered by the HMAC signature [1](#0-0)  or explicitly passed through `Utils::ShopValidator.sanitize!` before being trusted with `client_secret` [2](#0-1) [3](#0-2) , so an unprivileged attacker cannot forge those signatures without the app secret.

The webhook path is different: the HMAC only signs the raw body, while the shop identity is taken from a separate, unauthenticated header.

### Title
Webhook shop-tenant identity is not bound by the HMAC signature, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` verifies a webhook's HMAC using `Utils::HmacValidator.validate(request)` [4](#0-3) . That validation is computed only over `to_signable_string`, which returns the raw request body [5](#0-4) . The `shop` value used to attribute the event to a tenant is read from a completely separate, unauthenticated header (`x-shopify-shop-domain`) [6](#0-5) , and is forwarded straight into `WebhookMetadata` without any cross-check against the signed bytes [4](#0-3) .

### Finding Description
The identity binding that should hold is: `shop_domain_the_HMAC_authenticates == shop_domain_the_handler_acts_on`. In this gem:
- `HmacValidator.validate` recomputes `HMAC-SHA256(secret, verifiable_query.to_signable_string)` and compares to the `hmac` field [7](#0-6) .
- For `Webhooks::Request`, `to_signable_string` is just `@raw_body` — it never includes the shop domain, topic, or api-version headers [5](#0-4) .
- `shop` is read from the `shopify-shop-domain`/`x-shopify-shop-domain` HTTP header, which any caller can set arbitrarily [6](#0-5) .
- `Registry.process` verifies only the body/HMAC pair and then hands `request.shop` (the unauthenticated header) directly to the handler as the tenant identifier [4](#0-3) .

Because a `(raw_body, hmac)` pair is valid for *any* shop that uses the same app (the HMAC only depends on the app's shared `api_secret_key`, not on which shop produced the body), an attacker who legitimately installs the app on their own shop can capture one of their own valid webhook deliveries and replay the identical body/HMAC pair while substituting the `shop-domain` header for a victim shop. The signature still validates, since it never covered the shop claim in the first place, but the host application (using this gem exactly as documented) will process the event believing it originated from the victim's store.

### Impact Explanation
This is a cross-tenant identity-binding break at the exact layer this gem is responsible for (verifying that inbound Shopify traffic really belongs to the tenant it claims). Any consumer of `ShopifyAPI::Webhooks::Registry.process` inherits this gap: an attacker-controlled shop can inject data, trigger business logic, or pollute state attributed to an arbitrary victim shop (e.g. fake `orders/create`, `app/uninstalled`, GDPR webhooks, etc.), which is a cross-tenant access issue.

### Likelihood Explanation
Medium-High. Exploitation requires only: (1) the attacker's own legitimate app installation (any developer/free Shopify store), (2) one previously observed valid webhook delivery from their own store, and (3) network access to the app's public webhook endpoint. No knowledge of `api_secret_key` or any victim credentials is needed, and the webhook endpoint is intentionally public by design.

### Recommendation
Bind the shop identity cryptographically to the signed payload before trusting it:
- Include the `shop`, `topic`, and `api-version` values in the HMAC-signed material (or otherwise verify them against a value the app already trusts, e.g. by looking up the webhook by `webhook_id`/subscription rather than trusting the header).
- At minimum, document clearly that `WebhookMetadata#shop` is not authenticated by the HMAC and that consuming applications must independently verify shop identity (e.g., against an existing installed-shop registry) before acting on webhook data.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com` and subscribes to a webhook topic (e.g. `orders/create`).
2. Attacker triggers the event on their own store. Shopify POSTs to the app's webhook endpoint with headers `x-shopify-shop-domain: attacker.myshopify.com`, `x-shopify-hmac-sha256: <valid HMAC of raw body>`, and the raw JSON body.
3. Attacker captures `raw_body` and the `hmac-sha256` value from this legitimate delivery.
4. Attacker sends a new POST to the same public webhook endpoint with the identical `raw_body` and identical `x-shopify-hmac-sha256`, but changes `x-shopify-shop-domain` to `victim.myshopify.com`.
5. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC only over `raw_body` — it matches, so validation passes [8](#0-7) .
6. The registered handler is invoked with `WebhookMetadata.new(topic:, shop: "victim.myshopify.com", body: ..., ...)` [9](#0-8) , causing the host application to process/store data as if it came from the victim shop, even though it originated entirely from the attacker's own store.

### Citations

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

**File:** lib/shopify_api/webhooks/registry.rb (L188-200)
```ruby
        sig { params(request: Request).void }
        def process(request)
          raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)

          handler = @registry[request.topic]&.handler

          unless handler
            raise Errors::NoWebhookHandler, "No webhook handler found for topic: #{request.topic}."
          end

          handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop,
            body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))
        end
```

**File:** lib/shopify_api/webhooks/request.rb (L20-23)
```ruby
      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L35-38)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end
```

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
