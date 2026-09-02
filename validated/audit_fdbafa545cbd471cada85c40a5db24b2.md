### Title
Webhook `shop-domain` (and `topic`/`api-version`/`webhook-id`) headers are not covered by the HMAC signature, enabling cross-tenant webhook replay - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw request body, while the `shop` (and `topic`) values that the app uses to identify *which tenant* the webhook belongs to are taken from unauthenticated HTTP headers that are never included in the signed payload. Anyone who can obtain one validly-signed webhook body (e.g., a merchant who installed the app and receives webhooks for their own shop) can replay that exact body to the app's webhook endpoint with a different `x-shopify-shop-domain` (and/or `x-shopify-topic`) header. The HMAC check still passes because it only verifies the body bytes, so the app's handler will process the payload as if it belongs to a different shop.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

The `shop`, `topic`, `api_version`, and `webhook_id` fields are pulled straight from headers with no cryptographic binding to the body or to each other: [2](#0-1) 

`HmacValidator.validate` computes the signature purely from `verifiable_query.to_signable_string` (i.e., the raw body) and the shared secret: [3](#0-2) 

`Registry.process` treats a passing HMAC check as sufficient authentication for the whole request, including `request.shop`, which is then forwarded to the app's handler as authoritative tenant identity: [4](#0-3) 

The identity binding that should hold is: `hmac(body) valid` `⇒` `(shop, topic, body) is exactly what Shopify sent for that shop`. In reality the binding only proves `hmac(body) valid` `⇒` `body was produced with secret S at some point`, with `shop`/`topic`/`webhook_id` completely detached from that proof. Any party who has ever received one legitimately-signed webhook (trivially available to any merchant/developer who installs the app, since webhook payloads are delivered to the app's public endpoint and the HMAC secret is the app's single global `api_secret_key` shared across all shops) can resend the exact same bytes with a forged `shop-domain` header pointing at a victim shop, and the signature will still validate.

### Impact Explanation
This breaks tenant isolation (cross-tenant access), a Critical-severity outcome per the scope: the app will invoke the registered webhook handler believing the replayed data belongs to an arbitrary chosen shop, while the actual signed content originated from a different (attacker-controlled or previously observed) shop. Depending on how the host app uses `WebhookMetadata#shop` (e.g., to look up/update per-shop state, trigger GDPR/compliance actions, or write customer/order data under a shop record), this can lead to data being attributed to, or actions being taken against, the wrong tenant.

### Likelihood Explanation
Exploitation requires only the ability to send an HTTP POST to the app's public webhook endpoint with attacker-controlled headers and a body/HMAC pair that was legitimately observed once — no possession of `api_secret_key` is required, and no MITM/TLS interception is needed since the attacker supplies their own request. Any user who can install the app on their own store (or otherwise capture a delivered webhook) can harvest a valid `(body, hmac)` pair for reuse against other shops' identifiers.

### Recommendation
Bind the shop (and other routing metadata) into the value that is HMAC-verified — either by requiring the host application to correlate `request.shop` against the shop stored for the session/subscription that the `webhook_id` belongs to before trusting it, or by having `to_signable_string` incorporate the header values Shopify already signs into the canonical Shopify webhook HMAC scheme, and by validating that the resolved shop from `webhook_id`/topic registration matches the header-provided shop before invoking handlers.

### Proof of Concept
1. Install the app on Shop A; capture one delivered webhook: raw body `B` and header `x-shopify-hmac-sha256: H` (valid for secret `S`).
2. Replay a POST to the app's webhook endpoint with the same body `B` and header `H`, but set `x-shopify-shop-domain: shop-b.myshopify.com` (any other install of the app).
3. `HmacValidator.validate` (`lib/shopify_api/utils/hmac_validator.rb:26-31`) succeeds because it only checks `B` against `H`.
4. `Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-200`) dispatches the handler with `shop: "shop-b.myshopify.com"` and the body content from Shop A, demonstrating cross-tenant data/identity confusion.

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
