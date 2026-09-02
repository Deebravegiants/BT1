This confirms the documented API contract: the gem explicitly tells host apps that `data.shop` from `ShopifyAPI::Webhooks::Registry.process` is "The shop domain of the webhook" and shows a canonical usage pattern (`perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)`), i.e., host apps are expected to trust `data.shop` as an authenticated attribute of the verified webhook. This confirms the identity-binding break is in the gem's own documented contract, not a misuse by the host app.

### Title
Webhook shop-domain (and topic/webhook-id/api-version) headers are not covered by HMAC verification, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` verifies a webhook's authenticity solely via an HMAC over the raw request body. The `shop-domain`, `topic`, `webhook-id`, and `api-version` HTTP headers—despite being the values the gem hands to the app's handler as trusted, shop-attributed metadata—are never included in the signed content, so their integrity is not protected by the HMAC check at all.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 
while `shop`, `topic`, `api_version`, and `webhook_id` are read directly from HTTP headers with no cryptographic binding to the body or the HMAC: [2](#0-1) 

`Utils::HmacValidator.validate` computes the signature only over `verifiable_query.to_signable_string` (the body) and compares it to the `hmac-sha256` header: [3](#0-2) 

`Registry.process` uses the validated body's HMAC status to gate processing, then constructs `WebhookMetadata` directly from the *unauthenticated* headers, including `shop: request.shop`: [4](#0-3) 

The binding that is broken: `shop attributed to the webhook payload (request.shop, HMAC-unauthenticated header) == shop that actually produced/authorized the HMAC-signed body`. Because only the body contributes to the signature, any request carrying a `(body, hmac)` pair that is valid for the app's secret—regardless of which shop actually generated it—will pass `HmacValidator.validate` even if the `x-shopify-shop-domain` (and `topic`/`webhook-id`/`api-version`) headers are swapped for an arbitrary value.

An attacker who has legitimately received (or otherwise obtained) one valid `(body, hmac)` pair for the app—e.g., by installing the target app on their own store and capturing a genuine webhook delivery for it—can replay that exact body+hmac to the app's public webhook endpoint while substituting the `x-shopify-shop-domain` header with a victim shop's domain (and/or a different `topic`/`webhook-id`). `Registry.process` will pass HMAC verification (body unchanged) and invoke the registered handler with `WebhookMetadata` falsely attributing the event to the victim shop.

### Impact Explanation
This is a cross-tenant identity-binding failure that directly violates the app's trust boundary between shops. Per the gem's own documented contract (`docs/usage/webhooks.md`), `data.shop` is meant to be a trusted, shop-scoped identifier host apps use to route/store webhook data per tenant (e.g., `perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)`). Since this attribution is not authenticated, an attacker can inject arbitrary Shopify-shaped payloads under another tenant's identity into the app's per-shop processing pipeline—cross-tenant data poisoning/confusion without needing the app's `api_secret_key`, an access token, or any privileged account. This matches the "Critical - cross-tenant access" category: the confidentiality/integrity boundary between shop tenants inside the app is broken via the gem's webhook verification primitive.

### Likelihood Explanation
Exploitability requires only: (1) the app's public webhook HTTP endpoint (always publicly reachable per design), and (2) one genuine `(body, hmac)` sample for the app—trivially obtainable by installing the target app (many apps offer free trials/dev stores) and receiving any real webhook once. No secret material, tokens, or social engineering is required; the header manipulation is a simple unauthenticated HTTP replay.

### Recommendation
Include the security-relevant headers (`shop-domain`, `topic`, `webhook-id`, `api-version`) in the HMAC-signed content that `to_signable_string` produces (or otherwise cryptographically bind them, e.g., by having `HmacValidator` verify a canonicalized string of headers + body), so that any tampering with these headers invalidates the signature. At minimum, `shop` must be bound, since it is the tenant-identity field the app relies on.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker.myshopify.com` and triggers/receives a legitimate `orders/create` webhook delivery, capturing the raw body `B` and its valid `x-shopify-hmac-sha256` header value `H` (computed by Shopify over `B` using the app's secret).
2. Attacker sends a POST to the app's webhook endpoint with the same body `B` and header `x-shopify-hmac-sha256: H`, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses the tampered `shop-domain` header: [5](#0-4) 
4. `Utils::HmacValidator.validate` recomputes the HMAC over `B` only and it matches `H` (body untouched), so verification succeeds: [6](#0-5) 
5. `Registry.process` invokes the registered handler with `WebhookMetadata.new(... shop: "victim-shop.myshopify.com", body: parsed_body(B) ...)`: [4](#0-3) 
6. The host app, trusting `data.shop` per the documented contract, processes/stores the attacker-controlled order data as belonging to the victim shop.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery).returns(T::Boolean) }
        def validate(verifiable_query)
          return false unless verifiable_query.hmac

          result = validate_signature(verifiable_query, Context.api_secret_key)
          if result || Context.old_api_secret_key.nil? || T.must(Context.old_api_secret_key).empty?
            result
          else
            validate_signature(verifiable_query, T.must(Context.old_api_secret_key))
          end
        end

        private

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
