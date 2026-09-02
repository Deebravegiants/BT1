### Title
Webhook `shop`, `topic`, `webhook-id` and `api-version` Fields Are Trusted From Unsigned Headers While Only the Body Is HMAC-Verified - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature exclusively over the raw request body, while the shop identity (`shop-domain`), `topic`, `webhook-id`, and `api-version` come from unauthenticated HTTP headers that are never included in the signed payload. `Registry.process` validates only the body HMAC and then blindly forwards these unverified header values to the app's handler as the identity of the event, breaking the equality `shop authenticated == shop acted upon`.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

Meanwhile `shop`, `topic`, `webhook_id`, and `api_version` are all read straight from HTTP headers with no cryptographic binding to the body: [2](#0-1) 

`Registry.process` validates the HMAC of the body only, then constructs `WebhookMetadata` using the unauthenticated `request.shop`, `request.topic`, and `request.webhook_id` values and dispatches them to the app-defined handler as trusted identity fields: [3](#0-2) 

Because `Utils::HmacValidator.validate` only proves the body bytes were HMAC-signed by Shopify using the app's `api_secret_key` — it proves nothing about which shop, topic, or webhook the body belongs to: [4](#0-3) 

This breaks the identity binding `shop authenticated == shop delivered to handler`. Any merchant who has installed the app (an unprivileged, legitimately-authenticated party from the app's perspective, but untrusted with respect to *other* merchants' data) receives real webhook deliveries containing a valid `x-shopify-hmac-sha256` computed over their own webhook body using the shared app `api_secret_key`. Since the signature never covers the `shop-domain`, `topic`, or `webhook-id` headers, that same merchant can replay the identical `(raw_body, hmac)` pair to the app's webhook endpoint while substituting a different shop's domain (or a different registered topic) in the headers. `Registry.process` will still validate successfully (`Utils::HmacValidator.validate(request)` passes, since it only checks the body) and will invoke the handler with `WebhookMetadata` claiming the payload originated from an arbitrary, attacker-chosen shop/topic.

### Impact Explanation
This is a cross-tenant identity-spoofing vector: a party who is a legitimate merchant for shop A can cause the host application to process fabricated webhook events that are attributed to shop B (a shop they do not own or control), since the shop identity is not cryptographically bound to the verified bytes. Any host application that uses `data.shop` from `WebhookMetadata` to look up per-shop session/state (the pattern shown in the gem's own webhook documentation) can be tricked into corrupting or acting on another tenant's data, meeting the "cross-tenant access" criterion for Critical impact.

### Likelihood Explanation
Likelihood is realistic: obtaining one legitimate signed webhook delivery only requires installing the target app on any shop (a normal, unprivileged action), and Shopify webhook headers/body are fully attacker-controllable when relayed to the app's public endpoint. No access to `api_secret_key` or any privileged credential is required — only replay of headers that are already outside the signature's coverage.

### Recommendation
Include the shop domain, topic, webhook id, and API version in the HMAC-signable string (or otherwise cryptographically bind them, e.g. by validating them against a value obtained from an authenticated source such as the stored session for that shop) so that `Utils::HmacValidator.validate` fails if any of these header fields are altered relative to what Shopify actually signed.

### Proof of Concept
1. Install the target app on `attacker-shop.myshopify.com` and register any webhook topic.
2. Capture a legitimate webhook delivery: raw body `B` and header `x-shopify-hmac-sha256: H` (valid because it was computed by Shopify with the app's shared `api_secret_key`).
3. Replay the request to the app's webhook endpoint with the same body `B` and header `H`, but change `x-shopify-shop-domain` to `victim-shop.myshopify.com` (and/or `x-shopify-topic` to a different registered topic).
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because only `B` is checked; the handler is invoked with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", topic: ..., body: parsed(B), ...)`, causing the host app to act as though the event came from the victim shop.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
