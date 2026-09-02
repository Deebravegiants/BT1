### Title
Webhook `shop-domain` header is trusted but not covered by the HMAC signature, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb](lib/shopify_api/webhooks/request.rb))

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC of the raw request body, then forwards the `shop` value taken from the `X-Shopify-Shop-Domain` (or `shopify-shop-domain`) HTTP header — a field that is never included in the HMAC-signed content — to the app's registered handler as the tenant identifier.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , and `#shop` is read directly and unauthenticated from HTTP headers [2](#0-1) . `Utils::HmacValidator.validate` only checks that the HMAC over `to_signable_string` (the body) matches, using the app's shared `api_secret_key` [3](#0-2) . `Registry.process` performs exactly this body-only check and then immediately trusts `request.shop` to build the `WebhookMetadata` passed to the app's handler [4](#0-3) .

This breaks the intended binding: `shop-domain (header, unauthenticated) == shop (tenant that produced the HMAC-signed body)`. Because the `api_secret_key` is shared across all shops installed on the app (it is not per-shop), any merchant that has the app installed on their own shop is a legitimate holder of valid `(raw_body, hmac)` pairs for webhooks addressed to them. That merchant can capture one of their own genuine webhook deliveries and replay the identical body/HMAC to the app's public webhook endpoint while substituting a different `X-Shopify-Shop-Domain` value belonging to another tenant. `Utils::HmacValidator.validate` will still succeed (it never looks at the domain header), and `Registry.process` will hand the handler a `WebhookMetadata` claiming the payload belongs to the victim shop [5](#0-4) .

### Impact Explanation
Any app built on this gem that uses `WebhookMetadata#shop` to key off tenant data (look up the shop's session, credit inventory, update order status, disable/enable features, write audit logs, etc.) can be made to apply attacker-supplied webhook content under another merchant's tenant identity. This is a cross-tenant data-integrity/confidentiality break reachable by an ordinary, unprivileged merchant who has installed the app on their own store — no access token, `client_secret`, or other privileged credential is required, satisfying the Critical "cross-tenant access" bar.

### Likelihood Explanation
Likelihood is high for any installed app: the attacker only needs to be a legitimate but unprivileged merchant of the target app, capture one webhook delivered to their own store (trivial, since it is delivered to their own endpoint/logs), and replay it with a modified header to the same public webhook endpoint. No secret material beyond what's already visible to any merchant is needed.

### Recommendation
Bind the shop identity into the signed material, or otherwise cryptographically verify the `shop-domain` header against the caller's registered/installed shop before trusting it (e.g., include the header in the HMAC input, or cross-check `request.shop` against a shop that the app has a valid, previously stored session/access-token for) inside `ShopifyAPI::Webhooks::Registry.process` before dispatching to the handler.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` (normal, unprivileged merchant flow).
2. Shopify delivers a legitimate webhook to the app's endpoint with headers `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`, `X-Shopify-Hmac-Sha256: <valid hmac of raw body>`, and some `raw_body`.
3. Attacker captures this `(raw_body, hmac)` pair (they can trivially do so, e.g. by proxying their own webhook endpoint).
4. Attacker sends a new HTTP request directly to the app's public webhook endpoint with the same `raw_body` and `X-Shopify-Hmac-Sha256`, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
5. `Utils::HmacValidator.validate` passes because it only checks the body/HMAC pair [6](#0-5) .
6. `Registry.process` invokes the app's handler with `WebhookMetadata.new(..., shop: "victim-shop.myshopify.com", ...)`, causing the app to process attacker-controlled data under the victim's tenant context [7](#0-6) .

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
