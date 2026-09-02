### Title
Webhook `shop` identity is trusted from an unauthenticated header while HMAC only signs the raw body, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant identity (`shop`) purely from the `X-Shopify-Shop-Domain`/`shopify-shop-domain` HTTP header, but the HMAC signature that `ShopifyAPI::Utils::HmacValidator` verifies covers only the raw request body. Any actor who has legitimately received one authentic, correctly-signed webhook for their own shop (because every shop installed on an app shares the same `client_secret`) can replay that exact `(raw_body, hmac)` pair directly to the app's webhook endpoint while substituting an arbitrary `shop-domain` header value. The signature check still passes because the header is never part of the signed content, so the library hands the handler a `shop` value that is completely uncorrelated to what Shopify actually authenticated.

### Finding Description
The binding that must hold is:

`HMAC-verified bytes == bytes the library treats as authenticated tenant identity`

In `lib/shopify_api/webhooks/request.rb`:
```ruby
def shop
  T.cast(shopify_header("shop-domain"), String)
end
...
def to_signable_string
  @raw_body
end
``` [1](#0-0) 

`to_signable_string` (the string HMAC-verified by `Utils::HmacValidator.validate`) is exactly `@raw_body`, i.e. no header, including `shop-domain`, is included in the signable content: [2](#0-1) 

`Registry.process` validates the HMAC and then forwards the (unauthenticated) `request.shop` value straight into the dispatched `WebhookMetadata`, which is the value app code uses to identify which tenant/session the event belongs to:
```ruby
def process(request)
  raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)
  handler = @registry[request.topic]&.handler
  ...
  handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop,
    body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))
end
``` [3](#0-2) 

Because `shop`, `topic`, `api_version`, and `webhook_id` are all read from headers that sit outside the HMAC's signable string, an attacker who owns/controls any single shop that has the target app installed can capture a legitimate `(raw_body, X-Shopify-Hmac-Sha256)` pair Shopify sent them, then submit it directly (bypassing Shopify) to the app's public webhook endpoint with a forged `X-Shopify-Shop-Domain` header pointing at a victim shop. `HmacValidator.validate` recomputes the signature only from `raw_body`, so it still succeeds, and the forged `shop` value is delivered to the app's handler as if Shopify had authenticated it for that shop.

### Impact Explanation
This breaks the tenant/identity boundary the library is expected to guarantee for webhook processing: an unprivileged merchant who merely installed the app on their own store can inject webhook events attributed to a different shop into the app's processing pipeline, without possessing the app's `client_secret`, an access token, or any victim credentials. Any downstream logic that keys off `WebhookMetadata#shop` (e.g. to select which merchant's stored token/session to act on, or to attribute the payload to a shop record) can be tricked into acting on attacker-supplied data under a spoofed tenant identity — a cross-tenant confusion vulnerability.

### Likelihood Explanation
Exploitation requires only that the attacker be a genuine (even free-tier) merchant of the target app so they receive at least one real webhook delivery, plus the ability to send an arbitrary HTTP POST to the app's public webhook URL (which is by definition internet-reachable). No secrets, tokens, or privileged access are needed — this is reachable by any unprivileged internet user who installs the app once.

### Recommendation
Bind the trusted headers (`shop-domain`, `topic`, `webhook-id`, `api-version`) into the HMAC-verified content, or otherwise cryptographically tie them to the verified body (e.g. by including them in `to_signable_string`), so that a replayed body cannot be paired with a forged tenant/topic header and still pass verification.

### Proof of Concept
1. Install the target app (built on this gem) on an attacker-controlled shop `attacker.myshopify.com`.
2. Trigger any webhook topic the app subscribes to (e.g. `orders/create`) and capture the raw POST body and the `X-Shopify-Hmac-Sha256` header sent by Shopify.
3. Replay that exact body and HMAC header directly to the app's webhook endpoint, but set `X-Shopify-Shop-Domain: victim.myshopify.com`.
4. `Utils::HmacValidator.validate` recomputes the signature from the body only and returns `true`; `Registry.process` dispatches the handler with `WebhookMetadata#shop == "victim.myshopify.com"`, even though Shopify never sent this event for that shop.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-38)
```ruby
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
