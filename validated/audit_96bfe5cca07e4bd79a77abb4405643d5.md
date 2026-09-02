### Title
Webhook shop-domain header is not covered by the HMAC, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating an HMAC computed over the raw request body, while the `shop` (and `topic`/`api_version`/`webhook_id`) values used to route and identify the tenant are taken from unauthenticated HTTP headers that are never included in the signed payload.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

but `shop`, `topic`, `api_version`, and `webhook_id` are pulled directly from HTTP headers with no cryptographic binding to the body or the HMAC: [2](#0-1) 

`Registry.process` validates only the body/HMAC pair, then dispatches to the handler using the unauthenticated `request.shop` field: [3](#0-2) 

The identity binding that should hold is: `shop asserted to the handler == shop the HMAC actually authenticates`. Because the HMAC only covers `@raw_body`, that equality does not hold — the `shopify-shop-domain` header (and topic/webhook-id/api-version) can be freely substituted without invalidating the signature, as long as the body bytes are unchanged.

### Impact Explanation
A merchant who installs the app on their own shop legitimately receives webhooks with valid `hmac-sha256` values (computed with the app's real `api_secret_key`) for their own shop's payloads. Because the shop header is excluded from the signed content, that same attacker can replay the identical raw body/HMAC pair to the app's public webhook endpoint while substituting the `shopify-shop-domain` header for a victim shop. `Registry.process` will accept the HMAC as valid and hand the handler a `WebhookMetadata` claiming the data belongs to the victim shop: [4](#0-3) 

Any app logic keyed on `data.shop` (e.g., updating shop records, triggering uninstall/reinstall side effects, billing state, or app-specific data per tenant) can be manipulated into acting on the wrong tenant — a cross-tenant integrity/access issue.

### Likelihood Explanation
Exploitation requires only an unprivileged internet user to (a) install the target app on their own shop to obtain one legitimately-signed webhook body/HMAC pair, and (b) send that same body/HMAC to the app's public webhook endpoint with a forged `shopify-shop-domain` header pointing at any other shop. No access token, `api_secret_key`, or privileged access is needed — this is directly reachable through the gem's own validation logic in `HmacValidator`/`Registry#process`.

### Recommendation
Include `shop`, `topic`, `webhook_id`, and `api_version` in the signable content used for HMAC validation (or otherwise cryptographically bind them, e.g. via a MAC over `"#{shop}|#{topic}|#{webhook_id}|#{raw_body}"`), so that tampering with any of these header-derived identity fields invalidates the signature. At minimum, `Registry.process` should re-derive/validate `shop` from a source Shopify guarantees is bound to the signed payload rather than trusting the header verbatim.

### Proof of Concept
1. Install the target app on attacker-controlled shop `evil.myshopify.com`; Shopify delivers a webhook to the app's endpoint with headers `shopify-shop-domain: evil.myshopify.com`, `shopify-hmac-sha256: <valid HMAC of body B>`, body `B`.
2. Attacker captures this request (own traffic, no privileged access needed).
3. Attacker resends the same body `B` and the same `shopify-hmac-sha256` value to the app's webhook endpoint, but sets `shopify-shop-domain: victim.myshopify.com`.
4. `Utils::HmacValidator.validate(request)` in `Registry.process` succeeds because it only recomputes the HMAC over `@raw_body` (`to_signable_string`), which is unchanged.
5. The handler executes with `WebhookMetadata.new(topic: ..., shop: "victim.myshopify.com", body: parsed_body, ...)`, causing the app to process attacker-supplied data as if it originated from `victim.myshopify.com`. [3](#0-2) [5](#0-4)

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-38)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end

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
