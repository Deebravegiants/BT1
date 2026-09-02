Confirmed: `to_signable_string` in `lib/shopify_api/webhooks/request.rb:36-38` returns only `@raw_body`, and the HMAC in `lib/shopify_api/utils/hmac_validator.rb` is computed exclusively over that raw body via `verifiable_query.to_signable_string`. Meanwhile `shop`, `topic`, `api_version`, and `webhook_id` are all read straight out of unauthenticated HTTP headers and passed into the handler unchecked in `lib/shopify_api/webhooks/registry.rb:189-199`.

### Title
Webhook shop identity is read from an unauthenticated header not covered by the HMAC, enabling cross-tenant webhook replay - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` derives the merchant identity (`shop`) from the `x-shopify-shop-domain`/`shopify-shop-domain` HTTP header, but the HMAC signature that `Registry.process` validates only covers the raw request body, not this header.

### Finding Description
`Request#to_signable_string` returns solely `@raw_body`: [1](#0-0) 
and `HmacValidator.validate_signature` computes/compares the signature purely against that string: [2](#0-1) 
`Registry.process` accepts the request once `Utils::HmacValidator.validate(request)` passes, then builds `WebhookMetadata` directly from `request.shop`, `request.topic`, etc., all of which are pulled from headers: [3](#0-2) [4](#0-3) 

This is exactly the "field acted on but not covered by the HMAC" identity-binding break: the shop identity that the merchant handler code trusts (`data.shop`) is not equal to the shop bound to the HMAC-signed bytes (which sign nothing about shop identity at all). Any actor who can obtain one genuine `(raw_body, hmac)` pair signed with the app's own secret — for example, by installing the app on their own shop and capturing the webhook Shopify sends them — can replay that exact body/HMAC pair to the app's public webhook endpoint while substituting an arbitrary `x-shopify-shop-domain` header value. The signature check still passes because the header is never part of the signed content, yet the handler will process the payload as if it belongs to the spoofed shop.

### Impact Explanation
This breaks the binding `shop_authenticated_by_hmac == shop_used_by_handler`, letting a merchant/attacker who legitimately installed the app on shop A inject fabricated webhook data (order, customer, GDPR, etc.) attributed to an arbitrary shop B into the host application's per-tenant processing — a cross-tenant data-integrity/confidentiality issue reachable purely through this gem's `Webhooks::Registry`/`Request`/`HmacValidator` API, with no need for shop B's credentials.

### Likelihood Explanation
Exploitation only requires the attacker to be a legitimate (even free/trial) merchant able to install the target app on their own store to capture one valid `(body, hmac)` pair, then send an HTTP POST to the app's public webhook endpoint with a forged shop-domain header. No access to `api_secret_key`, tokens, or the victim shop is needed, and the webhook endpoint is by design internet-reachable.

### Recommendation
Bind the shop (and ideally topic) identity into the verified signature material, or otherwise cryptographically tie the header-derived `shop` value to the authenticated request — e.g., include the shop domain in `to_signable_string`, or have `Registry.process` cross-check `request.shop` against a value obtained from a trusted, signed source (such as re-deriving it via the GraphQL Admin session) before invoking the handler.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker.myshopify.com` and registers a webhook for a topic the app handles (e.g., `orders/create`).
2. Shopify delivers a webhook to the app's endpoint with headers `x-shopify-shop-domain: attacker.myshopify.com`, `x-shopify-hmac-sha256: <valid HMAC of raw_body>`, and some `raw_body`.
3. Attacker captures this exact `raw_body` and `hmac` value.
4. Attacker sends a new POST to the same app endpoint with the identical `raw_body` and `hmac` header, but sets `x-shopify-shop-domain: victim.myshopify.com`.
5. `HmacValidator.validate` (`lib/shopify_api/utils/hmac_validator.rb:13-22`) succeeds because it only checks `raw_body` against the HMAC.
6. `Registry.process` (`lib/shopify_api/webhooks/registry.rb:189-199`) invokes the registered handler with `WebhookMetadata.new(shop: "victim.myshopify.com", ...)`, causing the host app to process attacker-controlled data under the victim shop's tenant context.

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
