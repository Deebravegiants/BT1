This confirms the finding: the webhook HMAC (`ShopifyAPI::Webhooks::Request#to_signable_string` at `lib/shopify_api/webhooks/request.rb:36-38`) covers only `@raw_body`, while `shop`, `topic`, `webhook_id`, and `api_version` are read straight from unauthenticated HTTP headers (`lib/shopify_api/webhooks/request.rb:15-33`) and then trusted downstream — passed as `shop: request.shop` into `WebhookMetadata` in `Registry.process` (`lib/shopify_api/webhooks/registry.rb:189-199`) and documented as authoritative in `docs/usage/webhooks.md:12-17`, 125. This is exactly the "field acted on but not covered by the HMAC" bug class from the rules.

### Title
Webhook shop-identity headers are not covered by the HMAC, allowing cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable payload from the raw body only. The `shop-domain`, `topic`, `webhook-id`, and `api-version` headers are never included in the signed material, yet `Registry.process` trusts `request.shop` as the tenant identity when dispatching to the host app's handler.

### Finding Description
`Utils::HmacValidator.validate` verifies `verifiable_query.to_signable_string` against the HMAC header [1](#0-0) . For webhooks, `to_signable_string` returns only `@raw_body` [2](#0-1) , while `shop`, `topic`, `webhook_id`, and `api_version` are read verbatim from HTTP headers with no cryptographic binding to the body or to the HMAC [3](#0-2) . `Registry.process` only checks `Utils::HmacValidator.validate(request)` before dispatching, and then builds `WebhookMetadata` directly from the unauthenticated `request.shop`, `request.topic`, etc. [4](#0-3) . The equality the design implicitly assumes is: `shop header == tenant that produced/authorized this signed body`. In reality, the HMAC secret (`api_secret_key`) is shared by the app across all installed shops, not per-tenant, so any shop that installs the app can obtain validly-signed webhook bodies and is free to re-label them as belonging to a different shop, since the header is outside the signed scope. This directly matches the report's "small-position liquidation" bug class analog cited in the rules: an incentive/enforcement gap around a field that participates in a security decision but is excluded from the authenticated hash.

### Impact Explanation
Because `docs/usage/webhooks.md:12-17` and `WebhookMetadata` (`lib/shopify_api/webhooks/webhook_handler.rb:6-12`) explicitly instruct host apps to trust `data.shop` as "The shop domain of the webhook," any host application that uses this field to route data to per-tenant storage, queues, or authorization decisions (the documented and expected usage pattern, e.g. `perform_later(topic: data.topic, shop_domain: data.shop, ...)` in the gem's own docs example) will process attacker-labeled tenant data as if it belonged to the victim shop. This is a cross-tenant identity confusion enabled entirely by this gem's webhook verification API, since the gem asserts "this will verify the request did indeed come from Shopify" (`docs/usage/webhooks.md:125`) but does not verify which shop it came from.

### Likelihood Explanation
Exploitation requires only an ordinary, unprivileged Shopify merchant account: install the target app on an attacker-controlled shop, trigger any subscribed webhook topic (e.g., `orders/create`) to receive a validly HMAC-signed payload, then replay that exact `raw_body` + valid HMAC header to the app's public webhook endpoint while substituting the `X-Shopify-Shop-Domain` header (and optionally `topic`) with the victim's shop domain. No access token, `client_secret`, or elevated privilege is required — only a free developer/test store and knowledge of the target's `.myshopify.com` domain, which is typically discoverable.

### Recommendation
Include `shop`, `topic`, and `webhook_id` in the HMAC-signable string (or otherwise cryptographically bind them, e.g., by having the registry re-verify that the webhook was registered for the claimed shop via a per-shop lookup) so that the identity headers cannot be forged independently of the signed body. At minimum, document prominently that `data.shop`/`data.topic` are NOT integrity-protected by `HmacValidator` and must not be trusted for tenant routing without additional verification.

### Proof of Concept
1. Install the target app on attacker's own store `attacker.myshopify.com` and register an HTTP webhook (e.g., `orders/create`).
2. Trigger the topic (e.g., create an order in the attacker's store) to receive a real Shopify webhook POST with a valid `X-Shopify-Hmac-Sha256` header computed over the JSON body, per `lib/shopify_api/webhooks/request.rb:12`.
3. Capture the raw body and HMAC header exactly.
4. Replay the request to the app's webhook endpoint, keeping body and HMAC identical but changing `X-Shopify-Shop-Domain: attacker.myshopify.com` to `X-Shopify-Shop-Domain: victim.myshopify.com`.
5. `Utils::HmacValidator.validate` still returns `true` (it only hashes `@raw_body`), so `Registry.process` calls the app's handler with `WebhookMetadata(shop: "victim.myshopify.com", body: <attacker's order data>, ...)`, causing the host app to associate attacker-controlled data with the victim tenant.

### Citations

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

**File:** lib/shopify_api/webhooks/request.rb (L15-33)
```ruby
      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
      end

      sig { returns(String) }
      def api_version
        T.cast(shopify_header("api-version"), String)
      end

      sig { returns(String) }
      def webhook_id
        T.cast(shopify_header("webhook-id"), String)
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L35-38)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end
```

**File:** lib/shopify_api/webhooks/registry.rb (L188-199)
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
```
