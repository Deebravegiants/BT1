### Title
Webhook `shop` (and `topic`/`webhook_id`/`api_version`) headers are trusted for tenant identification without being covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant-identifying `shop` field (and `topic`, `webhook_id`, `api_version`) from unauthenticated HTTP headers, while the HMAC signature that `Registry.process` relies on to prove authenticity only covers the raw request body. An attacker who possesses one genuine, validly-signed webhook body/HMAC pair (e.g., delivered to their own shop) can replay it against the shared webhook endpoint while substituting the `shop-domain` header for a victim shop, and the signature check will still pass.

### Finding Description
`HmacValidator.validate` computes the signature only over `verifiable_query.to_signable_string`, and for webhooks that method returns just the raw body: [1](#0-0) 

```ruby
sig { override.returns(String) }
def to_signable_string
  @raw_body
end
```

Meanwhile, `shop`, `topic`, `webhook_id`, and `api_version` are pulled straight from HTTP headers with no relation to the signed content: [2](#0-1) 

`Registry.process` validates only the HMAC of the body and then dispatches the handler using these header-derived, unauthenticated values, including `shop`: [3](#0-2) 

```ruby
def process(request)
  raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)
  handler = @registry[request.topic]&.handler
  ...
  handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop,
    body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))
end
```

The identity binding that should hold is:
`shop used to authorize/scope the webhook action == shop bound inside the HMAC-signed content`

In this implementation that equality does not hold: `HmacValidator.validate` proves only `computed_signature(body, secret) == received_signature`; it says nothing about which shop the body belongs to. The `shop` header is attacker-controllable and is never included in `to_signable_string`, so the two sides of the binding are checked independently — exactly the bug class described in the report (a field acted upon but not covered by the authentication check).

### Impact Explanation
Any party capable of capturing one legitimately signed webhook body+HMAC (for example, a merchant receiving genuine webhooks to their own installed app instance, since the HMAC secret is the app-level `client_secret` shared across all of an app's installations) can replay that exact body/signature to the shared webhook endpoint while forging the `shop-domain` (and `topic`/`webhook_id`) header to point at a different, victim shop. Because `Registry.process` trusts `request.shop` for tenant attribution without it being covered by the signature, this allows cross-tenant confusion: app-side handlers that key persistence, cache invalidation, or mandatory compliance actions (`shop/redact`, `customers/redact`, `customers/data_request`) by the `shop` value from `WebhookMetadata` would act on the wrong tenant. This matches the Critical "cross-tenant access" impact category, since data or actions intended for one merchant's tenant boundary can be attributed to another merchant's tenant without holding that merchant's credentials.

### Likelihood Explanation
Medium-to-High: exploitation requires only a single genuine webhook delivery from any shop that has the target app installed (not privileged credentials, access tokens, or the `client_secret` itself), plus the ability to send an HTTP request to the app's public webhook endpoint with modified headers — both of which are within reach of an ordinary, unprivileged internet user who has installed the vulnerable app on any shop.

### Recommendation
Bind the tenant/topic identity into the material that is actually verified. For example, include `shop`, `topic`, and `webhook_id` in the signable content used by `HmacValidator`, or have `Registry.process` independently verify that the `shop`/`topic` header values are consistent with values embedded in the (already-authenticated) webhook body/metadata before dispatching to a handler, so that the identity used for authorization decisions is the same one covered by the signature check.

### Proof of Concept
1. App is installed on `attacker-shop.myshopify.com`; Shopify delivers a genuine webhook with body `B` and header `x-shopify-hmac-sha256: H`, where `H = HMAC-SHA256(client_secret, B)` — computed and verifiable per `lib/shopify_api/utils/hmac_validator.rb` lines 26-31 and `lib/shopify_api/webhooks/request.rb` lines 35-38.
2. Attacker captures `(B, H)` from their own shop's webhook delivery.
3. Attacker POSTs the same `B` and `H` to the app's shared webhook endpoint, but sets `x-shopify-shop-domain: victim-shop.myshopify.com` (and optionally a mandatory `topic` like `shop/redact`).
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks `B` against `H` (lib/shopify_api/webhooks/registry.rb lines 189-190).
5. The handler executes with `shop: "victim-shop.myshopify.com"` (lib/shopify_api/webhooks/registry.rb lines 198-199), even though that shop never sent or authorized this webhook — demonstrating the identity-binding break.

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
