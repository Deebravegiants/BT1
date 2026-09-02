Confirmed: `Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , while `shop`, `topic`, `webhook_id`, and `api_version` are all pulled from unauthenticated HTTP headers [2](#0-1) . `Registry.process` verifies only this body-based HMAC before dispatching to the handler with `request.shop` as the tenant identifier [3](#0-2) .

### Title
Webhook tenant identity (`shop-domain` header) is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes/verifies the HMAC over the raw request body only, but the shop domain used by the host application's webhook handler to identify the tenant is taken directly from an attacker-controllable HTTP header that is never included in the signed material.

### Finding Description
`HmacValidator.validate` calls `verifiable_query.to_signable_string`, and for webhook requests that method returns just `@raw_body`: [1](#0-0) 

The `hmac`, `topic`, `shop`, `api_version`, and `webhook_id` accessors all read straight from HTTP headers with no cryptographic binding to that HMAC: [4](#0-3) 

`Registry.process` validates only `Utils::HmacValidator.validate(request)` (i.e., body signature) and then immediately trusts `request.shop`/`request.topic` to build the `WebhookMetadata` passed to the app's registered handler: [3](#0-2) 

Because Shopify's webhook `client_secret` HMAC key is per-app (not per-shop), and the signed bytes are only the JSON body, an unprivileged internet user who legitimately receives webhooks for their own shop (e.g., by installing the app on a shop they control, or by observing any webhook delivery they are entitled to) can replay that exact body/HMAC pair to the app's webhook endpoint while substituting the `x-shopify-shop-domain` (and/or `x-shopify-topic`) header for a victim shop. The HMAC still validates, because the header values were never part of the signed content — breaking the equality that `HMAC-verified bytes == bytes the handler uses for tenant identity`.

### Impact Explanation
This is a cross-tenant identity confusion: the receiving application will process the forged webhook as if it originated from the victim shop, potentially triggering business logic keyed on `shop` (e.g., data deletion for `shop/redact`, order/customer state changes, cache invalidation, entitlement changes) for a shop the caller does not control. Since host apps are expected to trust `WebhookMetadata#shop` as the authenticated tenant (per this gem's documented API), this crosses a tenant boundary using only data verified by a body-only HMAC.

### Likelihood Explanation
Exploitation requires only the ability to send an arbitrary HTTP request with a previously-observed valid `(body, hmac)` pair and an attacker-chosen `shop-domain` header — no access to `api_secret_key`, tokens, or the target shop is needed. Any actor who can capture one legitimate webhook delivery (trivial for their own installed shop) can replay it against arbitrary shop domains.

### Recommendation
Include the shop domain (and ideally topic/webhook id) in the signed material verified by `HmacValidator`, or otherwise cryptographically bind the header-derived identity fields to the HMAC before they are trusted by webhook handlers, rather than relying solely on a body-only signature.

### Proof of Concept
1. Register a webhook handler for topic `orders/create` and note that `Registry.process` trusts `request.shop` from headers [3](#0-2) .
2. Capture a legitimate webhook delivery for attacker's own shop `attacker.myshopify.com`, containing `raw_body` and a valid `x-shopify-hmac-sha256` computed over that body with the app's `client_secret`.
3. Replay the same `raw_body`/`hmac` bytes to the app's webhook endpoint, but set header `x-shopify-shop-domain: victim.myshopify.com`.
4. `HmacValidator.validate` succeeds because it only checks `raw_body` against the HMAC [1](#0-0) ; `Registry.process` then invokes the handler with `shop: "victim.myshopify.com"`, causing the app to act on the victim tenant's behalf.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-33)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end

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
