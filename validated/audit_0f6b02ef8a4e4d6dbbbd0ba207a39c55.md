I found a concrete analog. The webhook HMAC verification only covers the **raw request body**, but the **shop identity** used to route/process the webhook is read from an HTTP header that is not covered by that signature.### Title
Webhook `shop` Identity Is Not Covered by HMAC Verification, Allowing Cross-Tenant Attribution Spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`Webhooks::Registry.process` accepts a webhook only after validating an HMAC that covers the **raw request body**, but the `shop` value that is subsequently handed to the app's `WebhookHandler` is read from an HTTP header that the HMAC never signs. This breaks the same identity-binding invariant as the reported `SessionKey` bug: the entity that is cryptographically validated (the body) is not the same entity that is trusted and acted upon (the `shop-domain` header).

### Finding Description
`Utils::HmacValidator.validate` computes the HMAC using `verifiable_query.to_signable_string`, and for `Webhooks::Request` that method returns only `@raw_body`: [1](#0-0) 

The `shop`, `topic`, `api_version`, and `webhook_id` values, however, are all pulled straight from HTTP headers, none of which are included in the signed string: [2](#0-1) 

`Registry.process` validates the HMAC and then, without re-checking the `shop` header against anything, forwards `request.shop` (attacker/header-controlled) to the app-supplied handler as the authoritative shop identity for the payload: [3](#0-2) [4](#0-3) 

This is the exact class of bug in the report: `_validateSelector`/`_validateSingleCall` verify that the **call** is legitimate (signer owns *a* session key, calling `claim()`), but never bind the **specific `sessionKey` parameter** used inside that call to the signer who produced the signature. Here, `HmacValidator.validate` verifies that the **body bytes** were signed by Shopify, but never binds the **shop identity** used by the handler to anything the signature covers. The equality that should hold but does not is:

`shop_bound_by_hmac(raw_body) == shop_used_by_handler(request.shop)`  — the left side is undefined (the body payloads for most topics do not embed the shop domain), while the right side is attacker/header-controlled.

### Impact Explanation
Any entity capable of obtaining one *validly signed* webhook body+HMAC pair for topic T (e.g., by legitimately installing the app on their own development/test store and receiving Shopify's real webhook calls) can replay that exact body and HMAC to the app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` header with a victim shop's domain. Because the signature check only covers `@raw_body`, the tampered request still passes `HmacValidator.validate`, and `Registry.process` will invoke the app's handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...)`, attributing attacker-chosen body content to the victim tenant. Depending on how the host app's `WebhookHandler` implementation uses `shop` (e.g., updating per-shop state, triggering shop-scoped side effects, or looking up a session/access token keyed by shop), this is a cross-tenant data/state confusion vector — the impact class explicitly listed as in-scope ("cross-tenant access").

### Likelihood Explanation
Exploitation requires only the ability to send an HTTP POST to the app's exposed webhook receiver endpoint with attacker-chosen headers and a previously-observed valid `(body, hmac)` pair — no possession of the app's `client_secret` or any merchant access token is required, satisfying the "unprivileged internet user" constraint. The only prerequisite is obtaining one legitimately-signed webhook (trivially done by installing the same public app on an attacker-owned store, which is normal, unprivileged usage of the app).

### Recommendation
Include the shop-identifying header(s) (and topic/webhook-id, to prevent cross-topic replay) in the HMAC-signed material, or otherwise cryptographically bind `shop-domain` to the signed body (e.g., derive/verify the shop from data already authenticated inside the signed payload, or require the host app to independently confirm that `request.shop` corresponds to a shop with a currently valid session before trusting it in `WebhookMetadata`). At minimum, document and enforce that `Registry.process` must not treat the header-derived `shop` as trusted for cross-tenant-sensitive operations unless the app performs its own additional shop verification.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker.myshopify.com` and configures/receives a real webhook for topic `orders/create` (or any registered topic). Shopify sends: body `B`, header `X-Shopify-Hmac-Sha256: H`, header `X-Shopify-Shop-Domain: attacker.myshopify.com`.
2. Attacker captures `(B, H)` — this pair is valid because `HmacValidator.validate` only checks `HMAC(secret, B) == H` (see `to_signable_string` at `lib/shopify_api/webhooks/request.rb:35-38`).
3. Attacker replays a new POST to the app's webhook endpoint with the same body `B` and header `X-Shopify-Hmac-Sha256: H`, but sets `X-Shopify-Shop-Domain: victim.myshopify.com`.
4. `Webhooks::Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-190`) calls `Utils::HmacValidator.validate(request)`, which passes because the signed content (`B`) is unchanged.
5. `Registry.process` builds `WebhookMetadata.new(shop: "victim.myshopify.com", body: JSON.parse(B), ...)` (`lib/shopify_api/webhooks/registry.rb:198-199`) and invokes the app's `handler.handle(data:)`, causing the app to process attacker-supplied content as if it originated from the victim's shop.

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

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L6-24)
```ruby
    class WebhookMetadata < T::Struct
      const :topic, String
      const :shop, String
      const :body, T::Hash[String, T.untyped]
      const :api_version, String
      const :webhook_id, String
    end

    module WebhookHandler
      include Kernel
      extend T::Sig
      extend T::Helpers
      interface!

      sig do
        abstract.params(data: WebhookMetadata).void
      end
      def handle(data:); end
    end
```
