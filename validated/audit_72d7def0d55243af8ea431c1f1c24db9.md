Confirmed root cause. The `hmac` covers only `@raw_body` (`to_signable_string` returns `@raw_body`, `lib/shopify_api/webhooks/request.rb:35-38`), while `shop`, `topic`, `webhook_id`, and `api_version` are all read straight from HTTP headers (`shopify_header`) with no cryptographic binding to the signed payload (`lib/shopify_api/webhooks/request.rb:15-33`). `Registry.process` validates only the HMAC of the body, then dispatches using the unauthenticated `request.shop` value as the tenant identifier passed to the handler (`lib/shopify_api/webhooks/registry.rb:188-199` — see `Utils::HmacValidator.validate(request)` followed by `WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)`).

### Title
Webhook tenant identity (`shop-domain` header) is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC over the raw body only (`to_signable_string` → `@raw_body`), but the `shop` (and `topic`/`webhook_id`/`api_version`) values used by `Registry.process` to identify the tenant and dispatch the payload are taken from unauthenticated HTTP headers that are never included in the signed content.

### Finding Description
`Utils::HmacValidator.validate` computes `HMAC(secret, verifiable_query.to_signable_string)` and compares it to `verifiable_query.hmac` [1](#0-0) . For webhook requests, `to_signable_string` returns only `@raw_body` [2](#0-1) , while `shop`, `topic`, `webhook_id`, and `api_version` are pulled directly from the `shopify-*`/`x-shopify-*` HTTP headers via `shopify_header` [3](#0-2) , with no cross-check that these headers correspond to the body's origin.

`Registry.process` only validates the body HMAC and then trusts `request.shop`/`request.topic` to build the dispatched `WebhookMetadata`: it never verifies that the `shop-domain` header was itself part of what Shopify signed. [4](#0-3) 

The equality this breaks: `shop authenticated by HMAC` should equal `shop used as the tenant key for dispatch`, but the gem only guarantees `body authenticated by HMAC`, and separately trusts `shop header value` for tenant routing — these are two independent, unbound pieces of data.

Because the HMAC only covers the body, any request with a *matching* `(body, hmac)` pair — even one legitimately produced by Shopify for one tenant — remains valid regardless of which `shop-domain` header value accompanies it. An unprivileged internet user who controls their own store can register the same webhook topic on the app, receive a legitimately-HMAC-signed webhook delivery for their own shop, then replay that exact `(raw_body, hmac-sha256 header)` pair to the app's webhook endpoint while substituting the `shopify-shop-domain` header with a victim shop's domain. `Utils::HmacValidator.validate` still succeeds (it only checks the body hash), and the handler receives `WebhookMetadata` claiming the victim's `shop` for data that was never actually sent by/for that shop.

### Impact Explanation
This is a cross-tenant identity binding failure in webhook processing: the app-level handler logic keys tenant-scoped effects (e.g., updating stored app data, triggering per-shop actions like uninstall handling, GDPR redaction flows, or shop-scoped side effects) off `WebhookMetadata#shop`, which is attacker-controllable independent of the verified HMAC. This allows an unprivileged party to make the app process/act on payload data attributed to a shop they do not control, i.e. cross-tenant access/confusion at the webhook ingestion boundary — meeting the Critical bar of cross-tenant access.

### Likelihood Explanation
Exploitation requires only the ability to (a) install the app on an attacker-controlled shop to receive one legitimately signed webhook of a chosen topic/body, and (b) send an HTTP POST to the app's public webhook endpoint with a forged `shop-domain` header — no access to `api_secret_key`, tokens, or the victim's credentials is needed. This is reachable by any unprivileged internet user who can create a Shopify development/trial store and target a merchant's public webhook endpoint.

### Recommendation
Bind the tenant/topic identity into the signed content check: either require the host application to include `shop-domain`, `topic`, and `webhook-id` in the HMAC-covered material (this would require Shopify to change its signing scheme), or, since that's not controllable by this gem, at minimum document/enforce that consumers must correlate the `shop-domain` header against the shop associated with the registered webhook subscription (e.g., verified via a separate authenticated lookup) rather than trusting the header value directly for tenant-scoped dispatch. `Utils::HmacValidator` should also expose a way for `to_signable_string` to incorporate header-derived identity fields where the underlying provider signs them.

### Proof of Concept
1. Attacker registers app on their own shop `attacker.myshopify.com`; app receives a legitimate webhook POST with `raw_body`, and header `x-shopify-hmac-sha256: <valid hmac of raw_body>`, `x-shopify-shop-domain: attacker.myshopify.com`, `x-shopify-topic: orders/create`.
2. Attacker resends the identical `raw_body` and `x-shopify-hmac-sha256` value to the app's webhook endpoint, but changes `x-shopify-shop-domain` to `victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new(raw_body:, headers:)` builds a request whose `hmac` and `to_signable_string` are unaffected by the header change [5](#0-4) .
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only checks the (unchanged) body against the (unchanged) hmac [4](#0-3) .
5. The handler is invoked with `WebhookMetadata.new(shop: "victim.myshopify.com", ...)`, causing the app to process attacker-supplied data as if it belongs to the victim shop.

### Citations

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
