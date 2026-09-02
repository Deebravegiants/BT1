### Title
Webhook `shop`, `topic`, and `webhook_id` fields are trusted and dispatched to handlers without being covered by the HMAC signature - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature over the raw request body only, while the `shop`, `topic`, `webhook_id`, and `api_version` fields — read from separate HTTP headers — are never included in the signed bytes. `Registry.process` validates the HMAC and then unconditionally forwards these unauthenticated header values to the app's webhook handler as the identity of the tenant (`shop`) the payload belongs to. This breaks the identity binding that `signed_bytes == verified_bytes` should hold for every field the handler acts on.

### Finding Description
`Utils::HmacValidator.validate` computes the signature over `verifiable_query.to_signable_string` and compares it against `verifiable_query.hmac`: [1](#0-0) 

For webhooks, `to_signable_string` returns only the raw HTTP body: [2](#0-1) 

But `shop`, `topic`, `webhook_id`, and `api_version` are pulled straight from HTTP headers and are not part of that signed string at all: [3](#0-2) 

`Registry.process` validates the HMAC of the body, then dispatches the handler using the unauthenticated `request.shop`, `request.topic`, and `request.webhook_id` values as the tenant/context identity for the event: [4](#0-3) 

The equality that should hold is: every field the handler acts upon (`shop`, `topic`, `webhook_id`, `body`) must be bound inside the HMAC-signed bytes. Instead, `signed_bytes = {raw_body}` while `acted_on_bytes = {raw_body, shop_header, topic_header, webhook_id_header}`. The `shop` field — used by the host app to know which merchant/tenant the payload is for — is completely outside the cryptographic binding.

### Impact Explanation
An unprivileged internet user who has installed the app on their own (attacker-controlled) shop will receive genuinely-signed webhook deliveries: a `(raw_body, hmac)` pair that is valid under the app's shared `api_secret_key`, since the secret is identical for every shop that installs the app. Because the `shop-domain` header is never part of the signed content, the attacker can replay that exact valid `(raw_body, hmac)` pair directly to the app's public webhook endpoint while substituting an arbitrary `shopify-shop-domain` (and `shopify-topic`/`shopify-webhook-id`) header value naming a victim shop. `HmacValidator.validate` will still return `true` (the body/HMAC pair is authentic), and `Registry.process` will hand the handler a `WebhookMetadata` claiming the data came from the victim's shop. Any host application logic that uses `data.shop` to select the tenant record, session, or credentials to act on is now processing attacker-supplied data under another tenant's identity — a cross-tenant confusion rooted entirely in this gem's signature scope.

### Likelihood Explanation
Any app developer using this gem's `Registry.process`/`Request` as documented is affected, since the signing scope is fixed by the gem, not configurable by the host app. Exploitation requires only: (1) the ability to install the app on any shop (self-signup, low privilege) to obtain one valid `(body, hmac)` sample, and (2) direct unauthenticated HTTP access to the app's public webhook endpoint, which is expected to be internet-reachable by design.

### Recommendation
Include the identity-relevant headers (`shop`, `topic`, `webhook_id`) in the HMAC-signed payload, or otherwise cryptographically bind the shop to the signed bytes, e.g.:

```ruby
sig { override.returns(String) }
def to_signable_string
  "#{shop}|#{topic}|#{webhook_id}|#{@raw_body}"
end
```

and require the app's Shopify to sign over that composite string, or alternatively document and enforce that `data.shop` must never be trusted without independently confirming the webhook subscription/`webhook_id` was registered for that exact shop before acting on tenant-scoped data.

### Proof of Concept
1. Attacker creates a development/trial store and installs the target Shopify app, so the app registers webhooks with it. Attacker's store receives a legitimate webhook POST with body `B` and header `X-Shopify-Hmac-Sha256: H`, where `H = HMAC-SHA256(api_secret_key, B)`.
2. Attacker captures this `(B, H)` pair from their own traffic to the app's public webhook endpoint.
3. Attacker crafts a new HTTP POST to the same public webhook endpoint with:
   - Body: same `B`
   - `X-Shopify-Hmac-Sha256: H` (unchanged, still valid)
   - `X-Shopify-Shop-Domain: victim-shop.myshopify.com` (forged)
   - `X-Shopify-Topic`, `X-Shopify-Webhook-Id` optionally forged as well
4. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: forged_headers)` builds successfully (only presence of headers is checked, not their consistency with the signed body).
5. `Registry.process(request)` calls `HmacValidator.validate(request)` which recomputes `HMAC(api_secret_key, B)` and matches `H` → validation passes.
6. The registered handler receives `WebhookMetadata.new(topic: forged_topic, shop: "victim-shop.myshopify.com", body: parsed(B), ...)`, causing the host app to process attacker-controlled data under the victim shop's identity. [5](#0-4) [6](#0-5)

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

**File:** lib/shopify_api/webhooks/request.rb (L15-38)
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
