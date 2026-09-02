### Title
Webhook shop-domain header is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`, and `ShopifyAPI::Utils::HmacValidator.validate` checks that signature against `Context.api_secret_key`. The `shop` accessor, however, is read directly from the `x-shopify-shop-domain`/`shopify-shop-domain` HTTP header, which is never part of the signed content. `ShopifyAPI::Webhooks::Registry.process` verifies the HMAC and then unconditionally trusts `request.shop` to build the `WebhookMetadata` handed to the app's handler. [1](#0-0) [2](#0-1) [3](#0-2) 

### Finding Description
The equality that should hold is: `bytes covered by HMAC == bytes that determine tenant identity`. Here it breaks down: the HMAC covers only `@raw_body` (the webhook payload text), while `request.shop`, the field the registry uses to attribute the delivered event to a specific merchant/tenant, comes from an unauthenticated header.

An app that installs on multiple shops (a completely normal, unprivileged scenario — anyone can install a public app on their own store) legitimately receives real webhooks from Shopify for their own shop's events, each with a valid HMAC over the raw body computed with the app's `api_secret_key`. Because the shop-domain header is excluded from the signature, that attacker/tenant can take one of their own genuinely-signed webhook deliveries (valid body + valid HMAC) and resend it to the app's webhook endpoint with the `x-shopify-shop-domain` header rewritten to point at a victim shop. `HmacValidator.validate` will still succeed (it only checks the body against the HMAC), and `Registry.process` will pass `WebhookMetadata.new(..., shop: request.shop, ...)` — now containing the victim's shop — into the host application's handler.

This is exactly the "field acted on but not covered by the HMAC" bug class from the report: expired-lock rewards binding failed because the multiplier state wasn't re-checked/kicked; here the tenant binding fails because the shop identity isn't cryptographically bound to the signed payload at all.

### Impact Explanation
Any app handler that trusts `WebhookMetadata#shop` to select per-tenant storage, credentials, or business logic (which is the documented purpose of this field) can be made to apply attacker-controlled webhook data under a victim shop's identity — a cross-tenant access/data-poisoning primitive requiring no access token, no `api_secret_key`, and no privileged account, only the ability to install the app on one's own store and replay/craft one HTTP request. This matches the Critical "cross-tenant access" impact category.

### Likelihood Explanation
Any merchant able to install the target app (a normal, unprivileged action) can capture a legitimately signed webhook for their own shop and replay it with a modified shop-domain header against the app's public webhook endpoint. No secrets, TLS interception, or social engineering are required — only observation of network requests the attacker's own browser/server naturally receives, which is within the "unprivileged internet user" threat model of this scan.

### Recommendation
Include the shop domain (and ideally the webhook id/topic) in the HMAC-signed payload verification, or require the host application to independently verify that `request.shop` matches an already-authorized/installed shop (existing session record) before trusting it, rather than only validating the raw body.

### Proof of Concept
1. App is installed on `attacker.myshopify.com`; Shopify delivers a webhook to the app's endpoint with headers `x-shopify-hmac-sha256: <valid-hmac-of-body>`, `x-shopify-shop-domain: attacker.myshopify.com`, and some JSON body.
2. Attacker captures this request (their own legitimately received webhook) and resends it to the same endpoint, only replacing `x-shopify-shop-domain` with `victim.myshopify.com`, leaving the body and HMAC header untouched.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `request.to_signable_string` (`@raw_body`) — unchanged — so validation succeeds. [4](#0-3) 
4. `request.shop` now returns `"victim.myshopify.com"`, and the handler receives `WebhookMetadata` attributing the attacker-controlled payload to the victim shop. [5](#0-4)

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
