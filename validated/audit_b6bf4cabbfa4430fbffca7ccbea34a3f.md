This confirms the root cause. The `Registry.process` method validates only `Utils::HmacValidator.validate(request)`, which per `VerifiableQuery` HMACs `request.to_signable_string` (the raw body only, see `lib/shopify_api/webhooks/request.rb` lines 35-38), while `request.shop`, `request.topic`, and `request.webhook_id` are read directly from unauthenticated headers (lines 20-33) and passed straight into the handler at `lib/shopify_api/webhooks/registry.rb` lines 198-199.### Title
Webhook `shop` (and `topic`/`webhook_id`) identity fields are not covered by the HMAC, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating the HMAC of the raw request body, but the `shop` (and `topic`/`webhook_id`) values that the handler treats as trusted are read from HTTP headers that are excluded from that HMAC computation.

### Finding Description
The equality the gem is supposed to guarantee is:
`bytes covered by HMAC == bytes the handler trusts as the webhook's identity (shop/topic/webhook_id)`

`Registry.process` only checks the HMAC and then forwards header-derived fields straight to the app's handler: [1](#0-0) 

`Utils::HmacValidator.validate` computes the signature over `verifiable_query.to_signable_string`: [2](#0-1) 

For a webhook `Request`, `to_signable_string` returns only the raw body (`@raw_body`) — it does not include the `shop`, `topic`, `webhook_id`, or `api_version` fields: [3](#0-2) 

Yet `shop`, `topic`, and `webhook_id` are all read straight from unauthenticated, attacker-controllable headers: [4](#0-3) 

and are passed into `WebhookMetadata`, which the host app's `WebhookHandler#handle` treats as authoritative for identifying which shop/tenant the event belongs to: [5](#0-4) 

Because the HMAC only binds the JSON body, any raw_body+hmac pair that was legitimately issued for one shop (e.g. by installing the app on an attacker-controlled store and capturing its own genuine webhook delivery) remains a valid HMAC signature no matter what `X-Shopify-Shop-Domain`, `X-Shopify-Topic`, or `X-Shopify-Webhook-Id` header values are substituted. `Utils::HmacValidator.validate` will still return `true` because it never looks at those headers, and `Registry.process` will dispatch the (attacker-relabeled) event to the handler as if it came from a different shop/topic.

### Impact Explanation
This breaks the tenant-identity binding the app relies on to route webhook data. An attacker who has legitimate access to an app installed on their own (unprivileged) store can capture a genuine `raw_body`+HMAC pair for a webhook of their choosing, then replay it directly to the app's public webhook endpoint with a forged `X-Shopify-Shop-Domain` header pointing at a victim shop (and/or a forged topic/webhook-id). The HMAC check still passes, so the app's webhook handler executes attacker-supplied body content under the identity of a different tenant. Depending on how the host app uses `WebhookMetadata#shop` (e.g., looking up that shop's stored access token/session, writing to that shop's tenant data store, or triggering shop-scoped side effects), this enables cross-tenant data injection/corruption — qualifying as cross-tenant access.

### Likelihood Explanation
High: webhook endpoints are typically public HTTP(S) endpoints reachable by anyone; no privileged credentials, `api_secret_key`, or Shopify-side control is required — only the ability to install the app once on an attacker's own store to obtain one genuine signed body/HMAC pair, and the ability to send an arbitrary HTTP POST with custom headers to the app's webhook URL.

### Recommendation
Include the identity-critical headers (`shop`, `topic`, and ideally `webhook_id`/`api_version`) in the signable string used for HMAC validation, or otherwise cryptographically bind them to the body (e.g., verify the header values against a value derived from a signed superset that Shopify controls). At minimum, update `ShopifyAPI::Webhooks::Request#to_signable_string` to combine the raw body with `shop`, `topic`, and `webhook_id`, and document that host applications must not trust these header-derived fields independently of the HMAC scope, matching Shopify's actual webhook verification contract (which only ever guarantees authenticity of the raw body, not header values) — if that is the true upstream contract, this finding should instead be treated as the gem failing to warn/enforce that host apps must additionally verify shop identity out-of-band (e.g., by confirming the shop exists in the app's session/token store) before trusting `WebhookMetadata#shop`.

### Proof of Concept
1. Attacker installs the target app on their own real, unprivileged Shopify store (`attacker-shop.myshopify.com`) and triggers a webhook event (e.g. `orders/create`), capturing the raw POST body and its `X-Shopify-Hmac-Sha256` value delivered to the app's public webhook endpoint.
2. Attacker resends the identical raw body and HMAC header to the same endpoint, but changes `X-Shopify-Shop-Domain` to `victim-shop.myshopify.com` (and optionally `X-Shopify-Topic`/`X-Shopify-Webhook-Id`).
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC only over `raw_body` — this matches, so validation succeeds (`lib/shopify_api/webhooks/registry.rb:190`, `lib/shopify_api/webhooks/request.rb:36-38`).
4. `Registry.process` builds `WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)` using the forged header values (`lib/shopify_api/webhooks/registry.rb:198-199`) and invokes the host app's `handler.handle`, which believes the event originates from `victim-shop.myshopify.com` even though the body content actually came from the attacker's own store.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
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
