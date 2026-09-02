### Title
Webhook `shop`, `topic`, `webhook_id`, and `api_version` fields are trusted from unauthenticated HTTP headers while the HMAC signature only covers the raw body - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its signable content from the raw request body only, but exposes `shop`, `topic`, `webhook_id`, and `api_version` from unsigned HTTP headers. `Registry.process` validates the HMAC and then passes those unsigned header values straight into the app's handler as if they were authenticated, breaking the equality "bytes verified == bytes acted on."

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

Meanwhile `shop`, `topic`, `webhook_id`, and `api_version` are read directly from HTTP headers with no cryptographic binding to the signature: [2](#0-1) 

`Utils::HmacValidator.validate` verifies the HMAC strictly against `to_signable_string`, i.e. the body bytes only: [3](#0-2) 

`Registry.process` performs this check and then forwards the unsigned header-derived `shop` (and `topic`, `webhook_id`, `api_version`) straight to the app's handler as trusted metadata: [4](#0-3) 

The documented usage pattern explicitly tells integrators to key application logic (e.g. `perform_later(topic: data.topic, shop_domain: data.shop, ...)`) off `data.shop`, treating it as an authenticated tenant identifier: [5](#0-4) 

The binding that should hold is: `hmac_verified_bytes == bytes_the_handler_acts_on_for_tenant_identity`. Instead, the gem verifies `HMAC(raw_body)` but the handler acts on `header["shop-domain"]`, which is disjoint from what was verified. Any party who can produce one valid `(raw_body, hmac)` pair signed with the app's real secret (e.g., a legitimate merchant who installs the app on their own shop and receives real Shopify webhooks for it) can replay that exact body/HMAC pair while swapping the `X-Shopify-Shop-Domain` header to a victim shop's domain. `Utils::HmacValidator.validate` will still pass because it only checks the body, and `Registry.process` will hand the handler a `WebhookMetadata` claiming the payload belongs to the victim shop.

### Impact Explanation
This breaks the cross-tenant isolation the HMAC check is supposed to guarantee: an attacker-controlled webhook payload (for their own store, or any store they can trigger events on) can be relabeled as belonging to a different merchant's shop while still passing signature validation. Any app logic that uses `data.shop` for authorization, data scoping, or record lookups (exactly as the gem's own documentation recommends) can be tricked into applying a malicious payload's `body` to a different tenant's records - a cross-tenant access/data-integrity violation, matching the Critical-impact "cross-tenant access" category.

### Likelihood Explanation
High. It requires no possession of `api_secret_key`, access token, or privileged account - only the ability to install the app on any shop (or capture one legitimate webhook delivery) and then send a directly-crafted HTTP request to the app's webhook endpoint with the same raw body/HMAC but a different `shop-domain` header, which `ShopifyAPI::Webhooks::Registry.process` will accept every time it is called, since `topic`, `shop`, `webhook_id`, `api_version` are never included in the HMAC computation.

### Recommendation
Include `shop`, `topic`, `webhook_id`, and `api_version` in the signable content verified against the HMAC (or otherwise cryptographically bind them to the request, e.g. by deriving them only from a value inside the verified body/JWT rather than raw headers), so that `Registry.process` cannot be tricked into associating a validly-signed body with an attacker-chosen shop.

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker.myshopify.com` (or reuses any webhook delivery they legitimately received), obtaining a real Shopify-delivered webhook request with headers:
   - `x-shopify-shop-domain: attacker.myshopify.com`
   - `x-shopify-hmac-sha256: <valid HMAC over body>`
   - raw body `B`
2. Attacker sends a new HTTP request directly to the app's webhook endpoint with the identical raw body `B` and identical `x-shopify-hmac-sha256`, but with `x-shopify-shop-domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses headers normally (`lib/shopify_api/webhooks/request.rb:45-63`), and `Utils::HmacValidator.validate` succeeds because it only checks `HMAC(B)` (`lib/shopify_api/utils/hmac_validator.rb:26-31`), independent of the `shop-domain` header.
4. `Registry.process` invokes the handler with `WebhookMetadata.new(... shop: request.shop ...)` where `request.shop` now returns `"victim.myshopify.com"` (`lib/shopify_api/webhooks/registry.rb:198-199`), causing the app to process the attacker's body as if it belongs to the victim shop.

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

**File:** docs/usage/webhooks.md (L10-29)
```markdown
If you want to register for an http webhook you need to implement a webhook handler which the `shopify_api` gem can use to determine how to process your webhook. You can make multiple implementations (one per topic) or you can make one implementation capable of handling all the topics you want to subscribe to. To do this simply make a module or class that includes or extends `ShopifyAPI::Webhooks::WebhookHandler` and implement the `handle` method which accepts the following named parameters: data: `WebhookMetadata`. An example implementation is shown below:

`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
- `api_version`, `String` - The api version of the webhook

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
