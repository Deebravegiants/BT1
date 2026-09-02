## Title
Webhook HMAC does not bind the `shop-domain` header, enabling cross‑tenant webhook forgery - (`lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw HTTP body, while `shop`, `topic`, `webhook_id`, and `api_version` are all read straight from unauthenticated HTTP headers. Because the app's HMAC secret (`client_secret`) is shared across every shop that installs the app, any unprivileged user who can trigger a webhook delivery to their own installation can capture a valid `(raw_body, hmac)` pair and replay it against the same endpoint with the `X-Shopify-Shop-Domain` header changed to a victim shop. `HmacValidator.validate` will still pass because it never checks the header, so `Registry.process` will hand the forged shop identity to the app's webhook handler.

### Finding Description
`Registry.process` authenticates a webhook solely via `Utils::HmacValidator.validate(request)`: [1](#0-0) 

`HmacValidator.validate_signature` computes the signature over `verifiable_query.to_signable_string`: [2](#0-1) 

But `Request#to_signable_string` is defined to be just the raw body — it does not include `shop`, `topic`, or `webhook_id`, all of which are read directly and only from request headers: [3](#0-2) 

This breaks the intended identity binding: `hmac verified over body` ≠ `shop asserted by the (unauthenticated) shop-domain header that is subsequently trusted as the webhook's tenant identity`. Since a single app's `client_secret` is shared by every merchant who installs that app, any merchant (an unprivileged internet user with respect to other tenants of the same app) can:
1. Install/use the app on their own store and receive a genuine webhook delivery, giving them a valid `(raw_body, hmac)` pair signed with the app's shared secret.
2. Replay that exact body+hmac to the app's webhook endpoint, but swap the `X-Shopify-Shop-Domain` (or `Shopify-Shop-Domain`) header to a victim shop's domain.
3. `HmacValidator.validate` passes (it only checks the body), and `Registry.process` calls the registered handler with `WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)` where `request.shop` is the forged, attacker-controlled header value: [4](#0-3) 

### Impact Explanation
This is a cross-tenant integrity break: the app's webhook handler will process attacker-influenced data (the body content, which the attacker controls to whatever degree their own store's webhook triggers allow) while believing it originates from a different, victim merchant. Any app logic that trusts `WebhookMetadata#shop` to scope data writes, cache invalidation, redaction (e.g., `customers/redact`, `shop/redact`), or state transitions can be corrupted or triggered against a tenant the attacker doesn't control — a cross-tenant access/data-integrity violation attributable entirely to this gem's failure to bind the shop identity into the HMAC-verified bytes.

### Likelihood Explanation
Any user who can install the app on a store they control (common for public apps) can legitimately receive one authentic webhook and its HMAC, then replay it with a modified header value. No access to `client_secret`, tokens, or privileged infrastructure is required — only observation of one genuine webhook delivery to the attacker's own endpoint.

### Recommendation
Bind the tenant-identifying fields into the value that is HMAC-verified, or otherwise independently authenticate the `shop-domain` header against the session/shop the webhook was registered for. At minimum, `to_signable_string` should not be the sole authentication anchor for `shop`; the shop should be cross-checked against a known/registered value (e.g., validate that `request.shop` matches the shop associated with the webhook subscription, or include the header set in the signed payload construction consistent with how Shopify's App Bridge / other SDKs pin the domain).

### Proof of Concept
1. Install the target app on attacker-owned shop `attacker.myshopify.com`; trigger a webhook (e.g. `customers/data_request`) with a body the attacker controls/observes.
2. Capture the raw POST body and the `X-Shopify-Hmac-Sha256` header value delivered by Shopify to the app's webhook endpoint.
3. Resend the identical body and HMAC header to the same endpoint, but set `X-Shopify-Shop-Domain: victim.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `HmacValidator.validate`, which succeeds because it only checks `raw_body` against the HMAC — it never inspects the shop header: [5](#0-4) 
5. The handler executes with `shop: "victim.myshopify.com"`, even though the payload originated from the attacker's own store.

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

**File:** lib/shopify_api/webhooks/request.rb (L10-38)
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

      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end
```
