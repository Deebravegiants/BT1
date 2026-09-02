This confirms the vulnerability path clearly: the documentation explicitly promises that `ShopifyAPI::Webhooks::Registry.process` will "verify the request did indeed come from Shopify" [1](#0-0) , and the handler is told it can trust `data.shop` as "The shop domain of the webhook" [2](#0-1) , yet the `shop` value is taken directly from an HTTP header that is never included in the HMAC signature computation.

### Title
Webhook shop-domain header is not covered by HMAC verification, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` validates a webhook's authenticity solely by checking the HMAC over the raw request body, but the `shop` (and `topic`/`api_version`/`webhook_id`) values are read from HTTP headers that are excluded from that signature. Any party who can obtain one genuine, HMAC-signed webhook body (e.g., from their own Shopify store) can replay that exact body to the app's webhook endpoint while substituting an arbitrary `x-shopify-shop-domain` header, and the request will still pass HMAC validation and be dispatched to the app's handler as if it originated from the victim's shop.

### Finding Description
`Registry.process` performs exactly one authenticity check:
```ruby
raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)
``` [3](#0-2) 

`HmacValidator.validate` computes the signature over `verifiable_query.to_signable_string` and compares it to the `hmac` header [4](#0-3) . For `Webhooks::Request`, `to_signable_string` returns only the raw request body:
```ruby
def to_signable_string
  @raw_body
end
``` [5](#0-4) 

Meanwhile `shop`, `topic`, `api_version`, and `webhook_id` are all pulled from headers that are not part of the signed material:
```ruby
def shop
  T.cast(shopify_header("shop-domain"), String)
end
``` [6](#0-5) 

After HMAC validation succeeds, `Registry.process` forwards this unauthenticated `shop` value straight to the app's handler:
```ruby
handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop,
  body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))
``` [7](#0-6) 

The identity binding that breaks is: `shop authenticated-by-HMAC` (what the gem's documentation and API contract imply) versus `shop parsed-from-unsigned-header` (what is actually delivered to the handler). Because the HMAC only covers `@raw_body`, an attacker who owns a real Shopify store can generate a legitimately-signed webhook (any topic/body they can trigger on their own store, e.g. `orders/create`), capture the valid `hmac-sha256` header for that exact body, then replay the same body/HMAC to the target app's webhook endpoint while setting `x-shopify-shop-domain` to a victim shop's domain. `HmacValidator.validate` will still pass since it only checks the body against the secret, and the app's handler — following the documented usage pattern of trusting `data.shop` [8](#0-7)  — will process/store the attacker-controlled body under the victim's tenant identity.

### Impact Explanation
This is a cross-tenant data integrity/injection vector: an unprivileged internet user (any legitimate merchant of the target app, or anyone who can trigger a webhook to their own store) can cause the app to attribute attacker-chosen webhook data/events to a shop they do not own, because the gem's own webhook contract fails to bind `shop` to the HMAC-verified payload. Depending on how the host app models `data.shop` for tenant-scoped writes (order processing, product updates, subscription/billing events, etc.), this can lead to cross-tenant data corruption or unauthorized actions performed against another merchant's account — matching the "cross-tenant access" impact class.

### Likelihood Explanation
Likelihood is moderate: the attacker needs at least one genuine HMAC-signed webhook body, which is trivially obtainable by operating any Shopify development/trial store and subscribing the target app to webhooks for it (a normal, unprivileged flow), then simply modifying the shop-domain header value when relaying the captured request to the target's public webhook endpoint. No possession of the app's `client_secret` or access tokens is required.

### Recommendation
Include the `shop` (and ideally `topic`, `api_version`, `webhook_id`) header values in the HMAC-signed material, or otherwise cryptographically bind the shop domain to the request before exposing it via `WebhookMetadata`, so `Utils::HmacValidator.validate` fails whenever these values are tampered with independently of the body.

### Proof of Concept
1. Attacker owns `attacker-shop.myshopify.com` and registers the target app's webhook for `orders/create`.
2. Shopify sends a legitimately signed webhook to the app:
   - Headers: `x-shopify-shop-domain: attacker-shop.myshopify.com`, `x-shopify-hmac-sha256: <valid HMAC of raw body>`
   - Body: attacker-controlled JSON (attacker can shape order data on their own store).
3. Attacker intercepts/replays this exact request to the app's webhook endpoint but changes only the header:
   - `x-shopify-shop-domain: victim-shop.myshopify.com`
   - Body and `x-shopify-hmac-sha256` unchanged.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only hashes `@raw_body` [5](#0-4) .
5. The app's handler receives `data.shop == "victim-shop.myshopify.com"` with attacker-controlled `data.body`, and performs tenant-scoped writes against the victim's records.

### Citations

**File:** docs/usage/webhooks.md (L12-14)
```markdown
`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
```

**File:** docs/usage/webhooks.md (L24-27)
```markdown
    def handle(data:)
      puts "Received webhook! topic: #{data.topic} shop: #{data.shop} body: #{data.body} webhook_id: #{data.webhook_id} api_version: #{data.api_version}"
      perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)
    end
```

**File:** docs/usage/webhooks.md (L125-125)
```markdown
To process an http webhook, you need to listen on the route(s) you provided during the Webhook registration process, then when the route is hit construct a `ShopifyAPI::Webhooks::Request` and call `ShopifyAPI::Webhooks::Registry.process`. This will verify the request did indeed come from Shopify and then call the specified handler for that webhook. An example in Rails is shown below:
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
