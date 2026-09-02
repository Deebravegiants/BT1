## Title
Webhook `shop` identity is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes and validates the webhook HMAC over the raw request body only, while the `shop-domain` header — which the registry hands to app code as the authoritative tenant identifier — is never included in the signed material. An attacker who can obtain any single validly-signed webhook body (e.g., by installing the target's public app on their own store and capturing a real Shopify-signed webhook delivery) can replay that exact body/HMAC pair to the app's webhook endpoint while swapping the `X-Shopify-Shop-Domain` header to a victim shop's domain. `HmacValidator.validate` still returns `true` because the header is outside the signed string, so the handler receives `WebhookMetadata` attributing the (attacker-controlled) event body to the victim shop.

### Finding Description
The equality this breaks is: `shop that Shopify cryptographically bound to the delivery` == `shop that the handler is told owns the delivery`.

- `ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

- `shop` is read from the `shopify-shop-domain`/`x-shopify-shop-domain` header, which is not part of the signed string: [2](#0-1) 

- `HmacValidator.validate` computes/compares HMAC only against `verifiable_query.to_signable_string` (i.e., the body), never the shop header: [3](#0-2) 

- `Registry.process` validates HMAC, then immediately trusts `request.shop` when constructing the metadata passed to the app's handler, without any additional binding to the signed body: [4](#0-3) 

Because the shop header is excluded from the signable string, any body+HMAC pair that is valid for shop A remains valid (per `HmacValidator.validate`) when replayed with the `shop-domain` header rewritten to shop B. The gem gives the host application no signal that the shop attribution is unauthenticated — `WebhookMetadata#shop` looks just as trustworthy as the verified body.

### Impact Explanation
This is a cross-tenant identity confusion: an attacker can cause the app to process a webhook event as if it belongs to an arbitrary victim shop, using only a signed payload they legitimately obtained for their own tenant (e.g., by installing a public app on their own store, or reusing any previously observed valid webhook). Depending on how the host app's handler uses `WebhookMetadata#shop`/`WebhookMetadata#body` (e.g., `app/uninstalled` to wipe victim data, `shop/update`, `customers/redact`, order/product mutations keyed off the shop), this can lead to unauthorized cross-tenant state changes or data exposure — matching the "cross-tenant access" impact category.

### Likelihood Explanation
Exploitability only requires the attacker to possess one legitimately-signed webhook body for any shop (trivial for a public app: install it on an attacker-controlled store and capture a real delivery), plus the ability to send an HTTP POST with modified headers to the app's public webhook endpoint. No `api_secret_key`, access token, or other secret is needed, since the header manipulated is outside the HMAC's coverage entirely.

### Recommendation
Bind the `shop-domain` (and ideally `topic`/`webhook-id`) into the value that is authenticated, or otherwise ensure the host application cannot rely on `WebhookMetadata#shop` as trusted without independently verifying that the shop is one the app has an active installation/session for and that a delivery for that (shop, webhook-id) pair hasn't already been consumed. At minimum, the docs/`WebhookMetadata` API should make explicit that `shop` is unauthenticated header data, and the registry should cross-check `shop`/`webhook-id` against known installed shops before dispatching to handlers.

### Proof of Concept
1. Install the target public app on an attacker-owned development store; trigger a webhook subscription event (e.g. `customers/create`) and capture the raw POST: headers `x-shopify-hmac-sha256`, `x-shopify-shop-domain: attacker-shop.myshopify.com`, and the raw JSON body.
2. Resubmit the identical raw body and `x-shopify-hmac-sha256` value to the app's webhook endpoint, but replace `x-shopify-shop-domain` with `victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which validates successfully because it only hashes `@raw_body` — the header swap has no effect on the check: [4](#0-3) 
4. The handler receives `WebhookMetadata` with `shop: "victim-shop.myshopify.com"` and the attacker-supplied body, believing the event legitimately originated from the victim's store.

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
