This confirms the finding. The `shop-domain` header is read verbatim and used as the tenant identity passed to webhook handlers, while `to_signable_string` only covers `@raw_body` — the `shop`, `topic`, `api-version`, and `webhook-id` headers are entirely excluded from the HMAC computation.### Title
Webhook tenant identity (`shop-domain` header) is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` reads the `x-shopify-shop-domain` header as the tenant identity for a webhook and hands it directly to the host application's handler as `WebhookMetadata#shop`, but the HMAC signature that `ShopifyAPI::Utils::HmacValidator.validate` checks is computed only over the raw request body. The `shop`, `topic`, `webhook-id`, and `api-version` headers are entirely outside the signed payload, so `Registry.process` accepts any `shop-domain` value paired with a validly-signed body, regardless of which shop the body was actually generated for.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

but `shop` (and `topic`, `webhook_id`, `api_version`) are read straight from unauthenticated headers: [2](#0-1) 

`ShopifyAPI::Webhooks::Registry.process` validates the request solely via `Utils::HmacValidator.validate(request)`, which calls `verifiable_query.to_signable_string` (i.e. only the body) against the app's shared secret, and then forwards the unauthenticated `request.shop` straight into the handler: [3](#0-2) 

`Utils::HmacValidator.validate_signature` proves this: it computes `compute_signature(verifiable_query.to_signable_string, secret)` and compares it to the received HMAC — nothing about the `shop` header participates in that computation: [4](#0-3) 

The identity binding that should hold is:
`shop header trusted by handler == shop cryptographically bound by HMAC`

but the actual relationship is:
`shop header trusted by handler ≠ any field covered by HMAC (only raw_body is signed)`

Because the app's client secret (used to key the HMAC) is the same for every shop that installs the app, any merchant/tenant that has installed the app receives real, validly-signed webhooks for their own shop. That merchant can capture a legitimate `(raw_body, x-shopify-hmac-sha256)` pair from their own tenant and resubmit it to the app's webhook endpoint with the `x-shopify-shop-domain` header changed to a victim shop's domain. `Utils::HmacValidator.validate` will still pass because the header is not part of the signed string, and `WebhookMetadata.shop` will report the victim's shop to the handler even though the body content originated from the attacker's own shop.

The `WebhookMetadata` struct built for the handler exposes exactly this unauthenticated field as `shop`: [5](#0-4) 

### Impact Explanation
Host applications built on this gem are expected to use `WebhookMetadata#shop` as the tenant key to route webhook data (e.g., update the correct merchant's local records, revoke access, trigger app-uninstall cleanup, etc.). An attacker who is a legitimate merchant/tenant of the app can forge the tenant identity on a signature-valid webhook delivery, causing the host app to process attacker-supplied data under another merchant's identity. This is a cross-tenant data-integrity/isolation break reachable by any unprivileged (but registered) app user, without needing the `client_secret`, an access token, or any privileged account — satisfying the "cross-tenant access" criteria.

### Likelihood Explanation
Exploitation requires only: (1) being a merchant who has installed the target app (to legitimately receive one real signed webhook), and (2) the ability to send an arbitrary HTTP POST to the app's public webhook endpoint with a modified `shop-domain` header while replaying the captured signed body and HMAC. No cryptographic secret or privileged credential is needed. This is a realistic, low-effort abuse path for any multi-tenant app relying on this gem's webhook processing for tenant identification.

### Recommendation
- **Short term**: Include the `shop-domain` (and ideally `topic`, `webhook-id`) header values in the signed payload used for HMAC verification (`to_signable_string`), or otherwise cryptographically bind the tenant identity to the signature, so a captured (body, HMAC) pair cannot be replayed under a different shop's identity. At minimum, document prominently that `WebhookMetadata#shop` is **not** authenticated by the HMAC and must not be trusted as a tenant boundary without additional verification (e.g., cross-checking against a known/registered shop list).
- **Long term**: Audit all fields exposed to host application code following a successful `HmacValidator.validate` call, and ensure that every field acted upon downstream (shop, topic, api_version, webhook_id) is either covered by the signature or clearly documented as unauthenticated.

### Proof of Concept
1. Attacker installs the target Shopify app on their own shop `attacker-shop.myshopify.com`, becoming a legitimate app tenant.
2. Attacker triggers (or waits for) a real webhook event (e.g., `orders/create`) on their own shop; Shopify sends a request to the app's webhook endpoint with:
   - `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`
   - `X-Shopify-Hmac-Sha256: <valid HMAC over raw_body>`
   - `raw_body: <attacker-controlled event JSON, e.g. an order payload>`
3. Attacker captures this exact `raw_body` and `X-Shopify-Hmac-Sha256` value.
4. Attacker resends an HTTP POST to the same webhook endpoint, keeping `raw_body` and `X-Shopify-Hmac-Sha256` identical, but replacing the header:
   - `X-Shopify-Shop-Domain: victim-shop.myshopify.com`
5. `ShopifyAPI::Webhooks::Request.new` builds the request from these headers; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `raw_body` only and matches the (unchanged) received HMAC — validation succeeds.
6. The handler is invoked with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: <attacker's data>, ...)`, causing the host application to process attacker-controlled data as if it belonged to `victim-shop.myshopify.com`.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
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
