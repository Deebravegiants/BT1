### Title
Webhook shop identity spoofing via HMAC that covers only the request body - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable content from the raw body only, while the `shop` (tenant identity) is read from an unsigned HTTP header. `Registry.process` validates the HMAC and then trusts that header value as the webhook's shop identity, breaking the binding: `bytes verified (raw_body) != bytes that determine tenant (shop-domain header)`.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

The `shop` accessor, however, is read straight from the `shopify-shop-domain`/`x-shopify-shop-domain` HTTP header, which is not part of the signed content: [2](#0-1) 

`Registry.process` validates the HMAC over the request (i.e., over `raw_body` only) via `HmacValidator.validate`, and — once that check passes — unconditionally forwards `request.shop` to the app's handler as the authoritative tenant identifier: [3](#0-2) 

`HmacValidator.validate` computes the signature purely from `verifiable_query.to_signable_string`, i.e. the body, and compares it to the header-supplied HMAC: [4](#0-3) 

Because the HMAC secret (`client_secret`) is the same for every shop that has installed a given app, a valid `(raw_body, hmac)` pair obtained from a legitimate webhook delivered to one merchant's own store remains cryptographically valid when replayed with the `shop-domain` header rewritten to name a different, victim shop. The gem has no mechanism to bind the signed body to the specific shop-domain header; it only proves "this body was signed by this app's secret," not "this body came from this shop." This is the exact "bytes verified vs. bytes parsed"/"shop authenticated vs. shop used as identity key" pattern called out in the analog rules.

### Impact Explanation
This is a cross-tenant identity confusion: an unprivileged user who has installed the app on their own shop (a normal, unprivileged install) can capture one authentic webhook (raw_body + hmac) and then submit it to the app's webhook endpoint while spoofing the `shop-domain` header to any other shop that also uses this app. `Registry.process` will pass HMAC validation and hand the attacker-controlled body to the app's handler tagged with the victim's shop, letting the attacker inject fabricated webhook data attributed to a shop they do not control. Depending on how the host application keys its webhook handling logic (order/customer/product state sync, access-token lookups, background jobs, etc.) off `WebhookMetadata#shop`, this enables cross-tenant data injection/corruption without any credential belonging to the victim shop.

### Likelihood Explanation
Medium-High: no secret material or victim credentials are required. An attacker who is themself a legitimate merchant installing the app can freely generate real, correctly signed webhook payloads for their own shop, capture the raw body and `X-Shopify-Hmac-Sha256` value, and replay them against the same publicly reachable webhook endpoint with an altered `X-Shopify-Shop-Domain` header. This is well within "unprivileged internet user" capability described in the task rules.

### Recommendation
Include the `shop` value in the HMAC-signed content (or otherwise cryptographically bind the shop identity to the request), e.g. incorporate the `shop-domain` header into `to_signable_string`, or require the host application to independently confirm that a shop-scoped access token/session exists and matches before treating `request.shop` as authoritative. At minimum, document (and preferably enforce in `Registry.process`) that the shop-domain header must be cross-checked against a known, previously provisioned webhook registration/session for that shop before dispatching to the handler.

### Proof of Concept
1. Attacker installs the app for their own shop `attacker-shop.myshopify.com` and triggers a webhook (e.g., `orders/create`) with body `B`; Shopify sends `X-Shopify-Hmac-Sha256: H` where `H = HMAC-SHA256(client_secret, B)`.
2. Attacker captures `B` and `H` from this legitimate request.
3. Attacker POSTs to the app's public webhook endpoint with:
   - Body: `B` (unchanged)
   - `X-Shopify-Hmac-Sha256: H` (unchanged, still valid because it only signs `B`)
   - `X-Shopify-Shop-Domain: victim-shop.myshopify.com` (rewritten)
   - `X-Shopify-Topic`: unchanged or attacker's choice of registered topic.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it validates `raw_body` (`B`) against `H`. [5](#0-4) 
5. The handler is invoked with `WebhookMetadata` where `shop == "victim-shop.myshopify.com"` but `body == B` (attacker's own, fully attacker-controlled data), completing the cross-tenant spoof.

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
