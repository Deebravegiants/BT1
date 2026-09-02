I have enough evidence to confirm the finding.

### Title
Webhook `shop` and `topic` identity fields are not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable content from the raw HTTP body only, while the `shop`, `topic`, `webhook_id`, and `api_version` values used to route and process the webhook are read from unauthenticated HTTP headers. `Registry.process` validates the HMAC and then dispatches the handler using these unsigned header values, so the tenant ("shop") and business meaning ("topic") of an otherwise validly-signed payload can be swapped by an attacker.

### Finding Description
The identity binding that should hold is: `hmac == HMAC(secret, shop || topic || raw_body)`. In practice the binding implemented is only `hmac == HMAC(secret, raw_body)`: [1](#0-0) [2](#0-1) [3](#0-2) 

`to_signable_string` returns only `@raw_body`, meaning the `shop` (`shop-domain` header) and `topic` header are never mixed into the HMAC computation. `HmacValidator.validate` then only checks the signature against `to_signable_string`: [4](#0-3) 

`Registry.process` accepts the request once the HMAC of the body passes, and then builds `WebhookMetadata` — including `shop` and `topic` — directly from the same unauthenticated headers, and hands it to the app-provided handler: [5](#0-4) 

Since all webhooks for a given app are signed with the *same* `api_secret_key` regardless of which shop triggered them (there is no per-shop signing secret and no per-shop material in the signable string), any unprivileged internet user who can install the app on their own store (or otherwise trigger any webhook to their own shop) obtains a raw body + valid HMAC pair that Shopify itself signed with the app's shared secret. That attacker can then resend the identical `raw_body`/HMAC to the app's public webhook endpoint while substituting the `X-Shopify-Shop-Domain` and `X-Shopify-Topic` headers with a victim shop and a sensitive topic (e.g. one of the mandatory GDPR topics `shop/redact`, `customers/redact`, `customers/data_request`, or a lifecycle topic such as `app/uninstalled`): [6](#0-5) 

`HmacValidator.validate` still returns `true` (it never inspected `shop` or `topic`), and the handler is invoked believing the event legitimately originated from the victim shop/topic — this is exactly the "field acted on but not covered by the HMAC" pattern: the check (HMAC over the body) answers a different question than the one the caller relies on downstream (which shop/topic this event is attributed to).

### Impact Explanation
This breaks the tenant-isolation guarantee of the webhook mechanism: an attacker with no privileged credentials can make a host application process arbitrary webhook bodies (from their own store) under an arbitrary victim shop domain and arbitrary topic of the attacker's choosing. Depending on how the host app implements its mandatory-topic handlers (data erasure, uninstall cleanup, session/token invalidation), this enables cross-tenant data manipulation or destructive actions being triggered against a shop the attacker doesn't own — satisfying the "cross-tenant access" Critical impact category, since the identity of the affected tenant is entirely attacker-controlled while riding on a Shopify-issued valid signature.

### Likelihood Explanation
Likelihood is high for any consumer of this gem's webhook helpers: the attacker only needs a legitimately owned/installed shop (trivial to obtain, e.g. a free Shopify developer/dev store) to harvest one valid `raw_body` + `hmac-sha256` pair per topic of interest, and standard HTTP tooling to replay it with rewritten headers to the public webhook endpoint. No access to `api_secret_key`, tokens, or the target shop is required.

### Recommendation
Include the `shop` and `topic` (and ideally `webhook_id`) values in the signable string that is HMAC-verified, or otherwise independently authenticate that the `shop-domain`/`topic` headers match a value cryptographically bound to the signed payload, before constructing `WebhookMetadata` and invoking the handler in `Registry.process`.

### Proof of Concept
1. Install the target app (using this gem) on an attacker-controlled Shopify development store, and capture a real inbound webhook delivery — its raw HTTP body and its `X-Shopify-Hmac-Sha256` header (valid, computed by Shopify with the app's shared `api_secret_key`).
2. Confirm the signature is only ever checked against the body: `ShopifyAPI::Utils::HmacValidator.validate(request)` in `Registry.process` (`lib/shopify_api/webhooks/registry.rb:190`) uses `request.to_signable_string`, which is `@raw_body` (`lib/shopify_api/webhooks/request.rb:35-38`) — no header is included.
3. Replay the captured raw body and HMAC header unmodified to the app's public webhook endpoint, but replace:
   - `X-Shopify-Shop-Domain: attacker-shop.myshopify.com` → `victim-shop.myshopify.com`
   - `X-Shopify-Topic: <original>` → `shop/redact` (or `app/uninstalled`, etc.)
4. `ShopifyAPI::Webhooks::Request.new(raw_body:, headers:)` builds successfully (all required headers present), `HmacValidator.validate` returns `true` (body unchanged), and `Registry.process` dispatches `WebhookMetadata.new(topic: "shop/redact", shop: "victim-shop.myshopify.com", body: request.parsed_body, ...)` to the registered handler — which now believes it received a legitimate redact/uninstall event for `victim-shop.myshopify.com`, despite the attacker never having any credentials for that shop.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-15)
```ruby
      sig { returns(String) }
```

**File:** lib/shopify_api/webhooks/request.rb (L20-23)
```ruby
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

**File:** lib/shopify_api/webhooks/registry.rb (L8-12)
```ruby
      MANDATORY_TOPICS = T.let([
        "shop/redact",
        "customers/redact",
        "customers/data_request",
      ].freeze, T::Array[String])
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
