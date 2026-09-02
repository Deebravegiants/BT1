Confirmed: `Registry.process` at [1](#0-0)  validates the HMAC and then hands the handler `request.shop`, `request.topic`, `request.webhook_id`, and `request.api_version`, none of which are covered by the signature (`Request#to_signable_string` returns only `@raw_body`) as seen at [2](#0-1) .

### Title
Webhook tenant identity (`shop-domain`) is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes the HMAC signature over the raw body only, while the `shop`, `topic`, `webhook_id`, and `api_version` values used downstream for tenant-scoped business logic come from unauthenticated HTTP headers.

### Finding Description
`Request#to_signable_string` returns `@raw_body` exclusively: [3](#0-2) . `HmacValidator.validate` computes the signature purely from that signable string and the app's shared `api_secret_key`, using `OpenSSL.secure_compare` against the received `hmac` header: [4](#0-3) . `Request#shop`, `#topic`, `#webhook_id`, and `#api_version` are all read straight from HTTP headers (`shopify-shop-domain`, `shopify-topic`, `shopify-webhook-id`, `shopify-api-version`) with no cryptographic binding to the body or to each other: [5](#0-4) . `Registry.process` validates only the HMAC of the body, then dispatches to the handler using `request.topic`, `request.shop`, `request.webhook_id`, and `request.api_version` verbatim: [1](#0-0) .

The broken identity binding is: **HMAC-verified bytes (body only) ≠ tenant identity used by the handler (`shop-domain` header)**. Because the app's `api_secret_key` is shared across all shops/tenants installing the app (it is not shop-specific), any party who legitimately receives one valid `(body, hmac)` pair for their own shop — e.g., by triggering a webhook-eligible action, or via a shop where they have merchant/collaborator access — can replay that exact `(body, hmac)` pair to the app's public webhook endpoint while substituting an arbitrary `x-shopify-shop-domain` header (and/or `topic`/`webhook_id`/`api-version` headers) pointing at a different, victim shop. `Registry.process` will accept it: the HMAC check passes (since it depends only on body+secret, not on the header values), and the handler executes attacker-chosen body content attributed to the victim's `shop`.

### Impact Explanation
This crosses a tenant boundary: an app's webhook handler typically uses the `shop` field to look up/update per-merchant records (e.g., "delete this shop's data", "update this shop's inventory record", "mark this shop's subscription cancelled"). Since `shop` is attacker-controlled and unauthenticated relative to the signature, an unprivileged party who can obtain any one valid signed webhook body for their own shop can forge cross-tenant events, causing the host application to apply attacker-controlled webhook payloads to a different merchant's data. This falls under cross-tenant access.

### Likelihood Explanation
Exploitability depends on the attacker being able to obtain at least one legitimately-signed `(body, hmac)` pair — trivially available to any developer/merchant who installs the app on their own shop and triggers a webhook (webhook payloads for common topics are largely predictable/structural, e.g., `orders/create`, `app/uninstalled`), since the same `api_secret_key` signs webhooks for every shop using the app. No access token, TLS interception, or privileged account is required — only the ability to send an HTTP POST to the app's public webhook endpoint with attacker-chosen headers.

### Recommendation
Include the tenant-identifying headers (`shop-domain`, and ideally `topic`/`webhook_id`) in the signable string so the HMAC binds them to the body, or otherwise authenticate the `shop` header against the signature before passing it to `WebhookMetadata`/handlers.

### Proof of Concept
1. Attacker installs (or otherwise has legitimate access to) the target app on `attacker-shop.myshopify.com` and triggers a webhook-eligible action (e.g., `orders/create`), capturing the raw POST body and its valid `x-shopify-hmac-sha256` header sent by Shopify (computed with the app's shared `api_secret_key`).
2. Attacker POSTs the exact same body and `x-shopify-hmac-sha256` value to the app's webhook endpoint, but sets `x-shopify-shop-domain: victim-shop.myshopify.com` (and optionally forges `x-shopify-topic`/`x-shopify-webhook-id`).
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only checks `raw_body` against the shared secret — see [4](#0-3)  and [6](#0-5) .
4. The registered handler executes with `WebhookMetadata.new(topic: request.topic, shop: "victim-shop.myshopify.com", body: request.parsed_body, ...)` per [7](#0-6) , causing the host application to process attacker-controlled data under the victim shop's tenant identity.

### Citations

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
