### Title
Webhook Shop Domain Spoofing via Cross-Tenant HMAC Replay — Shop Header Not Covered by HMAC Signature ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable string from the raw body only, while the `shop-domain`, `topic`, `webhook-id`, and `api-version` headers are never included in that signature. `Registry.process` validates only the HMAC-over-body and then forwards the *unauthenticated* `shop` header value straight to the app's webhook handler. Any actor who has ever legitimately received a genuine webhook (with a valid `hmac-sha256` header for a given body) for their own shop can replay that identical body+HMAC pair while substituting a different `shop-domain` header, and the gem will accept it as authentic and attribute the payload to the spoofed shop.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`HmacValidator.validate` computes the HMAC purely over `verifiable_query.to_signable_string` (i.e., the body) and compares it to the received `hmac`: [2](#0-1) 

`Registry.process` performs this HMAC check and then, on success, immediately trusts `request.shop` (parsed straight from the unauthenticated `shopify-shop-domain`/`x-shopify-shop-domain` header) to build the `WebhookMetadata` object passed to the app's handler: [3](#0-2) 

The identity binding that should hold is: **`shop` field used by the handler == `shop` field cryptographically bound to the HMAC-verified bytes**. In this code, that equality never holds — the HMAC only certifies the *body*, not the *shop* header that accompanies it. This is functionally the same class of bug as the reported analog: "a field acted on but not covered by the HMAC."

### Impact Explanation
An unprivileged attacker who merely installs the app on their own shop (or subscribes to any webhook topic legitimately) will receive real webhooks from Shopify with valid `hmac-sha256` values for their own body content. They can capture such a `(raw_body, hmac)` pair and replay it to the app's public webhook endpoint with the `x-shopify-shop-domain` header rewritten to point at a victim tenant's domain. Because `HmacValidator.validate` and `Registry.process` never bind `shop` to the signed bytes, the request passes validation, and the app's webhook handler receives `WebhookMetadata` claiming the data originated from the victim shop — while it actually came from the attacker. Any host application that uses `data.shop` to key data storage, trigger shop-scoped side effects, or authorize processing (a documented, expected usage pattern of this gem's webhook API) will attribute attacker-controlled payload/body content to the wrong tenant, resulting in cross-tenant data corruption/injection.

### Likelihood Explanation
Likelihood is high: the attacker requires no credentials, no access token, and no `api_secret_key`Ac just the ability to install the app on any shop (a normal unprivileged merchant action) and to POST to the app's public webhook receiver endpoint, which by design is unauthenticated apart from this gem's HMAC check.

### Recommendation
Include the `shop-domain` (and ideally `topic`/`webhook-id`) header values in the signable string used for HMAC computation, or otherwise cryptographically bind the shop identity to the verified payload before it is handed to the registered handler. At minimum, `Request#to_signable_string` should incorporate the shop header so that a body+HMAC pair valid for one shop cannot be replayed under a different shop's identity.

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com` and receives a legitimate webhook, e.g. body `{"id":1}` with header `x-shopify-hmac-sha256: <valid-hmac-for-that-body>` and `x-shopify-shop-domain: attacker-shop.myshopify.com`.
2. Attacker POSTs the exact same raw body and `hmac-sha256` header to the app's webhook endpoint, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks the HMAC against `raw_body` (see `Request#to_signable_string`, `lib/shopify_api/webhooks/request.rb:35-38`, and `HmacValidator.validate_signature`, `lib/shopify_api/utils/hmac_validator.rb:26-31`).
4. `Registry.process` calls the app's handler with `WebhookMetadata.new(... shop: request.shop ...)` where `request.shop` == `"victim-shop.myshopify.com"` (`lib/shopify_api/webhooks/registry.rb:198-199`), even though the payload originated from the attacker's shop.

### Citations

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
