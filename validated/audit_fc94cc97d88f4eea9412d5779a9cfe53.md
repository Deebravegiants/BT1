## Title
Webhook `shop`, `topic`, `webhook_id`, and `api_version` fields are trusted from unauthenticated HTTP headers while the HMAC only covers the raw body - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` extracts `shop`, `topic`, `webhook_id`, and `api_version` directly from HTTP headers, but its `to_signable_string` — the value that `Utils::HmacValidator` verifies against the `X-Shopify-Hmac-Sha256` header — only covers the raw request body. [1](#0-0)  This is the same class of bug as the audit's M-1 finding: a value that is *acted on* by the recipient's downstream logic is not covered by the cryptographic check that is supposed to authenticate the whole request.

### Finding Description
`ShopifyAPI::Webhooks::Registry.process` verifies the webhook by calling `Utils::HmacValidator.validate(request)`, then immediately trusts `request.shop`, `request.topic`, `request.webhook_id`, and `request.api_version` to build the `WebhookMetadata` passed to the app's handler: [2](#0-1) 

```ruby
def process(request)
  raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)
  handler = @registry[request.topic]&.handler
  ...
  handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop,
    body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))
end
```

`HmacValidator.validate` computes the HMAC over `verifiable_query.to_signable_string`, and for `Request` that method returns only `@raw_body`: [3](#0-2)  The `shop`, `topic`, `webhook_id`, and `api_version` accessors read straight from attacker-controllable headers with no participation in the signature: [4](#0-3) 

The identity binding that should hold is:
`shop attributed to the processed webhook == shop that the HMAC-secret-holder (Shopify) actually generated this payload for`

What is actually verified is only:
`raw_body bytes == raw_body bytes signed by Shopify`

Because the app's `api_secret_key` is a single client secret shared across every merchant that has installed the app (not a per-shop secret), any body payload that Shopify validly signed for **any** shop remains a validly-signed payload for **every** shop from this gem's point of view. An unprivileged user who controls their own shop (a legitimate, cheap way to get valid Shopify-signed webhook deliveries) can capture one of their own valid webhook deliveries, then replay it to the app's webhook endpoint with the `X-Shopify-Shop-Domain` header rewritten to a victim shop's domain (and/or the topic/webhook-id/api-version headers altered). `HmacValidator.validate` still passes because it only checks `@raw_body`, and `Registry.process` hands the handler a `WebhookMetadata` whose `shop` is the attacker-chosen victim domain, with the attacker's own (validly-signed) body content.

### Impact Explanation
This crosses the tenant boundary the gem is supposed to enforce: an app's webhook handler is invoked believing that a specific piece of Shopify-verified data belongs to shop B, while shop A (attacker) actually produced the body and forged the shop attribution. Any app that keys webhook side effects (order/product/customer sync, billing state changes, GDPR-relevant records, feature flags, etc.) by `WebhookMetadata#shop` can have attacker-controlled data written into or trigger actions against another merchant's tenant space purely by relaying HTTP requests — satisfying the "cross-tenant access" criterion, since the gem's own header-parsing/HMAC design, not host-application misuse, causes the shop identity to be unauthenticated.

### Likelihood Explanation
Exploitability only requires: (1) being an app user/merchant capable of installing the target app on one's own store to receive at least one legitimately Shopify-signed webhook body, and (2) the ability to POST an HTTP request to the app's public webhook endpoint with custom headers — both are unprivileged-internet-user capabilities with no access token, `api_secret_key`, or leaked credential needed.

### Recommendation
Include the security-relevant headers (`shop-domain`, `topic`, `webhook-id`, `api-version`) in the signed/verified representation, or otherwise cryptographically bind them to the payload before they are used to build `WebhookMetadata`. At minimum, `Request#to_signable_string` should not be the sole gate — the gem should verify that the `shop` header matches shop-scoped session/webhook registration data (e.g., a shop that this app is actually registered/installed for) rather than trusting the header value directly for tenant attribution.

### Proof of Concept
1. Attacker installs the app on their own shop `attacker.myshopify.com` and triggers any subscribed webhook topic, capturing the raw POST: headers `X-Shopify-Topic`, `X-Shopify-Hmac-Sha256`, `X-Shopify-Shop-Domain: attacker.myshopify.com`, and body `B` (validly HMAC-signed by Shopify using the app's shared `api_secret_key`).
2. Attacker replays the exact same body `B` and HMAC header to the app's webhook endpoint, but sets `X-Shopify-Shop-Domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses headers, `Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only hashes `@raw_body` (`to_signable_string`) — unaffected by the header change. [3](#0-2) 
4. `Registry.process` builds `WebhookMetadata.new(shop: "victim.myshopify.com", body: <attacker's parsed body>, ...)` and invokes the app's handler as if this data legitimately belongs to `victim.myshopify.com`. [5](#0-4)

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-43)
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

      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end

      sig { returns(T::Hash[String, T.untyped]) }
      def parsed_body
        JSON.parse(@raw_body)
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
