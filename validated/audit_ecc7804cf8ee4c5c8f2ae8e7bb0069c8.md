Based on my investigation, I've identified the strongest analog for this bug class in the codebase.

### Title
Webhook shop-domain identity not bound by HMAC, enabling cross-tenant webhook confusion - (File: lib/shopify_api/webhooks/request.rb)

### Summary
The Shopify webhook HMAC in this gem is validated over the raw request body only. The `shop` value used by `ShopifyAPI::Webhooks::Registry.process` to route and attribute the webhook is read from an HTTP header that is entirely outside the HMAC-covered bytes, so nothing binds "the shop whose secret produced this signature" to "the shop the app believes sent it."

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw body: [1](#0-0) . The `shop` accessor is read from the `shopify-shop-domain`/`x-shopify-shop-domain` header independently, and is never mixed into the signable string: [2](#0-1) .

`Registry.process` validates only the HMAC-over-body via `Utils::HmacValidator.validate(request)`, then immediately dispatches the handler using `request.shop` (the unauthenticated header) as the tenant identity for the event: [3](#0-2) . `HmacValidator.validate` itself only ever hashes `verifiable_query.to_signable_string`, i.e., the body, against the app's shared `api_secret_key`: [4](#0-3) .

This breaks the identity binding: `hmac_valid(body, secret) == true` is treated as proof that `shop = header.shop`, when in fact the header value is fully attacker-controllable independent of the signature. Because a single app's `api_secret_key` is shared across every shop that installs it, any merchant who has the app installed possesses (via their own genuine, Shopify-delivered webhook traffic) a body+HMAC pair that validates successfully — but the `shop` header accompanying that body is not cryptographically tied to it.

### Impact Explanation
If an attacker can present a request to the app's public webhook endpoint with a genuine `(body, hmac)` pair but an arbitrary `shop` header, `Registry.process` will call the topic handler with `WebhookMetadata#shop` set to a shop the attacker does not own. Any host application that uses `shop` from `WebhookMetadata` as a lookup key (e.g., to load that shop's session/access token, write data, or trigger merchant-facing side effects) will act as if the event originated from the victim tenant — i.e., cross-tenant data confusion/access, matching the "Critical - cross-tenant access" category.

### Likelihood Explanation
Exploitability depends on the attacker obtaining a valid `(body, hmac)` pair without knowing `api_secret_key`, since they cannot forge an HMAC for an arbitrary chosen body themselves. This requires observing an in-flight, genuinely-signed webhook delivery for their own shop (e.g., via traffic they can view before it reaches the app), which is a real but non-trivial precondition. This keeps the finding in the same "requires favorable timing/observation, not directly forgeable from nothing" category as the referenced analog report, rather than a fully self-contained, no-precondition exploit.

### Recommendation
Include the shop domain (and ideally topic/webhook-id) as part of the HMAC-signable material, or otherwise require the host application to independently authenticate `shop` against a known, previously-registered/installed shop for that `webhook_id`/subscription before dispatching the handler. At minimum, document that `WebhookMetadata#shop` is unauthenticated header data and must not be trusted as a sole tenant key.

### Proof of Concept
```ruby
# Attacker has legitimate app install on their own shop "attacker.myshopify.com"
# and can observe (e.g. via a debugging proxy they control before forwarding to
# the app, or a captured historical delivery) a genuine Shopify webhook delivery:
#   body = '{"id": 1, ...attacker-owned data...}'
#   x-shopify-hmac-sha256 = <valid HMAC of body under the app's real api_secret_key>
#
# The attacker resends the exact same body + hmac to the app's public webhook
# endpoint, but swaps the shop header to a victim shop:

headers = {
  "x-shopify-topic" => "orders/create",
  "x-shopify-hmac-sha256" => captured_valid_hmac,      # matches `body`, unrelated to shop
  "x-shopify-shop-domain" => "victim-shop.myshopify.com", # attacker-chosen, not signed
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: captured_body, headers: headers)
ShopifyAPI::Webhooks::Registry.process(request)
# => Utils::HmacValidator.validate(request) returns true (body/hmac match)
# => handler.handle(data: WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...))
```

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
