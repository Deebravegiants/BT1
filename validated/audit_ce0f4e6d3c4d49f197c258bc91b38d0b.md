### Title
Webhook shop-domain header is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-verifiable signature over the raw request body only, while the `shop` (and `topic`) values that the library hands to the application's webhook handler are taken directly from unauthenticated HTTP headers. The verified bytes (body) and the trusted-but-unverified bytes (shop-domain header) are not bound together, breaking the invariant `shop_authenticated == shop_used_for_tenant_dispatch`.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`#shop` and `#topic` are pulled straight from HTTP headers, with no involvement in the signature computation: [2](#0-1) 

`Registry.process` validates the HMAC and, on success, forwards the header-derived `shop` (and `topic`) straight to the application handler as trusted `WebhookMetadata`, with no cross-check that the body actually pertains to that shop: [3](#0-2) 

`Utils::HmacValidator.validate` computes `compute_signature(verifiable_query.to_signable_string, secret)` and only compares that digest to the received HMAC — it never touches `shop`: [4](#0-3) 

Because the app's `api_secret_key` is the same for every shop that installs the app, any shop that legitimately installs the app receives genuinely-HMAC-valid `(raw_body, hmac)` pairs for its own webhook deliveries. Since `shop-domain` is excluded from the signed string, an attacker who controls one installed shop can capture one of its own valid webhook deliveries and replay the identical body/HMAC pair to the app's public webhook endpoint while substituting the `shop-domain` header value with a victim shop's domain. `Utils::HmacValidator.validate` still returns `true` (the body/HMAC pair is unchanged and valid), and `Registry.process` will dispatch the handler with `shop: <victim-domain>`, `topic`, and the attacker-supplied body as if it were data genuinely originating from the victim shop.

This breaks the intended identity binding: the shop whose secret validated the payload (implicitly, "some install of this app") is not equal to the shop value the application uses to determine which tenant's data the payload applies to (the header value, chosen by whoever sends the HTTP request).

### Impact Explanation
This is a cross-tenant access primitive: a malicious merchant/app-installer can make the host application process arbitrary attacker-controlled webhook payloads under a victim shop's identity (e.g., forged `orders/create`, `customers/data_request`, or even `app/uninstalled` topics attributed to a different, victim shop). Downstream applications built on this gem use `WebhookMetadata#shop` for tenant-scoped side effects (creating/updating records, revoking access, triggering GDPR flows, etc.), so this can lead to data corruption, unauthorized state changes, or information disclosure across tenants — a Critical, cross-tenant access impact.

### Likelihood Explanation
Likelihood is moderate-to-high for a determined attacker: the prerequisite is simply installing the target app once on an attacker-controlled shop (which is generally self-service for public/embedded Shopify apps) and capturing one legitimate webhook delivery, then replaying it directly at the app's public webhook endpoint (typically a fixed, discoverable URL) with a modified `shop-domain` header. No knowledge of `api_secret_key` or any privileged credential is required — this is reachable entirely by an unprivileged internet user/merchant.

### Recommendation
Bind the `shop` (and `topic`) values into the HMAC-signed material, or otherwise cryptographically tie them to the verified body — e.g., include `shop-domain` and `topic` header values in `to_signable_string`, or require the host application to independently verify that `shop` matches a session/installation record before trusting the webhook. Short term: update `ShopifyAPI::Webhooks::Request#to_signable_string` to incorporate the shop-domain (and topic) headers so any tampering invalidates the HMAC. Long term: document that `WebhookMetadata#shop` must never be trusted without corroboration against the recipient's own webhook subscription/shop registry.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker-shop.myshopify.com`, receiving a legitimate webhook, e.g.:
   ```
   POST /webhooks
   X-Shopify-Topic: orders/create
   X-Shopify-Hmac-Sha256: <valid-hmac-for-body>
   X-Shopify-Shop-Domain: attacker-shop.myshopify.com
   Body: {"id":1,...}
   ```
2. Attacker resends the identical body and `X-Shopify-Hmac-Sha256` value directly to the app's public webhook endpoint, only replacing the shop header:
   ```
   POST /webhooks
   X-Shopify-Topic: orders/create
   X-Shopify-Hmac-Sha256: <same-valid-hmac-for-same-body>
   X-Shopify-Shop-Domain: victim-shop.myshopify.com
   Body: {"id":1,...}
   ```
3. `Utils::HmacValidator.validate` recomputes the HMAC over `to_signable_string` (the unchanged raw body) and it matches, so `Registry.process` invokes the handler with `WebhookMetadata.new(topic: "orders/create", shop: "victim-shop.myshopify.com", body: ..., ...)`, causing the host application to act on `victim-shop.myshopify.com`'s tenant data using attacker-supplied content.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-23)
```ruby
      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

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
