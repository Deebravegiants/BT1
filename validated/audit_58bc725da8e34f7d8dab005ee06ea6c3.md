This confirms the finding. The gem's own docs explicitly instruct host apps to trust `data.shop` as the tenant identifier for the webhook (e.g., `perform_later(topic: data.topic, shop_domain: data.shop, ...)`), while the HMAC only signs the request body.

### Title
Webhook `shop`/`topic`/`webhook_id`/`api_version` fields are trusted from unauthenticated headers while the HMAC only covers the request body, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`, meaning the HMAC signature validated by `Utils::HmacValidator` binds exclusively to the JSON body of a webhook request. The `shop`, `topic`, `webhook_id`, and `api_version` fields, which are read directly from HTTP headers (`shopify-shop-domain`, `shopify-topic`, etc.), are never part of the signed data.

### Finding Description
`ShopifyAPI::Webhooks::Registry.process` validates a webhook solely via `Utils::HmacValidator.validate(request)` [1](#0-0) , which computes the signature over `request.to_signable_string`, i.e. the raw body only [2](#0-1) . Meanwhile, `request.shop`, `request.topic`, `request.webhook_id`, and `request.api_version` are read verbatim from HTTP headers that are entirely outside the HMAC's coverage [3](#0-2) . After a successful HMAC check, `process` builds a `WebhookMetadata` object directly from these unauthenticated headers and dispatches it to the app's handler [4](#0-3) .

Because the app's `api_secret_key` is the same shared secret used to sign every webhook the app receives for every merchant that has installed it, a merchant (an "unprivileged internet user" relative to other tenants of the same app) can trigger a legitimate webhook to their own shop, capture a validly-signed `(body, hmac)` pair, and then replay that exact body/HMAC to the app's webhook endpoint while substituting the `x-shopify-shop-domain` (and optionally `x-shopify-topic`/`x-shopify-webhook-id`) header with a victim shop's domain. `HmacValidator.validate` will still succeed because it only checks the body against the HMAC, so the forged `shop` value passes straight through to `data.shop` in the handler, exactly as documented (`perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)`) [5](#0-4) .

This breaks the identity binding: `shop authenticated by HMAC` ≠ `shop used as the tenant/session key by the handler`, since the HMAC never authenticates the `shop` header at all.

### Impact Explanation
Any downstream logic that keys off `data.shop` to look up a session, access token, or tenant-scoped record (exactly as the gem's own documentation recommends) can be made to process data under an attacker-chosen shop identity, potentially corrupting or injecting cross-tenant records/webhook-triggered side effects (cross-tenant access), matching the Critical-impact criterion for cross-tenant access.

### Likelihood Explanation
Exploitation only requires the attacker to control one shop that has the target app installed (a normal, unprivileged merchant), be able to trigger any webhook event on their own store (trivial, e.g. updating a product), and then replay the captured body+HMAC with a modified shop header to the app's public webhook endpoint. No access to the app's `api_secret_key`, access tokens, or any privileged credential is required.

### Recommendation
Include `shop`, `topic`, `webhook_id`, and `api_version` in the HMAC-signed payload verification, or otherwise cryptographically bind the `shop` header to the signed body (e.g. validate it against Shopify's registered subscription for that specific `webhook_id`/topic instead of trusting the raw header), so header values cannot be swapped independently of the signed body.

### Proof of Concept
1. Attacker's own store (`attacker.myshopify.com`) has the vulnerable app installed and receives a legitimate webhook for `orders/create` with body `B` and header `x-shopify-hmac-sha256: H`, where `H = HMAC-SHA256(secret, B)`.
2. Attacker replays a POST to the app's webhook endpoint with the same body `B` and header `x-shopify-hmac-sha256: H`, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `Utils::HmacValidator.validate` recomputes `HMAC-SHA256(secret, B)` and it matches `H`, so the request is accepted [6](#0-5) .
4. `Registry.process` builds `WebhookMetadata.new(topic: request.topic, shop: request.shop, body: request.parsed_body, ...)` using the forged `shop` header [4](#0-3) , and the app's handler processes the attacker's webhook body as if it belonged to `victim-shop.myshopify.com`.

### Citations

**File:** lib/shopify_api/webhooks/registry.rb (L188-190)
```ruby
        sig { params(request: Request).void }
        def process(request)
          raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)
```

**File:** lib/shopify_api/webhooks/registry.rb (L198-199)
```ruby
          handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop,
            body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))
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

**File:** docs/usage/webhooks.md (L24-27)
```markdown
    def handle(data:)
      puts "Received webhook! topic: #{data.topic} shop: #{data.shop} body: #{data.body} webhook_id: #{data.webhook_id} api_version: #{data.api_version}"
      perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)
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
