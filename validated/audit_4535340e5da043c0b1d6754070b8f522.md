### Title
Webhook `shop` (and `topic`/`api-version`/`webhook-id`) fields are not covered by the HMAC signature, allowing cross-tenant webhook replay — (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` reads the tenant-identifying `shop` field from an HTTP header, but `to_signable_string` — the value the HMAC is computed and verified over — only returns the raw request body. The header carrying the shop domain is never bound into the HMAC. An attacker who obtains one legitimately-signed `(body, HMAC)` pair (e.g., by installing the app on their own store and capturing a webhook Shopify delivers to their endpoint) can replay the exact same body and HMAC while swapping the `X-Shopify-Shop-Domain` header to a victim shop, and `HmacValidator.validate` will still accept it.

### Finding Description
`Webhooks::Request` exposes: [1](#0-0) 
`shop` reads straight from `shopify-shop-domain`/`x-shopify-shop-domain` header with no cryptographic binding.

Meanwhile `to_signable_string`, the only input to signature verification, is: [2](#0-1) 

`HmacValidator.validate` computes the signature purely from `to_signable_string` (i.e., the raw body) and compares it to the `hmac-sha256` header: [3](#0-2) 

`Registry.process` validates only this HMAC-over-body, then forwards `request.shop` (attacker-controlled, unauthenticated) straight to the app's webhook handler as the tenant identifier: [4](#0-3) 

The equality that should hold is: `shop bytes covered by HMAC == shop bytes the app attributes the webhook body to`. Here, the HMAC covers only the body, while the `shop` used for tenant attribution is parsed independently from an unauthenticated header — the exact "field acted on but not covered by the HMAC" bug class.

### Impact Explanation
Any unprivileged internet user who can obtain one genuine `(raw_body, hmac-sha256)` pair for *any* shop (trivially available by installing a public app on their own free development store and capturing a delivered webhook) can:
1. Keep the body and HMAC unchanged (so HMAC validation passes).
2. Replace `X-Shopify-Shop-Domain` with a victim shop's domain.
3. POST this forged request to the app's webhook endpoint.

`ShopifyAPI::Webhooks::Registry.process` will accept it as authentic (HMAC checks out) and hand the handler a `WebhookMetadata` claiming the body originated from the victim shop. If the host application's handler uses `data.shop` to select the tenant/session/database row to update (which is exactly the documented purpose of `shop` in `WebhookMetadata`), this allows cross-tenant data injection/corruption — e.g., poisoning another merchant's locally stored order/customer/product state with attacker-chosen content, or triggering redaction/compliance webhook handling (`shop/redact`, `customers/redact`) against the wrong tenant. This is a cross-tenant access impact.

### Likelihood Explanation
High for an attacker willing to install the app once: obtaining a valid signed body/HMAC pair requires no privileged access — public apps can be installed on any development store, and any subscribed webhook topic yields a valid `(body, hmac)` pair signed with the app's real secret. Swapping the shop header is trivial since it is not part of the signed data.

### Recommendation
Bind the shop (and topic/webhook-id) into the value that is HMAC-verified, or otherwise cryptographically tie the header claims to the signed payload before trusting them for tenant attribution — e.g., require the host application to cross-check `request.shop` against a shop already known/authorized for the specific `webhook_id`/subscription, or include the shop domain in the signable string used by `to_signable_string` if Shopify's signing scheme is extended to support it. At minimum, document/enforce that `data.shop` from `WebhookMetadata` must never be trusted as an authenticated tenant identifier unless cross-validated against a pre-registered mapping (e.g., stored session's shop) before use.

### Proof of Concept
```ruby
# Step 1: Attacker installs the app on their own store "attacker-shop.myshopify.com"
# and captures a legitimate webhook Shopify sends them, e.g. for orders/create:
raw_body = '{"id":123,"note":"legit order body"}'
valid_hmac_b64 = "<hmac captured from Shopify's real request to attacker's endpoint>"

# Step 2: Attacker replays the SAME body + SAME hmac, but swaps the shop header
# to the victim's domain:
forged_headers = {
  "x-shopify-topic" => "orders/create",
  "x-shopify-hmac-sha256" => valid_hmac_b64,       # unchanged, still validates
  "x-shopify-shop-domain" => "victim-shop.myshopify.com", # forged
  "x-shopify-api-version" => "2024-01",
  "x-shopify-webhook-id" => "forged-id",
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: forged_headers)

# HMAC validation passes because it only checks raw_body, not the shop header:
ShopifyAPI::Utils::HmacValidator.validate(request) # => true

# Registry.process accepts it and calls the handler with shop: "victim-shop.myshopify.com"
ShopifyAPI::Webhooks::Registry.process(request)
```
`Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-200`) raises no error here since `Utils::HmacValidator.validate(request)` returns `true`; the handler receives `WebhookMetadata` attributing `raw_body` to `victim-shop.myshopify.com`, even though the body was never actually sent by Shopify for that shop.

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
