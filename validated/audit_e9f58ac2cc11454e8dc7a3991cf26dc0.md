### Title
Webhook HMAC signature does not bind the `shop`, `topic`, or `webhook_id` fields, allowing cross-tenant webhook forgery - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` only includes the raw request body in the HMAC-signable string. The `shop-domain`, `topic`, `webhook-id`, and `api-version` headers — which are trusted downstream to identify *which tenant* the webhook belongs to — are never covered by the signature, so they can be freely altered by anyone who can produce (or replay) a genuinely-signed body.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

But `Request#shop`, `#topic`, `#webhook_id`, and `#api_version` are all read from separate HTTP headers that are not part of that signable string: [2](#0-1) 

`HmacValidator.validate` computes the HMAC solely over `verifiable_query.to_signable_string` and compares it to the `hmac-sha256` header: [3](#0-2) 

`Registry.process` relies on this validation, then forwards the *unauthenticated* `request.shop`, `request.topic`, and `request.webhook_id` straight into `WebhookMetadata`, which is handed to the app's handler as the tenant identity for the event: [4](#0-3) 

Because the signature is only bound to the body, `shop == verified-owner-of(hmac)` does not hold — the equality the gem should guarantee (`hmac` authenticates `(shop, topic, webhook_id, body)`) is broken; it only authenticates `body`. Any entity that can obtain one validly-signed webhook body (e.g., a merchant installing the app on their own store and receiving genuine webhook deliveries) can splice that same signed body onto forged `shop-domain`/`topic`/`webhook-id` headers pointed at a different, victim tenant, and the request will still pass `Utils::HmacValidator.validate`.

### Impact Explanation
This breaks the tenant boundary the gem is supposed to enforce for webhook processing: `authenticated_shop == request.shop` is not actually verified. A host application that uses `data.shop` from `WebhookMetadata` (the documented and only field exposed for tenant identification) to look up the merchant's session/access token, or to route/attribute the event, can be made to act on behalf of, or apply attacker-controlled data to, a shop the attacker doesn't own — a cross-tenant confusion enabled entirely by this gem's signature scope, not by host misuse.

### Likelihood Explanation
Any developer/merchant able to install the app on a store they control receives fully valid, correctly signed webhook deliveries for that store. Splicing the verified body onto different `shop-domain`/`topic`/`webhook-id` headers requires no secret material — the `api_secret_key` is never needed, only observation of one legitimate delivery, which is why this is reachable by an unprivileged, non-credentialed actor relative to the victim tenant.

### Recommendation
Include the `shop-domain`, `topic`, and `webhook-id` header values in the HMAC-signable string (or otherwise cryptographically bind them, e.g. by hashing them alongside the body before comparison), so that `Utils::HmacValidator.validate` fails if any of these identity fields are altered relative to what Shopify actually signed.

### Proof of Concept
1. Attacker installs the app on `attacker.myshopify.com` and triggers a real webhook (e.g., `orders/create`). Shopify sends:
```
X-Shopify-Topic: orders/create
X-Shopify-Hmac-Sha256: <valid HMAC over body>
X-Shopify-Shop-Domain: attacker.myshopify.com
Body: {"id":1,...attacker-controlled order payload...}
```
2. Attacker resubmits the exact same body/HMAC to the app's webhook endpoint but rewrites the header:
```
X-Shopify-Shop-Domain: victim.myshopify.com
```
3. `ShopifyAPI::Webhooks::Request#hmac`/`#to_signable_string` only look at the body, so `Utils::HmacValidator.validate` (lib/shopify_api/utils/hmac_validator.rb:26-31) returns `true`.
4. `Registry.process` (lib/shopify_api/webhooks/registry.rb:188-200) builds `WebhookMetadata.new(shop: "victim.myshopify.com", body: <attacker payload>, ...)` and invokes the app's handler as though Shopify genuinely sent this event for `victim.myshopify.com`.

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
