### Title
Webhook `shop` and `topic` fields are trusted for tenant routing but excluded from the HMAC-signed bytes - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw HTTP body, while the `shop`, `topic`, `webhook_id` and `api_version` values consumed by `ShopifyAPI::Webhooks::Registry.process` are read straight from HTTP headers that are never included in the HMAC computation. This breaks the binding "bytes verified == bytes acted upon" for the tenant-identifying field.

### Finding Description
`ShopifyAPI::Webhooks::Request` implements `Utils::VerifiableQuery`. Its `to_signable_string` is defined as: [1](#0-0) 

only `@raw_body` is signed. The `shop` accessor, however, is pulled straight from the unauthenticated `shopify-shop-domain` / `x-shopify-shop-domain` header: [2](#0-1) 

`ShopifyAPI::Webhooks::Registry.process` validates the HMAC over the body only, then forwards the header-derived `shop` (and `topic`, `webhook_id`, `api_version`) to the host application's handler as the tenant identifier, without any additional binding check: [3](#0-2) 

So the equality the gem is supposed to guarantee — "the shop this webhook is attributed to" == "the shop covered by the HMAC" — does not hold: the HMAC only covers the body, and the header carrying the tenant identity is fully attacker-controllable once a valid `(body, hmac)` pair is known.

### Impact Explanation
Any party who can obtain one valid `(raw_body, x-shopify-hmac-sha256)` pair for the app's webhook endpoint (e.g. because they run their own shop with the app installed, or capture a single legitimate delivery) can replay that exact body/HMAC combination while substituting an arbitrary `x-shopify-shop-domain` (and `x-shopify-topic` / `x-shopify-webhook-id`) header. `Utils::HmacValidator.validate` will still pass because it only checks the body, and `Registry.process` will hand the forged `shop` value to the app's webhook handler as if it were authentic. Any host application that follows the gem's documented pattern of trusting `WebhookMetadata#shop` to select/route tenant data (the exact intended and documented use of this field) can be made to process a replayed payload under a different merchant's tenant context — a cross-tenant integrity violation.

### Likelihood Explanation
The attacker needs one previously-observed valid webhook delivery for the target app (trivial if the attacker owns any shop with the app installed) and the ability to POST to the app's public webhook URL with custom headers — no secret material required. This is a realistic, low-effort scenario for any unprivileged internet user who is also an app-installing merchant, matching the "field acted on but not covered by the HMAC" class explicitly called out in scope.

### Recommendation
Include the header-derived identifying fields (`shop-domain`, `topic`, `webhook-id`, `api-version`) in the value that is HMAC-verified, or independently verify that the `shop-domain` header matches a shop known to have a valid, non-replayed webhook subscription (e.g. bind webhook-id/timestamp to a replay cache) before passing it to the handler as trusted tenant context.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and receives one legitimate webhook delivery, capturing `raw_body` and the valid `x-shopify-hmac-sha256` value Shopify computed with the app's `client_secret`.
2. Attacker replays a request to the app's webhook endpoint with the exact same `raw_body` and `x-shopify-hmac-sha256`, but sets `x-shopify-shop-domain: victim-shop.myshopify.com` (and, if desired, a different `x-shopify-topic`).
3. `Utils::HmacValidator.validate(request)` in `lib/shopify_api/utils/hmac_validator.rb` calls `request.to_signable_string`, which returns only `raw_body`; the signature still matches, so validation succeeds.
4. `Registry.process` invokes the handler with `WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)` where `shop` is `"victim-shop.myshopify.com"`, even though the payload/HMAC never authenticated that shop — the handler processes attacker-supplied data attributed to the victim's tenant.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-23)
```ruby
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
