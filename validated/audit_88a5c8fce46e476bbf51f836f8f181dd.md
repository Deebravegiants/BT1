The docs explicitly state `ShopifyAPI::Webhooks::Registry.process` "will verify the request did indeed come from Shopify" (docs/usage/webhooks.md:125), meaning the library itself markets HMAC validation as proof of authenticity of the whole request including the `shop` metadata, when in reality only the raw body is covered.

### Title
Webhook `shop` identity is unauthenticated, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb, lib/shopify_api/webhooks/registry.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` verifies a webhook using `Utils::HmacValidator.validate(request)`, but the HMAC is computed only over the raw request body [1](#0-0) . The `shop` value that is subsequently trusted and handed to the app's webhook handler is read directly from the `x-shopify-shop-domain` HTTP header, which is never part of the signed data [2](#0-1) .

### Finding Description
`HmacValidator.validate` calls `verifiable_query.to_signable_string` and HMAC-verifies only that string against `verifiable_query.hmac` [3](#0-2) . For `Webhooks::Request`, `to_signable_string` returns just `@raw_body`, and `hmac` is derived from the `hmac-sha256` header [4](#0-3) [1](#0-0) . Meanwhile `topic`, `shop`, `api_version`, and `webhook_id` are all sourced from unauthenticated headers [5](#0-4) .

`Registry.process` treats a passing HMAC check as sufficient proof of authenticity for the entire request, then forwards the header-derived, unauthenticated `shop` straight into `WebhookMetadata` passed to the app's handler:
```
raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)
...
handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop, body: request.parsed_body, ...))
``` [6](#0-5) 

The binding that is broken can be stated as an equality that the code implicitly assumes but never checks: `shop_that_authorized_the_hmac == request.shop`. Because Shopify webhook HMACs for a given app are signed with the single, app-wide `api_secret_key` — not a per-shop secret — any tenant that has installed the app receives genuine webhook deliveries with a valid HMAC over a body that tenant fully controls (webhook payloads largely mirror data the merchant creates, e.g. an order they place in their own store). An attacker who is a legitimate merchant of the app (Tenant B) can capture one such genuine `(raw_body, hmac)` pair from their own store, then replay it directly to the app's webhook endpoint with the `x-shopify-shop-domain` header rewritten to a victim tenant's domain (Tenant A). `HmacValidator.validate` still succeeds because it never inspects the shop header, and the handler receives `WebhookMetadata` claiming the data belongs to Tenant A when it actually originated from and is controlled by Tenant B.

The docs for this gem describe `Registry.process` as verifying "the request did indeed come from Shopify" without qualifying that only the body — not the shop/topic identity — is authenticated [7](#0-6) , so an app built per this gem's documented contract has no reason to independently re-verify `data.shop` before using it (e.g. to key per-tenant storage as shown in the example handler) [8](#0-7) .

### Impact Explanation
This is a cross-tenant data-integrity break: a malicious/compromised merchant of a multi-tenant app can inject attacker-controlled webhook payloads that are attributed to a different, victim shop. Depending on the handler's logic (e.g. updating order/customer/inventory records keyed by `data.shop`), this can corrupt or exfiltrate another tenant's business state, or trigger tenant-scoped side effects (like sync or fulfillment logic) using attacker-supplied data — a cross-tenant access violation.

### Likelihood Explanation
Any merchant who has installed the app can trigger a real webhook delivery for their own shop (e.g., by placing an order), giving them a valid `(body, hmac)` pair signed with the shared `api_secret_key`. Replaying it against the app's public webhook endpoint with a forged `shop-domain` header requires no special privileges beyond normal HTTP access to the app's callback URL, which is the same endpoint Shopify itself posts to.

### Recommendation
Bind the `shop` (and ideally `topic`/`webhook_id`) identity to the HMAC-verified data instead of trusting unauthenticated headers. Options:
- Include the shop domain in the signable string when computing/verifying the webhook HMAC, if supported by an alternate verification scheme.
- Cross-check `request.shop` against a shop already known to the app for a currently active/authorized session, and reject webhooks for shops without an established relationship, before invoking the handler.
- Document explicitly in `docs/usage/webhooks.md` that only the body is authenticated, so downstream apps know they must independently validate the shop is legitimate for that body/topic combination.

### Proof of Concept
1. Tenant B installs the app and has scope to trigger a webhook for their own shop `tenant-b.myshopify.com` (e.g., create an order), receiving from Shopify:
   - Headers: `x-shopify-topic: orders/create`, `x-shopify-hmac-sha256: <valid HMAC over body>`, `x-shopify-shop-domain: tenant-b.myshopify.com`
   - Body: attacker-controlled order JSON.
2. Tenant B captures this raw body and HMAC header value (they can sniff their own inbound traffic to their own app instance/logs, or via a proxy they control since it's their own webhook).
3. Tenant B crafts a new POST to the same webhook endpoint with:
   - The same raw body and same `x-shopify-hmac-sha256` value (still valid, since HMAC covers body only).
   - `x-shopify-shop-domain` rewritten to `victim-tenant.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only checks `@raw_body` against the HMAC [1](#0-0) .
5. `handler.handle` is invoked with `WebhookMetadata.new(shop: "victim-tenant.myshopify.com", body: <Tenant B's attacker-controlled data>, ...)` [9](#0-8) , causing the app to process attacker data as if it belonged to the victim tenant.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-13)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end
```

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

**File:** docs/usage/webhooks.md (L123-126)
```markdown
## Process a Webhook

To process an http webhook, you need to listen on the route(s) you provided during the Webhook registration process, then when the route is hit construct a `ShopifyAPI::Webhooks::Request` and call `ShopifyAPI::Webhooks::Registry.process`. This will verify the request did indeed come from Shopify and then call the specified handler for that webhook. An example in Rails is shown below:

```
