### Title
Webhook Shop/Topic Identity Not Bound to HMAC Signature Enables Cross-Tenant Webhook Spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable content from the raw body alone, while the `shop`, `topic`, and `webhook_id` fields — read from unauthenticated HTTP headers — are trusted and forwarded to the registered webhook handler unmodified. This breaks the identity binding: `shop used by handler ≠ shop covered by HMAC`, allowing a party who captures one valid `(raw_body, hmac)` pair to relabel it to a different shop and have the app process it as belonging to that other tenant.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

But `shop`, `topic`, and `webhook_id` are read straight from HTTP headers with no cryptographic binding to the body or to each other: [2](#0-1) 

`Registry.process` validates the HMAC over the body via `Utils::HmacValidator.validate(request)`, and — once that passes — trusts `request.shop`, `request.topic`, and `request.webhook_id` to build the `WebhookMetadata` that's handed to the app's registered handler: [3](#0-2) 

`Utils::HmacValidator.validate` itself only checks the signature that `to_signable_string` returns, i.e., the body: [4](#0-3) 

Because `shop-domain`, `topic`, and `webhook-id` are not part of the signed payload, they are not bound to the HMAC that authenticates the request. Any party who legitimately receives (or captures) one valid `(raw_body, hmac)` pair — for example, from a webhook triggered on their own shop and delivered to the app's public webhook endpoint they control/observe — can resend the exact same body/HMAC to the app's webhook endpoint while substituting a different `X-Shopify-Shop-Domain` (or topic/webhook-id) header. The signature still validates (it only covers the body), and the handler processes the payload as if it belonged to the victim shop named in the spoofed header.

This is the same root-cause pattern as the referenced bug class: a value that is *acted upon* (here, the shop identity used for tenant attribution/session lookups inside the handler) is not covered by the authentication mechanism (HMAC) that is supposed to protect the request.

### Impact Explanation
This allows cross-tenant data confusion: webhook data legitimately generated for shop A can be attributed to shop B inside the app if the header is swapped, without needing shop B's secret or the app's `client_secret`/access token. Depending on how the app's registered `WebhookHandler` uses `WebhookMetadata#shop` (e.g., to look up per-shop sessions, write shop-scoped records, or trigger mandatory GDPR redact flows), this can lead to cross-tenant data corruption or disclosure — matching the "cross-tenant access" Critical impact category.

### Likelihood Explanation
Exploitation requires the attacker to first obtain one valid `(raw_body, hmac)` pair. This is plausible for an unprivileged attacker who is a legitimate merchant using the app: they can trigger a webhook event on their own shop (e.g., placing an order) and observe the exact request their own shop's webhook delivery generates to the app's endpoint (since it is a normal HTTP POST to a public URL they can monitor, e.g. by fronting the endpoint with a proxy they control before forwarding to the app). No access to the app's `client_secret` or any other shop's credentials is required.

### Recommendation
Bind `shop`, `topic`, and `webhook_id` into the HMAC-signed content (or otherwise independently verify them, e.g. by validating the shop against an expected/registered shop before dispatching to handlers), rather than trusting header values that fall outside the HMAC's coverage. At minimum, `to_signable_string` should incorporate the shop-domain header so that a captured request cannot be relabeled to a different tenant while remaining HMAC-valid.

### Proof of Concept
1. Attacker registers the app on their own shop `attacker.myshopify.com` and triggers a webhook (e.g., `orders/create`) that Shopify delivers to the app's public webhook endpoint.
2. Attacker captures the exact `raw_body` and `X-Shopify-Hmac-Sha256` header from that delivery (e.g., by fronting their own delivery URL with infrastructure they control, or via any request logging they have access to for their own shop's traffic).
3. Attacker resends the identical `raw_body` and `hmac` header to the app's webhook endpoint, but sets `X-Shopify-Shop-Domain: victim.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only checks the HMAC over `raw_body` — unaffected by the header change.
5. The handler is invoked with `WebhookMetadata.new(shop: "victim.myshopify.com", body: <attacker's body>, ...)`, causing the app to process attacker-controlled data under the victim shop's identity.

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
