## Title
Webhook shop-domain (and topic) header trusted without HMAC coverage, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook purely by recomputing an HMAC over the raw request body, then hands the caller-supplied `shop`, `topic`, `webhook_id`, and `api_version` HTTP headers straight to the app's handler. None of those headers are part of the signed material, so the binding "the shop whose HMAC verified == the shop the handler is told the event came from" is not enforced.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

while `shop`, `topic`, `webhook_id`, and `api_version` are read directly, and unauthenticated, from HTTP headers: [2](#0-1) 

`Utils::HmacValidator.validate` only verifies that `HMAC(api_secret_key, raw_body)` matches the supplied `hmac` header — it never touches `shop`, `topic`, or the other headers: [3](#0-2) 

`Registry.process` then trusts the header-derived `shop`/`topic`/`webhook_id` and forwards them to the app's handler as authenticated metadata once the body HMAC passes: [4](#0-3) 

Because Shopify apps use a single, app-wide `api_secret_key` shared across **every** shop that installs the app (it is not per-tenant), any merchant/attacker who installs the app on their own store can receive genuine, correctly-HMAC-signed webhooks for arbitrary bodies they can influence (e.g. by creating/updating resources on their own store). The attacker can then resend that same `(raw_body, hmac)` pair to the app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` (and/or `X-Shopify-Topic`) header with a victim shop's domain. `HmacValidator.validate` still passes, because it only checks `raw_body` against the shared secret — never the shop header — so the gem tells the host application "this event is authentically from `shop`" when in fact `shop` was never covered by the signature.

The identity binding that should hold is:
`shop authenticated by HMAC == shop delivered to the handler`
but the gem instead implements:
`body authenticated by HMAC` and, independently, `shop taken from an unauthenticated header`.

### Impact Explanation
This breaks tenant isolation (Critical — cross-tenant access): a host application relying on `WebhookMetadata#shop` (as documented/intended usage of this gem) to route webhook effects to the correct tenant's data can be made to apply attacker-controlled webhook payloads against a different, victim tenant's records — e.g., spoofing `app/uninstalled` to wipe another shop's stored session, or injecting fabricated `orders/create`/`products/create` payloads attributed to a shop the attacker does not own. No access token, `client_secret`, or victim credential is required — only that the attacker be able to install the same app on their own store, which is available to any unprivileged internet user.

### Likelihood Explanation
High likelihood: the attacker needs no secret material. They only need to be a normal (unprivileged) merchant able to install the target Shopify app on a store they control, capture one legitimately-signed webhook delivery, and replay it with a modified `shop-domain`/`topic` header to the app's public webhook endpoint. This requires no network position, no TLS interception, and no leaked credentials.

### Recommendation
Bind the shop (and ideally topic) into the material that is authenticated, or otherwise verify the header-derived `shop` against session/tenant state after HMAC validation, before handing it to the handler. Concretely:
- Cross-check `request.shop` against a shop that is registered/known to the app (e.g. an existing session) before dispatch, and/or
- Refuse to trust `shop`/`topic` header values as authenticated identity — require the host application to independently confirm tenant ownership — and document this gap prominently if header binding cannot be added to the signature itself (Shopify's webhook signing scheme only covers the body, so the gem must add its own tenant-binding check).

### Proof of Concept
1. Attacker registers/installs the target Shopify app on their own store `attacker.myshopify.com`.
2. Attacker triggers a webhook delivery whose body they control (e.g. creates a product with attacker-crafted title/description, causing `products/create` to fire). Shopify signs it with the app's single `api_secret_key`:
   ```
   POST /webhooks
   X-Shopify-Topic: products/create
   X-Shopify-Hmac-Sha256: <valid HMAC over raw_body>
   X-Shopify-Shop-Domain: attacker.myshopify.com
   <raw_body>
   ```
3. Attacker replays the identical `raw_body`/`X-Shopify-Hmac-Sha256` to the same endpoint but rewrites the shop header:
   ```
   POST /webhooks
   X-Shopify-Topic: products/create
   X-Shopify-Hmac-Sha256: <same valid HMAC>
   X-Shopify-Shop-Domain: victim.myshopify.com
   <same raw_body>
   ```
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only checks `HMAC(api_secret_key, raw_body)` — this still matches, so validation passes.
5. The handler receives `WebhookMetadata.new(topic: "products/create", shop: "victim.myshopify.com", body: <attacker-controlled data>, ...)` and the host application processes attacker-controlled data as if it originated from `victim.myshopify.com`. [5](#0-4)

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-28)
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
