### Title
Webhook `shop` identity is not bound to the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-verifiable content from the raw body only, while the `shop` (tenant identity) used downstream by `ShopifyAPI::Webhooks::Registry.process` is read from an unauthenticated header. Any party capable of producing one validly-signed webhook body/HMAC pair for the shared app `client_secret` (i.e., any merchant with the app installed) can replay that body with an arbitrary `shopify-shop-domain` header and have the library accept it as coming from a different tenant.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop` is derived purely from an HTTP header that plays no part in the signable string: [2](#0-1) 

`HmacValidator.validate` only checks that the received `hmac` matches `compute_signature(verifiable_query.to_signable_string, secret)`, i.e. it validates the body bytes, never the `shop` field: [3](#0-2) 

`Registry.process` then trusts `request.shop` as the tenant identity and hands it straight to the app's webhook handler without any additional binding check: [4](#0-3) 

This breaks the identity equality that should hold: `shop covered by the HMAC == shop acted on by the handler`. Since the app's `client_secret` is shared across every shop that installs the app (it is not per-shop), any merchant who has the app installed can legitimately obtain a body + valid HMAC pair for their own shop, then resend it to the app's webhook endpoint with the `shopify-shop-domain` (or `x-shopify-shop-domain`) header rewritten to a victim shop's domain. `HmacValidator.validate` will still return `true` (it never inspects the header), and `Registry.process` will dispatch the payload to the handler tagged with the attacker-chosen `shop`, `topic`, `webhook_id`, and `api_version` — none of which are covered by the signature.

### Impact Explanation
This is a cross-tenant identity confusion: data belonging to one shop can be attributed to another shop merely by relabeling an unauthenticated header, without needing the victim's access token, `client_secret`, or any credential beyond having the app installed on any shop. A host application that keys per-tenant side effects (e.g., writing order/customer data, triggering GDPR redaction flows for `shop/redact`, `customers/redact`) off `WebhookMetadata#shop` as provided by this gem can be made to apply attacker-supplied data/actions against another merchant's tenant record.

### Likelihood Explanation
Requires only that the attacker's own shop have the target app installed (a normal, unprivileged position for any merchant), and the ability to POST directly to the app's public webhook endpoint with modified headers — no interception, no leaked secrets, and no privileged Shopify credentials are needed, since only the raw body (not headers) is HMAC-protected.

### Recommendation
Include the tenant-identifying header (`shop`, and ideally `topic`/`webhook_id`) in the value that is HMAC-verified, or otherwise cryptographically bind them to the payload before dispatching to `Registry.process`, e.g. by having `to_signable_string` incorporate the shop domain, or by requiring the host application to separately verify shop-webhook association (already-registered webhook ids per shop) rather than trusting the header verbatim.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and receives a legitimate webhook, e.g. topic `orders/create`, with a real `shopify-hmac-sha256` value computed by Shopify using the app's shared `client_secret` over some `raw_body`.
2. Attacker resends the exact same `raw_body` and `shopify-hmac-sha256` value to the app's public webhook endpoint, but sets `shopify-shop-domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` accepts the request (all required headers present) and `Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only recomputes the HMAC over `raw_body`.
4. The handler is invoked with `WebhookMetadata.new(topic: "orders/create", shop: "victim-shop.myshopify.com", body: ..., ...)`, causing the host application to process attacker-controlled data under the victim shop's identity.

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
