### Title
Webhook `shop-domain` header is trusted for tenant identity without being covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`Registry.process` validates a webhook by HMAC-verifying only the raw request body, then separately reads the tenant identity (`shop`) from an HTTP header that is not part of the signed payload. This is the same class of bug as the Solidity `Queue.remove` finding: an item/field that should be atomically bound to a validated state (queue membership / cryptographic authenticity) is instead only partially checked, leaving a piece of untrusted data (`baseQueue.queue[addrToRemove]` / the `shop-domain` header) that downstream logic (`contains` / webhook handlers) treats as trustworthy when it is not.

### Finding Description
`Webhooks::Registry.process` does:
```ruby
raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)
...
handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop, ...))
``` [1](#0-0) 

`Utils::HmacValidator.validate` computes the signature over `request.to_signable_string`, which for `Webhooks::Request` is only the raw HTTP body (`@raw_body`): [2](#0-1) 

However `request.shop` (the tenant identity ultimately passed to the app's webhook handler) is read from the `X-Shopify-Shop-Domain` HTTP header, which is never part of the HMAC-signed material: [3](#0-2) 

The equality that is supposed to hold is: `shop bound by HMAC == shop used to identify the tenant in handler.handle`. In reality, only the raw body is authenticated; the `shop` value used for tenant attribution is taken from an unauthenticated header, exactly as in the reported Solidity bug where `queue[addrToRemove]` is removed from the linked-list pointers but the underlying storage entry — the thing `contains` checks — is never actually cleared/bound to the new state.

### Impact Explanation
If a webhook body does not itself embed the shop domain (many topics' JSON payloads do not include the initiating shop), an app relying on this gem's `WebhookMetadata#shop` to route/attribute data to a merchant/tenant can be made to process a legitimately-signed webhook (signed with the app's own secret over the body) under an attacker-chosen `shop` value, since the header is fully attacker-controllable if the HTTP layer in front of the gem does not independently pin it. This breaks the tenant/shop identity binding and can lead to cross-tenant data association (e.g., writing webhook data against the wrong shop's record) — a High/Critical-adjacent cross-tenant issue depending on how the host app is wired.

### Likelihood Explanation
Exploitability depends on whether the host application passes through raw, attacker-influenced headers to `Webhooks::Request.new(headers: ...)` without independently validating that `shop-domain` matches an expected/allowed tenant, and whether the specific webhook topic's HMAC (computed only over the body) can be replayed or observed with a different `shop-domain` header value by an entity that can trigger or intercept legitimate webhook deliveries (e.g., a merchant re-sending their own webhook payload with a substituted domain, or infrastructure that reflects attacker-supplied headers). This is more of a design gap in the gem (the value used for tenant identity is never part of the authenticated payload) than a directly attacker-forgeable HMAC break, so likelihood is moderate and highly dependent on host integration — but it is a genuine identity-binding defect in this gem's own webhook verification API, not merely a documentation issue.

### Recommendation
Include the shop domain (and ideally the topic) inside the HMAC-signed material, or otherwise cryptographically bind `request.shop` to the verified payload before exposing it via `WebhookMetadata`, so that `Utils::HmacValidator.validate(request)` cannot pass while `request.shop` is an unauthenticated value. At minimum, document and enforce that host applications must independently confirm `request.shop` against an already-authenticated session/shop record before trusting it, mirroring how `Queue.remove` should fully clear the removed entry so `contains` cannot report a stale, incorrect state.

### Proof of Concept
1. Construct a valid webhook POST body for a topic whose signature is computed only over the body (per `Webhooks::Request#to_signable_string`).
2. Compute a valid `X-Shopify-Hmac-Sha256` value for that body using the app's secret (available to anyone who can capture/replay a legitimate webhook, e.g. via a proxy the host operates, or via any endpoint that reflects attacker-supplied headers into the gem's request object).
3. Set `X-Shopify-Shop-Domain` to a different shop domain than the one that actually triggered the webhook.
4. Call `ShopifyAPI::Webhooks::Registry.process(request)`; `Utils::HmacValidator.validate(request)` returns `true` because it only checks the raw body, and `handler.handle` receives `WebhookMetadata` with the attacker-chosen `shop`, as shown at [1](#0-0) 
demonstrating that the shop attribution is not actually bound to the cryptographically verified content.

### Citations

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
