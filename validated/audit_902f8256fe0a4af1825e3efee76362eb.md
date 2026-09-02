Based on my analysis, I've confirmed the vulnerability with exact code evidence.

### Title
Webhook `shop-domain` and `topic` identity fields are not covered by HMAC verification, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` reads the tenant-identifying `shop-domain` and `topic` values from HTTP headers, but `to_signable_string`, which is what `HmacValidator` verifies, only returns the raw body. This breaks the identity binding: `shop` (used to route/attribute a processed webhook) is never checked against `hmac`.

### Finding Description
`ShopifyAPI::Utils::HmacValidator.validate` computes the expected signature over `verifiable_query.to_signable_string` and compares it to the `hmac` claim using `OpenSSL.secure_compare`: [1](#0-0) 

For webhooks, `Request#to_signable_string` returns only the raw body: [2](#0-1) 

But `Request#shop`, `Request#topic`, `Request#webhook_id`, and `Request#api_version` are all read directly from unauthenticated headers, with no cryptographic binding to the HMAC-verified body: [3](#0-2) 

`Registry.process` validates only the HMAC-over-body, then forwards the *unverified* `request.shop`, `request.topic`, and `request.webhook_id` straight to the app's handler as the tenant/topic identity for the payload: [4](#0-3) 

The binding that should hold is: `hmac == HMAC(body ‖ shop ‖ topic)`, but the actual implementation only enforces `hmac == HMAC(body)`. `shop` and `topic` are therefore attacker-controllable bytes that pass "verification" unchanged.

**Exploit path**: An unprivileged attacker who legitimately installs the target app on their own store (or otherwise captures one genuine `(raw_body, hmac)` pair delivered by Shopify — e.g. from their own shop's webhook traffic) possesses a valid signature for that body. Because the header fields are outside the signed content, the attacker can replay that exact body/HMAC pair to the app's public webhook endpoint while substituting the `X-Shopify-Shop-Domain` header with a victim shop's domain (and/or a different `X-Shopify-Topic`). `HmacValidator.validate` still returns `true` (body/HMAC pair unchanged), and `Registry.process` will hand the attacker's payload to the handler tagged as belonging to the victim shop and/or a different topic than the one actually signed for.

### Impact Explanation
This crosses a tenant boundary: a webhook payload originating from the attacker's own shop can be attributed to a victim shop (or a different topic) inside the host application, since the gem provides no guarantee that `shop`/`topic` correspond to what Shopify actually signed. Depending on how the host app persists/acts on webhook data keyed by `WebhookMetadata#shop` (e.g., updating shop-scoped records, triggering shop-scoped side effects), this can lead to cross-tenant data corruption/injection using data the attacker fully controls (their own shop's webhook body) while impersonating another tenant's identity. This matches the Critical "cross-tenant access" category under the given impact criteria.

### Likelihood Explanation
Moderate: it requires the attacker to possess at least one genuine `(body, hmac)` pair, which merely requires installing the app on any account they control (or otherwise triggering webhook delivery for a shop they own) — no compromise of `api_secret_key` or an access token is needed. The webhook endpoint is by design internet-reachable and unauthenticated aside from HMAC. This mirrors the reasoning in the referenced report: the check verifies "bytes" (here, body bytes) that are disjoint from the identity fields (`shop`, `topic`) actually acted upon.

### Recommendation
Extend the webhook HMAC verification (or add a secondary check) to bind the `shop-domain` and `topic` header values into the signed content, or otherwise cryptographically/contextually validate them (e.g., require the caller to pass the expected shop/topic and compare against `request.shop`/`request.topic`, rejecting mismatches) before invoking the handler. At minimum, document prominently that `request.shop` and `request.topic` are unauthenticated and that host applications must independently validate them against known/expected values before trusting them.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker-shop.myshopify.com` and triggers any webhook topic (e.g. `orders/create`), capturing the genuine request Shopify sends: raw body `B` and header `X-Shopify-Hmac-Sha256: H` (valid HMAC of `B` under the app's `api_secret_key`, which the attacker never learns).
2. Attacker sends a forged HTTP POST to the app's webhook endpoint with:
   - Body: `B` (unchanged)
   - `X-Shopify-Hmac-Sha256: H` (unchanged)
   - `X-Shopify-Shop-Domain: victim-shop.myshopify.com` (forged)
   - `X-Shopify-Topic: <any topic the app has a handler for>` (optionally forged)
3. `ShopifyAPI::Webhooks::Request.new` parses these headers; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which computes `HMAC(B)` and compares to `H` — this passes because only `B` is signed. [4](#0-3) 
4. The handler receives `WebhookMetadata.new(topic: <forged topic>, shop: "victim-shop.myshopify.com", body: parsed(B), ...)`, processing attacker-controlled content under the victim's tenant identity.

### Citations

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
