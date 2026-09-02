This confirms the vulnerability: the docs explicitly instruct handlers to trust `data.shop` as "The shop domain of the webhook" for dispatching tenant-specific work, while the gem's HMAC only signs the raw body.

### Title
Webhook `shop` (and `topic`) identity header is not covered by HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant identity (`shop`) and event `topic` exclusively from unauthenticated HTTP headers (`x-shopify-shop-domain`, `x-shopify-topic`), while the cryptographic integrity check (`HmacValidator`) only covers the raw request body. This breaks the intended binding: `HMAC-verified bytes == (body, shop, topic)`. In reality: `HMAC-verified bytes == body only`, and `(shop, topic)` are trusted unconditionally after only a presence check.

### Finding Description
`Registry.process` verifies a webhook exclusively via: [1](#0-0) 

The HMAC check calls `Utils::HmacValidator.validate(request)`, which computes the signature over `request.to_signable_string`: [2](#0-1) 

`Request#to_signable_string` returns only the raw body — no shop, topic, or webhook_id are included in the signed material: [3](#0-2) 

Meanwhile `shop` and `topic` are read directly and unconditionally from attacker-controllable HTTP headers with no cryptographic binding to the request body: [4](#0-3) 

These unauthenticated values are then forwarded as the tenant identity to the app's business logic via `WebhookMetadata`: [5](#0-4)  and the struct definition [6](#0-5) .

The gem's own documentation confirms host applications are expected to use `data.shop` as the authoritative tenant identifier to route/queue work: [7](#0-6) .

Because all shops installed on a given app share the same `api_secret_key` (`ShopifyAPI::Context.api_secret_key`, used identically for every tenant), any entity capable of obtaining one valid `(raw_body, hmac)` pair — for example, an attacker who installs the app on their own store and thus legitimately receives webhooks with a correctly computed HMAC for their own shop — can replay that exact `raw_body` to the app's shared webhook endpoint while substituting the `X-Shopify-Shop-Domain` header with a victim shop's domain. Since the HMAC never covered the shop header, `HmacValidator.validate` still returns `true`, and the handler executes attacker-supplied body content under the victim shop's identity.

### Impact Explanation
This is a cross-tenant integrity/identity-binding break: an attacker-controlled webhook payload (which they can craft the *content* of via their own store's data, e.g. product/order titles, notes, custom fields, metafields — many of which are attacker-editable text fields) is processed by the app as if it originated from, and belongs to, an arbitrary victim shop. Depending on what the app does in its `WebhookHandler#handle` (persisting order/product data keyed by `data.shop`, triggering shop-scoped side effects, invalidating/creating records, etc.), this allows an unprivileged internet user who merely installs the app on their own store to inject or corrupt data associated with any other merchant's tenant record — a cross-tenant access/integrity violation.

### Likelihood Explanation
Reasonably likely for any real-world deployment: the only prerequisite is that the attacker installs the target app on their own store (a normal, unprivileged action for any public app) to legitimately obtain one valid `(body, hmac)` pair, then replays it to the shared webhook endpoint with a forged `shop-domain` header. No secret material, TLS interception, or privileged access is required.

### Recommendation
Include the tenant-identifying headers (`shop-domain`, `topic`, and ideally `webhook-id`/`api-version`) in the HMAC-signed material, or otherwise cryptographically bind them to the body before trusting them (e.g., derive the signable string from a canonical concatenation of headers + body, matching what should legitimately be signed). At minimum, `Request#to_signable_string` should not silently omit fields (`shop`, `topic`) that are subsequently used by the library/host application as an authenticated tenant identity.

### Proof of Concept
1. Attacker installs the target Shopify app on `attacker.myshopify.com`, completing OAuth normally (no special privilege required).
2. Attacker triggers a webhook event on their own store (e.g., updates a product with a payload containing malicious/attacker-chosen JSON body content) and captures the raw POST body plus the `X-Shopify-Hmac-Sha256` header Shopify sent to the app's webhook endpoint.
3. Attacker replays this exact `(raw_body, X-Shopify-Hmac-Sha256)` pair to the app's webhook endpoint, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com` and any `X-Shopify-Topic` desired.
4. `ShopifyAPI::Webhooks::Request.new` accepts it (all required headers present), and `HmacValidator.validate` succeeds because it only checks `raw_body` against the shared `api_secret_key` — unaffected by the forged shop header. [8](#0-7) 
5. `Registry.process` invokes the registered handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: <attacker-controlled JSON>, ...)`, and the host application processes attacker-controlled content under the victim's tenant identity.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

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

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L6-12)
```ruby
    class WebhookMetadata < T::Struct
      const :topic, String
      const :shop, String
      const :body, T::Hash[String, T.untyped]
      const :api_version, String
      const :webhook_id, String
    end
```

**File:** docs/usage/webhooks.md (L24-27)
```markdown
    def handle(data:)
      puts "Received webhook! topic: #{data.topic} shop: #{data.shop} body: #{data.body} webhook_id: #{data.webhook_id} api_version: #{data.api_version}"
      perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)
    end
```
