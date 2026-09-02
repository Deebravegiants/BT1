This confirms the finding. The `Request#to_signable_string` returns only `@raw_body`, and `Request#shop` reads the `shopify-shop-domain` header independently, so the shop attribution is never covered by the HMAC computation.### Title
Webhook `shop` tenant identifier is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable payload from only the raw request body, while the `shop` (tenant) field used by the host application to route/authorize webhook data is read from an independent, unsigned HTTP header. `Registry.process` validates the HMAC and then unconditionally trusts `request.shop` as the tenant identity when invoking the app's handler.

### Finding Description
`Request#to_signable_string` returns `@raw_body` only: [1](#0-0) 

`Request#shop` is derived purely from the `shopify-shop-domain` / `x-shopify-shop-domain` header, which is never included in the signable string: [2](#0-1) 

`Registry.process` validates the HMAC over the body via `Utils::HmacValidator.validate(request)`, and — once that check passes — builds `WebhookMetadata` directly from `request.shop`, handing it to the app-defined handler as the authoritative tenant identifier: [3](#0-2) 

`WebhookMetadata#shop` is a plain `String` field with no further verification, and the documented handler pattern uses it directly to scope work to a shop (e.g., enqueueing a job keyed by `shop_domain: data.shop`): [4](#0-3) 

The identity binding that should hold is: `hmac_signed_bytes == bytes_that_determine_the_tenant`. Here, `hmac_signed_bytes = raw_body` but `tenant_bytes = shop-domain header`, so the two are disjoint. Any request whose body byte-for-byte matches a body the attacker has previously received a valid signature for (i.e., a webhook legitimately delivered to the attacker's own shop) can be replayed with the `shop-domain` header rewritten to any other shop domain, and `HmacValidator.validate` will still return `true`, because the header is outside the signed material. `Registry.process` will then invoke the app's handler with `data.shop` set to the victim shop while `data.body` still originates from the attacker's own legitimately-signed webhook.

### Impact Explanation
This breaks the tenant boundary the host app relies on: an unprivileged internet user who legitimately operates one Shopify shop (and therefore legitimately receives real, validly-HMAC-signed webhooks for their own shop) can forge webhook deliveries attributed to a different, victim shop simply by replaying their own signed body with a modified `shop-domain` header. Any host application logic that uses `data.shop` to select a tenant record, credentials, or database scope (which is exactly the pattern this gem's own documentation recommends) can be tricked into writing, deleting, or acting on data for a shop the attacker does not control — a cross-tenant access primitive achieved without possessing the app's `client_secret`, an access token, or the victim's credentials.

### Likelihood Explanation
Exploitability requires only that the attacker control a shop that is a legitimate installer of the target app (any developer/merchant with a free dev store), collect one legitimately-signed webhook of a topic/body shape they want to spoof, and replay it to the app's webhook endpoint with the `shop-domain` header altered. No secret material or privileged access is needed beyond running the app on the attacker's own store, which is the normal, expected way apps are installed and tested. This is a low-effort, reliably reproducible attack path through the gem's own webhook verification API.

### Recommendation
Include the tenant-identifying header(s) (`shop-domain` and, ideally, `topic`) inside the HMAC-signed material, or otherwise cryptographically bind them to the body (e.g., compute the HMAC over a canonical string containing body + shop + topic instead of the raw body alone). At minimum, document prominently that `data.shop` in `WebhookMetadata` is unauthenticated and must not be trusted as a tenant boundary without additional verification (such as cross-checking against the shop associated with an active, previously-established session/webhook registration for that topic).

### Proof of Concept
1. Attacker installs the target Shopify app on their own shop `attacker.myshopify.com` and triggers a webhook (e.g., `orders/create`) they control the body content of.
2. Shopify delivers the webhook with a valid `x-shopify-hmac-sha256` computed over the raw body using the app's `client_secret`, and `x-shopify-shop-domain: attacker.myshopify.com`.
3. Attacker captures the raw request (body + headers) and resends it to the app's webhook endpoint, only changing `x-shopify-shop-domain` to `victim.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `to_signable_string` (i.e., the unchanged raw body) — validation succeeds because the shop header was never part of the signed bytes: [5](#0-4) 
5. The handler is invoked with `WebhookMetadata.new(..., shop: "victim.myshopify.com", body: <attacker's body>)`, causing the host app to process attacker-controlled data as if it originated from the victim shop.

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
