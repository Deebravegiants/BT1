### Title
Webhook tenant identity (`shop`) is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` only validates the HMAC over the raw request body, never over the `shop-domain` header. That header is nonetheless what the gem hands to the host app as the authenticated tenant identifier (`WebhookMetadata#shop`). An attacker who can obtain any single valid `(body, hmac)` pair for a topic (e.g. by triggering a webhook on their own, attacker-controlled shop) can replay that exact body/HMAC to the app's webhook endpoint while substituting an arbitrary `shop-domain` header, and the signature check will still pass.

### Finding Description
The equality the gem should enforce is:

`shop that produced/authorized the HMAC == shop attributed to the webhook data`

Instead, the gem only checks:

`HMAC(secret, raw_body) == received_hmac`

and separately, unauthenticated, parses:

`shop = headers["shopify-shop-domain"]`

`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0)  , and `shop` is read straight from the header with no cryptographic relation to the signed bytes [2](#0-1) . `Registry.process` validates only this body HMAC before dispatching to the app's handler: `raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)` [3](#0-2) , and it forwards `request.shop` as the tenant identifier straight to the handler: `handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop, ...))` [4](#0-3) . `HmacValidator.validate` itself only ever signs `verifiable_query.to_signable_string`, which for `Request` is exactly the raw body [5](#0-4) .

The gem's own documentation confirms that `data.shop` is treated by consuming apps as the authoritative tenant/shop for the webhook, and is expected to be used to route/attribute work to the correct merchant: `puts "Received webhook! topic: #{data.topic} shop: #{data.shop} body: #{data.body}..."` / `perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)` [6](#0-5) . Because `shop` is not part of the signed material, the gem itself provides no binding between "HMAC verified" and "shop attributed."

### Impact Explanation
This is a cross-tenant integrity break at the trust boundary the gem is specifically responsible for (`Registry.process` / `Request`), matching the "bytes verified versus bytes parsed" analog in the prompt's bug class: the HMAC verifies raw body bytes, but the identity-bearing field (`shop`) that the host application relies on for tenant attribution is parsed independently and unauthenticated. An attacker who can generate one legitimate `(body, hmac)` pair — trivially available to any developer who installs their own Shopify dev store/app and captures one webhook, or via any topic that fires webhooks on demand — can resend that exact payload to a victim app's webhook endpoint with a forged `shop-domain` header. The `Registry.process` code will accept it as valid (HMAC checks out) and hand the attacker-chosen `shop` value to the app's handler as if it were the authenticated tenant, potentially causing the host app to process/store/act on data under the wrong merchant's identity — i.e., cross-tenant data confusion, which maps to the "Critical - cross-tenant access" impact category defined in scope.

### Likelihood Explanation
Likelihood is bounded by two facts: (1) the header value itself is not attacker-controlled over TLS from Shopify normally, and (2) exploitation requires the attacker to first legitimately capture a valid `(raw_body, hmac)` pair, which is straightforward since any Partner/developer can create their own dev store, subscribe to a webhook topic, and observe the exact body/HMAC that Shopify sends for their own actions. Replaying that captured payload with a spoofed header against a **different merchant's app installation endpoint is unprivileged** and requires no credentials belonging to the victim shop. This is a real, reachable design gap inside `lib/shopify_api/webhooks/request.rb` and `registry.rb` and not merely a host-app misconfiguration, since the gem itself only signs the body and exposes the header-derived `shop` as trusted metadata.

### Recommendation
Bind the tenant identity to the signed material, or explicitly document/enforce that `shop-domain`/`webhook-id` are not to be trusted for authorization decisions without additional server-side verification (e.g., requiring apps to cross-check `data.shop` against a shop for which they hold an active, previously-established session/access token before processing). At minimum, the gem should not silently pass an unauthenticated `shop` value to `WebhookMetadata` without flagging that only the body is HMAC-verified.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker-shop.myshopify.com` and triggers a webhook (e.g. `orders/create`), capturing the raw POST body and the `X-Shopify-Hmac-Sha256` header Shopify sent.
2. Attacker POSTs the exact same `raw_body` and `hmac` header to the victim app's webhook endpoint, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only recomputes HMAC over `@raw_body` [1](#0-0)  — validation succeeds because the body/HMAC pair is genuinely valid (just for a different shop).
4. The handler is invoked with `WebhookMetadata.new(..., shop: "victim-shop.myshopify.com", ...)` [4](#0-3) , causing the app to process attacker-supplied webhook content as though it belonged to the victim tenant.

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

**File:** lib/shopify_api/webhooks/registry.rb (L188-199)
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
```

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-22)
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
```

**File:** docs/usage/webhooks.md (L24-27)
```markdown
    def handle(data:)
      puts "Received webhook! topic: #{data.topic} shop: #{data.shop} body: #{data.body} webhook_id: #{data.webhook_id} api_version: #{data.api_version}"
      perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)
    end
```
