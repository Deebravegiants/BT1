### Title
Webhook Shop-Domain Header Not Covered by HMAC Enables Cross-Tenant Webhook Spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable content from the raw body only, while the `shop` (and `topic`/`webhook_id`/`api_version`) values are read from unauthenticated HTTP headers. `Utils::HmacValidator` and `Webhooks::Registry.process` only verify that the body matches a valid signature, then trust `request.shop` as the tenant identity handed to the app's webhook handler. Any party capable of relaying a request to the app's webhook endpoint can keep a previously-issued, validly-signed body/HMAC pair and substitute an arbitrary `x-shopify-shop-domain` (or `shopify-shop-domain`) header value, causing the gem to report a different, attacker-chosen shop to the host application's handler.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop` is derived purely from a header that is never part of the signed data: [2](#0-1) 

`HmacValidator.validate` computes and compares the signature exclusively over `verifiable_query.to_signable_string`: [3](#0-2) 

`Registry.process` validates the HMAC and then immediately trusts `request.shop` as the tenant identity forwarded to the registered handler, with no additional binding check between the verified body and the shop header: [4](#0-3) 

The binding this breaks: `shop authenticated by HMAC` should equal `shop delivered to the handler`, but here `hmac covers {raw_body}` while `shop delivered = header["shopify-shop-domain"]`, an entirely independent, unauthenticated field. Since the signature never binds to the shop identity, a valid `(body, hmac)` pair issued by Shopify for shop A can be replayed with the header changed to shop B, and the gem will report the event as originating from shop B.

### Impact Explanation
This crosses a tenant boundary inside the gem's own webhook-processing code path: the `shop` value that host applications rely on (as seen in `WebhookMetadata.new(... shop: request.shop ...)`) is not authenticated, only the body is. A host application that (reasonably, per this gem's documented API) trusts `data.shop` to determine which merchant's data/record to update can be made to apply another merchant's webhook payload to the wrong tenant, i.e., cross-tenant data confusion/access. This matches the "Critical - cross-tenant access" impact category.

### Likelihood Explanation
Exploitation only requires a party who can obtain one legitimately signed webhook delivery for their own shop (any merchant that installs the app receives such webhooks) and the ability to POST a modified copy of it (same raw body/HMAC, different shop header) to the app's public webhook endpoint. No knowledge of `api_secret_key` is needed, no privileged access, and no cryptographic break — only reuse of a previously-observed valid signature with a substituted unauthenticated header.

### Recommendation
Include the shop domain (and ideally topic/webhook id) as part of the value that must be authenticated before being trusted, or reject/ignore `request.shop` unless it can independently be corroborated (e.g., match it against the shop the delivery was registered for) rather than trusting the raw header once the body-only HMAC passes. At minimum, document prominently that `request.shop` is unauthenticated data and must not be used as a sole tenant-selection key without additional server-side verification.

### Proof of Concept
1. App has webhooks registered; shop `a.myshopify.com` (any existing/installed merchant, i.e., an unprivileged actor from the app's perspective) receives a legitimate webhook delivery from Shopify:
   - Headers: `x-shopify-shop-domain: a.myshopify.com`, `x-shopify-hmac-sha256: <valid-hmac-of-body>`, `x-shopify-topic: orders/create`
   - Body: `{"id":123,...}`
2. Attacker (that same merchant, or anyone able to intercept/replay the request to the app's public webhook URL) resends the exact same body and HMAC, but changes the header to:
   - `x-shopify-shop-domain: victim-shop.myshopify.com`
3. `HmacValidator.validate` in `lib/shopify_api/utils/hmac_validator.rb` recomputes the HMAC over the unchanged raw body and it still matches, so validation succeeds.
4. `Registry.process` in `lib/shopify_api/webhooks/registry.rb` calls the handler with `shop: request.shop` == `"victim-shop.myshopify.com"`, even though the payload was never authorized for that shop, demonstrating the cross-tenant identity confusion caused by the shop-domain header being excluded from the signed content.

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
