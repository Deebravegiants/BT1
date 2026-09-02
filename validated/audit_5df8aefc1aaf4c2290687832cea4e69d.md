## Finding

### Title
Webhook `shop-domain` header is not covered by the HMAC signature, allowing cross-tenant webhook forgery - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable string from the raw body only, while the `shop` (and `topic`) values used by the application are read from separate, unsigned HTTP headers. Since Shopify apps use one shared `api_secret_key` across every shop that installs them, any user who can trigger a genuine webhook for their own (attacker-controlled) shop can capture a valid `(raw_body, hmac)` pair and replay it to the app's webhook endpoint with the `shop-domain` header rewritten to point at a victim shop, producing a request that passes HMAC validation while being falsely attributed to another tenant.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop`, `topic`, and other identifying fields are read straight from attacker-suppliable headers and are not part of the signed content: [2](#0-1) 

`Utils::HmacValidator.validate` verifies only `verifiable_query.to_signable_string` (the body) against the secret — it never binds the `shop` header into the signature: [3](#0-2) 

`Registry.process` treats a passing HMAC check as sufficient proof of authenticity and forwards `request.shop` straight into the handler payload without any additional binding to the signed body: [4](#0-3) 

The broken identity equality is: `shop the HMAC authenticates` (i.e., "this app-secret-holder produced this body") ≠ `shop attributed to the event downstream` (`request.shop`, taken from an unauthenticated header). Because the `api_secret_key` is shared by the app across all installing shops (not per-shop), any installer of the app is capable of generating a validly-signed `(body, hmac)` pair for their own shop, then re-submitting it with a different `shop-domain` header value.

### Impact Explanation
A malicious merchant who has installed the target app can forge webhook deliveries that the app will process as if they originated from a different, victim shop, while HMAC validation still succeeds. Since `WebhookMetadata`/handler logic typically keys per-tenant state, GDPR actions, or business logic off of `data.shop`, this enables cross-tenant data injection/attribution — e.g., causing the app to apply attacker-controlled order/customer data to another merchant's tenant records, or triggering mandatory compliance webhooks (`shop/redact`, `customers/redact`, `customers/data_request`) against a victim shop. This matches the Critical "cross-tenant access" impact class.

### Likelihood Explanation
Exploitation requires only that the attacker be a legitimate (even low-privilege) installer of the app — an "unprivileged" party relative to other tenants — capable of triggering one webhook delivery for their own shop (trivial, e.g. by placing a test order) to obtain a valid `(raw_body, hmac)` pair, and the ability to POST directly to the app's public webhook endpoint with a modified `shop-domain` header. No access to the app's `client_secret` or another merchant's credentials is needed.

### Recommendation
Bind the shop (and ideally topic) into the value that is HMAC-verified, or otherwise require the caller to separately confirm that the `shop-domain` header matches a shop known to have that webhook subscription/topic registered (e.g., cross-check against the shop’s stored session/webhook registration before invoking the handler), rather than trusting the unauthenticated header once the shared-secret HMAC over the body passes.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker-shop.myshopify.com`.
2. Attacker triggers a real webhook (e.g. `orders/create`) and captures the raw POST body and the `x-shopify-hmac-sha256` header Shopify sent — this HMAC is valid because it is computed with the app's single shared `api_secret_key` over the body only.
3. Attacker resends this exact `(raw_body, hmac)` pair directly to the app's public webhook endpoint, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks the body/HMAC pairing: [5](#0-4) 
5. The registered handler is invoked with `WebhookMetadata` carrying `shop: "victim-shop.myshopify.com"` and attacker-controlled body content, even though the event never originated from that shop.

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
