## Title
Webhook shop-domain and topic headers are not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, while `shop`, `topic`, `webhook_id`, and `api_version` are all read from unauthenticated HTTP headers. `Utils::HmacValidator.validate` verifies the HMAC exclusively over `to_signable_string` (the body), so the header fields that `Registry.process` uses to route the webhook and identify the tenant are never bound to the signature.

### Finding Description
`Request#to_signable_string` is defined as: [1](#0-0) 

only `@raw_body` is signed. The `shop`, `topic`, and `webhook_id` accessors are pulled straight from HTTP headers without any cryptographic binding: [2](#0-1) 

`HmacValidator.validate` / `validate_signature` compute and compare the signature strictly against `verifiable_query.to_signable_string` (the body): [3](#0-2) 

`Registry.process` trusts the unauthenticated `request.topic` and `request.shop` after only validating the body HMAC, then dispatches to the handler with that unauthenticated shop/topic as the tenant identity: [4](#0-3) 

The identity binding that should hold is: `shop_header == shop_that_Shopify_actually_signed_the_payload_for` (and similarly for `topic`). Because the signed bytes are only the body, this equality is never checked — the shop and topic used to dispatch the webhook are decoupled from what was cryptographically attested.

An unprivileged party who legitimately receives real webhook deliveries for their own store (any merchant that installs the app is, from the app's perspective, an untrusted external actor relative to other tenants) can capture a genuine `(raw_body, hmac)` pair from their own shop's webhook, then replay it to the app's webhook endpoint with the `shop-domain` (and/or `topic`) header rewritten to point at a victim shop. `Utils::HmacValidator.validate` still returns `true` because the body and HMAC are unchanged and valid; `Registry.process` then invokes the handler with `WebhookMetadata` claiming the victim shop/topic, feeding attacker-controlled body content into the victim tenant's processing path.

### Impact Explanation
This breaks tenant isolation: a webhook payload provably signed for one merchant can be relayed and accepted by the host application as if it belonged to a different merchant (cross-tenant access), since the gem does not bind `shop`/`topic` to the signature it verifies.

### Likelihood Explanation
Medium: exploitation requires the attacker to control (or capture) at least one legitimately-signed webhook body from any shop that has the app installed — a bar any real merchant/attacker can clear without needing the app's `client_secret` or another tenant's credentials — then replay it with modified headers to the app's webhook endpoint.

### Recommendation
Include `shop`, `topic`, and `webhook_id` in the signable string (or otherwise cryptographically bind them, e.g., derive them only from a per-shop signed context rather than raw headers) so `HmacValidator.validate` fails whenever any of these header-derived fields are altered relative to what was actually signed by Shopify.

### Proof of Concept
1. Merchant M installs the app; Shopify sends a legitimate webhook to the app's endpoint with headers `x-shopify-shop-domain: m.myshopify.com`, `x-shopify-topic: orders/create`, body `B`, and `x-shopify-hmac-sha256: HMAC(secret, B)`.
2. Attacker (merchant M, or anyone who intercepted the request) captures `B` and the valid HMAC.
3. Attacker replays the exact same request to the app's webhook endpoint but sets `x-shopify-shop-domain: victim.myshopify.com`.
4. `Utils::HmacValidator.validate` (lib/shopify_api/utils/hmac_validator.rb:13-21) succeeds because it only checks `HMAC(secret, B)` against the unchanged body `B`.
5. `Registry.process` (lib/shopify_api/webhooks/registry.rb:189-199) dispatches to the handler with `shop: "victim.myshopify.com"`, causing the host app to process attacker-supplied body content under the victim tenant's identity.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-23)
```ruby
      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

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
