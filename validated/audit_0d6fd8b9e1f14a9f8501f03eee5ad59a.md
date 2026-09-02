### Title
Webhook `shop` and `topic` fields are not covered by the HMAC signature, allowing tenant/topic spoofing on an otherwise "validated" webhook - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` treats a webhook request as authenticated once `Utils::HmacValidator.validate(request)` succeeds, and then dispatches to the app's handler using `request.shop` and `request.topic`. However, the HMAC signature computed by `HmacValidator` only covers the raw request body — the `shop-domain`, `topic`, `webhook-id`, and `api-version` values are read straight from unauthenticated HTTP headers and are never included in the signed content. This breaks the identity binding: `shop` used for tenant dispatch != `shop` covered by the HMAC.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw body: [1](#0-0) 

while `shop`, `topic`, `webhook_id`, and `api_version` are pulled directly from HTTP headers with no cryptographic binding: [2](#0-1) 

`Utils::HmacValidator.validate` computes the signature purely over `verifiable_query.to_signable_string` (i.e., the body only) and compares it with the `hmac` header: [3](#0-2) 

`Registry.process` gates dispatch on this HMAC check succeeding, and then builds `WebhookMetadata` — the object handed to the app's business logic — straight from the same unauthenticated headers (`request.shop`, `request.topic`, `request.webhook_id`, `request.api_version`): [4](#0-3) 

The equality that should hold is: *the shop/topic value the handler acts on == the shop/topic value cryptographically bound by the signature*. In this implementation, the signature binds only the body bytes, so:
`bytes verified (body) != fields acted upon (shop, topic, webhook_id, api_version)`.

An attacker who legitimately installs the app on their own shop (an unprivileged, self-controlled tenant) receives real Shopify webhooks with valid HMACs for their own shop/topic. Because the signature never covers the `shop-domain` or `topic` headers, the attacker can replay the exact same `(raw_body, hmac)` pair to the app's webhook endpoint while substituting an arbitrary `shopify-shop-domain` (and/or `shopify-topic`) header. `HmacValidator.validate` still succeeds (it never inspected those headers), and `Registry.process` will happily route the payload to the handler tagged with the attacker-chosen shop/topic.

### Impact Explanation
Any application built on this gem that uses `WebhookMetadata#shop` (the field this library's own webhook flow explicitly hands to handlers) to key persistence, entitlement, or billing logic can be made to attribute a validly-signed payload to a different tenant than the one it actually originated from. This is a cross-tenant identity-binding break directly caused by the gem's webhook verification API creating a false sense of full request authentication.

### Likelihood Explanation
Exploitation requires no secrets, tokens, or privileged access — only the ability to install the app on any shop (which an unprivileged internet user attacker can do for a free/dev store) and the ability to send arbitrary HTTP headers to the app's public webhook endpoint, which any app developer using this gem exposes to receive Shopify webhooks. The `HmacValidator`/`Request` design is fixed within the gem, so every consumer that relies on `WebhookMetadata#shop`/`#topic` inherits this gap.

### Recommendation
Bind the identifying headers (`shop-domain`, `topic`, and ideally `webhook-id`) into the value that is HMAC-validated, or otherwise document/enforce that `Registry.process` must independently verify `request.shop` against a known/installed shop list before dispatch. At minimum, `Utils::HmacValidator.validate` should not be treated (nor presented via its boolean return) as validating anything beyond the raw body; `WebhookMetadata` construction in `Registry.process` should not implicitly trust header-derived `shop`/`topic` as verified.

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com` and triggers a real webhook (e.g., `orders/create`), capturing the raw POST body and the `X-Shopify-Hmac-Sha256` header Shopify sent — both valid and matching the app's `client_secret`.
2. Attacker replays the request to the app's webhook endpoint but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com` (and/or a different `X-Shopify-Topic`), keeping the original body and HMAC header unchanged.
3. `HmacValidator.validate` (`lib/shopify_api/utils/hmac_validator.rb:26-31`) recomputes the HMAC over the unchanged body and it matches — validation passes.
4. `Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-199`) builds `WebhookMetadata` with `shop: "victim-shop.myshopify.com"` and dispatches to the app handler, which now processes attacker-controlled data as if it belonged to the victim shop.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-28)
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
