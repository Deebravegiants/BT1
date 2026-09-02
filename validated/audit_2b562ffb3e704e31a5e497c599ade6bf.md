### Title
Webhook `shop`/`topic` Headers Are Not Bound by the HMAC Signature, Enabling Cross-Tenant Webhook Spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` signs only the raw request body for HMAC verification, while the `shop-domain`, `topic`, `webhook-id`, and `api-version` values used by `ShopifyAPI::Webhooks::Registry.process` to route and attribute the webhook are taken from unauthenticated HTTP headers that are never part of the signed payload. This is the same class of bug as the oracle report: a value that is *acted upon* (here, tenant/topic attribution) is not covered by the integrity check (here, the HMAC) that is supposed to bind it.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#hmac`, `#topic`, `#shop`, `#webhook_id`, and `#api_version` are each read independently from HTTP headers, none of which participate in the signature: [2](#0-1) 

`HmacValidator.validate` only checks the signature over `to_signable_string` (i.e. the body) against `Context.api_secret_key`: [3](#0-2) 

`Registry.process` validates the HMAC and then trusts `request.topic` and `request.shop` — which are not bound by that HMAC — to route to a handler and to attribute the event to a tenant: [4](#0-3) 

Because the `api_secret_key` is a single, app-wide secret shared across every shop that has installed the app (not a per-shop secret), any merchant who has installed the app can trivially obtain a legitimately-signed `(body, hmac)` pair for their own shop (e.g. by triggering a `shop/update` or similar low-sensitivity webhook on their own store and capturing the delivery). That merchant — an otherwise unprivileged internet user with respect to *other* tenants' data — can then replay that exact body and HMAC directly to the app's webhook endpoint while substituting the `x-shopify-shop-domain` header (and/or `x-shopify-topic` header) for a victim shop. `HmacValidator.validate` still succeeds because the signed content (the body) is unchanged; `Registry.process` then hands the forged `shop`/`topic` to the app's handler as if the event genuinely originated from the victim shop.

This breaks the intended identity binding: **`hmac` is meant to guarantee `(body, shop, topic)` == what Shopify sent**, but the implementation only guarantees `hmac` == `sign(body)`, leaving `shop` and `topic` unauthenticated inputs to security-relevant routing/attribution logic — directly analogous to the oracle bug where the price returned by the aggregator (`minPrice`) was used to make lending decisions without checking whether it actually reflected the true bound.

### Impact Explanation
This allows cross-tenant data/event attribution: a malicious merchant can cause the host application to process a webhook event as if it belongs to a different, victim shop, using only a validly-signed body they legitimately received for their own store. Depending on the host app's webhook handlers, this can trigger unauthorized state changes, data corruption, or spurious lifecycle events (e.g. forged `app/uninstalled`, `shop/update`, or GDPR-mandatory webhooks) attributed to a shop the attacker does not control — a cross-tenant boundary violation, which is listed as Critical impact.

### Likelihood Explanation
The `api_secret_key` is shared across all installations of the app (not shop-specific), and any real merchant using the app can generate at least one legitimately-signed webhook body/HMAC pair by interacting with their own store in ways that trigger a webhook subscribed by the app. Crafting the forged HTTP request (same body/HMAC, different `shop-domain`/`topic` header) requires no special privilege, credentials, or access token — only unauthenticated HTTP access to the app's public webhook endpoint.

### Recommendation
Include `topic`, `shop-domain`, and `webhook-id` (in addition to the body) in the value that is HMAC-signed/verified, or otherwise cryptographically bind them to the signature (e.g., by having `to_signable_string` concatenate the canonicalized headers with the body). At minimum, document and enforce that `shop`/`topic` must never be trusted for tenant-sensitive decisions unless they are covered by the HMAC.

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker-shop.myshopify.com` (a legitimate, unprivileged install).
2. Attacker triggers a low-sensitivity subscribed webhook (e.g. `shop/update`) on their own store, and captures the raw POST body `B` and the `X-Shopify-Hmac-Sha256` header value `H` that Shopify sends to the app's webhook endpoint (both signed with the app's single shared `api_secret_key`).
3. Attacker sends a new POST request directly to the app's webhook endpoint with:
   - body = `B` (unchanged)
   - header `X-Shopify-Hmac-Sha256` = `H` (unchanged)
   - header `X-Shopify-Shop-Domain` = `victim-shop.myshopify.com` (forged)
   - header `X-Shopify-Topic` = `shop/update` (same or forged to another registered topic)
4. `Utils::HmacValidator.validate` succeeds because it only checks `H` against `sign(B)` [5](#0-4) .
5. `Registry.process` dispatches to the registered handler with `shop: "victim-shop.myshopify.com"` [6](#0-5) , causing the host app to process an event as belonging to a shop the attacker does not own/control.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-33)
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
