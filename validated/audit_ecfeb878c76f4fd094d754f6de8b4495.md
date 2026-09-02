### Title
Webhook `shop-domain`, `topic`, and `webhook-id` headers are trusted without being covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` verifies incoming webhooks by HMAC-validating only the raw request body, while the `shop`, `topic`, `webhook_id`, and `api_version` values used by the handler are read from unauthenticated HTTP headers. Because the signature never binds these header fields to the body, a body/HMAC pair that is genuinely valid for one tenant can be replayed with a different `shop-domain` (or `topic`/`webhook-id`) header and will still pass validation, letting an attacker impersonate an arbitrary shop.

### Finding Description
`Utils::HmacValidator.validate` computes the signature over `verifiable_query.to_signable_string` and compares it with the `hmac` value: [1](#0-0) 

For webhooks, `to_signable_string` returns only the raw HTTP body, while `shop`, `topic`, `webhook_id`, and `api_version` are pulled straight from attacker-controllable HTTP headers, none of which are covered by the signable string: [2](#0-1) 

`Registry.process` gates handler execution purely on this body-only HMAC check, then forwards the unauthenticated header values (`request.shop`, `request.topic`, `request.webhook_id`, `request.api_version`) directly to the app's handler: [3](#0-2) 

The identity binding that should hold is:
`shop_header == shop_that_actually_generated_and_signed_this_body`

but the gem only enforces:
`HMAC(secret, body) == received_hmac`

with no cryptographic tie between `body` and `shop_header`/`topic_header`/`webhook_id_header`. Any unprivileged internet user can install the target app on a Shopify dev store they control (a normal, unprivileged action - creating a free development store and installing a public/dev app is not a privileged operation), causing Shopify to send them a genuinely HMAC-signed webhook body for their own shop. Because the signature never binds the `shop-domain` header, the attacker can resend that same body and HMAC value to the app's webhook endpoint while substituting an arbitrary victim `shop-domain` (and/or `topic`/`webhook-id`) header. `HmacValidator.validate` still succeeds because it only re-derives the HMAC from the (unchanged) body, and `Registry.process` will hand the handler a `WebhookMetadata` claiming the payload came from the victim shop.

### Impact Explanation
This breaks the tenant-identity binding that host applications rely on `ShopifyAPI::Webhooks` to enforce: apps generally key merchant data, session/access-token lookups, and side effects (e.g., billing, `shop/redact`, `app/uninstalled` handling) off the `shop` value delivered in `WebhookMetadata`. Since that value is not authenticated, an attacker can forge webhook events attributable to a shop domain they do not control, which is a cross-tenant integrity issue: an unprivileged party can inject events "from" another tenant, potentially triggering data mutation, deletion, or notification logic scoped to a shop they never authorized. This matches the "cross-tenant access" class of impact.

### Likelihood Explanation
Exploitation requires only: (1) the ability to install the target app once on any shop (routine, unprivileged, e.g. a free development store), which yields one legitimately signed body+HMAC pair, and (2) sending an HTTP POST with a modified `x-shopify-shop-domain` (and optionally `x-shopify-topic`/`x-shopify-webhook-id`) header to the app's public webhook endpoint. No secret, token, or privileged access is needed, and the vulnerable code path (`HmacValidator.validate` + `Registry.process`) is exercised on every inbound webhook by design, so likelihood is high wherever a host app trusts `WebhookMetadata#shop`/`#topic`/`#webhook_id` for authorization or data-scoping decisions.

### Recommendation
Include the tenant-identifying headers (`shop-domain`, `topic`, `webhook-id`, `api-version`) in the signable string used for HMAC verification, or otherwise cryptographically bind them to the body (e.g., compute the HMAC over a canonicalized `headers + body` string) so that a valid signature can only be replayed for the exact shop/topic/webhook-id it was issued for. At minimum, document prominently that `WebhookMetadata#shop` is not authenticated by `HmacValidator` and must be independently cross-checked by host applications against their own installed-shop registry before being trusted.

### Proof of Concept
1. Install the target Shopify app on an attacker-controlled development store `attacker-shop.myshopify.com`. Shopify sends a webhook request such as:
   ```
   POST /webhooks
   x-shopify-topic: orders/create
   x-shopify-hmac-sha256: <valid HMAC over BODY, computed with the app's real api_secret_key>
   x-shopify-shop-domain: attacker-shop.myshopify.com
   x-shopify-webhook-id: <id>
   x-shopify-api-version: 2024-01
   Body: BODY
   ```
2. Capture `BODY` and the accompanying `x-shopify-hmac-sha256` value.
3. Replay the exact same body and HMAC header, but change `x-shopify-shop-domain` to `victim-shop.myshopify.com` (and, if desired, alter `x-shopify-webhook-id`/`x-shopify-topic`).
4. `ShopifyAPI::Webhooks::Request.new` accepts the forged headers (no signature check happens on headers), and `Utils::HmacValidator.validate(request)` returns `true` because `to_signable_string` only re-hashes the unchanged `BODY`: [4](#0-3) 
5. `Registry.process` invokes the registered handler with `shop: "victim-shop.myshopify.com"`, even though that shop never sent this webhook, demonstrating the cross-tenant spoofing: [3](#0-2)

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

**File:** lib/shopify_api/webhooks/request.rb (L15-38)
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
