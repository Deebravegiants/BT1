### Title
Webhook `shop-domain` header is trusted for tenant dispatch but not covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` derives the webhook's `topic`, `shop`, `api_version`, and `webhook_id` from HTTP headers, but its `to_signable_string` used for HMAC verification only returns the raw request **body** (`@raw_body`). `ShopifyAPI::Webhooks::Registry.process` validates the HMAC and then dispatches the payload to the registered handler using `request.shop` as the tenant identifier, without that field ever being part of the signed material.

### Finding Description
The binding that should hold is: `shop-domain header used for tenant dispatch == shop-domain value that Shopify actually cryptographically attested to`.

- `Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 
- `Request#shop`, `#topic`, `#api_version`, `#webhook_id` are all pulled straight from headers, none of which are included in `to_signable_string`: [2](#0-1) 
- `Registry.process` validates the HMAC against the `VerifiableQuery` interface (i.e., against `to_signable_string` = body only) and then immediately trusts `request.shop` and `request.topic` to build `WebhookMetadata` passed to the app's handler: [3](#0-2) 
- `HmacValidator.validate` computes and compares the signature purely over `verifiable_query.to_signable_string`: [4](#0-3) 

Because the signature only covers the body bytes, the `shop-domain` (and `topic`/`api_version`/`webhook_id`) headers can be swapped for arbitrary values while the HMAC remains valid, as long as the body is unchanged. Any unprivileged internet user who can install the app on their own shop can legitimately generate their own genuinely-signed webhook deliveries (body + valid HMAC pair) for their own tenant, then replay that exact `(body, hmac)` pair to the app's webhook endpoint while substituting a victim's `shop-domain` (and/or `topic`) header. `HmacValidator.validate` will still pass because it never inspects the header, and `Registry.process` will hand the attacker-controlled body to the handler tagged as `shop: <victim-shop>`.

### Impact Explanation
This breaks the tenant boundary the gem is meant to enforce for webhook processing: the `shop` value handed to application webhook handlers is supposed to be an authenticated statement from Shopify about which store a payload belongs to, but here it is an unauthenticated, attacker-controllable HTTP header. An application built on top of this gem that trusts `WebhookMetadata#shop` (as the documented API instructs it to, since it is asserted to come from a verified webhook request) to route/attribute webhook data (e.g., update per-shop database rows, revoke access, process `shop/redact`/`customers/redact`/GDPR topics, or apply order/customer state changes) can be made to apply attacker-supplied data or events under another merchant's identity - i.e., cross-tenant access/data confusion, achieved purely from the internet with no credentials beyond the ability to install the app on one's own store.

### Likelihood Explanation
High likelihood of exploitability given the gem's contract: `Registry.process` explicitly does `Utils::HmacValidator.validate(request)` and then trusts `request.shop`/`request.topic` for dispatch, with no secondary binding checking those headers against the signed body. Any actor capable of self-installing the app (any Shopify merchant, an "unprivileged internet user" relative to other tenants) can capture a valid `(raw_body, hmac)` pair from their own legitimate webhook delivery and resend it with a modified `shop-domain` header to the app's webhook endpoint.

### Recommendation
Include `shop`, `topic`, `api_version`, and `webhook_id` in the signed/verifiable representation (e.g., have `to_signable_string` incorporate a canonical representation of these header values alongside the body, or independently verify that the `X-Shopify-Shop-Domain` matches the shop associated with the session/subscription that the webhook was registered for). At minimum, document and enforce that `WebhookMetadata#shop` must never be trusted as an authenticated tenant identifier unless it is cross-checked against a shop-scoped webhook registration record maintained by the app (not solely against the gem's HMAC check).

### Proof of Concept
1. Attacker installs the app on their own shop `attacker.myshopify.com` and registers/receives a genuine webhook (e.g. `orders/create`), capturing the exact `raw_body` and the `X-Shopify-Hmac-Sha256` header Shopify sent for that delivery. This delivery is fully legitimate and requires no secret knowledge - only observation of a request the attacker itself received.
2. Attacker crafts a new HTTP POST to the same app webhook endpoint, using the identical `raw_body` and `X-Shopify-Hmac-Sha256` value captured in step 1, but sets:
   - `X-Shopify-Shop-Domain: victim.myshopify.com`
   - `X-Shopify-Topic:` any registered topic (unchanged or swapped, since topic is also unauthenticated)
3. The app calls `ShopifyAPI::Webhooks::Registry.process(request)`:
   - `Utils::HmacValidator.validate(request)` succeeds because it only hashes `@raw_body`, which is unchanged from the original legitimate delivery. [5](#0-4) 
   - The handler is invoked with `WebhookMetadata.new(topic: request.topic, shop: request.shop, body: request.parsed_body, ...)`, where `shop` is `"victim.myshopify.com"` even though the payload actually originated from the attacker's own shop. [6](#0-5) 
4. Any application logic keyed off `WebhookMetadata#shop` (e.g., "apply this order update to shop X's records") is now applied to the victim tenant using attacker-fabricated body content, demonstrating the cross-tenant identity confusion caused by the unauthenticated header.

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
