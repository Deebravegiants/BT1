### Title
Webhook `shop` identity is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, while the `shop` (and `topic`, `webhook-id`, `api-version`) values used by `ShopifyAPI::Webhooks::Registry.process` to build `WebhookMetadata` are taken directly from unauthenticated HTTP headers that are never part of the HMAC-signed content. This breaks the identity binding `hmac-authenticated-content == data trusted for tenant identification`.

### Finding Description
`ShopifyAPI::Utils::HmacValidator.validate` computes and compares an HMAC over `verifiable_query.to_signable_string`: [1](#0-0) 

For webhook requests, `to_signable_string` is defined to return only `@raw_body`: [2](#0-1) 

But `shop`, `topic`, `api_version`, and `webhook_id` are all pulled from HTTP headers that are completely outside the signed payload: [3](#0-2) 

`Registry.process` validates the HMAC (over the body only), then constructs `WebhookMetadata` using the unauthenticated `request.shop` header value and hands it to the app's registered handler as the tenant identity for the event: [4](#0-3) 

Because the app's `api_secret_key` is shared across every shop that installs the app (not per-tenant), any unprivileged internet user can install the app on their own store, trigger a webhook, and legitimately receive a `(raw_body, valid hmac)` pair signed with the app's shared secret. Since the signature never covers the `x-shopify-shop-domain` (or `shopify-shop-domain`) header, that attacker can replay the same raw body and valid HMAC to the app's webhook endpoint while substituting an arbitrary `shop-domain` header value. `HmacValidator.validate` will still pass (it only checks the body-derived signature), and `Registry.process` will dispatch the event to the handler tagged with the attacker-chosen `shop`, impersonating any other tenant of the app.

### Impact Explanation
This is a cross-tenant identity confusion: the field the host application relies on to scope webhook data to a specific merchant (`shop`) is not bound to the cryptographic proof of authenticity. A malicious app-installer can cause the library to report forged/attacker-controlled event data as belonging to a victim shop, letting them inject fabricated events into another tenant's processing pipeline (e.g., fake `orders/create`, `app/uninstalled`, or GDPR topics) without ever needing the victim's credentials.

### Likelihood Explanation
Any user can install a Shopify app that uses this gem on their own store (no special privileges required), receive a genuinely-signed webhook, and then replay it with a modified `shop-domain` header against the same public webhook endpoint. No secret material beyond a normal, self-service app install is needed, and the header is trivial to forge since it is not part of the signed content.

### Recommendation
Include the trusted identity fields (`shop-domain`, and ideally `topic`/`webhook-id`) in the HMAC-signed payload used by `to_signable_string`, or otherwise cryptographically bind the shop-domain header to the signature validation (e.g., validate that the `shop` reported matches a shop actually authorized/installed for this secret, or sign header+body together) before trusting `request.shop` in `WebhookMetadata`.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com`, triggering any webhook topic handled by the app; captures the raw POST body `B` and its valid `x-shopify-hmac-sha256` header `H` (signed with the app's shared `api_secret_key`).
2. Attacker sends a new POST to the app's webhook endpoint with the same body `B` and header `H`, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `HmacValidator.validate` in `lib/shopify_api/utils/hmac_validator.rb` recomputes the signature over `B` only and it matches `H`, so validation succeeds.
4. `Registry.process` in `lib/shopify_api/webhooks/registry.rb` dispatches the handler with `WebhookMetadata.shop == "victim-shop.myshopify.com"`, even though the request never proved any relationship to that shop.

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
