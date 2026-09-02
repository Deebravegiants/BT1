This confirms the vulnerable path: the docs explicitly instruct developers to key their per-shop logic (job enqueueing, tenant identification) off `data.shop`, which is derived from an unauthenticated header, while the HMAC only signs the raw body.

### Title
Webhook `shop` field is not covered by HMAC verification, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` derives the `shop` (and `topic`, `webhook_id`, `api_version`) attributes from HTTP headers, but `to_signable_string` — the value that `Utils::HmacValidator` actually verifies — returns only the raw request body. The `x-shopify-shop-domain` header is never included in the HMAC computation, so a request's declared shop identity is not cryptographically bound to the signature that authenticates the request.

### Finding Description
`ShopifyAPI::Webhooks::Registry.process` authenticates a webhook solely via `Utils::HmacValidator.validate(request)`: [1](#0-0) 

`HmacValidator` computes and compares the signature only over `verifiable_query.to_signable_string`: [2](#0-1) 

For webhook requests, `to_signable_string` is defined to be just the raw HTTP body, while `shop` is read from a separate, unsigned header: [3](#0-2) 

This is the identity-binding gap: the HMAC verifies **bytes of the body**, but the application logic acts on **the shop asserted in a header that is never part of the signed bytes** — `hmac(body) == valid` is treated as proof that `shop` is authentic, when in fact `shop` could be any value in `∀ possible header values`.

Once validation passes, `Registry.process` passes the attacker-controlled `shop` straight into the handler's `WebhookMetadata`, and the gem's own documentation instructs integrators to key tenant-specific work (e.g., enqueuing background jobs `perform_later(topic: data.topic, shop_domain: data.shop, ...)`) off this value: [4](#0-3) [5](#0-4) 

### Impact Explanation
An attacker who is a legitimate (even free-trial) merchant of the app receives real, validly-signed webhooks from Shopify for their own shop (body B, HMAC = HMAC(secret, B)). Because `shop` is not part of the signed content, the attacker can capture one such request and replay it to the same webhook endpoint with the `x-shopify-shop-domain` header rewritten to a victim shop's domain. `HmacValidator.validate` still succeeds (it only checks `B` against the unchanged HMAC), and the handler receives `WebhookMetadata` claiming the data belongs to the victim shop. Any downstream logic that uses `data.shop` to look up per-tenant sessions/records or attribute the payload to a tenant will process attacker-controlled/attacker-owned data under the victim's identity — a cross-tenant data-confusion condition rooted entirely in this gem's request/verification design.

### Likelihood Explanation
Exploitation requires the attacker to have registered as a legitimate app user (to obtain at least one validly-signed webhook body+HMAC pair from Shopify) and to be able to POST to the app's public webhook endpoint with custom headers, which is trivial for any unprivileged internet user once they know or guess the endpoint. No secrets, TLS interception, or privileged access are required — this is a pure header/body binding gap in `Request`/`HmacValidator`.

### Recommendation
Include the shop domain (and topic/webhook id) inside the value used by `to_signable_string`, or otherwise cryptographically bind the header-derived identity fields to the HMAC verification, so that `hmac(body)` alone cannot be replayed with an arbitrary `shop` header. At minimum, document and encourage integrators to independently confirm the shop has an active install/session before trusting `data.shop`, and consider validating that the `shop` header matches an active session/webhook registration prior to invoking the handler.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and triggers a real webhook (e.g., `orders/create`), capturing the raw body `B` and header `x-shopify-hmac-sha256: HMAC(secret, B)` sent by Shopify.
2. Attacker POSTs the identical body `B` and HMAC header to the app's webhook endpoint, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses headers/body; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks `HMAC(secret, B)` against `to_signable_string` (`B`), never inspecting the `shop` header. [6](#0-5) 
4. The handler is invoked with `WebhookMetadata.new(..., shop: "victim-shop.myshopify.com", body: parsed(B), ...)`, and any per-tenant logic keyed off `data.shop` now operates under the victim's identity using attacker-supplied data.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

**File:** lib/shopify_api/webhooks/request.rb (L20-38)
```ruby
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

      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end
```

**File:** docs/usage/webhooks.md (L19-30)
```markdown
```ruby
module WebhookHandler
  extend ShopifyAPI::Webhooks::WebhookHandler

  class << self
    def handle(data:)
      puts "Received webhook! topic: #{data.topic} shop: #{data.shop} body: #{data.body} webhook_id: #{data.webhook_id} api_version: #{data.api_version}"
      perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)
    end
  end
end
```
```
