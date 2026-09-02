### Title
Webhook `shop` domain used for tenant routing is not covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body [1](#0-0)  while `Registry.process` treats the `shop` value parsed from the `x-shopify-shop-domain` / `shopify-shop-domain` header as the trusted tenant identifier and hands it directly to the app's webhook handler [2](#0-1) . The header is read via `shopify_header("shop-domain")` [3](#0-2)  and is never included in the bytes that are HMAC-verified.

### Finding Description
The binding that should hold is: `shop_used_for_tenant_dispatch == shop_covered_by_hmac`. In this gem it does not.

`HmacValidator.validate` computes `computed_signature = HMAC-SHA256(secret, verifiable_query.to_signable_string)` and compares it to the value returned by `verifiable_query.hmac` [4](#0-3) . For webhooks, `hmac` is read from the `hmac-sha256` header and `to_signable_string` is just `@raw_body` [5](#0-4) [1](#0-0) . So the HMAC only proves that the body bytes were signed by Shopify with the app's secret; it says nothing about which shop the header claims the webhook is for.

`Registry.process` only checks `Utils::HmacValidator.validate(request)` (body HMAC) and then dispatches using `request.shop`, taken straight from the header, into `WebhookMetadata.new(topic: request.topic, shop: request.shop, body: request.parsed_body, ...)` which is passed to the app's `handler.handle` [2](#0-1) .

Because the `shop-domain` header is attacker-controllable independently of the signed body, and Shopify's own HMAC secret is shared across all shops that install an app (it is the app's `client_secret`, not a per-shop secret), any legitimate webhook delivery for Shop A (a real, HMAC-valid `{body, hmac}` pair captured or replayed from Shop A) can be redelivered by an unprivileged party with the `shop-domain` header rewritten to Shop B. `HmacValidator.validate` will still pass because it only checks the body, and the handler will process Shop-A's payload as if it belongs to Shop B — i.e., cross-tenant data gets attributed/dispatched to the wrong tenant's handler context, breaking the shop-identity binding the gem is supposed to enforce before calling into per-shop application logic.

### Impact Explanation
This crosses a tenant boundary: the merchant/tenant identity (`shop`) attached to webhook data delivered to the host application is not authenticated, only the body content is. Applications that key their per-shop session/store lookup off `WebhookMetadata#shop` (as the gem's own documentation instructs — `ShopifyAPI::Webhooks::Registry.process` is described as verifying "the request did indeed come from Shopify" before dispatch ) can be made to process another shop's webhook payload under the wrong shop identity, i.e. cross-tenant access facilitated entirely within this gem's verification logic.

### Likelihood Explanation
Exploitation requires capturing or being sent one valid `(raw_body, hmac)` pair for any shop (webhook deliveries are not secret to the receiving endpoint's network path, and retries/replays are a normal part of webhook delivery), then resending it with a modified `shop-domain` header value. No knowledge of `api_secret_key` or any access token is required — only reuse of already-observed signed bytes with an unauthenticated header changed. This is a directly reachable flaw in `Registry.process`'s own validation contract.

### Recommendation
Include the `shop` (and ideally `topic`/`webhook_id`) header values in the HMAC-covered signable content, or otherwise cryptographically bind them to the body before dispatch, so `Registry.process` cannot be tricked into associating a validly-signed body with an unauthenticated shop domain.

### Proof of Concept
```ruby
# Attacker captures a legitimate webhook delivery destined for shop-a.myshopify.com:
headers = {
  "x-shopify-topic" => "orders/create",
  "x-shopify-hmac-sha256" => captured_valid_hmac,   # valid for @raw_body, signed with app secret
  "x-shopify-shop-domain" => "shop-a.myshopify.com",
}
raw_body = captured_raw_body

# Attacker resends the same signed body but swaps the shop header:
tampered_headers = headers.merge("x-shopify-shop-domain" => "shop-b.myshopify.com")

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: tampered_headers)
ShopifyAPI::Webhooks::Registry.process(request)
# HmacValidator.validate only checks raw_body's HMAC -> passes.
# handler.handle receives WebhookMetadata(shop: "shop-b.myshopify.com", body: shop-a's payload)
``` [2](#0-1) [1](#0-0)

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-13)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
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
