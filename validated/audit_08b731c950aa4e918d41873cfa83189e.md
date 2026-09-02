Confirmed: `Webhooks::Request` implements `VerifiableQuery` with `to_signable_string` returning only `@raw_body`, while `shop`, `topic`, `webhook_id`, and `api_version` are pulled from HTTP headers that are never fed into the signable string. `HmacValidator.validate` (`lib/shopify_api/utils/hmac_validator.rb`) only checks the raw body against the HMAC, and `Registry.process` (`lib/shopify_api/webhooks/registry.rb`) trusts `request.shop` for tenant attribution after that check passes.

### Title
Webhook shop-domain header is not covered by HMAC verification, allowing cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant-identifying `shop` (and `topic`/`webhook_id`/`api_version`) from HTTP headers, but the HMAC signature that `Registry.process` verifies is computed solely over the raw request body via `to_signable_string`. Any party capable of obtaining one genuine `(raw_body, hmac)` pair for their own shop can resubmit that exact payload to the app's webhook endpoint with a different `x-shopify-shop-domain` header, and it will still pass HMAC validation, causing the app to process the webhook as if it belonged to another tenant.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop`, `topic`, `api_version`, and `webhook_id` are all read straight from HTTP headers, which are outside of the signed material: [2](#0-1) 

`HmacValidator.validate` computes the HMAC exclusively from `verifiable_query.to_signable_string` (i.e., the body) and compares it to the `hmac` header: [3](#0-2) 

`Registry.process` treats a passing HMAC check as authorization to trust `request.shop` for dispatch to the app's handler: [4](#0-3) 

The identity binding that should hold is: `shop header value == shop the signed body actually originated from`. Because the HMAC only binds the body, not the header, this equality is never enforced by the gem — the `shop` field is "acted on" (passed to the handler and typically used by the host app to select which tenant's records to update, per the documented handler example `perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)`) without being covered by the cryptographic check.

### Impact Explanation
This is a cross-tenant identity-binding break: a body+HMAC pair legitimately produced for Shop A can be replayed with the `x-shopify-shop-domain` header rewritten to Shop B, and `Utils::HmacValidator.validate` will still return `true` since it never inspects the header. The receiving app then executes its webhook handler believing the event originated from Shop B, potentially applying Shop A's data/mutations to Shop B's tenant context. Any actor who can install the app on their own shop (a merchant, hence "unprivileged" with respect to other tenants) can capture a genuine webhook for their own store and use it to inject spoofed events attributed to any other shop domain, since nothing before the HMAC check enforces `shop == origin of the signed bytes`.

### Likelihood Explanation
Exploitation requires only the ability to install the app once (to receive one real signed webhook body/HMAC pair for the attacker's own shop) and the ability to send an HTTP request to the app's public webhook endpoint with a modified header — no knowledge of `api_secret_key` is needed since the HMAC still matches the unmodified body. This is straightforward to carry out for any app that dispatches business logic based on `data.shop` from `WebhookMetadata`, as recommended in the gem's own documentation.

### Recommendation
Bind the shop (and topic/webhook id) into the material that is HMAC-verified, or otherwise cryptographically tie the `shop-domain` header to the specific signed body (e.g., have `to_signable_string` incorporate the header values, or independently verify that the `shop` header matches a shop the app has an active installation/session for before dispatching to the handler).

### Proof of Concept
1. App installs on `attacker-shop.myshopify.com`; attacker captures a legitimate webhook POST, including `raw_body`, and headers `x-shopify-hmac-sha256`, `x-shopify-topic`, `x-shopify-webhook-id`, `x-shopify-shop-domain: attacker-shop.myshopify.com`.
2. Attacker resends the identical request to the app's webhook endpoint, changing only `x-shopify-shop-domain` to `victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC from `request.to_signable_string` (the unmodified `raw_body`) and compares against the unmodified `hmac` header — validation succeeds. [4](#0-3) 
4. The registered handler is invoked with `WebhookMetadata` carrying `shop: "victim-shop.myshopify.com"`, even though the signed body never originated from that shop, and the host app (following the gem's documented pattern) performs tenant-scoped work keyed on this spoofed value.

### Citations

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
