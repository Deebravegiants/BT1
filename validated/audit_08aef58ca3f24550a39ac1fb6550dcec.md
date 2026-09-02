### Title
Webhook `shop`, `topic`, and `webhook_id` fields are trusted from unauthenticated HTTP headers while the HMAC only covers the raw body — ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`, so the HMAC signature verified by `Utils::HmacValidator` binds solely to the request body. The `shop`, `topic`, `webhook_id`, and `api_version` values consumed by `Webhooks::Registry.process` and handed to the app's `WebhookHandler` are read straight from HTTP headers that are never part of the signed content.

### Finding Description
`Request#to_signable_string` (`lib/shopify_api/webhooks/request.rb:35-38`) is:
```ruby
def to_signable_string
  @raw_body
end
``` [1](#0-0) 

`shop`, `topic`, `webhook_id`, `api_version` are all read directly from headers with no cryptographic binding to the HMAC: [2](#0-1) 

`Registry.process` validates the HMAC of the body only, then trusts the header-derived `shop`/`topic`/`webhook_id` to build `WebhookMetadata` passed to the app's handler: [3](#0-2) 

`Utils::HmacValidator.validate` computes the signature over `verifiable_query.to_signable_string` (i.e., the body only) using the app's single, shop-independent `Context.api_secret_key`: [4](#0-3) 

Because the same `api_secret_key` signs every webhook body for every shop that installs the app, and the signature does not cover the shop/topic headers, the required equality that should hold is:

```
HMAC(body) authenticates (body, shop, topic, webhook_id)
```

but the actual implementation only satisfies:

```
HMAC(body) authenticates (body)
```

The `shop`/`topic`/`webhook_id` are effectively unauthenticated attacker-controlled bytes forwarded straight into the handler, breaking the binding between "the bytes the HMAC verified" and "the bytes the handler acts on" — the exact bug class called out in the rules (fields acted on but not covered by the HMAC).

### Impact Explanation
Any unprivileged internet user can install the app on their own development/free store (a normal, unprivileged action) and trigger a real webhook delivery to the app's public webhook endpoint. This produces a legitimate `(raw_body, HMAC)` pair signed with the app's shared `api_secret_key`. The attacker can then replay that exact body+HMAC to the app's webhook endpoint while forging the `x-shopify-shop-domain` (and/or `x-shopify-topic`, `x-shopify-webhook-id`) headers to name a different, victim shop. `Utils::HmacValidator.validate` still returns `true` because it only checks the body, and `Registry.process` forwards the forged `shop`/`topic` into the handler as if they were authentic. Depending on how the host application's `WebhookHandler` uses `WebhookMetadata#shop` (e.g., looking up which merchant's session/data to update, or fulfilling mandatory `shop/redact` / `customers/redact` / `customers/data_request` compliance webhooks), this enables cross-tenant data corruption or a forged data-erasure/access request against a shop the attacker does not own. This is a cross-tenant confusion vulnerability rooted directly in this gem's webhook verification code, not merely a host-application misuse issue, because the gem itself asserts the webhook is "valid" (`InvalidWebhookError` not raised) while exposing unauthenticated `shop`/`topic` fields as if verified.

### Likelihood Explanation
High. No privileged credentials are required beyond installing the app as any merchant would (a normal, low-friction action for public/embedded apps), and HTTP headers are trivially forgeable by any client sending the replayed body to the app's public webhook URL. The only skill required is capturing one legitimate webhook delivery to one's own store and replaying it with modified headers.

### Recommendation
Include the security-relevant headers (`shop`, `topic`, `webhook_id`, `api_version`) in the signable string used for HMAC verification, or otherwise cryptographically bind them to the body (e.g., verify `shop` against an expected/pre-registered shop for the installation, and include `topic`/`shop` in the canonical string that is HMAC'd) so that any header tampering invalidates the signature.

### Proof of Concept
1. Install the target app on attacker-controlled store `attacker-shop.myshopify.com`.
2. Trigger any webhook delivery (e.g., `orders/create`) to the app's webhook endpoint, capturing the exact `raw_body` and `x-shopify-hmac-sha256` header — both valid because they were legitimately signed with the app's `api_secret_key`.
3. Replay the same `raw_body` and `x-shopify-hmac-sha256` to the same endpoint, but replace the `x-shopify-shop-domain` header with `victim-shop.myshopify.com` (and optionally change `x-shopify-topic` to `shop/redact` or `customers/redact`).
4. `ShopifyAPI::Utils::HmacValidator.validate` returns `true` (only the body is checked), and `ShopifyAPI::Webhooks::Registry.process` invokes the registered handler with `WebhookMetadata.new(topic: "shop/redact"/forged, shop: "victim-shop.myshopify.com", ...)`, i.e., the host application acts on the victim shop believing the webhook was authenticated for that shop.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-22)
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
```
