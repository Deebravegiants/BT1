### Title
Webhook `shop`, `topic`, and `webhook_id` identity fields are not covered by the HMAC signature, enabling cross-tenant webhook header spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature over the raw request body only, while the `shop`, `topic`, and `webhook_id` values that the host application uses for tenant/event identification are read from unauthenticated HTTP headers. `Utils::HmacValidator.validate` only proves the body bytes are authentic, not that the accompanying header metadata belongs to that body.

### Finding Description
`Request#to_signable_string` returns solely `@raw_body`: [1](#0-0) 

But `shop`, `topic`, and `webhook_id` — the fields the host app uses to decide *which tenant/record* the webhook applies to — are pulled straight from HTTP headers with no cryptographic binding to the body or to each other: [2](#0-1) 

`Registry.process` validates only the HMAC of the body, then immediately trusts `request.shop` and `request.topic` (taken from headers) to dispatch to the handler: [3](#0-2) 

The identity binding the code implicitly assumes is:
`HMAC_valid(raw_body) == HMAC_valid(raw_body, shop, topic, webhook_id)`

That equality is false. The HMAC only authenticates the byte string of the body; it says nothing about the `shopify-shop-domain`, `shopify-topic`, or `shopify-webhook-id` headers delivered alongside it. Any two webhook deliveries with byte-identical bodies (e.g., two different `orders/create` events that happen to produce identical JSON, or any topic whose payload the attacker can also legitimately receive from their own dev/test store) yield HMAC values that remain valid no matter which `shop-domain`/`topic`/`webhook-id` headers are attached, because those headers were never part of the signed content.

### Impact Explanation
An unprivileged internet user who possesses a genuine `(raw_body, valid HMAC)` pair — trivially obtainable by owning any Shopify development store and registering the same webhook topic against it — can replay that exact body+HMAC pair to a victim host application's webhook endpoint while substituting the `shopify-shop-domain` header for a target merchant's shop domain (and/or a different `webhook-id`/`topic` header, as long as the topic mapped by `Registry.process` still resolves to a registered handler). `Utils::HmacValidator.validate(request)` will still return `true` because it only checks `@raw_body` against the HMAC, and `WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)` will hand the host application a `shop` value that was never actually verified. Any host app that trusts `request.shop`/`WebhookMetadata#shop` post-validation as proof the event genuinely originated for that tenant (a very common assumption, since the API's contract is "HMAC validated ⇒ trustworthy Shopify webhook") can be made to process cross-tenant data under a forged shop identity — this is the cross-tenant access class explicitly in scope.

### Likelihood Explanation
Medium-High. No `api_secret_key`, access token, or privileged account is required — only a valid `(body, hmac)` pair, which any developer can generate for themselves by registering a webhook on their own store and capturing the delivery, or by using any publicly documented/sample webhook payload whose HMAC can be produced once with any secret the attacker legitimately controls (their own app+store pairing) and whose body happens to match a payload structure the target expects. The header spoofing itself requires nothing more than crafting an arbitrary HTTP POST to the target's public webhook endpoint — a capability available to any unprivileged internet user, since Shopify webhook endpoints are, by design, publicly reachable HTTP(S) endpoints.

### Recommendation
Include the identity-critical headers (`shop-domain`, `topic`, `webhook-id`, `api-version`) in the signed/verified material, or independently verify them against the HMAC-protected body content before trusting them. At minimum, `to_signable_string` should incorporate `shop`, `topic`, and `webhook_id` (e.g., as a canonicalized prefix/suffix to the raw body) so that a mismatch between the headers and the signed value is rejected by `HmacValidator.validate`, and `Registry.process` should not treat `request.shop`/`request.topic` as authenticated unless they have been included in what the HMAC actually covers.

### Proof of Concept
1. Attacker creates or has access to any Shopify store/app pairing (their own dev shop) and registers a webhook for topic `orders/create`. Shopify signs the delivery with `HMAC-SHA256(raw_body, api_secret_key)` and sends headers `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`, `X-Shopify-Topic: orders/create`, `X-Shopify-Webhook-Id: <id>`.
2. Attacker captures the exact `raw_body` bytes and the corresponding `X-Shopify-Hmac-Sha256` value from that legitimate delivery (this pair is valid against the target app too, since both apps/webhooks share the *same* target application's `api_secret_key` context if attacker is a legitimate installed merchant of the same app — which is the typical multi-tenant SaaS case for Shopify apps).
3. Attacker sends a forged POST to the victim host application's webhook endpoint using the *same* `raw_body` and `X-Shopify-Hmac-Sha256`, but with headers rewritten:
   ```
   X-Shopify-Topic: orders/create
   X-Shopify-Hmac-Sha256: <captured value>
   X-Shopify-Shop-Domain: victim-shop.myshopify.com
   X-Shopify-Webhook-Id: <arbitrary>
   ```
4. `ShopifyAPI::Webhooks::Request.new(raw_body:, headers:)` accepts the request (required headers present), and `Utils::HmacValidator.validate(request)` returns `true` because it only checks `raw_body` against the HMAC: [4](#0-3) 
5. `Registry.process` invokes the registered handler with `WebhookMetadata.new(topic: "orders/create", shop: "victim-shop.myshopify.com", ...)` — a shop identity that was never actually cryptographically proven, having been supplied purely via an unauthenticated header, letting the attacker's own (legitimately signed) payload be processed under the victim's tenant identity.

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
