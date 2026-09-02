### Title
Webhook `shop` identity is not covered by the HMAC signature, enabling cross-tenant webhook forgery - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable string from the raw request body only, while the `shop` (tenant) attribute that the library exposes to the host application's webhook handler is read from an unauthenticated header. Any actor capable of producing a validly-signed webhook payload for their own (attacker-controlled) shop can replay that exact payload while altering the `shop-domain` header, and the signature check will still pass, because the header is never part of what is signed.

### Finding Description
`Utils::HmacValidator.validate` verifies the request by comparing `verifiable_query.hmac` against an HMAC computed over `verifiable_query.to_signable_string`: [1](#0-0) 

For webhook requests, `to_signable_string` returns only `@raw_body`: [2](#0-1) 

But the `shop` value that is later dispatched to the app's webhook handler is pulled straight from the `X-Shopify-Shop-Domain` HTTP header, which is not covered by the signature at all: [3](#0-2) 

`Registry.process` only checks the HMAC (over the body) before forwarding `request.shop` as the tenant identifier to the handler: [4](#0-3) 

The intended identity binding is: `HMAC-verified bytes == bytes that determine which tenant (shop) the event belongs to`. In this implementation that equality does not hold — the verified bytes are `raw_body` only, while the tenant-determining byte range is the unauthenticated `shop-domain` header. Consequently:
- Before the attacker's request: a legitimately signed webhook body/HMAC pair exists only for the shop that Shopify actually sent it for (e.g. the attacker's own test/dev store, which the attacker fully controls and can trigger events on).
- After the attacker's request sequence: the attacker resends that same (still validly signed) body with the `X-Shopify-Shop-Domain` header rewritten to a victim shop domain. `HmacValidator.validate` still returns `true` (it never looked at the header), so `Registry.process` dispatches the payload to the handler as if it came from the victim shop.

This lets an unprivileged actor who merely has (or can obtain) one legitimately-signed webhook payload — including from their own store — forge webhook events attributed to any other shop, without ever needing `api_secret_key`, an access token, or any credential belonging to the victim.

### Impact Explanation
This breaks the tenant/shop authentication boundary that host applications rely on: many apps use `WebhookMetadata#shop` (built directly from `request.shop`) to decide which merchant's data record to update, which webhook idempotency/dedup key to use, or which internal tenant context to operate in. An attacker forging events "from" a victim shop can inject false data attributed to that shop (e.g., fake `orders/create`, `app/uninstalled`, GDPR, or shop-update events), corrupting per-tenant state or triggering tenant-scoped side effects for a shop the attacker does not control. This is a cross-tenant access issue caused entirely by a gap in this gem's own HMAC-binding logic.

### Likelihood Explanation
The only prerequisite is possession of one validly HMAC-signed webhook payload for any shop, which is trivially obtainable by an attacker who installs the target app on their own store (a routine, unprivileged action) and lets it deliver a real webhook. From there, replaying the identical bytes with a modified `shop-domain` header is a simple HTTP replay — no cryptographic secret, access token, or victim credential is required.

### Recommendation
Bind the shop identity into the verified signature material, or otherwise re-authenticate it independently of the header:
- Extend `Request#to_signable_string` (or the HMAC validation call site) to include the `shop-domain`, `topic`, and `webhook-id` headers in the material used to compute/verify the signature, not just the raw body, OR
- After HMAC validation, cross-check `request.shop` against a shop value obtained from a source that is itself bound to the signature (e.g. requiring the caller to independently confirm the shop is one for which the app holds an active session/access token) before dispatching to the handler.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker-shop.myshopify.com` and triggers any webhook (e.g. `app/uninstalled`), capturing the raw POST: `raw_body`, and header `X-Shopify-Hmac-Sha256: <valid-hmac-for-raw_body>`, `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`.
2. Attacker resends the identical `raw_body` and identical `X-Shopify-Hmac-Sha256` value to the app's webhook endpoint, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `request.to_signable_string` (`raw_body`, unchanged) — validation passes.
4. `handler.handle` is invoked with `WebhookMetadata.new(... shop: request.shop ...)` where `request.shop` now returns `"victim-shop.myshopify.com"`, i.e. the app processes an attacker-controlled payload as if it were an authentic event from the victim shop. [5](#0-4)

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

**File:** lib/shopify_api/webhooks/request.rb (L10-38)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end

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
