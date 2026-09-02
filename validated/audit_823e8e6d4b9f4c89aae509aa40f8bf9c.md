### Title
Webhook HMAC signature does not cover `shop-domain`, `topic`, or `webhook-id` headers, enabling cross-tenant webhook spoofing - (`File: lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, while `ShopifyAPI::Webhooks::Registry.process` uses the unauthenticated `shopify-shop-domain` (and `topic`/`webhook-id`) headers to build the `WebhookMetadata` that is handed to the app's webhook handler. Because the HMAC only binds the body, an unprivileged attacker who legitimately owns a Shopify store can capture one of their own genuine, validly-signed webhook deliveries and replay it against a target app's webhook endpoint with the `shopify-shop-domain` header rewritten to a victim shop, producing a webhook that passes signature verification while claiming to originate from a different tenant.

### Finding Description
`Request#to_signable_string` is defined as: [1](#0-0) 

This is the only data that `Utils::HmacValidator.validate` signs/verifies via `VerifiableQuery#to_signable_string`: [2](#0-1) 

However `Request#shop`, `#topic`, and `#webhook_id` are all read straight from HTTP headers, which are not part of the signed data: [3](#0-2) 

`Registry.process` verifies only the body HMAC and then trusts `request.shop`/`request.topic`/`request.webhook_id` when constructing the metadata passed into the app's registered handler: [4](#0-3) 

The binding that is broken is: **shop identity verified by the HMAC (over body only) ≠ shop identity acted on by the handler (from the unauthenticated header)**. Any party that can obtain one valid `(raw_body, hmac)` pair — which any merchant who installs the app can obtain from their own genuine webhook traffic, since Shopify signs webhooks with the app's shared secret for every installed shop — can resend that exact body/HMAC pair to the app's public webhook endpoint while substituting an arbitrary `shopify-shop-domain` (and `shopify-topic`/`shopify-webhook-id`) header. `Registry.process` will accept it as authentic and dispatch it to the handler tagged with the attacker-chosen shop, topic, and webhook id.

### Impact Explanation
This breaks the tenant boundary the gem is supposed to enforce for webhook delivery: an app relying on `WebhookMetadata#shop`/`#topic` to route webhook side effects (e.g., updating per-shop state, uninstall/redact processing, cache invalidation) can be made to apply another shop's genuine, correctly-signed payload under a victim shop's identity, or to re-tag a payload with an arbitrary topic (e.g., turning a benign event into a spoofed `shop/redact` or `customers/data_request` mandatory webhook). This is a cross-tenant integrity violation stemming purely from this gem's own HMAC-coverage/identity-binding decision in `Webhooks::Request` and `Webhooks::Registry`.

### Likelihood Explanation
Any actor who can install the target app on their own store (a normal, unprivileged action) automatically receives legitimately HMAC-signed webhook deliveries from Shopify for their shop. Capturing one such `(body, hmac)` pair and replaying it with a modified `shopify-shop-domain`/`shopify-topic` header against the app's public webhook endpoint requires no secrets, tokens, or elevated access — only the ability to send an HTTP request, which satisfies the "unprivileged internet user" bar.

### Recommendation
- Include `shop-domain`, `topic`, and `webhook-id` (in addition to the body) in the signed/verified string, or otherwise cryptographically bind them to the request before dispatch, so a captured `(body, hmac)` pair cannot be replayed under a different shop or topic identity.
- Short of changing the signed payload, at minimum cross-check `request.shop` against the shop associated with the session/installation record the app already has on file before invoking handlers, rather than trusting the header value implicitly.

### Proof of Concept
1. Attacker installs the target Shopify app on their own development/trial store (`attacker-shop.myshopify.com`) and triggers a webhook event (e.g., `orders/create`), capturing the raw HTTP request Shopify sends to the app's webhook endpoint, including the `X-Shopify-Hmac-Sha256` header and raw body.
2. Attacker resends this exact request to the same app endpoint, but replaces the `X-Shopify-Shop-Domain` header with `victim-shop.myshopify.com` (and optionally `X-Shopify-Topic` with a different registered topic such as `shop/redact`).
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `request.to_signable_string` (the unchanged raw body) and succeeds, since the header change did not alter the signed bytes: [5](#0-4) 
4. The app's handler executes with `WebhookMetadata#shop == "victim-shop.myshopify.com"` even though the payload was never generated for or by that shop.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
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
