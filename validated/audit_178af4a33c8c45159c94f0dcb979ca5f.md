### Title
Webhook `shop`/`topic`/`webhook_id` headers are trusted without being covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` is documented to "verify the request did indeed come from Shopify" before invoking the app's handler with the webhook's `shop`, `topic`, `webhook_id`, and `api_version`. In reality, the HMAC only authenticates the raw request body; the identity-bearing headers are read from unauthenticated input and are never bound to the signature.

### Finding Description
`ShopifyAPI::Webhooks::Request` exposes `shop`, `topic`, `webhook_id`, and `api_version` purely as header lookups: [1](#0-0) 

but `to_signable_string`, the value that is actually HMAC-verified, only returns the raw body: [2](#0-1) 

`HmacValidator.validate` computes the signature strictly over `to_signable_string` (i.e., the body) and compares it to the `hmac` header: [3](#0-2) 

`Registry.process` calls this validator and then, on success, unconditionally trusts `request.shop`, `request.topic`, and `request.webhook_id` when constructing the data passed to the app's handler: [4](#0-3) 

The equality the code implicitly assumes is:
`HMAC(secret, raw_body) == received_hmac` ⟹ `(shop, topic, webhook_id, api_version)` are authentic.

What is actually proven is only:
`HMAC(secret, raw_body) == received_hmac` ⟹ `raw_body` is authentic (was signed with this app's `client_secret` at some point).

Because the `client_secret` is shared across every shop that has installed the app, any merchant who installs the app can trigger a real webhook delivery to their own endpoint for their own shop (e.g., by placing an order), capturing a legitimately-signed `(raw_body, hmac)` pair. They can then replay that exact body/HMAC to the app's public webhook endpoint while substituting the `shop-domain`, `topic`, and `webhook-id` headers with a different shop's domain and topic. `HmacValidator.validate` will still pass, since it only checks the body, and `Registry.process` will hand the handler a `WebhookMetadata` claiming the data originated from the victim shop.

### Impact Explanation
This breaks the tenant-identity binding the library's documentation promises ("This will verify the request did indeed come from Shopify"). A host application that relies on `data.shop` from `WebhookMetadata` to route/attribute the payload per-tenant (as the gem's own docs example demonstrates: `perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)`) can be made to process attacker-supplied data under a different shop's identity — a cross-tenant confusion where actions are attributed to, or performed against, a shop the attacker doesn't own.

### Likelihood Explanation
Any unprivileged actor who can install the target app on their own store (a normal, unprivileged action for any Shopify merchant) can obtain a validly-signed body/HMAC pair and replay it against the shared public webhook endpoint with forged shop/topic/webhook-id headers. No access token, `api_secret_key`, or privileged account is required — only the ability to trigger an event on your own installed instance and re-POST it with different headers.

### Recommendation
Bind the identity-bearing headers into the signed payload before verification (e.g., include `shop-domain`, `topic`, and `webhook-id` in the string that is HMAC'd, or independently verify `shop` against the session/shop the app expects for that webhook path), rather than trusting header values that fall entirely outside the HMAC's coverage.

### Proof of Concept
1. Install the target Shopify app on attacker-controlled shop `attacker.myshopify.com`.
2. Trigger a real webhook (e.g., `orders/create`) so Shopify sends a POST to the app's webhook URL with a legitimately-computed `x-shopify-hmac-sha256` for the raw body.
3. Capture `raw_body` and its valid `hmac` value.
4. Re-POST the same `raw_body` (and same `hmac`) to the app's webhook endpoint, but replace the `x-shopify-shop-domain` header with `victim.myshopify.com` and/or the `x-shopify-topic`/`x-shopify-webhook-id` headers with different values.
5. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate`, which passes because it only checks the body against the shared secret: [5](#0-4) 
6. The registered handler receives `WebhookMetadata` with `shop: "victim.myshopify.com"` even though the payload was actually produced and signed against the attacker's own shop.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-38)
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
