### Title
Webhook `shop` and `topic` identity fields are not covered by HMAC verification, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` binds the HMAC signature to the raw request body only, while `shop`, `topic`, `webhook_id`, and `api_version` are all read from unauthenticated HTTP headers. `Registry.process` validates the HMAC and then trusts these header-derived fields to build `WebhookMetadata`, which the host app's handler acts on as the identity of the webhook's origin shop.

### Finding Description
This mirrors the analog bug class in the reference report: the rule used to bind the security-relevant identity to the verified payload is inconsistent between what is checked and what is used.

`Utils::HmacValidator.validate` computes the HMAC purely over `verifiable_query.to_signable_string`: [1](#0-0) 

For webhooks, `to_signable_string` returns only the raw body: [2](#0-1) 

But `shop`, `topic`, `webhook_id`, and `api_version` are all parsed straight from HTTP headers, which are never included in the signable string and thus never covered by the HMAC: [3](#0-2) 

`Registry.process` validates the HMAC (over body only) and then immediately trusts `request.shop` and `request.topic` — taken from unauthenticated headers — to build the `WebhookMetadata` object handed to the app's handler: [4](#0-3) 

The identity binding that should hold is: `shop used by handler == shop that the HMAC-signed body actually originated from`. Because the HMAC only binds the *body* bytes, and `shop`/`topic` are read from bytes (headers) that are never verified, this equality does not hold. Any unprivileged internet user who can obtain **one** valid `(body, hmac)` pair — trivially available by installing the app on their own store and receiving one webhook, or observing any publicly-known/mandatory webhook payload format — can replay that exact body and its valid HMAC digest to the app's webhook endpoint while attaching an arbitrary `shopify-shop-domain` and `shopify-topic` header. `HmacValidator.validate` will still succeed because it never inspects the headers, and `Registry.process` will hand the forged `shop`/`topic` combination to the app's handler as if it were authentic.

### Impact Explanation
This breaks the tenant boundary the host application relies on: the app is told "this data event happened for shop X" when in fact an external, unauthenticated party chose X and the payload's real origin was unrelated (or a body the attacker crafted for their own store). Any host application that uses `WebhookMetadata#shop` to decide which tenant's data to update, delete, or export (the exact use case for the mandatory `shop/redact`, `customers/redact`, `customers/data_request` topics defined in `Registry::MANDATORY_TOPICS`) can be tricked into performing tenant-scoped actions against an arbitrary victim shop chosen by the attacker, or into misclassifying the event topic. This is a cross-tenant identity confusion at the gem's own verification boundary, matching the High-impact bar (cross-tenant action driven by an unverified identity field).

### Likelihood Explanation
The only prerequisite is the ability to send an HTTP POST to the app's public webhook endpoint (any unprivileged internet user) plus one legitimately HMAC-signed body/HMAC pair, which is trivially obtainable by installing the app on an attacker-controlled test store and capturing the resulting webhook request. No access to `api_secret_key`, tokens, or privileged accounts is required — the attacker never needs to forge the HMAC itself, only replay a genuine one under attacker-chosen headers.

### Recommendation
Include the identity-bearing fields (`shop-domain`, `topic`, and ideally `webhook-id`/`api-version`) in the HMAC-verified signable content, or otherwise cryptographically bind them to the body (e.g., verify the header values against a canonical string that is part of the HMAC input), so that `HmacValidator.validate` fails if any of these headers are altered relative to the originally-signed request.

### Proof of Concept
1. Attacker installs the target app on their own Shopify development store and lets it receive one real webhook, e.g. `orders/create`, capturing the raw body `B` and its valid `shopify-hmac-sha256` header value `H` (computed over `B` with the app's shared secret).
2. Attacker sends a POST to the app's webhook endpoint with:
   - body: `B` (unchanged)
   - `shopify-hmac-sha256`: `H` (unchanged, still valid for body `B`)
   - `shopify-shop-domain`: `victim-shop.myshopify.com` (attacker-chosen, not the attacker's real shop)
   - `shopify-topic`: `shop/redact` (attacker-chosen, differs from the topic `B` was originally generated for)
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes HMAC over `@raw_body` only (`lib/shopify_api/webhooks/request.rb:35-38`) — validation succeeds because `B` and `H` are unmodified.
4. `Registry.process` builds `WebhookMetadata.new(topic: "shop/redact", shop: "victim-shop.myshopify.com", body: JSON.parse(B), ...)` and invokes the host app's handler as if `victim-shop.myshopify.com` genuinely sent a `shop/redact` event, even though neither field was ever verified.

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

**File:** lib/shopify_api/webhooks/request.rb (L35-38)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
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
