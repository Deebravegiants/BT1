### Title
Webhook `shop`, `topic`, and `webhook-id` identity headers are not covered by the HMAC signature, enabling cross-tenant spoofing on replay - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable content from the raw body only, while the `shop`, `topic`, `webhook_id`, and `api_version` values are read straight from unauthenticated HTTP headers and handed to the app's webhook handler as trusted tenant-identifying metadata.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Utils::HmacValidator.validate` verifies the HMAC exclusively against `to_signable_string`: [2](#0-1) 

`Registry.process` then trusts `request.shop`, `request.topic`, `request.webhook_id`, and `request.api_version` — none of which are part of the signed content — to build `WebhookMetadata` that is handed to the app's handler as authenticated tenant context: [3](#0-2) 

The `shop` accessor is populated purely from the `shopify-shop-domain` / `x-shopify-shop-domain` header with no relation to the HMAC: [4](#0-3) 

The identity binding that should hold is: `hmac_signed_content == (raw_body, shop, topic, webhook_id)`, but the actual binding implemented is `hmac_signed_content == raw_body` only. This breaks the equality `shop_header == shop_bound_by_hmac`.

### Impact Explanation
An unprivileged internet user who can install the app on their own Shopify development store (a normal, unprivileged self-service action) will receive genuine webhook deliveries for their own shop — each with a body and a correctly computed HMAC signature (both non-secret, observable on the wire/in their own app logs). Because the HMAC only signs the body, that same `(body, hmac)` pair remains valid regardless of the `shop-domain` header sent alongside it. The attacker can replay the captured request to the app's public webhook endpoint while substituting the `shop-domain` header (and/or `topic`/`webhook-id`) with a victim shop's domain or a different topic. `HmacValidator.validate` still succeeds (it never inspects the header), and `Registry.process` forwards the attacker-chosen `shop` value to the app's handler as if Shopify itself vouched for it. If the host application uses `data.shop` to select which merchant's database record to update (the documented, expected usage pattern per this gem's own webhook docs), this yields cross-tenant data corruption/exfiltration triggered entirely from bytes an unprivileged user controls.

### Likelihood Explanation
Likelihood is elevated because: (1) obtaining a valid `(body, hmac)` pair requires nothing more than installing the app on one's own store — a routine, unprivileged action available to any internet user; (2) the webhook endpoint is by design a public, unauthenticated HTTP endpoint; (3) the gem's own documentation instructs apps to build tenant identity directly from `data.shop` passed into the handler, meaning host applications following the documented API are structurally exposed. Exploitation does not require the app's `client_secret`, an access token, or any credential — it only requires the network reachability every legitimate webhook already has.

### Recommendation
Include the identity-critical headers (`shop-domain`, `topic`, and ideally `webhook-id`/`api-version`) in the HMAC-signable content, or otherwise independently verify that the `shop` used to dispatch a webhook corresponds to the same tenant the raw body's payload actually references (e.g., cross-check against the payload's own shop/domain fields) before constructing `WebhookMetadata`. Shopify's server-side webhook signing only covers the body by design, so at minimum this gem should document prominently that `request.shop`/`request.topic` are *not* cryptographically authenticated and must not be used as sole tenant-selection input, or the gem should refuse processing when a previously-seen `(body, hmac)` pair is replayed with a different header combination (e.g., via idempotency tracking keyed on `webhook_id`).

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com` and receives a legitimate webhook, e.g. for `orders/create`, with body `B` and header `X-Shopify-Hmac-Sha256: H` (valid because `H = HMAC(secret, B)`).
2. Attacker resends the exact same `B` and `H` to the app's public webhook URL, but sets `X-Shopify-Shop-Domain: victim.myshopify.com` (and, if desired, a different `X-Shopify-Topic`).
3. `Webhooks::Request.new` parses the forged headers; `HmacValidator.validate` recomputes `HMAC(secret, B)` and compares only against `B`, which is unchanged, so validation passes: [5](#0-4) 
4. `Registry.process` dispatches to the handler with `shop: "victim.myshopify.com"`, `body: request.parsed_body` (the attacker's own order data), and the app processes it under the victim's tenant context — a cross-tenant write/read using data the attacker fully controls.

### Citations

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
