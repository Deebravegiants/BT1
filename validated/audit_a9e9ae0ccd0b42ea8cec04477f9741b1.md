## Analysis

The reachable analog here is Shopify webhook processing. The HMAC signature Shopify sends only covers the raw request body, while the `shop`, `topic`, `webhook_id`, and `api_version` values are taken directly from unauthenticated HTTP headers and are never part of what gets HMAC-verified. [1](#0-0) [2](#0-1) [3](#0-2) 

### Title
Webhook `shop-domain` header is trusted without being bound by the HMAC signature - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, so `Utils::HmacValidator.validate` authenticates the body bytes only. `Request#shop`, `#topic`, `#webhook_id`, and `#api_version` are read straight from HTTP headers with no cryptographic binding to that signature. `Registry.process` accepts the HMAC as proof of authenticity for the whole request and then forwards `request.shop` (an unauthenticated header value) directly into `WebhookMetadata`, which application code uses to attribute the payload to a tenant.

### Finding Description
`HmacValidator.validate_signature` computes `compute_signature(verifiable_query.to_signable_string, secret)` and compares it to the `hmac-sha256` header via `OpenSSL.secure_compare`. For `Webhooks::Request`, `to_signable_string` is defined as `@raw_body` only:

```ruby
sig { override.returns(String) }
def to_signable_string
  @raw_body
end
```

The identity binding that should hold is:
`shop attributed by the handler == shop that actually produced/authorized the signed body`

But the `shop` value consumed by `Registry.process` is taken from a header that is completely outside the signed material:

```ruby
def shop
  T.cast(shopify_header("shop-domain"), String)
end
```

```ruby
def process(request)
  raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)
  ...
  handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop, ...))
end
```

Before the request: body `B` was signed by Shopify producing `HMAC(secret, B)` for shop `S1`.
After an attacker's crafted request: the same `(B, HMAC(secret,B))` pair is replayed with `x-shopify-shop-domain` (and/or `x-shopify-topic`, `x-shopify-webhook-id`) swapped to `S2`. `HmacValidator.validate` still returns `true` because it only checks `B` against the signature — it never inspects `shop`, `topic`, or `webhook_id`. The handler then executes `WebhookMetadata` attributed to `S2` while it actually authenticates only that `B` was signed for *some* shop, not for `S2` specifically.

### Impact Explanation
This breaks the tenant-identity binding between the cryptographically verified payload and the shop the application logic will act on. Any host application that uses `WebhookMetadata#shop` to route the payload to the record/tenant it stores locally (which is the documented usage pattern for this field, per the webhook handler API) can be made to process one shop's data under another shop's identity — a cross-tenant condition. Depending on the handler, this can lead to data being written into, or state changed for, the wrong merchant's tenant using a payload the attacker did not need the ability to forge (only to capture/replay), since the header fields riding along with a legitimately-signed body are never checked.

### Likelihood Explanation
Exploitation requires the attacker to possess one valid `(raw_body, hmac)` pair — obtainable by observing/logging any real webhook delivery (webhook bodies are not secrets and commonly appear in logs, error trackers, or are visible to anyone who can observe a delivery, e.g., a compromised or curious third-party integration, proxy, or log aggregator) — and then POST it to the app's webhook endpoint with a modified `shop-domain`/`topic`/`webhook-id` header. No `api_secret_key`, access token, or privileged account is required; the HMAC check will still pass because the signature never covered those header fields.

### Recommendation
Bind the shop (and topic/webhook_id) into the material that is HMAC-verified, or otherwise cryptographically tie them to the verified body — e.g., include them in `to_signable_string`, or independently confirm the `shop` value against the shop that owns the currently active session/registration before invoking the handler, rejecting the request if there is a mismatch.

### Proof of Concept
1. Capture a legitimate webhook delivery for `shop-a.myshopify.com`: raw body `B` and header `x-shopify-hmac-sha256: H` where `H = Base64(HMAC-SHA256(secret, B))`.
2. Replay the same body `B` and header `H` to the app's webhook endpoint, but set `x-shopify-shop-domain: shop-b.myshopify.com` (and optionally change `x-shopify-topic`/`x-shopify-webhook-id`).
3. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: {...})` is constructed; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because `to_signable_string` only returns `B`, unchanged.
4. `handler.handle(data: WebhookMetadata.new(topic: ..., shop: "shop-b.myshopify.com", body: JSON.parse(B), ...))` executes with the forged shop, even though the signature never certified that `B` belongs to `shop-b.myshopify.com`.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L11-38)
```ruby
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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
