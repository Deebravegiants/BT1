### Title
Webhook `shop` (and `topic`) header trusted for tenant identification without being covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` — the value that `HmacValidator` HMACs and verifies — is defined as the raw HTTP body only. The `shop`, `topic`, `webhook_id`, and `api_version` values are read directly from HTTP headers and are never included in the signed content, yet `Registry.process` forwards `request.shop` straight to the app's webhook handler as the authoritative tenant identifier.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop`, `topic`, `webhook_id`, and `api_version` are all pulled from headers, entirely outside the signed material: [2](#0-1) 

`HmacValidator.validate` only checks `verifiable_query.hmac` against `compute_signature(verifiable_query.to_signable_string, secret)`, i.e. against the body alone for webhook requests: [3](#0-2) 

`Registry.process` validates the HMAC and then immediately trusts `request.shop` (and `request.topic`) as the tenant/routing identity passed to the app's handler: [4](#0-3) 

The broken binding, stated as an equality that should hold but doesn't:
`shop_that_the_HMAC_authenticates == shop_the_handler_acts_on`

In reality the HMAC authenticates only the body bytes; the `shop` value handed to the handler is unauthenticated header data. Any party capable of producing one validly-signed webhook body (e.g., by installing the app on their own development/test store and receiving genuine Shopify webhooks for it, since `client_secret` is not required to *observe* a real webhook, only to forge one from scratch) can replay that exact `(body, hmac)` pair to the app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` (and/or `X-Shopify-Topic`) header for a different shop. `HmacValidator.validate` still returns `true` because it never looked at the header, and `Registry.process` calls the handler with `WebhookMetadata.new(shop: request.shop, ...)` reporting the victim's shop domain alongside the attacker's own (validly-signed) body content.

### Impact Explanation
This breaks the tenant boundary the gem is expected to enforce for webhook processing: `HmacValidator` is the sole authenticity gate before `Registry.process` invokes the app's handler, and that gate does not bind the identity field (`shop`) that the handler is documented to rely on for tenant attribution. Any host application following the gem's intended usage pattern — using `WebhookMetadata#shop` to decide which merchant's data/state the webhook body applies to — can be made to attribute attacker-controlled (though genuinely-signed) payload content to an arbitrary victim shop domain, which is cross-tenant data confusion/injection between merchants. This matches the Critical "cross-tenant access" impact category.

### Likelihood Explanation
Any unprivileged actor who can install the target app on a shop they control (a normal, permitted action for any Shopify developer/merchant) will receive real webhook deliveries with valid HMAC signatures for their own shop's events. Capturing one such `(raw_body, X-Shopify-Hmac-Sha256)` pair and replaying it against the app's public webhook endpoint with a forged `X-Shopify-Shop-Domain` header requires no secret material and no privileged access — it is a pure header-substitution replay against the app's public HTTP endpoint, entirely reachable by an unprivileged internet user.

### Recommendation
Include the identity-relevant headers (`shop domain`, `topic`, and ideally `webhook_id`/timestamp/nonce if available) in the signed/verified material, or otherwise cryptographically bind them to the request before trusting them — e.g., verify the HMAC over a canonical string that concatenates the header values with the raw body, not the raw body alone. At minimum, document and/or enforce that `request.shop` is untrusted until independently corroborated by the app (e.g., cross-checked against a shop known from prior OAuth session data) before being used as a tenant key.

### Proof of Concept
1. Attacker installs the app on their own store `attacker.myshopify.com` and enables a webhook subscription (e.g., `orders/create`).
2. Attacker triggers/receives a legitimate webhook delivery, capturing:
   - raw body `B`
   - header `X-Shopify-Hmac-Sha256: H` (valid HMAC of `B` using the app's `client_secret`)
3. Attacker sends a POST to the victim app's webhook endpoint with:
   - body `B` (unchanged)
   - header `X-Shopify-Hmac-Sha256: H` (unchanged, still valid since it only signs `B`)
   - header `X-Shopify-Shop-Domain: victim-shop.myshopify.com` (forged)
   - header `X-Shopify-Topic: orders/create` (unchanged or forged)
4. `ShopifyAPI::Utils::HmacValidator.validate` returns `true` because `to_signable_string` only checks `B` against `H`. [5](#0-4) 
5. `Registry.process` invokes the app's handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: parsed(B), topic: ..., ...)`, causing the app to act on attacker-supplied body content under the victim's tenant identity.

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
