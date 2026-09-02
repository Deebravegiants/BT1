### Title
Webhook shop attribution is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/utils/hmac_validator.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by verifying the HMAC of the raw request body. The shop that the webhook is attributed to (`X-Shopify-Shop-Domain` / `shopify-shop-domain` header) is never included in the signed data, so the binding "HMAC-verified secret owner" == "shop the data is attributed to" does not hold.

### Finding Description
`ShopifyAPI::Webhooks::Request` implements `Utils::VerifiableQuery`, but its `to_signable_string` returns only the raw body: [1](#0-0) 

The `shop` accessor is read straight from the `shopify-shop-domain`/`x-shopify-shop-domain` header, entirely outside the signed payload: [2](#0-1) 

`Registry.process` verifies only the HMAC of the request (i.e., the body) and then hands the *unauthenticated* `request.shop` straight to the app's handler as the tenant identifier: [3](#0-2) 

`HmacValidator.validate` computes the signature over `verifiable_query.to_signable_string` (the body only) using `Context.api_secret_key`: [4](#0-3) 

Because the signature covers only the body bytes, any `(body, hmac)` pair that is valid for the app's shared secret remains valid no matter what value is placed in the `shop-domain` header. A merchant who has the app installed on their own store (Shop A) can capture a legitimate webhook delivery (body + HMAC, both generated honestly by Shopify for Shop A) and replay it to the app's public webhook endpoint with the `X-Shopify-Shop-Domain` header rewritten to Shop B. `Utils::HmacValidator.validate` still returns `true` because it never looks at the shop header, and `WebhookMetadata.shop` — the field the gem explicitly hands to the app as the tenant identifier — is spoofed: [5](#0-4) 

The gem's own documentation instructs integrators to key their tenant-scoped processing directly off this unauthenticated field: [6](#0-5) 

This is structurally the same class of bug as the reported analog: the check that establishes trust (HMAC over body) does not cover the field that is subsequently used to make an authorization/attribution decision (the shop header), exactly like the reported `end - start` vs `end - block.timestamp` mismatch let a check pass while acting on the wrong operand.

### Impact Explanation
Any app built on this gem that keys per-tenant behavior (creating/updating/deleting local records, dispatching jobs, or making API calls scoped "for shop X") off `WebhookMetadata#shop` — exactly as the gem's own docs recommend — can be made to attribute genuine, HMAC-valid webhook data to an arbitrary other shop of the attacker's choosing. This is a cross-tenant confusion primitive: an attacker who is a legitimate merchant on their own shop can forge webhook attribution for any other shop known to have installed the app, without needing that shop's credentials, `client_secret`, or access token.

### Likelihood Explanation
`HmacValidator.validate` is unconditionally satisfied by a normal, unmodified webhook body and its normal HMAC — no cryptographic secret needs to be recovered, only the header needs to be rewritten before it reaches the app's webhook controller. Any actor who can install the app on a store (i.e. any Shopify merchant) can generate a valid `(body, hmac)` pair at will and replay it with an altered shop header. No special network position, TLS interception, or leaked secret is required.

### Recommendation
Include the shop domain (and ideally topic / webhook id) in the HMAC-signed material, or independently verify that the shop asserted in the header matches a shop the app has a valid, previously-established installation/session for before trusting `WebhookMetadata#shop` in `Registry.process`. At minimum, `Utils::HmacValidator` / `Webhooks::Request#to_signable_string` should bind the shop header into the value that is HMAC-verified so a body+HMAC pair cannot be replayed under a different shop identity.

### Proof of Concept
1. App has `shopify_api` gem installed, is installed on `shop-a.myshopify.com`, and registers `orders/create` with a handler that does `perform_later(shop_domain: data.shop, ...)` as shown in the gem's own docs.
2. Attacker owns `shop-a.myshopify.com`, creates an order, and captures Shopify's legitimate webhook delivery: raw body `B` and header `X-Shopify-Hmac-Sha256: H` (valid for the app's `api_secret_key`).
3. Attacker POSTs the exact same `B` and `H` to the app's webhook endpoint, but sets `X-Shopify-Shop-Domain: shop-b.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes HMAC over `request.to_signable_string` (== `B`) and compares to `H` — validation succeeds because the shop header was never part of the signed data.
5. The handler receives `WebhookMetadata` with `shop == "shop-b.myshopify.com"` and `body` containing Shop A's order data, and processes/stores it as if it belonged to Shop B.

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
