### Title
Webhook Shop-Domain Spoofing via HMAC Signature Scope Mismatch (Cross-Tenant) - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
### Finding Description
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating an HMAC over the raw request body, then trusts the unauthenticated `shop-domain` header to attribute the payload to a tenant.

The `to_signable_string` method used for HMAC computation returns only `@raw_body`: [1](#0-0) 

But `shop` (and `topic`, `webhook_id`, `api_version`) are read directly from HTTP headers, entirely outside the signed material: [2](#0-1) 

`Registry.process` validates the HMAC and then immediately builds `WebhookMetadata` using the unauthenticated `request.shop`, handing it to the app's registered handler as the tenant identity for the event: [3](#0-2) 

`HmacValidator.validate` (shared with the OAuth callback flow) simply recomputes the HMAC over whatever `to_signable_string` returns and compares it to the received signature — it has no notion of which fields "should" be covered: [4](#0-3) 

The identity binding that should hold is: **bytes verified by the HMAC == bytes/fields acted upon** (i.e., the `shop` used to route/attribute the webhook should be covered by the same signature that authenticates the payload). Here that binding is broken: only the body is authenticated, while the `shop` field that downstream app code keys tenant-scoped actions on is taken from a header the HMAC never touches.

### Impact Explanation
Because the `shop-domain` header is not part of the signed material, any body+HMAC pair that is authentically correlated (i.e., a real signature over that exact body, computed with the app's `client_secret`) remains valid no matter what `shop-domain` header accompanies it. A webhook payload legitimately delivered for shop A (which an attacker who runs/controls shop A can capture, since they receive their own webhooks) can be replayed verbatim to the app's public webhook endpoint with the `shop-domain` header rewritten to shop B. `Utils::HmacValidator.validate` still returns `true`, and the app's handler executes attacker-influenced webhook logic (e.g., data updates, uninstall handling, GDPR-style deletion, order/customer state changes) against a victim tenant it does not control. This is cross-tenant access/action performed under a spoofed tenant identity, which is the intended blast radius of the analog vulnerability pattern (identity not bound by the authenticator).

### Likelihood Explanation
Exploitability requires only: (1) the attacker be able to trigger at least one webhook topic on any shop they control (trivial — install the target app on their own development/free store and cause any subscribed event), and (2) direct network access to the app's webhook endpoint, which is by definition a public internet endpoint. No access to `api_secret_key`, TLS interception, or privileged accounts is needed — the attacker only replays data they legitimately received for their own tenant while forging an unrelated header. This is reachable by any unprivileged internet user who can install the target app.

### Recommendation
Include the tenant-identifying headers (`shop-domain`, and ideally `topic`/`webhook-id`) in the material that is HMAC-verified, or independently bind them, e.g.:
- Extend `Webhooks::Request#to_signable_string` to incorporate `shop`, `topic`, and `webhook_id` alongside the body so any tampering invalidates the signature; or
- After HMAC validation, cross-check `request.shop` against a shop that the app already has an active, previously-established session for, and reject webhooks for domains with no known relationship, rather than trusting the header outright as the routing key passed to handlers.

### Proof of Concept
1. Attacker registers the target app on a shop they control (`attacker-shop.myshopify.com`) and subscribes to any webhook topic the app registers via `ShopifyAPI::Webhooks::Registry`.
2. Attacker triggers the topic (e.g., updates a resource) so Shopify delivers a real webhook to the app's public callback URL, and captures the exact raw request body and the `X-Shopify-Hmac-Sha256` header value from that delivery (e.g. via a debugging proxy they control, since it's their own server-bound traffic).
3. Attacker crafts a new HTTP POST to the same app webhook endpoint, reusing the captured raw body and `X-Shopify-Hmac-Sha256` header unchanged, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new` parses headers/body normally; `Utils::HmacValidator.validate(request)` recomputes HMAC over the (unchanged) body and it matches, so `Registry.process` proceeds.
5. `Registry.process` invokes the app's handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", topic:, body:, ...)`, causing the app to act as if the (attacker-controlled) payload originated from the victim shop.

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
