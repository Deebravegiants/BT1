This confirms the finding: the webhook HMAC in `ShopifyAPI::Webhooks::Request` covers only the raw body, while `shop`, `topic`, `webhook_id`, and `api_version` are read from unauthenticated HTTP headers and passed straight through to the app's handler unchecked.

### Title
Webhook HMAC signature does not bind `shop-domain`, `topic`, or `webhook-id` headers, allowing forged tenant identity in processed webhooks - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` treats a webhook request as authentic once `Utils::HmacValidator.validate(request)` succeeds, and then forwards `request.shop`, `request.topic`, and `request.webhook_id` — all values read straight from attacker-controllable HTTP headers — into `WebhookMetadata` given to the app's handler. But the HMAC signature only ever covers the raw request body.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns just `@raw_body` [1](#0-0) , and `HmacValidator.validate` computes/compares the HMAC purely against that signable string [2](#0-1) . Meanwhile `shop`, `topic`, `webhook_id`, and `api_version` are all parsed from HTTP headers (`x-shopify-shop-domain`, `x-shopify-topic`, `x-shopify-webhook-id`, `x-shopify-api-version`) that are never part of the signed content [3](#0-2) .

`Registry.process` validates the HMAC and then immediately trusts `request.shop`/`request.topic`/`request.webhook_id` to construct the `WebhookMetadata` passed to the app's handler, with no cross-check that these header values are consistent with whatever shop/topic actually produced the signed body [4](#0-3) . The equality that should hold — `shop-domain header == shop that produced this exact signed body` — is never enforced anywhere in the gem; the HMAC only proves "signed with this app's `api_secret_key`," not "signed for this specific shop or topic."

Since the `api_secret_key` is shared across all shops that have installed the app, any body+HMAC pair that is valid for one shop's webhook delivery is *also* a cryptographically valid HMAC pair regardless of which `shop-domain`/`topic`/`webhook-id` headers accompany it, because those fields are outside the signed bytes. An attacker who can obtain one legitimate `(raw_body, hmac)` pair delivered to the app's public webhook endpoint (e.g., by installing the app on their own store and capturing a webhook Shopify sends them) can replay that exact body/HMAC to the same endpoint while substituting a different `x-shopify-shop-domain` (someone else's shop), `x-shopify-topic`, and `x-shopify-webhook-id`. `HmacValidator.validate` still returns `true` because it only checks the body bytes, and the forged headers flow straight into the handler as authoritative tenant/topic/dedup identity.

### Impact Explanation
This breaks the identity binding "bytes verified versus bytes parsed": the gem verifies the body was HMAC-signed by the app's secret, but the app-facing `WebhookMetadata#shop` (used by handlers to route processing/storage per tenant per the documented handler contract [5](#0-4) ) is not actually bound to that signature. Any handler that trusts `data.shop` to scope which tenant's data to update (the exact usage pattern shown in the gem's own documentation, e.g. `perform_later(topic: data.topic, shop_domain: data.shop, ...)` [6](#0-5) ) can be tricked into attributing another shop's webhook data — cross-tenant confusion — using a body/HMAC pair the attacker legitimately obtained for their own shop.

### Likelihood Explanation
Exploitation requires an attacker to obtain at least one valid `(raw_body, hmac)` pair — achievable without any privileged credentials by simply installing the app as a normal merchant on a store they control, since apps are typically installable by any Shopify merchant and mandatory webhooks (e.g. `customers/data_request`) are delivered to every installer. The webhook endpoint is intentionally public/unauthenticated (that's the entire point of HMAC-based validation), so replaying the captured body with swapped headers requires nothing beyond normal internet access to the app's callback URL.

### Recommendation
Include `shop-domain`, `topic`, and `webhook-id` (or minimally `shop`) in the HMAC-signed content, or otherwise cryptographically bind them to the body before validation — e.g. compute the signature over `shop + topic + webhook_id + raw_body`. Short of changing Shopify's webhook signing scheme (which this gem doesn't control), the gem should at minimum document prominently, and ideally provide a helper to let apps verify, that `request.shop`/`request.topic`/`request.webhook_id` are **not** covered by the HMAC and must be independently cross-checked by the host application (e.g., against the shop's known installed session before trusting `data.shop` for tenant-scoped writes).

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com` (any merchant can do this) and captures a legitimately delivered webhook request, e.g.:
   ```
   POST /callback/customers/data_request
   x-shopify-topic: customers/data_request
   x-shopify-hmac-sha256: <valid HMAC of raw body B>
   x-shopify-shop-domain: attacker-shop.myshopify.com
   x-shopify-webhook-id: wh-1
   Body: B
   ```
2. Attacker replays the exact same body `B` and `hmac` value to the same endpoint but swaps the shop/topic headers:
   ```
   POST /callback/orders/create
   x-shopify-topic: orders/create
   x-shopify-hmac-sha256: <same valid HMAC of raw body B>
   x-shopify-shop-domain: victim-shop.myshopify.com
   x-shopify-webhook-id: wh-2
   Body: B
   ```
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only checks the HMAC against `B` — it passes [7](#0-6) .
4. The `orders/create` handler is invoked with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", topic: "orders/create", body: <attacker's parsed body B>, webhook_id: "wh-2", ...)` — data attributed to a shop that never sent it, and to a topic it wasn't actually sent for [8](#0-7) .

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
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

**File:** docs/usage/webhooks.md (L12-17)
```markdown
`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
- `api_version`, `String` - The api version of the webhook
```

**File:** docs/usage/webhooks.md (L19-29)
```markdown
```ruby
module WebhookHandler
  extend ShopifyAPI::Webhooks::WebhookHandler

  class << self
    def handle(data:)
      puts "Received webhook! topic: #{data.topic} shop: #{data.shop} body: #{data.body} webhook_id: #{data.webhook_id} api_version: #{data.api_version}"
      perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)
    end
  end
end
```
