### Title
Webhook `shop` identity is not covered by HMAC verification, allowing shop-domain spoofing on an otherwise validly-signed webhook - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
The bug class described in the external report is "an identity value is trusted without being bound to the cryptographic proof that authenticates the request." The closest reachable analog in this gem is in the webhook pipeline: `ShopifyAPI::Webhooks::Request#shop` is read straight from the `shopify-shop-domain`/`x-shopify-shop-domain` HTTP header, but the HMAC signature that `Registry.process` validates is computed only over the raw request body, never over that header.

### Finding Description
`Utils::HmacValidator.validate` computes and compares the signature against `verifiable_query.to_signable_string`. For webhooks, `Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

Meanwhile, `Request#shop` is parsed from the `shopify-shop-domain` header, a value that is never part of the signed payload: [2](#0-1) 

`Registry.process` gates handling on `Utils::HmacValidator.validate(request)` succeeding, then immediately forwards `request.shop` — the unverified header — into `WebhookMetadata`, which is the trusted "tenant" identity given to the host application's handler: [3](#0-2) [4](#0-3) 

The identity equality that should hold is: `shop used to authorize/attribute the webhook == shop bound inside the HMAC-signed payload`. In this implementation, the equality instead is: `shop used to authorize/attribute the webhook == shop header sent by the request`, which is attacker-controlled and independent of the HMAC.

This exactly mirrors the "self-assign" bug class in the report — there, `super_admin` was accepted without checking a binding to the mint. Here, `shop` (the tenant identity) is accepted without checking a binding to the signed bytes.

### Impact Explanation
An attacker who controls a shop that has installed the target app receives real, validly-signed webhooks from Shopify for their own shop (HMAC computed with the app's `client_secret`, over the body only). Because the signature never covers the `shop-domain` header, the attacker can take a legitimately-signed webhook payload/HMAC pair and resend it to the app's webhook endpoint with the `shopify-shop-domain` header rewritten to a victim shop. `Utils::HmacValidator.validate` still succeeds (it only checks the body), and `Registry.process` will hand the handler a `WebhookMetadata` claiming `shop: "victim.myshopify.com"` with attacker-controlled body content. Any host application that trusts `WebhookMetadata#shop` as the tenant key (which is the documented/intended use of this field) can be induced to attribute or apply attacker data to another merchant's tenant — a cross-tenant data/action confusion.

### Likelihood Explanation
Medium-to-high: exploitation requires only that the attacker (1) operates a shop with the target app installed so they can obtain at least one genuinely signed webhook, and (2) can reach the app's public webhook HTTP endpoint with a modified header — both are available to any ordinary, unprivileged app installer/internet user, no leaked secrets or privileged access needed.

### Recommendation
Bind the trusted shop identity to the signed payload rather than an unauthenticated header:
- Include the `shop-domain` (and other Shopify-controlled routing headers) in the HMAC-signed data, or
- Cross-check `request.shop` against a shop value embedded in the signed webhook body (where Shopify includes one), and reject the request if they diverge, before constructing `WebhookMetadata`.

### Proof of Concept
1. Attacker's own shop `attacker.myshopify.com` has the target app installed; Shopify delivers a legitimate webhook to the app with headers `shopify-shop-domain: attacker.myshopify.com`, `shopify-hmac-sha256: <valid-hmac-of-body>`, and some JSON body.
2. Attacker intercepts/replays this exact request but changes only the header to `shopify-shop-domain: victim.myshopify.com`, leaving body and `hmac-sha256` untouched, and POSTs it to the app's public webhook endpoint.
3. `ShopifyAPI::Webhooks::Request.new` parses this into a `Request` object; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only validates `@raw_body` against the (unchanged) HMAC — see `to_signable_string` returning `@raw_body` [1](#0-0) .
4. `Registry.process` builds `WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)` with `shop == "victim.myshopify.com"` [5](#0-4) , and the host application's `handler.handle` executes believing the (attacker-supplied) body legitimately originated from the victim's shop.

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

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L6-12)
```ruby
    class WebhookMetadata < T::Struct
      const :topic, String
      const :shop, String
      const :body, T::Hash[String, T.untyped]
      const :api_version, String
      const :webhook_id, String
    end
```

**File:** lib/shopify_api/webhooks/registry.rb (L198-199)
```ruby
          handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop,
            body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))
```
