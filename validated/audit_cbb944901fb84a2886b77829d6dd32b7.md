### Title
Webhook shop-domain header is not covered by the HMAC signature, enabling cross-tenant shop spoofing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, while `#shop` is read directly from the `X-Shopify-Shop-Domain` (or `Shopify-Shop-Domain`) header, a value that is never part of what the HMAC covers. `Registry.process` validates the HMAC against the body only and then hands `request.shop` straight to the app's webhook handler as the tenant identifier. An attacker who can obtain one genuinely signed webhook (e.g., by installing the app on their own store, which is a normal, unprivileged action) can replay that same body/HMAC pair while swapping the shop-domain header to any victim shop, and the signature check still passes.

### Finding Description
The identity binding that should hold is:

`shop_bytes_covered_by_hmac == shop_bytes_used_as_tenant_identifier`

In this gem that equality is broken:

- `HmacValidator.validate` only ever verifies `verifiable_query.to_signable_string` against the HMAC: [1](#0-0) 
- `Webhooks::Request#to_signable_string` returns just `@raw_body`, never the shop header: [2](#0-1) [3](#0-2) 
- `Registry.process` validates the HMAC and then trusts `request.shop` unconditionally to build the `WebhookMetadata` passed to the app's handler: [4](#0-3) 

Because the `shop-domain` header sits entirely outside the signed payload, HMAC validity only proves "this body was produced with the app's secret at some point," not "this body belongs to this shop." Any bytes that were legitimately signed for shop A (e.g., an `orders/create` payload from an attacker's own trial/test store, which they fully control and can capture) remain HMAC-valid when replayed with the shop header rewritten to shop B. `Registry.process` will still call the handler with `shop: "victim-shop.myshopify.com"` and the attacker-supplied body, since nothing re-derives or cross-checks the shop from signed material.

This mirrors the report's bug class: a field (`shop`) that is acted upon (used as the tenant/session key passed to the handler) is not covered by the very authentication mechanism (`HMAC`) that is supposed to prove the request's origin — analogous to the swETH oracle/calculator sharing an unguarded input that silently defeats the intended check.

### Impact Explanation
Any downstream app logic that trusts `WebhookMetadata#shop` to select which tenant's records to read/update/create (a standard and expected usage pattern for this field) can be made to attribute attacker-controlled webhook data to an arbitrary victim shop, without the attacker ever needing that victim's credentials, access token, or `client_secret`. This is a cross-tenant data-integrity/access issue reachable purely from a request the attacker fully controls, satisfying the Critical "cross-tenant access" bar.

### Likelihood Explanation
The prerequisite is only that the attacker have or create their own Shopify store to legitimately trigger a real, HMAC-signed webhook (a normal unprivileged action any developer/merchant can perform), then replay that captured HTTP request to the victim app's webhook endpoint with the `shop-domain` header changed. No secret material, no interception of TLS, and no access token are required, since the gem does not bind the shop identity into the signed bytes it verifies.

### Recommendation
Include the shop domain (and ideally the webhook topic/id) inside `to_signable_string` for webhook requests, or at minimum have `Registry.process`/the consuming app verify that `request.shop` corresponds to a shop with an active, previously-registered webhook subscription/session before invoking the handler, rather than trusting the unsigned header value outright.

### Proof of Concept
1. Install the target app (or a test copy of it) on an attacker-owned store `attacker.myshopify.com`, triggering a genuine `orders/create` webhook delivery with a valid `X-Shopify-Hmac-Sha256` header computed over the JSON body.
2. Capture the raw body and HMAC header from that delivery (e.g., via a local proxy since the attacker fully controls the receiving tunnel/endpoint during testing, or by using their own logging).
3. Replay the exact same body and `X-Shopify-Hmac-Sha256` value to the app's real webhook endpoint, but set `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
4. `HmacValidator.validate` succeeds because it only checks the body against the secret; `Registry.process` builds `WebhookMetadata.new(... shop: "victim-shop.myshopify.com" ...)` and invokes the handler, which now processes attacker-supplied order data as if it belonged to the victim shop.

### Citations

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
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
