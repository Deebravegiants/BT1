### Title
Webhook shop/topic identity is not bound to the HMAC-verified body, allowing cross-tenant webhook spoofing via header substitution - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC of the raw request body, then trusts the `shop`, `topic`, `webhook_id`, and `api_version` values taken from HTTP headers that are **not** covered by that HMAC to route and label the payload to a specific tenant.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , and `Utils::HmacValidator.validate_signature` computes/compares the HMAC exclusively over that signable string [2](#0-1) . The `shop`, `topic`, `webhook_id`, and `api_version` accessors are read straight from request headers and are excluded from the signed material entirely [3](#0-2) .

`Registry.process` only checks `Utils::HmacValidator.validate(request)` (i.e., body authenticity) before handing the *header-derived, unauthenticated* `shop`, `topic`, and `webhook_id` straight to the app's handler as `WebhookMetadata`: [4](#0-3) .

This breaks the identity binding `shop_authenticated == shop_used_by_handler`: the HMAC only proves "this exact body byte sequence was produced with the app's secret at some point in time," it proves nothing about which shop, topic, or webhook id the body is *currently* being claimed to belong to. Anyone who can obtain one genuine `(raw_body, hmac)` pair signed by Shopify (trivially done by installing the app on a shop they control and capturing a real webhook delivery) can replay that exact body/hmac to the app's public webhook endpoint while substituting the `X-Shopify-Shop-Domain`, `X-Shopify-Topic`, and `X-Shopify-Webhook-Id` headers to any value they choose. `Utils::HmacValidator.validate` will still pass because it never looks at those headers, and `Registry.process` will invoke the handler as if the (attacker-chosen) shop/topic genuinely originated that payload.

### Impact Explanation
This crosses a tenant boundary: an unprivileged internet user (any merchant/developer who can install the app on a store they control, or who intercepts one legitimate delivery) can make the host application's webhook handler believe an arbitrary shop domain sent an arbitrary (Shopify-signed, but content-fixed) payload/topic combination. Depending on how the host app's `WebhookHandler#handle` uses `data.shop` (e.g., to look up/create/delete per-tenant records, revoke sessions on `app/uninstalled`, or process `customers/redact`/`shop/redact` compliance topics), this enables cross-tenant data corruption, spoofed compliance/uninstall events against a victim tenant, or injection of one tenant's data into another tenant's processing pipeline — all without ever needing the app's `client_secret`, an access token, or any credential belonging to the victim.

### Likelihood Explanation
Obtaining one valid `(raw_body, hmac)` pair requires nothing beyond installing the target app on any store (including a free/dev store) and capturing a webhook delivery on the wire or via any logging/mirroring the attacker controls for their own shop — the attacker never needs the app's secret. Building the forged request (same body/hmac bytes, substituted headers) is a straightforward HTTP replay. The public webhook endpoint is, by design, reachable by anyone (it must accept unauthenticated POSTs from "Shopify"), so there is no additional network-position requirement.

### Recommendation
Bind the routing identity to the authenticated payload instead of trusting headers independently:
- Include `shop`, `topic`, and `webhook_id` (and ideally a timestamp) in the HMAC-signed material, or
- Require the body itself (once parsed) to assert/confirm the shop the webhook concerns, and reject when it disagrees with the header, or
- At minimum, document/enforce that `webhook_id` be treated as an idempotency key tied to `(shop, topic)` pairs recorded from prior deliveries, and reject re-use of a `(raw_body, hmac)` pair under a different `shop`/`topic` header combination.

### Proof of Concept
1. Attacker installs the target Shopify app on `attacker-shop.myshopify.com` and triggers a real webhook (e.g. `orders/create`), capturing the raw POST body and the `X-Shopify-Hmac-Sha256` header Shopify sent — no app secret required.
2. Attacker (or anyone) sends a new POST to the app's public webhook endpoint using the exact same raw body and `X-Shopify-Hmac-Sha256` value, but sets:
   - `X-Shopify-Shop-Domain: victim-shop.myshopify.com`
   - `X-Shopify-Topic:` any registered topic (or leave as-is)
   - `X-Shopify-Webhook-Id:` a fresh UUID
3. `ShopifyAPI::Webhooks::Request.new(raw_body:, headers:)` is constructed; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks `raw_body` against the secret [5](#0-4) .
4. The registered handler is invoked with `WebhookMetadata.new(topic: request.topic, shop: "victim-shop.myshopify.com", body: request.parsed_body, ...)` [6](#0-5) , causing the host application to process attacker-supplied content as if it authentically originated from the victim shop.

### Citations

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
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
