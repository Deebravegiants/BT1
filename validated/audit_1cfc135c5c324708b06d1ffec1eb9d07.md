### Title
Webhook `shop-domain` and `topic` headers are not covered by the HMAC signature, allowing shop-identity spoofing on replay of a legitimate webhook - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw HTTP body, and `Utils::HmacValidator.validate` verifies the HMAC exclusively against that body. The `shop` and `topic` values used by `ShopifyAPI::Webhooks::Registry.process` to route and label the webhook are read directly from HTTP headers, which are entirely outside the scope of what the HMAC authenticates.

### Finding Description
`Request#to_signable_string` is defined as `@raw_body` only [1](#0-0) , while `shop` and `topic` are derived purely from unauthenticated headers (`shopify-shop-domain`/`x-shopify-shop-domain`, `shopify-topic`/`x-shopify-topic`) [2](#0-1) . `Registry.process` validates the HMAC against the body via `Utils::HmacValidator.validate(request)`, then dispatches the handler using `request.topic` and `request.shop` taken straight from those headers [3](#0-2) . `HmacValidator.validate_signature` recomputes the HMAC only over `to_signable_string` (the body) and compares it to the received value [4](#0-3) .

The binding that should hold is: `HMAC(body, headers) == received_hmac` and `shop_asserted_to_handler == shop_that_produced_this_signed_payload`. In this implementation, the second equality does not hold — `shop_asserted_to_handler` is read from an unauthenticated header while the HMAC only authenticates the body bytes. Any request bearing a `(body, hmac)` pair produced by Shopify for shop A can be replayed with the `shop-domain` header changed to shop B (or `topic` changed to any registered topic), and it will still pass `HmacValidator.validate` because the signature check never inspects the headers.

### Impact Explanation
This is a cross-tenant boundary break in the identity binding the gem is responsible for enforcing on the app's behalf: the app-level webhook handler receives `WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)` with a `shop`/`topic` that Shopify never certified via HMAC for this body. An unprivileged internet user who can obtain (or is sent, e.g. via a webhook for their own store, which any merchant naturally receives) one valid `(body, hmac)` pair can replay it toward the app's webhook endpoint with an arbitrary `shop-domain` header. Downstream handlers that key persistence, cache invalidation, or business logic off `data.shop` (as the documented/expected usage pattern encourages, see `WebhookMetadata` consumption in `test_process_with_new_format_headers`) can be made to attribute another merchant's (attacker-chosen) webhook payload to a victim shop, or vice versa — i.e., cross-tenant data confusion driven entirely through this gem's trust decision, without any secret, token, or privileged access.

### Likelihood Explanation
Moderate. It requires an attacker to already possess one genuine `(body, hmac)` pair — trivially available to any merchant who installs the app and can trigger a webhook for their own store — and then be able to send an arbitrary HTTP request to the app's public webhook endpoint with modified headers. No `client_secret`, access token, or privileged account is needed; only network access to the endpoint and one legitimately received webhook.

### Recommendation
Include the identity-relevant headers (`shop-domain` and `topic`, and ideally `api-version`) in the signable payload, or otherwise cryptographically bind them (e.g., have `HmacValidator` compute over a canonical string composed of the raw body plus these header values) so `to_signable_string` in `lib/shopify_api/webhooks/request.rb` reflects everything the handler will later trust. Alternatively, document explicitly that host applications must independently re-verify `shop`/`topic` against server-side state before trusting `WebhookMetadata`, since the gem's HMAC check does not cover them.

### Proof of Concept
1. App has webhook endpoint wired to `ShopifyAPI::Webhooks::Registry.process`.
2. Attacker's own store (shop A, attacker-controlled/legit merchant) triggers a real webhook; attacker captures the raw request: `raw_body`, `x-shopify-hmac-sha256`, `x-shopify-topic`, `x-shopify-shop-domain: shop-a.myshopify.com`.
3. Attacker resends the identical `raw_body` and `x-shopify-hmac-sha256` to the same endpoint, but sets `x-shopify-shop-domain: victim-shop.myshopify.com` (and/or a different registered `x-shopify-topic`).
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which only hashes `@raw_body` [1](#0-0)  — validation succeeds because the body is unchanged.
5. The handler is invoked with `WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: parsed_body, ...)` [5](#0-4) , causing the app to process attacker-controlled data as though it originated from `victim-shop.myshopify.com`.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-23)
```ruby
      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

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
