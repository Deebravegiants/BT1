### Title
Webhook HMAC signature does not cover the `shop-domain` (or `topic`/`webhook-id`) header, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb], [File: lib/shopify_api/webhooks/registry.rb], [File: lib/shopify_api/utils/hmac_validator.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, while `ShopifyAPI::Webhooks::Registry.process` uses the (unsigned) `shop-domain`, `topic`, and `webhook-id` headers to build the `WebhookMetadata` that is handed to the app's handler. Because the HMAC only binds the body, any unprivileged internet user who has installed the app on their own store (and can therefore legitimately obtain a `(body, hmac)` pair signed with the app's shared `client_secret`) can replay that exact body to the app's webhook endpoint while forging the `shop-domain` header to claim the event belongs to a different merchant. `HmacValidator.validate` will still succeed because it never inspects `shop`.

### Finding Description
`Utils::HmacValidator.validate_signature` computes the signature over `verifiable_query.to_signable_string` and compares it against the `hmac` header value: [1](#0-0) 

For webhooks, `to_signable_string` is defined as just the raw body: [2](#0-1) 

but `shop`, `topic`, and `webhook_id` are all read from separate, HMAC-uncovered HTTP headers: [3](#0-2) 

`Registry.process` validates only the HMAC (i.e., only the body) and then builds `WebhookMetadata` directly from these unsigned header values, handing them to the app's registered handler as the trusted tenant/event identity: [4](#0-3) 

The binding broken: `shop field used by the handler to scope tenant-specific action` ≠ `shop field covered by the HMAC that authenticates the request`. All webhooks for a given app are signed with the same `api_secret_key` regardless of which shop sent them, so a `(raw_body, hmac)` pair legitimately obtained from the attacker's own store's webhook delivery remains valid when replayed with a forged `shopify-shop-domain` header pointing at a victim shop.

### Impact Explanation
This crosses a tenant boundary purely with a spoofed header, since the piece of data the gem hands the host application to identify "which merchant this event is for" (`WebhookMetadata#shop`) is not authenticated at all — only the JSON body is. An attacker who is nothing more than an unprivileged installer of the app on their own shop can cause the receiving app to process webhook data (e.g., order/customer/app-uninstall events) under an arbitrary victim shop's identity, matching the "cross-tenant access" Critical-impact category.

### Likelihood Explanation
Likelihood is moderate-to-high for any app that (a) is publicly installable (most public apps), and (b) uses `WebhookMetadata#shop` from this gem as the authoritative tenant key in its handler — which is exactly the intended, documented usage of `Registry.process`/`WebhookMetadata`. No secret material is required beyond installing the app once as an ordinary merchant.

### Recommendation
Bind the `shop` (and ideally `topic`/`webhook_id`) header into the HMAC-signable content, or otherwise cryptographically bind them to the body before comparison, so that a body+hmac pair cannot be replayed under a different shop identity. At minimum, `Utils::HmacValidator.validate` should be extended (or a new validator introduced) so that `Webhooks::Request#to_signable_string` incorporates the `shop-domain` header, ensuring the header used downstream for tenant attribution is the same data that was authenticated.

### Proof of Concept
1. Attacker installs the target public app on their own store, `attacker.myshopify.com`, obtaining a legitimate webhook delivery (e.g., `orders/create`) with body `raw_body` and header `shopify-hmac-sha256: hmac`.
2. Attacker replays this exact `raw_body` to the app's webhook endpoint, but sets `shopify-shop-domain: victim.myshopify.com` (keeping the same `hmac`).
3. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which only checks `hmac` against `raw_body` — validation passes: [5](#0-4) 
4. The handler receives `WebhookMetadata.new(shop: "victim.myshopify.com", ...)` and processes/acts as if the event legitimately originated from the victim shop.

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
