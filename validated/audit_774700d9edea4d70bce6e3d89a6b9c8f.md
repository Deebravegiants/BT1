Confirmed: `Utils::VerifiableQuery` requires only `hmac` and `to_signable_string`, and `Webhooks::Request#to_signable_string` returns only `@raw_body`, excluding all headers (topic, shop-domain, webhook-id, api-version) from the signed payload.This confirms the full path: `Registry.process` builds the `WebhookMetadata` struct — including `shop`, `topic`, `webhook_id`, `api_version` — entirely from unauthenticated headers, after only validating the HMAC over the raw body [1](#0-0) , and hands it directly to the host app's `WebhookHandler#handle` [2](#0-1) .

### Title
Webhook HMAC only authenticates the raw body, not the `shop`/`topic`/`webhook-id` headers, allowing tenant-identity spoofing on replay - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` validates a webhook solely by checking that the HMAC signature matches `to_signable_string`, which is defined to be only the raw request body [3](#0-2) . The `shop`, `topic`, `webhook_id`, and `api_version` values are all pulled straight from HTTP headers that are never covered by the HMAC [4](#0-3) , yet those same unauthenticated values are packaged into `WebhookMetadata` and passed to the host application's handler as trusted identity data [1](#0-0) .

### Finding Description
The binding the gem should guarantee is: `HMAC-verified content == the identity fields the handler acts on`. Instead, the gem verifies:

`HMAC(secret, raw_body) == received_hmac`

and then trusts `shop = headers["shopify-shop-domain"]`, `topic = headers["shopify-topic"]`, `webhook_id = headers["shopify-webhook-id"]` unconditionally, since `Utils::HmacValidator.validate` only ever calls `verifiable_query.to_signable_string`, which for `Request` is `@raw_body` alone [5](#0-4) [3](#0-2) .

Because the shop/topic/webhook-id headers are excluded from the signed content, an attacker who has captured or legitimately received one valid `(raw_body, hmac)` pair for the app's secret (e.g., by installing the app on their own store and receiving a real webhook) can replay that exact body+HMAC to the app's public webhook endpoint while substituting an arbitrary `shopify-shop-domain` (or `shopify-topic`/`shopify-webhook-id`) header. `Registry.process` will still find `Utils::HmacValidator.validate(request)` to be true (the body/HMAC pair is genuinely valid) [6](#0-5) , and will dispatch to the handler with `WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)` carrying the attacker-chosen, unauthenticated shop domain [7](#0-6) . Any host application that uses `data.shop` to key session/token lookups, per-tenant data writes, or authorization decisions is misled into believing HMAC-verified content originated from, or pertains to, a shop it did not.

This breaks the equality `shop_that_produced_the_signed_body == shop_attributed_to_the_request_by_the_library`, which is exactly the "field acted on but not covered by the HMAC" class of defect.

### Impact Explanation
This enables cross-tenant confusion: a party controlling one tenant (their own installed shop) can cause the host application's webhook handler to process (or attribute) HMAC-validated payload data under a different, victim shop's identity, since the only cryptographically-bound value is the body — not the shop/topic metadata the handler relies on for tenant scoping. This matches the "cross-tenant access" impact category.

### Likelihood Explanation
Exploitation requires the attacker to already possess one legitimately signed `(raw_body, hmac)` pair for the target app's secret — attainable by any user who installs the app on their own store and receives an ordinary webhook delivery, requiring no leaked credentials or privileged access, only unauthenticated header substitution on replay to the app's public webhook endpoint.

### Recommendation
Include the `shop`, `topic`, and `webhook_id` header values in the HMAC-signed content (or independently verify them against values already associated with the same webhook subscription/store) rather than relying on the body alone; `Request#to_signable_string` and `Utils::HmacValidator` should bind all fields the handler treats as authenticated identity, not just the body.

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com` and receives one legitimate webhook delivery with body `B` and valid header `x-shopify-hmac-sha256: H` (where `H = HMAC(secret, B)`).
2. Attacker replays an HTTP POST to the app's webhook endpoint with the same body `B` and header `x-shopify-hmac-sha256: H`, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes `HMAC(secret, B)` and finds it equal to `H` — validation succeeds [6](#0-5) .
4. The handler receives `WebhookMetadata` with `shop: "victim-shop.myshopify.com"` and body `B`, despite `B` never having been generated for, or verified against, that shop [7](#0-6) .

### Citations

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

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L6-24)
```ruby
    class WebhookMetadata < T::Struct
      const :topic, String
      const :shop, String
      const :body, T::Hash[String, T.untyped]
      const :api_version, String
      const :webhook_id, String
    end

    module WebhookHandler
      include Kernel
      extend T::Sig
      extend T::Helpers
      interface!

      sig do
        abstract.params(data: WebhookMetadata).void
      end
      def handle(data:); end
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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
