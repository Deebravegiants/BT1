This confirms the vulnerability pattern. The `Registry.process` method validates only `Utils::HmacValidator.validate(request)`, which computes the HMAC exclusively over `to_signable_string` (the raw body) as defined in `lib/shopify_api/webhooks/request.rb`. The `shop` field, sourced from the `shopify-shop-domain`/`x-shopify-shop-domain` header, is never included in the signed content, yet it is passed directly into `WebhookMetadata` and handed to the app's `handler.handle` callback as the tenant identifier.

### Title
Webhook shop-domain header not covered by HMAC allows cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` derives the `shop` (tenant identity) from the `shopify-shop-domain` HTTP header, but the HMAC signature validated by `Utils::HmacValidator` only covers the raw request body. Any party capable of obtaining one genuinely-signed webhook body/HMAC pair (e.g., by installing the app on their own store and receiving a legitimate webhook) can replay that exact body and HMAC to the app's public webhook endpoint while substituting an arbitrary `shopify-shop-domain` header. The signature still validates, and the handler is invoked believing the payload originated from the spoofed shop.

### Finding Description
`Utils::HmacValidator.validate` computes and compares the signature strictly against `verifiable_query.to_signable_string`: [1](#0-0) 

For webhooks, `to_signable_string` returns only `@raw_body`: [2](#0-1) 

Meanwhile `shop`, `topic`, `api_version`, and `webhook_id` are all read straight from attacker-controllable HTTP headers, none of which factor into the HMAC computation: [3](#0-2) 

`Registry.process` validates only the HMAC of the body, then dispatches to the registered handler using the unverified `request.shop`, `request.topic`, and other header-derived fields as trusted metadata: [4](#0-3) 

The binding broken is: **shop authenticated by HMAC vs. shop delivered to the handler** — these are not the same value. The HMAC proves the body's integrity/authenticity against `api_secret_key`, but says nothing about which shop, topic, or webhook-id the body is associated with. Because the app's own client (this gem) treats the header-sourced `shop`/`topic`/`webhook_id` as authenticated once `HmacValidator.validate` passes, host applications built on top of `WebhookMetadata` will trust cross-tenant-sensitive fields that were never actually signed.

### Impact Explanation
An attacker who can obtain any single valid `(raw_body, hmac)` pair — trivially available by installing the target app on their own store, since Shopify signs webhooks using the app's single global `api_secret_key` shared across all installations — can forge the `shop`, `topic`, and `webhook_id` headers on a replayed request to the app's public webhook endpoint. If the host application uses `WebhookMetadata#shop` to key data writes/lookups (the intended and documented use, per `handler.handle(data: WebhookMetadata.new(topic: ..., shop: request.shop, ...))`), this enables cross-tenant data confusion: injecting another merchant's webhook events under an attacker-chosen shop, or vice versa, without ever needing that shop's own credentials. This meets the Critical bar of "cross-tenant access" via a credential/tenant-binding bypass rooted in this gem's own verification logic.

### Likelihood Explanation
Exploitation only requires: (1) any store that has this exact app installed (which can be the attacker's own store, if the app is publicly installable), (2) network access to POST to the webhook endpoint (already public by design), and (3) capturing one legitimate webhook delivery. No access to `api_secret_key`, access tokens, or the target shop's credentials is required. Every field except the raw body is forgeable at will.

### Recommendation
Bind the tenant/topic identity into the signed content that HmacValidator verifies, e.g., include `shop`, `topic`, and `webhook_id` in `to_signable_string` (or perform a secondary comparison against values embedded/derivable from the verified body), so that spoofing a header without the correspondingly-signed value fails validation. At minimum, document prominently that `WebhookMetadata#shop`/`#topic`/`#webhook_id` are NOT covered by the HMAC and must not be used by host apps as a trusted tenant key without independent verification (e.g., cross-checking against the session/shop the webhook subscription was registered under).

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com`, triggering a legitimate `orders/create` webhook. Attacker captures the raw POST body `B` and its valid header `x-shopify-hmac-sha256: H` (computed by Shopify using the shared `api_secret_key`).
2. Attacker sends a new POST to the app's public webhook endpoint with the same body `B` and the same `hmac` header `H`, but sets `x-shopify-shop-domain: victim-shop.myshopify.com` and/or a different `x-shopify-webhook-id`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only checks `B` against `H`: [5](#0-4) 
4. The registered `handler.handle` receives `WebhookMetadata` with `shop: "victim-shop.myshopify.com"` even though the payload was never actually sent by Shopify for that shop, causing the host app to process/store the attacker's data as if it belonged to the victim tenant.

### Citations

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

**File:** lib/shopify_api/webhooks/request.rb (L15-33)
```ruby
      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
      end

      sig { returns(String) }
      def api_version
        T.cast(shopify_header("api-version"), String)
      end

      sig { returns(String) }
      def webhook_id
        T.cast(shopify_header("webhook-id"), String)
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
