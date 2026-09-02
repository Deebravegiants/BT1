### Title
Webhook `shop`, `topic`, `webhook_id`, and `api_version` are trusted from unauthenticated HTTP headers while the HMAC only signs the raw body - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature over the raw request body only, but the shop domain, topic, webhook id, and API version consumed by `ShopifyAPI::Webhooks::Registry.process` are read straight from HTTP headers that are never included in the signed payload. An attacker who possesses one valid `(body, hmac)` pair (e.g. a legitimate webhook delivered to their own store) can replay it to the app's webhook endpoint with the `shop-domain` (and/or `topic`/`webhook-id`) header swapped to a value of their choosing, and the signature check still passes.

### Finding Description
`Registry.process` validates the webhook exclusively via `Utils::HmacValidator.validate(request)`, which in turn calls `request.to_signable_string`: [1](#0-0) 

This method returns only `@raw_body` - none of the identifying headers are part of the signed message: [2](#0-1) 

Yet immediately after the HMAC check passes, `Registry.process` dispatches to the registered handler using `request.shop`, `request.topic`, and `request.webhook_id` - all parsed from headers, none of which were part of what the HMAC verified: [3](#0-2) 

`HmacValidator.validate` computes `compute_signature(verifiable_query.to_signable_string, secret)` and compares it against `verifiable_query.hmac`: [4](#0-3) 

The identity binding that should hold is:
`hmac == HMAC(secret, body)` **and** `shop/topic/webhook_id used by the handler == shop/topic/webhook_id that were part of what was authenticated`.

In this implementation only the first half holds; the second half is false, because `shop`, `topic`, and `webhook_id` are read from `@headers` (attacker-controlled transport metadata) and never fed into `to_signable_string`. This is the same class of bug as the reported `mintLegendaryGobbler` issue: a value that is *used* by downstream logic (`gobblersOwned` / here, `shop`) is not actually covered by the mechanism (`_mint()` accounting / here, the HMAC) that is supposed to make it trustworthy.

### Impact Explanation
Any party capable of obtaining one legitimately signed webhook body+HMAC pair for the app (for instance, a merchant who has installed the app and receives real webhooks to their own endpoint, or anyone who can otherwise capture one delivery) can replay that exact body to the app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` (and/or topic/webhook-id) header for an arbitrary different shop domain. The HMAC will still validate because it only certifies the body bytes, so `Registry.process` will hand the handler a `WebhookMetadata` claiming the event came from a shop the attacker does not operate. Host applications built on this gem commonly use the reported `shop` to look up that shop's session/access token or to trigger shop-scoped side effects (e.g., data-erasure workflows, order processing, cache invalidation), so this enables cross-tenant event forgery — an attacker-chosen shop identity is injected into the app's webhook processing pipeline without the attacker controlling or being authorized for that shop.

### Likelihood Explanation
Exploitation requires no access to `api_secret_key`, no compromised credentials, and no privileged account: it only requires capturing one authentic webhook `(body, hmac)` pair, which is trivial for any merchant who installs the app (they receive real webhooks addressed to their own shop) or for anyone able to observe a single delivery over an unencrypted/misconfigured channel. Because the header substitution requires nothing more than replaying an HTTP request with modified headers, likelihood is high once one genuine webhook has been observed.

### Recommendation
Include the identity-bearing headers (`shop-domain`, `topic`, `webhook-id`, `api-version`) in the signable string used for HMAC verification, or otherwise cryptographically bind them to the body before trusting them in `Registry.process`. At minimum, `to_signable_string` should incorporate these values so that tampering with any of them invalidates the HMAC.

### Proof of Concept
1. Attacker installs the app on their own store `attacker-shop.myshopify.com` and receives a legitimate webhook delivery, e.g. topic `orders/create`, with raw body `B` and header `X-Shopify-Hmac-Sha256: H` (valid for `B`) and `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`.
2. Attacker replays the exact same body `B` and HMAC header `H` to the app's webhook endpoint, but changes `X-Shopify-Shop-Domain` to `victim-shop.myshopify.com`.
3. `Webhooks::Request.new(raw_body: B, headers: {...spoofed shop...})` is constructed; `Utils::HmacValidator.validate(request)` recomputes `HMAC(secret, B)`, which still equals `H`, so validation passes.
4. `Registry.process` invokes the registered handler with `WebhookMetadata.new(topic: "orders/create", shop: "victim-shop.myshopify.com", body: parsed_body, ...)`, causing the host application to process an event as if it originated from `victim-shop.myshopify.com`, even though that shop never sent it.

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
