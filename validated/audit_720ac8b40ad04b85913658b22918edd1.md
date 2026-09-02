### Title
Webhook `shop-domain` header is not covered by the HMAC signature, enabling cross-tenant webhook replay/spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates a webhook by validating an HMAC computed over the raw request body only. The `shop` identity that is handed to the app's `WebhookHandler` is read from the unauthenticated `X-Shopify-Shop-Domain` header, which is never included in the signed material. This breaks the equality that should hold: `shop bound by HMAC == shop delivered to handler`.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop` is derived straight from the `shopify-shop-domain`/`x-shopify-shop-domain` header, with no cryptographic binding to the body or the HMAC: [2](#0-1) 

`Registry.process` validates the HMAC against the body via `Utils::HmacValidator.validate`, then immediately forwards `request.shop` (and other unauthenticated headers) into `WebhookMetadata`, which is delivered to the app's handler as the trusted tenant identifier: [3](#0-2) 

`WebhookMetadata` stores `shop` as a plain `String` field with no verification step: [4](#0-3) 

The HMAC secret (`Context.api_secret_key`) is the app's single client secret — identical for every shop that has installed the app. It is not shop-specific. Because the HMAC is computed only over the body, a request with a given `(raw_body, hmac)` pair remains valid for *any* `shop-domain` header value the request author chooses to send, since that header plays no role in `to_signable_string`.

### Impact Explanation
An unprivileged attacker who legitimately installs the app on their own shop (or otherwise obtains one valid `(raw_body, hmac)` pair, e.g. by triggering/capturing a webhook delivery from their own tenant) can replay that exact body+HMAC pair to the app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` header with a victim shop's domain. `HmacValidator.validate` will pass (it never looks at the shop header), and the host application's `WebhookHandler#handle` will receive `WebhookMetadata` claiming the event belongs to the victim shop. If the host app uses this `shop` value to look up per-tenant state, update records, or drive authorization decisions (the documented and expected usage pattern for `Registry.process`/`WebhookHandler`), this results in cross-tenant data corruption or disclosure — i.e., the attacker can inject events attributed to a shop they do not control, using only their own legitimately obtained credential material and no privileged access, breaking the tenant isolation boundary. This matches the Critical "cross-tenant access" impact class.

### Likelihood Explanation
Likelihood is realistic but requires attacker effort: the attacker must be a real (even trial) merchant/installer of the target app, capture one legitimate webhook body+HMAC pair from their own store, and then replay it against the app's public webhook endpoint with a forged `shop-domain` header (webhook endpoints are typically public HTTP endpoints reachable by anyone, as shown in the documented Rails example). No secret material, TLS interception, or privileged account access is required — this exactly matches the "field acted on but not covered by the HMAC" bug class called out in the rules. The severity of impact depends on what the host app does with `data.shop`, which is outside this gem, but the gem's contract explicitly hands this unauthenticated value to the handler as trusted tenant metadata.

### Recommendation
Include the shop domain (and ideally topic/webhook-id) in the HMAC-signed material, or otherwise cryptographically bind the `shop-domain` header to the signature before constructing `WebhookMetadata`. At minimum, document prominently that `WebhookMetadata#shop` is *not* authenticated by the HMAC and must not be trusted for tenant-scoping decisions without an independent verification step (e.g., cross-checking against a known/authorized shop list or session store).

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and receives a genuine webhook delivery with body `B` and header `X-Shopify-Hmac-Sha256: H` (valid because `H = HMAC-SHA256(api_secret_key, B)`).
2. Attacker POSTs to the app's webhook endpoint:
```
POST /webhooks
X-Shopify-Topic: orders/create
X-Shopify-Hmac-Sha256: H
X-Shopify-Shop-Domain: victim-shop.myshopify.com
Body: B
```
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes HMAC over `B` only and succeeds — it never inspects `X-Shopify-Shop-Domain`: [5](#0-4) 
4. The handler is invoked with `WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: parsed_body, ...)`, causing the host app to process/act on data as if it originated from the victim shop.

### Citations

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

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L6-12)
```ruby
    class WebhookMetadata < T::Struct
      const :topic, String
      const :shop, String
      const :body, T::Hash[String, T.untyped]
      const :api_version, String
      const :webhook_id, String
    end
```
