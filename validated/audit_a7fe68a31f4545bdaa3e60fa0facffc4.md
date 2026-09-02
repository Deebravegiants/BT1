### Title
Webhook `shop`, `topic`, and `webhook_id` fields are read from unauthenticated headers and are not covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, while `shop`, `topic`, `api_version`, and `webhook_id` are read directly from HTTP headers that are never included in the HMAC computation. `Registry.process` validates the HMAC against the body alone and then trusts these unauthenticated header values to select the handler and to populate `WebhookMetadata.shop`, which the host application uses to attribute the payload to a tenant.

### Finding Description
The HMAC-verified byte range and the fields the code acts on are not the same set of bytes, breaking the intended binding `hmac == HMAC(secret, body ∥ shop ∥ topic)`: [1](#0-0) 

`hmac` is computed only from `@raw_body` (`to_signable_string` returns `@raw_body`), but `shop`, `topic`, and `webhook_id` are pulled straight from the `shopify-shop-domain`, `shopify-topic`, and `shopify-webhook-id` headers with no cryptographic tie to the signed body.

`Registry.process` validates the HMAC on the `Request` object and then immediately trusts these same unauthenticated header values: [2](#0-1) 

Since only the body is signed, any actor who possesses one valid `(body, hmac)` pair — for example a merchant/attacker who legitimately installed the app on their own shop and captured a genuine webhook delivery for that shop — can replay that exact body/HMAC pair to the app's webhook endpoint while substituting an arbitrary `x-shopify-shop-domain` header (and `x-shopify-topic`/`x-shopify-webhook-id`). `HmacValidator.validate` will still succeed because it only checks the body bytes: [3](#0-2) 

The handler is then invoked with `WebhookMetadata` built from the attacker-controlled `shop` value, so the host application processes/attributes the (validly-signed) payload to a shop that never sent it — a cross-tenant identity confusion, breaking the equality `request.shop (authenticated) == request.shop (acted upon)`.

### Impact Explanation
This lets an attacker who controls one legitimately-signed webhook body cause the host application to associate that payload/event with an arbitrary other shop identifier of their choosing, since the shop attribution is never bound by the signature. Depending on how the host app uses `WebhookMetadata.shop` (e.g., looking up a session/access token for that shop, writing tenant-scoped data), this can lead to cross-tenant data corruption or processing actions under another tenant's identity, meeting the Critical "cross-tenant access" bar.

### Likelihood Explanation
The attacker only needs one authentic `(body, hmac)` pair, which is trivially obtainable by installing the app on their own store (a legitimate, unprivileged flow) and capturing the webhook Shopify sends them. No access to `api_secret_key` or another merchant's credentials is required to forge the header values, since headers are entirely outside the signed byte range.

### Recommendation
Include the shop domain (and ideally topic/webhook id) in the HMAC-signable string, or otherwise cryptographically bind them to the verified body (e.g., verify a hash of the header set alongside the body), so `Registry.process` cannot be tricked into attributing a validly-signed payload to a spoofed shop.

### Proof of Concept
1. Install the app on attacker-owned shop `attacker.myshopify.com`; capture a webhook delivery: `raw_body`, and header `x-shopify-hmac-sha256` (valid for that body).
2. Replay a POST to the app's webhook endpoint with the same `raw_body`/`hmac` header, but set `x-shopify-shop-domain: victim.myshopify.com`.
3. `HmacValidator.validate` passes (body unchanged); `Registry.process` calls the handler with `WebhookMetadata.new(shop: "victim.myshopify.com", ...)`, causing the host app to process the event as if it came from the victim shop.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
