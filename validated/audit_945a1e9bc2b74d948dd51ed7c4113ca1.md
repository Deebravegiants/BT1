### Title
Webhook HMAC verification does not cover the `shop-domain` header, allowing shop-identity spoofing in processed webhooks - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, and `HmacValidator` verifies the HMAC solely against that body. The `shop` (and `topic`) values used by `Registry.process` to build `WebhookMetadata` and dispatch to the host app's handler come from HTTP headers that are never included in the signed data, breaking the binding between "HMAC-authenticated bytes" and "shop identity acted upon."

### Finding Description
`Request#to_signable_string` is defined as: [1](#0-0) 
which returns only `@raw_body`. The `shop` accessor is read straight from the `shopify-shop-domain`/`x-shopify-shop-domain` header without ever being folded into the signed string: [2](#0-1) 

`HmacValidator.validate` computes and compares the HMAC exclusively over `verifiable_query.to_signable_string`: [3](#0-2) 

`Registry.process` trusts `request.shop` (and `request.topic`) to build the data passed to the host app's handler after only checking the body HMAC: [4](#0-3) 

The equality that should hold is: `shop bound by HMAC == shop acted upon by the handler`. In this implementation, `shop acted upon` (`request.shop`, forwarded into `WebhookMetadata.shop`) is never part of the bytes covered by `shop bound by HMAC` (only `@raw_body` is signed). Any entity that possesses one genuinely Shopify-signed webhook body/HMAC pair — which merely requires operating a shop that has installed the app and receiving one legitimate webhook delivery, no `api_secret_key` needed — can resubmit that same body+HMAC to the app's webhook endpoint with an arbitrary `shop-domain` header. `HmacValidator.validate` will still return `true` because it never inspects the header, and `Registry.process` will hand the handler a `WebhookMetadata` claiming the payload belongs to whichever shop the attacker put in the header.

### Impact Explanation
Host applications are expected to use `WebhookMetadata#shop` as the tenant identifier when persisting/acting on webhook payloads (that's the documented purpose of the field). Because the shop identity is unauthenticated, an attacker who has legitimately received one valid signed webhook for their own shop can replay it while claiming it belongs to a different merchant's shop, causing the host app to associate/store attacker-controlled data under another tenant's identity — a cross-tenant data integrity violation reachable purely by an internet-accessible party without any privileged credential.

### Likelihood Explanation
High: an attacker only needs to install the app on any shop (a normal, unprivileged action) to receive one legitimately signed webhook delivery, then can freely resend that same body/HMAC pair to the app's public webhook endpoint with a modified `shop-domain` header. No secret material is required.

### Recommendation
Include the shop domain (and topic) in the signable string used for HMAC computation, or otherwise cryptographically bind the header-derived `shop`/`topic` values to the signed payload before trusting them in `Registry.process`/`WebhookMetadata`.

### Proof of Concept
1. Install the app on `attacker-shop.myshopify.com`; capture one legitimate webhook delivery — raw body `B` and header `x-shopify-hmac-sha256: H` (valid HMAC of `B`), plus `x-shopify-shop-domain: attacker-shop.myshopify.com`.
2. Send a new HTTP request to the host application's webhook endpoint with the same body `B` and same `x-shopify-hmac-sha256: H`, but set `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` accepts the headers, `HmacValidator.validate` succeeds (it only checks `B` against `H`), and `Registry.process` invokes the handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: parsed(B), ...)`, causing the host app to attribute attacker-controlled payload data to `victim-shop`.

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
