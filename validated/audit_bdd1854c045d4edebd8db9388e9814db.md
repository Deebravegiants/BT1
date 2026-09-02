### Title
Webhook `shop` identifier is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes the webhook HMAC over the raw body only, while the `shop` (and `topic`/`webhook-id`) values used by `Webhooks::Registry.process` to route and act on the event are taken from unauthenticated HTTP headers that are excluded from that signature. Any party that possesses one validly-signed webhook body (trivially obtainable by installing the app on their own store) can replay that exact body with a rewritten `X-Shopify-Shop-Domain` header pointing at a victim shop, and the HMAC check still passes.

### Finding Description
`HmacValidator.validate` verifies `verifiable_query.hmac` against `compute_signature(verifiable_query.to_signable_string, secret)` [1](#0-0) . For webhooks, `to_signable_string` returns only the raw HTTP body: [2](#0-1) 

The `shop` accessor, however, is read straight from the `shopify-shop-domain`/`x-shopify-shop-domain` header, which is never included in the signed material: [3](#0-2) 

`Registry.process` validates only the body HMAC and then forwards `request.shop` (and `request.topic`, `request.webhook_id`) straight to the application's handler as trusted metadata: [4](#0-3) 

This breaks the intended binding: `shop header value == shop that produced the signed body`. The `hmac` proves only "this body was produced by an app secret holder," not "this body belongs to this shop." Any caller that can obtain one genuinely-signed webhook body — for example by installing the app on a store they control and capturing a real webhook delivery — can resend that identical body to the app's webhook endpoint while substituting an arbitrary `X-Shopify-Shop-Domain` value. Because the header is outside the signable string, `Utils::HmacValidator.validate` still returns `true`, and `Registry.process` dispatches the handler with `shop:` set to the attacker-chosen value.

This is the same bug class as the `OasisSwapPair.swapCalculatingRebate` report: a security-relevant field (`feeController`/here, `shop`) is acted upon by downstream logic without being covered by the authenticity check (the fee-rebate identity check / here, the HMAC), letting an unprivileged caller substitute an identity that was never authenticated for that specific request.

### Impact Explanation
Applications built on this gem are documented to trust `WebhookMetadata#shop` from `Registry.process` to determine which merchant's records the event pertains to. Because that value is unsigned, an attacker who has legitimate access to any single shop capable of installing the app can forge webhook deliveries that are attributed to any other tenant shop, as long as they can produce or replay an appropriately-shaped signed body (many webhook topics have a fixed/guessable/replayable body, or the attacker controls the body content of their own store's webhook and merely changes which shop it's claimed to belong to). This is a cross-tenant data/action confusion: a party from Tenant A causes the host application to process an event as though it originated from Tenant B, potentially triggering writes, notifications, or business logic scoped to Tenant B based on attacker-supplied body content.

### Likelihood Explanation
Exploitation only requires network access to the app's public webhook endpoint and the ability to install the app (or otherwise obtain one genuinely-signed webhook payload), which is available to any unprivileged internet user for apps with public/free installation. No `api_secret_key`, access token, or privileged account is needed — the attacker never needs to know the app's secret because they are replaying a body Shopify already signed for them, just with a doctored shop header.

### Recommendation
Include the shop domain (and ideally topic/webhook id) inside the signed material, or otherwise cryptographically bind them to the raw body before trusting the header, e.g. verify the header's shop value belongs to a known, previously-installed session/shop before dispatching, or require the host application to independently reconcile `request.shop` against a session store keyed by an already-verified identity for that webhook, rather than exposing `shop` as an unauthenticated field on `Request`. At minimum, document prominently that `Request#shop`/`WebhookMetadata#shop` is unauthenticated and must not be used for authorization decisions without additional verification (e.g., cross-checking against the app's own installed-shop records).

### Proof of Concept
1. Install the target app (this is any app built on this gem) on an attacker-controlled development store `attacker-shop.myshopify.com`; trigger a webhook of interest (e.g. `orders/create`) and capture the raw request, including the valid `X-Shopify-Hmac-Sha256` header and body.
2. Replay the captured request to the same app's webhook endpoint, changing only `X-Shopify-Shop-Domain` to `victim-shop.myshopify.com` (the body and HMAC header are left untouched).
3. `Utils::HmacValidator.validate` recomputes the HMAC over `@raw_body` only [1](#0-0)  — unchanged from step 1 — so validation succeeds.
4. `Registry.process` invokes the registered handler with `shop: request.shop` set to `victim-shop.myshopify.com` [5](#0-4) , causing the host application to process attacker-supplied data as an event belonging to the victim tenant.

### Citations

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

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
