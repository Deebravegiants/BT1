I have enough evidence to confirm the vulnerability.

### Title
Webhook `shop` and `topic` identifiers are not covered by HMAC verification, enabling cross-tenant replay confusion - (File: lib/shopify_api/webhooks/request.rb, lib/shopify_api/webhooks/registry.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook by validating the HMAC signature, but the signature is computed only over the raw request body. The `shop`, `topic`, `webhook_id`, and `api_version` values that identify *which tenant and event* the webhook belongs to are read straight from HTTP headers and are never included in the signed bytes. This breaks the intended binding: `HMAC(body) == valid` should imply `shop header == the shop that produced this body`, but the library only proves the former, then trusts the latter unconditionally when building `WebhookMetadata` and dispatching it to the app's handler.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Utils::HmacValidator.validate` computes the HMAC purely over that signable string and compares it to the `hmac-sha256` header: [2](#0-1) 

`Registry.process` gates on that HMAC check, then immediately builds a `WebhookMetadata` object from unauthenticated header fields (`request.shop`, `request.topic`, `request.webhook_id`, `request.api_version`) and hands it to the host app's handler: [3](#0-2) 

`request.shop`, `request.topic`, `request.webhook_id`, and `request.api_version` are all pulled directly from HTTP headers with no cryptographic tie to the signed body: [4](#0-3) 

The equality that the check is supposed to enforce is:
`HMAC_valid(body) == true` implies `shop header value == shop that Shopify actually generated this HMAC/body for`

But the real behavior is only:
`HMAC_valid(body) == true` implies `body bytes were HMAC'd with the app's secret at some point (for some shop, at some time)`

Because a merchant who has legitimately installed the app receives their own, genuinely-signed webhook deliveries (valid `hmac-sha256` for their own body), that merchant — an ordinary, unprivileged app user with no special access — can capture one such `(raw_body, hmac)` pair from their own tenant and resubmit it to the app's webhook endpoint with the `X-Shopify-Shop-Domain` (and/or `X-Shopify-Topic`/`X-Shopify-Webhook-Id`) header rewritten to name a different, victim shop. `HmacValidator.validate` still passes because it only checks the body/HMAC pair, and `Registry.process` will hand the handler a `WebhookMetadata` claiming the event belongs to the victim shop, with the attacker's forged/replayed body content.

### Impact Explanation
This falls under the Critical "cross-tenant access" category: an app that trusts `WebhookMetadata#shop` (as the library's documented contract implies it should, since it is the field the API exposes specifically for this purpose) to route data or perform per-tenant side effects (e.g., updating the record for `shop`, deleting data, marking a shop's subscription/plan, writing to the tenant's row keyed by `shop`) can be made to apply an attacker-controlled shop's tenant-scoped webhook body to a different, victim shop identifier. No `api_secret_key`, access token, or client secret is required by the attacker — they only need to be an installed (unprivileged) merchant capable of receiving one legitimate webhook for their own store, which is normal, unprivileged access.

### Likelihood Explanation
Likelihood is moderate-to-high: any merchant who installs the app can trigger at least one real webhook to their own endpoint (e.g. by editing a resource, or via the mandatory GDPR webhooks), capture the `raw_body` + `hmac-sha256` header pair, and replay it against the same public webhook endpoint with a substituted `shop-domain` header. No secret material or privileged access is needed — only the ability to observe one's own genuine webhook traffic (e.g., via request logging middleware, a proxy, or a debug endpoint) and resend an HTTP POST.

### Recommendation
Include the identifying headers (`shop`, `topic`, `webhook_id`, `api_version`) in the signable string used for HMAC verification, or otherwise cryptographically bind them to the signed body, so that `Registry.process` cannot be fed a body validly signed for one shop/topic while claiming a different shop/topic in the metadata passed to the handler. At minimum, document prominently that `WebhookMetadata#shop`/`#topic` are unauthenticated headers and that host applications must independently corroborate them (e.g., against the webhook subscription that was registered), since the current API surface implies they were verified alongside the HMAC.

### Proof of Concept
1. Attacker installs the app on their own store `attacker.myshopify.com` and observes a legitimate webhook delivery to the app's `/webhooks` endpoint, e.g.:
   ```
   X-Shopify-Topic: orders/create
   X-Shopify-Hmac-Sha256: <valid-hmac-for-body>
   X-Shopify-Shop-Domain: attacker.myshopify.com
   Body: {"id":1,...attacker-controlled order payload...}
   ```
2. Attacker resends the exact same body and `X-Shopify-Hmac-Sha256` value to the same endpoint, but changes the shop header:
   ```
   X-Shopify-Topic: orders/create
   X-Shopify-Hmac-Sha256: <same-valid-hmac>
   X-Shopify-Shop-Domain: victim.myshopify.com
   Body: {"id":1,...attacker-controlled order payload...}
   ```
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only checks `request.to_signable_string` (the raw body) against the HMAC — this still succeeds because the body/HMAC pair is unchanged, as shown in [5](#0-4) .
4. The handler receives `WebhookMetadata.new(topic: "orders/create", shop: "victim.myshopify.com", body: {...attacker data...}, ...)`, as constructed in [6](#0-5) , causing the app to process attacker-supplied data under the victim shop's identity.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-23)
```ruby
      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
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
