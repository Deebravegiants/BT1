### Title
Webhook `shop-domain` (and `topic`) headers are not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant-identifying `shop` attribute from the `x-shopify-shop-domain` HTTP header, but the HMAC signature that `Utils::HmacValidator.validate` checks is computed only over the raw request body. The header that tells the handler *which shop* the webhook is for is never bound to the signature, so it can be swapped without invalidating the HMAC.

### Finding Description
`Request#shop` reads the shop identity straight from a header: [1](#0-0) 

but `Request#to_signable_string`, which is what `HmacValidator` actually verifies, only returns `@raw_body`: [2](#0-1) 

`Registry.process` validates the HMAC and then trusts `request.shop` (and `request.topic`) directly when building the `WebhookMetadata` handed to the app's handler: [3](#0-2) 

The identity binding the code implicitly assumes is:

`HMAC-verified bytes == the full set of attributes the handler acts on (body, shop, topic)`

But in reality only `raw_body` is covered:

`HMAC-verified bytes (raw_body) ≠ bytes the handler trusts (raw_body + shop-domain header + topic header)`

Because Shopify webhook HMACs are computed with the app's single `client_secret` (the same secret for every shop that installs the app), any shop that installs the app can legitimately receive a webhook with a valid `x-shopify-hmac-sha256` value for some body. An attacker who controls such a shop can capture that valid `(raw_body, hmac)` pair and replay it to the app's webhook endpoint with the `x-shopify-shop-domain` header changed to a victim shop's domain (and/or the `x-shopify-topic` header changed). `HmacValidator.validate` will still pass because it only recomputes the digest over `raw_body`, and `Registry.process` will invoke the handler believing the payload originated from the victim shop.

### Impact Explanation
This breaks the tenant boundary the gem is supposed to enforce for webhook delivery: the `shop` value passed into `WebhookMetadata` and ultimately into the host application's per-shop business logic (e.g., updating shop-scoped records, triggering shop-scoped side effects, mandatory `shop/redact` compliance flows) can be attacker-controlled even though the request passes HMAC "validation." This is a cross-tenant data integrity/authenticity issue — an attacker-controlled shop can inject webhook events that are processed as if they came from a different, victim shop.

### Likelihood Explanation
Any unprivileged user who can install the app on their own store (a normal, unprivileged action for a public/dev app) can obtain a validly HMAC-signed `(raw_body, hmac)` pair, then simply resend it to the app's webhook endpoint with a forged `shop-domain` (and optionally `topic`) header. No access to the `client_secret`, an access token, or any privileged account is required — only the ability to trigger any webhook delivery to their own installed app and replay the HTTP request with edited headers.

### Recommendation
Include the `shop-domain` (and `topic`) header values in the HMAC signable string (i.e., bind them cryptographically to the signature, the way Shopify's own HMAC scheme is documented to only cover the body — so instead the gem should independently corroborate the shop by, e.g., verifying it against a known/registered session's shop, or otherwise treat header-only shop/topic values as untrusted until corroborated), or at minimum document loudly that `request.shop`/`request.topic` are unauthenticated and must be cross-checked by the host application against a shop-scoped access token/session before use.

### Proof of Concept
1. Attacker installs the app on their own store `attacker-shop.myshopify.com` and triggers any webhook (e.g. `orders/create`). Shopify sends:
   - Body: `raw_body`
   - Headers: `x-shopify-hmac-sha256: <valid_hmac>`, `x-shopify-shop-domain: attacker-shop.myshopify.com`, `x-shopify-topic: orders/create`
2. Attacker resends this exact HTTP request to the app's webhook endpoint, changing only:
   - `x-shopify-shop-domain: victim-shop.myshopify.com`
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `request.to_signable_string` (`raw_body` only) — unchanged — so validation succeeds: [4](#0-3) 
4. The registered handler receives `WebhookMetadata` with `shop: "victim-shop.myshopify.com"` even though the payload actually originated from the attacker's own shop, letting the attacker inject spoofed webhook data attributed to a shop they do not control.

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
