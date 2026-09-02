## Analysis Result

### Title
Webhook HMAC Signature Does Not Bind the Shop Domain, Topic, or Webhook ID - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
The gem's webhook verification only computes/validates an HMAC over the raw request body. The `shop`, `topic`, `webhook_id`, and `api_version` values — all of which are read from HTTP headers and handed to the host application's handler as trusted, tenant-identifying metadata — are never included in the signed content. This mirrors the report's bug class: a field that is *acted on* (used to attribute the event to a specific merchant/tenant) is not *covered* by the authenticity check (HMAC), breaking the identity binding `verified_bytes == acted_upon_bytes`.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

Meanwhile `shop`, `topic`, `webhook_id`, and `api_version` are all parsed straight from HTTP headers with no cryptographic protection: [2](#0-1) 

`Registry.process` validates the HMAC against `to_signable_string` (i.e., body only), and then forwards the *unauthenticated* `shop`, `topic`, and `webhook_id` header values straight into `WebhookMetadata` passed to the app's handler: [3](#0-2) 

So the equality that should hold — *the shop/topic/webhook_id that the HMAC authenticates* == *the shop/topic/webhook_id the handler acts on* — does not hold. The HMAC only authenticates the byte string of the body; the tenant-identifying headers are trusted implicitly.

### Impact Explanation
Because the app's `client_secret`/`api_secret_key` is shared across all merchants using the app (single-tenant secret, multi-tenant usage), any body+HMAC pair that is valid for one shop is *also valid* for a request claiming to be from a different shop, since `shop` is not part of the signed content. If the host application uses `WebhookMetadata#shop` (as is the documented/expected usage) to select which tenant's data or session to update — the classic and only intended purpose of this field in the wiki-documented handler flow — an attacker who can obtain a validly-signed (body, hmac) pair for a webhook delivered to their own installation can replay it against the app's public webhook endpoint while spoofing the `X-Shopify-Shop-Domain` header to point at a victim shop, causing cross-tenant data confusion/writes attributed to the wrong merchant.

### Likelihood Explanation
The webhook endpoint is, by design, a public unauthenticated HTTP endpoint (the HMAC is the *only* authentication mechanism), so it is directly reachable by any unprivileged internet user. The blocking factor is obtaining one valid (body, HMAC) pair, which requires either installing the app on an attacker-controlled store and observing a delivery (e.g., via Shopify's own webhook delivery/log inspection tooling in the Partner dashboard, which surfaces the delivered payload and headers) or otherwise capturing one legitimate delivery. Given that installing the app on one's own store is an unprivileged action, this is a realistic path once *any* such capture is possible, but it does depend on the attacker being able to view a delivered payload+HMAC — this is not as trivially "zero-privilege, zero-setup" as pure HMAC bypass would be.

### Recommendation
Include the tenant-identifying headers (`shop`, `topic`, `webhook_id`, `api_version`) in the signable string used for HMAC verification, or otherwise cryptographically bind them (e.g., require the caller to additionally verify `shop` against the session/store the app expects for the given webhook subscription) before trusting `WebhookMetadata#shop` for any tenant-scoped action.

### Proof of Concept
1. Install the target app on an attacker-owned/controlled test shop `attacker.myshopify.com`.
2. Trigger any subscribed webhook event; capture the delivered raw body `B` and the `X-Shopify-Hmac-Sha256` header value `H` (valid for `B` against the app's shared secret) via Shopify's webhook delivery logs/inspection tooling.
3. Send a POST directly to the app's public webhook endpoint with body `B`, header `X-Shopify-Hmac-Sha256: H` (unchanged — still valid, since HMAC only covers `B`), but with `X-Shopify-Shop-Domain: victim-shop.myshopify.com` (and any `X-Shopify-Topic`/`X-Shopify-Webhook-Id` desired).
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks `B` against `H`; the forged `shop`/`topic`/`webhook_id` headers pass through unauthenticated to the handler, as shown in [3](#0-2) .

### Citations

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
