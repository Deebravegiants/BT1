## Analysis

The reachable analog is in the webhook‑processing path: `ShopifyAPI::Webhooks::Registry.process` validates the HMAC but the HMAC only covers the raw body — the shop, topic and webhook‑id headers are never bound into the signature. This mirrors the report's "field acted on but not covered by the HMAC" pattern. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) 

### Title
Webhook HMAC does not bind the `shop-domain`/`topic`/`webhook-id` headers, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, and `Utils::HmacValidator.validate` computes/compares the HMAC exclusively against that body. `Registry.process` treats a passing HMAC check as proof that the entire request — including the `shop`, `topic` and `webhook_id` values pulled from HTTP headers — is authentic and hands them straight to the app's webhook handler. Since those header values are never part of the signed material, they are fully attacker-controlled while the body+signature pair can come from a legitimately-signed webhook the attacker obtained for their own (attacker-owned) shop.

### Finding Description
`Request#to_signable_string` is defined as `@raw_body` only: [2](#0-1) 

`shop`, `topic`, `webhook_id`, and `api_version` are all read straight from unauthenticated headers with no participation in the signature: [5](#0-4) 

`HmacValidator.validate_signature` recomputes the HMAC purely from `verifiable_query.to_signable_string` (i.e. the body) and compares it to the received `hmac`: [3](#0-2) 

`Registry.process` uses a successful HMAC check as the sole authenticity gate, then forwards the *unauthenticated* `request.shop`, `request.topic`, and `request.webhook_id` directly into `WebhookMetadata` passed to the app's handler: [4](#0-3) 

The broken identity binding, expressed as an equality that should hold but doesn't:
`shop that produced the HMAC-signed bytes` == `shop the handler is told the event came from`

Any unprivileged internet user can install the target app on a shop they control (or otherwise trigger a webhook delivery for a topic they control), capturing a genuinely Shopify-signed `(raw_body, hmac)` pair for their own store. They can then POST that identical body/HMAC pair to the app's webhook endpoint while substituting `X-Shopify-Shop-Domain` (and optionally `X-Shopify-Topic`/`X-Shopify-Webhook-Id`) with a victim shop's domain. `HmacValidator.validate` still passes because the signature never covered those headers, and `Registry.process` dispatches the handler believing the event originates from the victim shop.

### Impact Explanation
This breaks tenant isolation: the app's webhook handler acts on data (e.g., GDPR/`shop/redact`, `app/uninstalled`, order/customer mutations) while believing it is scoped to the victim shop, when it is actually attacker-supplied content the attacker signed for their own tenant. This is a cross-tenant access primitive — an unprivileged attacker can make the host application perform shop-scoped side effects under a victim shop's identity, satisfying the "Critical - cross-tenant access" impact bar.

### Likelihood Explanation
Likelihood is Medium-to-High: any user can self-install the target Shopify app for free (or use a development store) to legitimately obtain a signed webhook body+HMAC pair for topics of their choosing, then replay it with a forged shop header against the same app's public webhook endpoint. No access to `api_secret_key`, access tokens, or any privileged credential is required — only observation of one legitimately delivered webhook for a shop the attacker controls.

### Recommendation
Bind the shop (and ideally topic/webhook-id) into the value that is authenticated, not just the raw body:
- Have the host application independently verify that `request.shop` corresponds to a shop it has actually installed/knows about (this is already advisable), and/or
- Extend `VerifiableQuery`/`to_signable_string` so the HMAC computation incorporates the shop-domain header when available, rejecting mismatches, and
- Document explicitly in `Webhooks::Registry.process` that `request.shop`/`topic`/`webhook_id` are unauthenticated header values and must be cross-checked by the caller against known installed shops before being trusted for tenant-scoped side effects.

### Proof of Concept
1. Attacker installs the target app on `attacker.myshopify.com` (or triggers any webhook topic they control) and captures the resulting POST: raw body `B` and header `X-Shopify-Hmac-Sha256: H` (a valid signature of `B` under the app's secret).
2. Attacker sends a new POST to the app's webhook endpoint with the same body `B` and header `H`, but sets:
   - `X-Shopify-Shop-Domain: victim-shop.myshopify.com`
   - `X-Shopify-Topic: <topic of choice>`
3. `Utils::HmacValidator.validate` recomputes HMAC over `B` only, matches `H`, and passes.
4. `Registry.process` builds `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: parsed(B), topic: ..., ...)` and invokes the registered handler, which now performs shop-scoped work attributing attacker-controlled data to the victim shop. [4](#0-3)

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
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
