### Title
Webhook Tenant Spoofing via Unsigned `shop-domain` Header - ([File: lib/shopify_api/webhooks/registry.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by HMAC-validating the raw request body, then trusts the unsigned `x-shopify-shop-domain` (or `shopify-shop-domain`) header to identify which merchant/tenant the event belongs to. Because the HMAC signature never covers this header, the binding `hmac_signed_shop == request.shop` does not exist, allowing an attacker who can obtain one valid `(body, hmac)` pair to relabel it to an arbitrary victim shop.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw HTTP body: [1](#0-0) 

The `shop`, `topic`, `webhook_id`, and `api_version` fields are all pulled straight from HTTP headers, independently of the signed body: [2](#0-1) 

`Utils::HmacValidator.validate` computes the HMAC exclusively over `verifiable_query.to_signable_string` (i.e., the raw body) and compares it to the `hmac` header: [3](#0-2) 

`Registry.process` performs this body-only HMAC check and then immediately trusts `request.shop` to build the `WebhookMetadata` that is dispatched to the app's business-logic handler, without any additional check that the `shop` header was itself covered by the signature: [4](#0-3) 

This is exactly the bug class in the external report generalized to this codebase: a value (`slot0`/`sqrtPriceX96` there, `shop-domain` header here) is used to make a security-relevant decision (tenant attribution) but is not covered by the integrity mechanism that is supposed to authenticate the whole message (TWAP-protected price there, HMAC signature here). The equality that should hold — `shop_bound_by_hmac == shop_used_for_tenant_dispatch` — is broken because the HMAC only binds the body, not the shop header.

### Impact Explanation
Because the shop identity is never part of the signed content, any attacker capable of producing one valid `(raw_body, hmac)` pair for the app's `client_secret` (e.g., by having the app installed on their own shop and triggering a webhook whose body they control) can replay that exact body/HMAC pair while substituting the `x-shopify-shop-domain` header for a victim shop. `Registry.process` will still pass HMAC validation and will invoke the app's webhook handler with `WebhookMetadata#shop` set to the victim's domain, causing the host application to process attacker-controlled webhook data as if it originated from a different tenant. This is a cross-tenant data-integrity break in an unprivileged, internet-reachable code path (the app's public webhook endpoint), matching the report's "Critical - cross-tenant access" impact category.

### Likelihood Explanation
The `Registry.process` method is the exact, documented entry point host apps call to process every incoming Shopify webhook, so the vulnerable code path is always reachable by anyone who can send HTTP requests to the app's webhook endpoint. No secret material, session, or elevated privilege is required beyond obtaining one legitimately-signed webhook body (trivially available to any merchant who installs the app on their own store and generates events).

### Recommendation
Bind the shop identity to the signed payload before dispatching to handlers — e.g., verify that the `shop` header value present in the delivery matches a shop that the app has an active, previously-established session/installation for (looked up independently of the header), or require the host application to cross-check `request.shop` against Shopify's registered webhook delivery metadata rather than trusting the header outright. At minimum, document prominently that `Registry.process` performs no tenant-binding beyond an unauthenticated header and that host applications must not use `request.shop` as an authorization decision without an independent installation/session lookup.

### Proof of Concept
1. Attacker installs the target app on `attacker.myshopify.com` and triggers any subscribed webhook topic (e.g. `products/update`) with a body they fully control.
2. Attacker captures the resulting `x-shopify-hmac-sha256` header and raw body — both valid, since the HMAC is computed only over the body using the app's shared `client_secret`. [5](#0-4) 
3. Attacker resends the identical body and HMAC header to the app's webhook endpoint, but sets `x-shopify-shop-domain: victim.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` validates the HMAC successfully (body unchanged) and calls the handler with `WebhookMetadata.new(... shop: "victim.myshopify.com" ...)`. [6](#0-5) 
5. The host application processes attacker-controlled data under the victim shop's tenant context.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-23)
```ruby
      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

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
