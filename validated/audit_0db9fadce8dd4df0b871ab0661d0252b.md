## Analysis

The report's underlying bug class is: a value used downstream to make security/tenant decisions is not bound by the same cryptographic check that establishes trust. In this gem's webhook processing path, that same class of flaw exists.

`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw HTTP body: [1](#0-0) 

But `shop`, `topic`, `api_version`, and `webhook_id` are all derived from unauthenticated HTTP headers: [2](#0-1) 

`Registry.process` validates the HMAC against the body only, then immediately trusts `request.topic` and `request.shop` — values never covered by that signature — to route and label the payload: [3](#0-2) 

The equality the code implicitly (and incorrectly) assumes is:
`bytes_verified_by_HMAC (raw_body) == bytes_the_app_acts_on (raw_body + shop_header + topic_header)`

This is false — the shop/topic/webhook_id headers are parsed and acted upon but never covered by the HMAC signature.

### Title
Webhook `shop`, `topic`, and `webhook_id` headers are not covered by HMAC verification, enabling cross-tenant webhook replay - (File: `lib/shopify_api/webhooks/registry.rb`, `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` validates only the HMAC over the raw request body via `Utils::HmacValidator.validate(request)`, but the `shop`, `topic`, and `webhook_id` values used to route and label the payload are taken from HTTP headers that are entirely excluded from the signed content (`Request#to_signable_string` returns `@raw_body` alone).

### Finding Description
Any party who can obtain one genuine, HMAC-signed webhook body/signature pair — e.g., by installing the app on their own store and triggering a webhook event for a topic the app subscribes to — can replay that exact `(raw_body, hmac)` pair to the app's webhook endpoint while substituting the `shop-domain` (and/or `topic`/`webhook-id`) header with an arbitrary value. Because `HmacValidator.validate` only recomputes the signature over `@raw_body` (`lib/shopify_api/utils/hmac_validator.rb:27-31`, `lib/shopify_api/webhooks/request.rb:35-38`), the forged headers do not affect signature validity, and `Registry.process` accepts the request as authentic: [3](#0-2) 

The resulting `WebhookMetadata` handed to the app's handler carries the attacker-chosen `shop` value alongside the body content, so the host application's handler — which relies on this gem's HMAC verification as its authenticity guarantee — will process the body as if it legitimately originated from, and pertains to, the spoofed shop.

### Impact Explanation
This breaks the tenant-identity binding the gem is supposed to provide: `shop_verified_by_hmac` should equal `shop_the_handler_acts_on`, but it does not. A handler that uses `data.shop` to select which tenant's record to update, create, or delete (the documented usage pattern shown in `WebhookMetadata`) can be made to apply another merchant's webhook content to an arbitrary target shop, i.e., cross-tenant data confusion/injection, without ever needing that shop's credentials. This matches the Critical "cross-tenant access" category.

### Likelihood Explanation
Low-to-Medium: exploitation requires the attacker to first obtain one valid `(body, hmac)` pair, which is straightforward for anyone able to install the app or otherwise trigger a webhook delivery on their own shop (a normal, unprivileged action for any Shopify merchant/developer). No access token, `api_secret_key`, or account privilege on the target tenant is required.

### Recommendation
Extend `Utils::VerifiableQuery`/`Request#to_signable_string` (or add a separate binding check in `Registry.process`) so that the HMAC verification covers the `shop`, `topic`, and `webhook_id` values, or otherwise cryptographically bind these header values to the signed payload before they are trusted for routing/labelling in `Registry.process`.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com` and triggers a subscribed webhook topic (e.g. `orders/create`), capturing the raw body `B` and the valid `X-Shopify-Hmac-Sha256` header `H` that Shopify sent to the app's webhook endpoint.
2. Attacker sends a new POST request to the same webhook endpoint with body `B` and header `X-Shopify-Hmac-Sha256: H` unchanged, but with `X-Shopify-Shop-Domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses these headers; `Utils::HmacValidator.validate` recomputes HMAC over `B` only and it matches `H`, so `Registry.process` proceeds.
4. The registered handler receives `WebhookMetadata` with `shop: "victim.myshopify.com"` and body `B`, causing the host application to act on attacker-controlled content as if it belongs to `victim.myshopify.com`.

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

**File:** lib/shopify_api/webhooks/request.rb (L35-43)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end

      sig { returns(T::Hash[String, T.untyped]) }
      def parsed_body
        JSON.parse(@raw_body)
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
