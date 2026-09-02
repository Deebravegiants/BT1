### Title
Webhook `shop-domain` header is not covered by the HMAC signature, allowing shop-identity spoofing on replayed webhooks - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` only returns the raw request body, while `shop`, `topic`, `webhook_id`, and `api_version` are all read straight from unauthenticated HTTP headers. `Utils::HmacValidator.validate` (used by `Webhooks::Registry#process`) verifies only that the body matches the HMAC; the `shop-domain` header used downstream to attribute the webhook to a tenant is never bound to that signature.

### Finding Description
`ShopifyAPI::Webhooks::Request` implements the `VerifiableQuery` interface with: [1](#0-0) 

`hmac` is taken from the `X-Shopify-Hmac-SHA256` header, and `to_signable_string` returns only `@raw_body`. `shop` is read from a completely separate, unauthenticated header (`shop-domain`) with no cryptographic tie to the signature.

`Webhooks::Registry#process` validates the request purely via this HMAC check and then hands the raw, unauthenticated `shop` value to the handler: [2](#0-1) 

Because `HmacValidator.validate_signature` only compares `compute_signature(verifiable_query.to_signable_string, secret)` (i.e., a signature over the body) to the received signature: [3](#0-2) 

...any request whose body+HMAC pair is valid for *some* shop (e.g., the attacker's own shop, which can legitimately trigger webhook deliveries with a genuine Shopify-computed HMAC) will also pass validation if the `X-Shopify-Shop-Domain` header is swapped for an arbitrary victim shop domain. The equality the code implicitly (and incorrectly) assumes is:
`shop authenticated by HMAC == shop delivered to the handler`
but in reality only `body authenticated by HMAC` holds; `shop` is fully attacker-controlled.

### Impact Explanation
An unprivileged internet user who can obtain one legitimate, validly-signed webhook delivery (trivially possible by installing the target app on their own free/dev store and triggering any webhook topic) can replay that body+HMAC pair to the app's public webhook endpoint while substituting the `shop-domain` (and `webhook-id`/`topic`, if desired, though topic is not required to correlate) header with any other shop's domain. `Webhooks::Registry#process` will accept it as authentic and invoke the app's webhook handler with `WebhookMetadata#shop` set to the forged domain. Any host application that trusts `data.shop` to select which tenant's records to look up, update, or delete (a standard pattern for multi-tenant Shopify apps) will act on the wrong tenant's data using attacker-supplied body content — a cross-tenant data-integrity/confusion issue reachable by any user with an unprivileged Shopify store, without needing the app's `client_secret` or any credentials belonging to the app or the victim shop.

### Likelihood Explanation
High. Getting a valid signed webhook payload requires nothing more than installing the target app on an attacker-owned (e.g. free trial) store and triggering any webhook event — no special privilege or leaked secret needed. Forging arbitrary header values on an HTTP POST is trivial. The vulnerable code path (`Registry.process` → `HmacValidator.validate` → handler dispatch) is exercised on every inbound webhook request with no additional binding check.

### Recommendation
Include the identity-relevant headers (`shop`, `topic`, `webhook_id`, `api_version`) in the signable content, or otherwise cryptographically bind them to the payload/signature before calling `handler.handle`. At minimum, document that host applications must independently look up/verify that the resolved `shop` value corresponds to a shop with an active session/installation for this app before trusting webhook payload data, since the gem itself does not bind `shop` to the HMAC.

### Proof of Concept
1. Install the target Shopify app on attacker-controlled shop `attacker.myshopify.com`.
2. Trigger any subscribed webhook topic (e.g., `orders/create`) in that shop; Shopify delivers a POST with a real `X-Shopify-Hmac-Sha256` header computed over the raw JSON body using the app's `client_secret`.
3. Capture `raw_body` and the `X-Shopify-Hmac-Sha256` value from this legitimate delivery.
4. Resend an HTTP POST to the app's webhook endpoint with the identical `raw_body` and `X-Shopify-Hmac-Sha256` header, but set `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
5. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks `raw_body` against the HMAC: [4](#0-3) 
6. The registered handler is invoked with `WebhookMetadata.new(topic: request.topic, shop: request.shop, body: request.parsed_body, ...)` where `shop` is `"victim-shop.myshopify.com"` — an identity chosen entirely by the attacker, despite the payload originating from the attacker's own store.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-38)
```ruby
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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
