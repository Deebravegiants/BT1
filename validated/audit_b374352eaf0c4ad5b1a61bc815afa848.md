## Title
Webhook `shop-domain`, `topic`, and `webhook-id` headers are trusted but excluded from HMAC verification, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` signs only the raw request body, while `ShopifyAPI::Webhooks::Registry.process` dispatches to handlers using the unsigned `shop`, `topic`, and `webhook_id` header values. An attacker who legitimately receives one valid `(body, hmac)` pair for their own shop can replay it with arbitrary `shop-domain`/`topic` header values that pass HMAC validation, letting them impersonate webhooks for a different, victim shop.

### Finding Description
`HmacValidator.validate` computes the HMAC over `verifiable_query.to_signable_string` and compares it to the `hmac` field: [1](#0-0) 

For webhooks, `to_signable_string` returns only the raw HTTP body — none of the Shopify-supplied headers are part of the signed content: [2](#0-1) 

`shop`, `topic`, and `webhook_id`, however, are read straight from these unsigned headers: [3](#0-2) 

`Registry.process` validates only the HMAC (which covers the body) and then dispatches the handler using the unsigned `shop`, `topic`, and `webhook_id`: [4](#0-3) 

This breaks the binding `hmac ⟹ (body, shop, topic, webhook_id)` that a webhook consumer implicitly relies on. The HMAC only proves "this body was produced with `api_secret_key`"; it says nothing about which shop or topic it belongs to. Because Shopify sends a distinct, validly-signed webhook to every merchant that installs the app (including an attacker's own store), an attacker who operates their own shop with the app installed can capture a legitimate `(raw_body, X-Shopify-Hmac-Sha256)` pair from their own webhook traffic, then resend it to the same endpoint with a forged `X-Shopify-Shop-Domain` (a victim shop) and/or a different `X-Shopify-Topic`/`X-Shopify-Webhook-Id`. `Utils::HmacValidator.validate` will still pass because it only checks the body against the shared secret, and `Registry.process` will invoke the app's handler with `WebhookMetadata` claiming the attacker-controlled shop/topic: [5](#0-4) 

Any host application that uses `WebhookMetadata#shop` to select the tenant record to read/write (the documented and expected usage pattern) will act on the wrong tenant's data using attacker-supplied body content, i.e., a shop-identity binding is broken by a field (`shop`) that is acted on but not covered by the HMAC.

### Impact Explanation
This allows cross-tenant access/manipulation: an unprivileged internet user who legitimately controls one shop's installation of the app can forge webhook deliveries that the app processes as belonging to a completely different, victim shop. Depending on the handler logic (mandatory webhooks like `app/uninstalled`, `customers/redact`, order/product webhooks, etc.), this can trigger data deletion, data corruption, or unauthorized state changes scoped to another merchant — a direct violation of tenant isolation, matching the "Critical - cross-tenant access" impact bucket.

### Likelihood Explanation
The attacker only needs to be a legitimate (even free/trial) installer of the app on their own shop to harvest one valid `(body, hmac)` pair — no access to `api_secret_key`, tokens, or privileged accounts is required. Replaying the captured request with modified headers to the app's public webhook endpoint is trivial (a raw HTTP request), since `Request.new` and `Registry.process` never re-validate that the headers used for dispatch correspond to what was signed.

### Recommendation
Include `shop-domain`, `topic`, and `webhook-id` (and `api-version`) in the HMAC-signable content, or otherwise cryptographically bind them to the signed body (e.g., derive an HMAC over a canonical string containing body + these headers, mirroring what `Oauth::AuthQuery#to_signable_string` does for OAuth callbacks). At minimum, document and warn implementers that `shop`, `topic`, and `webhook_id` are unauthenticated and must not be trusted for tenant selection without additional verification (e.g., cross-checking against a shop that the app already has an active session/install for).

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com` and receives a legitimate webhook, e.g.:
   ```
   POST /webhooks
   X-Shopify-Topic: orders/create
   X-Shopify-Hmac-Sha256: <valid-hmac-for-body>
   X-Shopify-Shop-Domain: attacker-shop.myshopify.com
   X-Shopify-Webhook-Id: aaaa-...
   Body: {"id": 1, ...attacker-controlled order payload...}
   ```
2. Attacker replays the identical body and `X-Shopify-Hmac-Sha256` value to the same app endpoint, but changes:
   ```
   X-Shopify-Shop-Domain: victim-shop.myshopify.com
   X-Shopify-Topic: app/uninstalled
   ```
3. `ShopifyAPI::Webhooks::Request.new` parses these headers; `Utils::HmacValidator.validate` succeeds because it only checks the (unchanged) body against `api_secret_key`.
4. `Registry.process` looks up the handler for `app/uninstalled` and invokes it with `shop: "victim-shop.myshopify.com"`, causing the app to execute uninstall/cleanup logic against the victim tenant using attacker-supplied body data — demonstrating cross-tenant webhook spoofing.

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
