## Analysis Result

### Title
Webhook shop identity is not covered by HMAC verification, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb](lib/shopify_api/webhooks/request.rb))

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC of the raw request body, then unconditionally trusts the `shop` value taken from a separate, unsigned HTTP header to attribute the payload to a tenant. Because the shop identity is not bound to the HMAC, any request bearing a body/HMAC pair that validates for *some* shop can be replayed with an arbitrary `shop-domain` header value, and the handler will process it as if it belongs to that different shop.

### Finding Description
`ShopifyAPI::Utils::HmacValidator.validate` computes/compares the signature over `verifiable_query.to_signable_string`. For webhooks, `Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

None of the Shopify-supplied headers — including `shop`, `topic`, `api_version`, or `webhook_id` — are included in the signable string: [2](#0-1) 

`Registry.process` validates only this body HMAC, then constructs `WebhookMetadata` directly from the unauthenticated `request.shop` header value and hands it to the app's handler: [3](#0-2) 

The identity binding that should hold is:
`shop authenticated by HMAC == shop used by the handler to select/mutate tenant data`

In this implementation that equality does not hold: the HMAC only proves "this body was signed with the app's secret for *a* shop," not "this body belongs to the shop named in this header." A user who legitimately installs the app on their own shop receives real, correctly-signed webhooks for their own store (valid body + valid HMAC). They can capture such a webhook and resend it to the app's public webhook endpoint with the `x-shopify-shop-domain` (or `shopify-shop-domain`) header rewritten to name a different (victim) shop. `Utils::HmacValidator.validate` still succeeds because it only checks the body against the secret, and `Registry.process` passes the attacker-chosen `shop` value straight into the handler.

### Impact Explanation
This breaks the tenant boundary the webhook handler relies on: an unprivileged merchant (someone who has installed the app on any single shop) can inject events that a host application will treat as originating from a shop they do not own, since `request.shop` — not covered by the signature — is the only tenant discriminator passed to the handler. Depending on what the host application does with `WebhookMetadata#shop` (e.g., writing store settings, product data, or triggering shop-scoped actions from webhook content), this enables cross-tenant data injection/corruption, matching the "cross-tenant access" impact category.

### Likelihood Explanation
Exploitation requires only: (1) the attacker install the target app on a shop they control (no elevated privilege), (2) trigger a webhook topic that is registered, and (3) resend the captured HTTP request with a modified shop-domain header to the app's public webhook endpoint. No knowledge of `api_secret_key` or access tokens is needed since the attacker's own webhook is genuinely signed by Shopify for their shop; only the unsigned header is forged.

### Recommendation
Include the shop-identifying header (and ideally topic/api-version/webhook-id) in the signable string used for HMAC verification, or otherwise independently authenticate the `shop-domain` header (e.g., require it to match a shop that has an active, previously-established registration/session before dispatching to handlers). At minimum, document in `Registry.process`/`Request` that `shop` is not integrity-protected and must not be trusted for tenant selection without additional verification by the host application.

### Proof of Concept
```ruby
# 1. Attacker owns "attacker-shop.myshopify.com" and has installed the app.
# Shopify sends a legitimately signed webhook for a topic the app registered:
raw_body = '{"id": 1, "malicious": "payload"}'
valid_hmac = OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), api_secret_key, raw_body)

# 2. Attacker replays the same body/HMAC to the app's public webhook endpoint,
#    but swaps the shop-domain header to the victim's shop:
headers = {
  "x-shopify-topic" => "orders/create",
  "x-shopify-hmac-sha256" => Base64.encode64(valid_hmac), # unchanged, still valid
  "x-shopify-shop-domain" => "victim-shop.myshopify.com", # forged, not covered by HMAC
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: headers)
ShopifyAPI::Webhooks::Registry.process(request)
# => HmacValidator.validate succeeds (only checks raw_body),
#    handler.handle receives WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: attacker_data, ...)
```

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
