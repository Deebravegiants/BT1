I found a concrete analog matching the "field acted on but not covered by the HMAC" bug class in the webhook processing pipeline.

### Title
Webhook shop/topic attribution is not covered by the HMAC signature, enabling cross-tenant webhook forgery - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` derives `shop`, `topic`, `webhook_id`, and `api_version` from raw, unauthenticated HTTP headers, while the HMAC signature it validates covers only the raw request body. `ShopifyAPI::Webhooks::Registry.process` trusts these header-derived fields to dispatch the webhook to a handler and to construct `WebhookMetadata`, without any of them being bound to the signature that supposedly authenticates the request.

### Finding Description
`Utils::HmacValidator.validate` computes `compute_signature(verifiable_query.to_signable_string, secret)` and compares it against `verifiable_query.hmac` [1](#0-0) . For webhook requests, `to_signable_string` returns only `@raw_body` [2](#0-1) , while `shop`, `topic`, `webhook_id`, and `api_version` are read directly from HTTP headers that are never included in the signable string [3](#0-2) .

`Registry.process` validates only the HMAC over the body, then immediately trusts `request.topic` and `request.shop` to select a handler and construct the dispatched metadata: [4](#0-3) 

The equality the code implicitly assumes is: `bytes verified by HMAC == bytes the handler acts on for tenant attribution`. In reality: `bytes verified by HMAC (raw_body only) != identity fields consumed (shop, topic, webhook_id, api_version — all header-derived)`. Because Shopify's HMAC scheme for webhooks signs only the body, any header can be freely modified without invalidating the signature, as long as the attacker can produce (or replay) a body/HMAC pair signed with the app's own secret — for example from a webhook legitimately delivered to their own shop for the same app. Swapping the `x-shopify-shop-domain` (and/or `x-shopify-topic`) header on that captured request preserves a valid HMAC, since the header is outside the signed payload.

### Impact Explanation
This breaks the shop-attribution identity binding used by the host application to route webhook data to the correct tenant. A malicious merchant using the app can capture one legitimate, validly-signed webhook delivery for their own shop, then relay it with a forged `shop` header pointing at another shop, causing `WebhookMetadata.new(shop: request.shop, ...)` to report an arbitrary attacker-chosen shop as the source of legitimate-looking, correctly-HMAC-verified data [5](#0-4) . Any host application that trusts `data.shop` from a "verified" webhook (as the gem explicitly signals it is, via `HmacValidator.validate`) to look up sessions/tenants can be tricked into applying attacker-supplied webhook data under another tenant's identity — a cross-tenant access/confusion condition.

### Likelihood Explanation
Any merchant who has installed the app can trivially obtain at least one validly HMAC-signed webhook body/signature pair for their own shop (webhooks are delivered to their configured endpoint, or they can trigger typical topics like `app/uninstalled`, `orders/create`, etc.). Forging the `x-shopify-shop-domain` header requires no cryptographic secret and no privileged access — it only requires the ability to send an HTTP request to the app's webhook endpoint, which is a public/internet-facing endpoint by design.

### Recommendation
Include `shop`, `topic`, and any other security-relevant identity fields in the HMAC-signed payload used for verification (i.e., extend `to_signable_string` to bind these header values, or independently re-verify `shop`/`topic` against a value bound to the raw body/HMAC pair), so that a valid signature over one body cannot be replayed against a different tenant identity.

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com` and triggers/captures a legitimate webhook, e.g. `orders/create`, with headers:
   - `x-shopify-hmac-sha256: <valid HMAC over raw body>`
   - `x-shopify-shop-domain: attacker-shop.myshopify.com`
   - `x-shopify-topic: orders/create`
2. Attacker resends the exact same raw body and HMAC header to the app's webhook endpoint, but changes:
   - `x-shopify-shop-domain: victim-shop.myshopify.com`
3. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only checks the (unchanged) raw body against the (unchanged) HMAC [6](#0-5) .
4. The handler receives `WebhookMetadata` with `shop: "victim-shop.myshopify.com"` even though the payload actually originated from, and was signed for, `attacker-shop.myshopify.com` [5](#0-4) .

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
