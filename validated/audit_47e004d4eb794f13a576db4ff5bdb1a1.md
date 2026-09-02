## Title
Webhook `shop` identity is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC over the raw request body only, while the `shop` (and `topic`/`webhook_id`) values consumed by the webhook handler come from separate, unsigned HTTP headers. `Registry.process` accepts any request whose body-HMAC validates and then dispatches to the handler using the unverified `shop` header value, breaking the binding between "bytes verified by HMAC" and "shop identity acted upon."

### Finding Description
`Utils::HmacValidator.validate` verifies the request's `hmac` against `to_signable_string`. For webhooks, `to_signable_string` is defined as just the raw body: [1](#0-0) 

```
def to_signable_string
  @raw_body
end
```

Meanwhile `shop` is read from the `x-shopify-shop-domain`/`shopify-shop-domain` header, entirely outside the HMAC-signed content: [2](#0-1) 

`Registry.process` validates only the body HMAC, then dispatches using this unverified `shop` value: [3](#0-2) 

Because the app's webhook HMAC secret (`Context.api_secret_key`) is shared across every shop/tenant installed on the app (it is not shop-specific), any tenant who receives a legitimately-signed webhook for their own shop can capture that request and replay it to the app's webhook endpoint after only changing the `x-shopify-shop-domain` header to a victim shop's domain. The HMAC still validates (it only covers the untouched body), so `Registry.process` accepts the forged request and calls the handler with `shop: request.shop` set to the victim's domain — an identity a malicious tenant fully controls.

Formally, the binding the gem should enforce is:
`shop authenticated by HMAC == shop acted upon by the handler`
but the actual check enforces only:
`bytes verified by HMAC (raw_body) != shop field consumed by handler (unsigned header)`

This mirrors the reported bug class: a security check (the HMAC signature) is evaluated over data that does not include the field being trusted for identity/authorization purposes downstream.

### Impact Explanation
Any host application that uses `WebhookMetadata#shop` (as provided by this gem) to scope database lookups, session retrieval, or authorization decisions is vulnerable to cross-tenant confusion: a legitimate merchant on the app can trigger handler logic as if it came from an arbitrary other merchant/shop by simply swapping the shop header on a replayed, validly-HMAC'd body. This can lead to cross-tenant data access or state changes, satisfying the "Critical - cross-tenant access" impact bar.

### Likelihood Explanation
Exploitation only requires the attacker to be a legitimate, unprivileged tenant of the target app (any merchant can install most public apps) capable of receiving one real webhook and replaying an HTTP request with a modified header — no access to `api_secret_key`, tokens, or TLS interception is needed.

### Recommendation
Include the shop domain (and topic/webhook id, if they are relied upon for identity/authorization) inside the HMAC-signed content, or otherwise cryptographically bind them to the verified body (e.g., verify the shop against a shop the app already possesses a session/token for, rather than trusting the header value for authorization). At minimum, document that `WebhookMetadata#shop` must never be used for authorization decisions without an independent authenticity check, since it is not covered by `HmacValidator.validate`.

### Proof of Concept
1. Attacker installs the target app on `attacker.myshopify.com` and triggers a webhook (e.g. `orders/create`), receiving a POST from Shopify with headers `x-shopify-shop-domain: attacker.myshopify.com`, `x-shopify-hmac-sha256: <valid hmac over raw body>`, and body `B`.
2. Attacker replays this exact request to the app's webhook endpoint, changing only the `x-shopify-shop-domain` header to `victim.myshopify.com`; body `B` and the HMAC header are left untouched.
3. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks `HMAC(raw_body, api_secret_key)` — unaffected by the header change. [4](#0-3) 
4. The handler receives `WebhookMetadata.new(... shop: "victim.myshopify.com" ...)` and executes app logic as though the event originated from the victim shop. [5](#0-4)

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

**File:** lib/shopify_api/webhooks/registry.rb (L188-199)
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
```
