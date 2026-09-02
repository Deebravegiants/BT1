## Finding

### Title
Webhook `shop` (and topic/API-version) identity fields are not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes the HMAC-verifiable signable string from the raw body only, while the `shop` (tenant) identifier, `topic`, `api_version`, and `webhook_id` are all read directly from unauthenticated HTTP headers and are never part of the signed content. Any request bearing a body/HMAC pair that is valid for the shared app `client_secret` can be replayed with an arbitrary `shop-domain` header, and `Webhooks::Registry.process` will accept it and hand the attacker-chosen shop to the app's business logic.

### Finding Description
`Webhooks::Registry.process` validates a webhook solely via `Utils::HmacValidator.validate(request)`: [1](#0-0) 

`HmacValidator.validate` computes `compute_signature(verifiable_query.to_signable_string, secret)` and compares it to the `hmac` field via constant-time comparison: [2](#0-1) 

For `Webhooks::Request`, `to_signable_string` returns only the raw request body — `@raw_body` — while `shop`, `topic`, `api_version`, and `webhook_id` are parsed straight out of HTTP headers with no cryptographic binding to that body: [3](#0-2) 

After the HMAC check passes, `process` immediately trusts `request.shop` (and `request.topic`) to build `WebhookMetadata` and dispatch to the registered handler: [4](#0-3) 

The identity binding that should hold is: **`shop` used to authorize/attribute the webhook event == the shop cryptographically bound to the signed payload**. That equality is never enforced — `shop` is never part of `to_signable_string`, so it is verified via headers but never actually covered by the HMAC.

Critically, in the Shopify app model, `Context.api_secret_key` (the HMAC key) is the same `client_secret` shared across **every merchant shop** that installs the app — it is not per-tenant. This means:
- Before: any shop `A` that installs the app can trigger a real webhook delivery for itself, obtaining a `(body, hmac)` pair that is valid under the shared secret.
- After: that same attacker replays the identical `(body, hmac)` pair directly to the app's webhook endpoint, but substitutes the `x-shopify-shop-domain` header with victim shop `B`'s domain.
- `HmacValidator.validate` still returns `true` (it never looked at `shop`), and `Registry.process` dispatches the handler with `shop: "B"` even though the payload was never actually generated for `B`.

This breaks the identity binding "shop authenticated == shop the payload is attributed to," the same bug class described in the source report where a value participates in security-relevant state (the shop attribution used by the handler) without being covered by the validated signature.

### Impact Explanation
This enables cross-tenant confusion: an attacker who is a legitimate (even unprivileged/free) installer of the app on their own shop can forge webhook events that the app's handler will process as if they originated from a different, victim shop. Depending on what the host application's webhook handler does with `WebhookMetadata#shop` (e.g., invalidate victim data, update victim state, trigger `shop/redact` / `customers/redact` compliance flows, or write against records keyed by `shop`), this can lead to cross-tenant data corruption or unauthorized actions attributed to another merchant — satisfying the "cross-tenant access" criterion.

### Likelihood Explanation
Likelihood is realistic but not trivial: the attacker must be able to install the app on at least one shop (many apps allow free/open installs) to receive one genuinely-signed webhook body/HMAC pair, and must be able to reach the app's webhook HTTP endpoint directly with custom headers (a normal internet-facing endpoint, since this gem's `Request` class accepts headers from any request, not just ones originating from Shopify's IP ranges). No access token, `api_secret_key`, or privileged credential is required beyond the attacker's own tenant's webhook deliveries.

### Recommendation
- **Short term**: Extend `Webhooks::Request#to_signable_string` (or add a post-HMAC check in `Registry.process`) to bind the `shop` (and ideally `topic`) header values into what's verified — e.g. reject/flag requests where the `shop` associated with a delivery cannot be independently corroborated (such as checking the shop has an active, matching webhook subscription id via `Registry.get_webhook_id`/API lookup, or requiring source IP allow-listing for Shopify's published webhook IP ranges).
- **Long term**: Document explicitly (and enforce where possible) that `shop-domain` on inbound webhook requests is untrusted attacker-controllable data that must never be used for tenant-authorization decisions without additional verification, since Shopify's own HMAC scheme only covers the body.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com`, completing OAuth normally (no special privilege required).
2. Attacker triggers a webhook-eligible action (e.g. creates an order) causing Shopify to deliver a webhook to the app's endpoint with a body `B` and a valid `x-shopify-hmac-sha256` header computed with the app's shared `client_secret`.
3. Attacker intercepts/logs this `(B, hmac)` pair (they own this shop, so they can, e.g. via a debugging proxy, or simply construct `B` themselves for topics whose body they can predict).
4. Attacker sends a new POST request directly to the app's public webhook endpoint with:
   - Body = `B`
   - `x-shopify-hmac-sha256` = the same valid hmac
   - `x-shopify-shop-domain` = `victim-shop.myshopify.com`
   - `x-shopify-topic` = original topic
5. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only checks `body` against `hmac`, ignoring `shop-domain` — validation succeeds.
6. The app's registered handler is invoked with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...)`, causing the app to process an event as if it came from the victim shop, despite it never having sent it.

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
