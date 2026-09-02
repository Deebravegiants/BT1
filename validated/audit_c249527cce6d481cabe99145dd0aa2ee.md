This confirms the identity binding break: `ShopifyAPI::Webhooks::Registry.process` validates the HMAC only against `request.to_signable_string`, which is `@raw_body` alone [1](#0-0) , while `request.shop`, `topic`, `api_version`, and `webhook_id` are all read directly from unauthenticated HTTP headers [2](#0-1) . `Registry.process` then passes `request.shop` straight into the handler's `WebhookMetadata` without re-deriving it from the signed body [3](#0-2) .

### Title
Webhook shop attribution bypass via unauthenticated `shop-domain` header - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` binds the HMAC only to the raw request body, never to the `shop-domain`, `topic`, `api-version`, or `webhook-id` headers. `ShopifyAPI::Webhooks::Registry.process` accepts the request once the body-only HMAC checks out, then trusts `request.shop` (an unauthenticated header) to attribute the event to a tenant.

### Finding Description
The equality the gem is supposed to enforce is: `shop that produced the signed bytes == shop credited by Registry.process`. In `HmacValidator.validate`, the signature is computed over `verifiable_query.to_signable_string` [4](#0-3) . For `Webhooks::Request`, that signable string is `@raw_body` only [1](#0-0) . The `shop`, `topic`, `api_version`, and `webhook_id` accessors instead read straight from the `shopify-*`/`x-shopify-*` headers [2](#0-1) , which are never included in the HMAC computation.

`Registry.process` validates the HMAC, then immediately builds `WebhookMetadata` using `request.shop` (the header value) and hands it to the app's handler, which routes/persists data per-shop based on that value [3](#0-2) . Any party capable of observing one legitimate webhook delivery (e.g., a shared/misconfigured proxy, logging pipeline, or a webhook subscriber for their own shop that can also submit requests to the app's public webhook endpoint) can replay the exact same raw body and HMAC while substituting a different `shop-domain` header value. Because the HMAC never covered that header, `HmacValidator.validate` still returns `true`, and `Registry.process` calls the handler believing the event belongs to the attacker-chosen shop.

### Impact Explanation
This breaks the tenant-identity binding between the cryptographically-verified bytes and the shop the application acts on behalf of. If the host application uses `data.shop` (as the shipped documentation explicitly instructs: `"perform_later(topic: data.topic, shop_domain: data.shop, ...)"`) to select which shop's records to update, this enables cross-tenant data injection/corruption — an attacker-controlled shop identifier is stamped onto a payload that passed cryptographic verification, so the application code has no signal to distinguish it from a legitimate webhook for that shop. This matches the "Critical - cross-tenant access" impact category.

### Likelihood Explanation
Exploitation requires capturing one valid raw-body+HMAC pair (not the secret itself) — a body/HMAC pair is not shop-specific, so a party who has legitimate access to any one of the app's own webhook deliveries (e.g. because they are a customer of the app operating their own shop, or observe traffic through infrastructure) can resubmit it with a modified `shop-domain` header to the app's public webhook endpoint. Every consumer that follows the documented `data.shop`-based handling pattern is affected without any additional app-side mistake.

### Recommendation
Include `shop`, `topic`, `api_version`, and `webhook_id` header values in the HMAC-signed material (or otherwise cryptographically bind them to the body, e.g. by having `to_signable_string` incorporate the normalized headers) so that any tampering with those headers invalidates the signature. At minimum, document prominently that `data.shop` is unauthenticated relative to the HMAC and must not be trusted for tenant routing without an independent verification (e.g., cross-checking against the shop stored for the resource identified in the signed body).

### Proof of Concept
1. Attacker owns `attacker-shop.myshopify.com` and has installed the target app, so Shopify legitimately sends the attacker a webhook: `raw_body = {"id":123,...}`, headers include `x-shopify-hmac-sha256: <valid mac over raw_body>` and `x-shopify-shop-domain: attacker-shop.myshopify.com`.
2. Attacker captures this valid `(raw_body, hmac)` pair (they receive it directly, since it was sent to their own endpoint/shop).
3. Attacker POSTs to the target app's public webhook route with the same `raw_body` and same `x-shopify-hmac-sha256`, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `HmacValidator.validate(request)` recomputes the HMAC over `raw_body` only and it matches, so `Registry.process` proceeds and invokes the handler with `WebhookMetadata#shop == "victim-shop.myshopify.com"` [3](#0-2) , even though the payload never originated from Shopify for that shop.

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
