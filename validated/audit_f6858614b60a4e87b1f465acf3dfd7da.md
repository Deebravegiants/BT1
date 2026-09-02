Based on the analysis, I have enough evidence to finalize the finding.

### Title
Webhook shop/topic identity fields are not covered by HMAC verification, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature over the raw request body only, while the `shop`, `topic`, `webhook_id`, and `api_version` fields consumed by webhook handlers are read directly from unauthenticated HTTP headers. `Registry.process` validates the HMAC but then trusts these header-derived values when constructing `WebhookMetadata`, breaking the binding between "bytes verified" and "identity fields acted on."

### Finding Description
`Utils::HmacValidator.validate` is called on the `Request` object in `Registry.process`, and internally computes the signature over `verifiable_query.to_signable_string`: [1](#0-0) 

`to_signable_string` returns only `@raw_body`: [2](#0-1) 

However, `shop`, `topic`, `webhook_id`, and `api_version` — the identity fields used to route and label the webhook — are all pulled straight from HTTP headers, none of which are part of the signed payload: [3](#0-2) 

`Registry.process` passes these unauthenticated header values straight into `WebhookMetadata`, which is handed to the host application's handler as the trusted tenant/topic identity for the payload: [1](#0-0) [4](#0-3) 

The equality that should hold is: `shop bound by HMAC == shop delivered to handler`. In this implementation, the HMAC binds only the body bytes; `shop` (and `topic`/`webhook_id`) are asserted by the header and never cross-checked against anything derived from the signature. Because HMAC validation succeeds as long as the body matches the signature — regardless of what `shop-domain`/`topic`/`webhook-id` headers say — any request carrying a body+HMAC pair that is valid for the app's secret (e.g., a genuine webhook the attacker legitimately received for their own shop, since they can install the app on their own store) can have its `shop-domain`, `topic`, and `webhook-id` headers rewritten arbitrarily before replay to the app's webhook endpoint, and `Utils::HmacValidator.validate` will still return `true`.

### Impact Explanation
An attacker who has installed the app on their own shop (an unprivileged, legitimate install) receives genuinely-signed webhooks for their own tenant. Because the signature only covers the body, the attacker can replay that valid (body, HMAC) pair while substituting the `shop-domain` header for a victim shop and/or the `topic`/`webhook-id` headers for a different registered topic. `Registry.process` will accept it as authentic and hand the host app a `WebhookMetadata` claiming the (attacker-supplied) victim shop and/or topic. Any host application that relies on `data.shop` or `data.topic` to select which tenant's records to update, which handler logic path to run, or for idempotency/audit decisions is exposed to cross-tenant data confusion — data belonging to one shop can be processed and stored under a different shop's identity, or a payload can be mis-routed to a different topic's handler with different security assumptions. This matches the "cross-tenant access" class of impact.

### Likelihood Explanation
Reaching this requires only: (1) the attacker be a valid app installer on their own shop (unprivileged, no special credential beyond normal app usage), and (2) knowledge of the app's public webhook endpoint, which is standard for any Shopify app. No access to `api_secret_key`, tokens, or the app's infra is needed — the attacker uses their own genuinely-issued webhook signature and only forges HTTP headers on replay, which are entirely attacker-controlled on the wire.

### Recommendation
Include the identity fields (`shop`, `topic`, and ideally `webhook_id`/`api_version`) in the signed payload used for HMAC verification, or otherwise cryptographically bind the header values to the body (e.g., verify them against Shopify's TLS-terminated request metadata rather than trusting client-supplied headers alone). At minimum, document clearly that `WebhookMetadata#shop`/`#topic` are not authenticated by the HMAC and must not be used by host applications as a tenant-trust boundary without additional verification (e.g., cross-checking against the shop associated with the offline session/access token used to originally register the webhook).

### Proof of Concept
1. Install the app on attacker-owned shop `attacker.myshopify.com`; Shopify sends a legitimate webhook with a valid `x-shopify-hmac-sha256` for the raw body, signed with the app's `api_secret_key`.
2. Attacker captures this `(raw_body, hmac)` pair.
3. Attacker crafts a new HTTP request to the app's webhook endpoint using the identical `raw_body` and `hmac` header, but sets `x-shopify-shop-domain: victim-shop.myshopify.com` and/or `x-shopify-topic: orders/create`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only checks the body against the HMAC — validation succeeds.
5. The handler receives `WebhookMetadata` with `shop: "victim-shop.myshopify.com"`, `topic: "orders/create"`, and the attacker's own webhook body — an authenticated-looking payload with attacker-controlled tenant identity.

### Citations

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

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L6-12)
```ruby
    class WebhookMetadata < T::Struct
      const :topic, String
      const :shop, String
      const :body, T::Hash[String, T.untyped]
      const :api_version, String
      const :webhook_id, String
    end
```
