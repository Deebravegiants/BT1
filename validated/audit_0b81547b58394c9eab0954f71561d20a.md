### Title
Webhook `shop-domain` header (and `topic`/`webhook-id`) is not covered by the HMAC signature, allowing tenant-identity spoofing on an otherwise HMAC-valid webhook request - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` derives the HMAC-signable content solely from the raw request body, while the `shop` (and `topic`, `webhook_id`, `api_version`) used to identify the tenant are taken directly from HTTP headers that are never part of the signed material. `Registry.process` validates only the body HMAC and then forwards the header-derived `shop` to the app's handler as the trusted tenant identifier.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop` (and `topic`, `webhook_id`, `api_version`) come from headers that are parsed but never mixed into the signed string: [2](#0-1) 

`Registry.process` validates the HMAC over the body only, then immediately trusts `request.shop` as the tenant identity passed to the handler: [3](#0-2) 

`HmacValidator.validate` confirms the check is purely `hmac(secret, raw_body) == received_hmac`, with no header binding whatsoever: [4](#0-3) 

The identity binding that should hold is: `shop header == shop cryptographically bound to the signed bytes`. Here, the equality that actually holds is only `hmac == HMAC(secret, raw_body)`; the `shop` header is unconstrained by that proof. Anyone who can obtain one genuine `(raw_body, hmac)` pair signed with the app's secret — for example, a merchant who has legitimately installed the app on their **own** store and therefore receives real Shopify webhooks with valid HMACs computed by the same `api_secret_key` — can replay that exact body/HMAC pair to the app's public webhook endpoint while substituting the `shopify-shop-domain` (and optionally `shopify-topic`/`shopify-webhook-id`) header to name a **different, victim** shop. `Registry.process` will accept the HMAC (it's valid for the body) and hand the handler a `WebhookMetadata` claiming to belong to the victim shop, even though the payload content actually originated from the attacker's own store.

This is exactly the "field acted on but not covered by the HMAC" class of bug from the reference report (there, `transferUnstakedOut`/`recoverUnstaking` skipped the frozen-validator identity check that every other path enforced; here, the webhook processing path skips binding the header-derived shop identity to the HMAC-verified bytes that every other consumer of `VerifiableQuery` — e.g. `AuthQuery`, which does include `shop` in `to_signable_string` — correctly enforces).

### Impact Explanation
This breaks tenant isolation for any app built on this gem's webhook registry: an attacker who is merely an unprivileged shop owner (using the app legitimately on their own store) can forge webhook deliveries that the app will process under a different (victim) shop's identity. Depending on how the app's `WebhookHandler` uses `WebhookMetadata#shop`, this can lead to cross-tenant data corruption or cross-tenant state changes attributed to a shop the attacker does not control — matching the "cross-tenant access" Critical impact category, since the app cannot distinguish this forged request from a legitimate webhook for the victim shop.

### Likelihood Explanation
Requires the attacker to possess one valid `(raw_body, hmac)` pair produced with the app's `api_secret_key`. This is trivially obtainable by any merchant who installs the app on their own store (a normal, unprivileged action) and captures one real webhook delivery. No access to the app's `api_secret_key`, access tokens, or any privileged account is required — only the ability to send an arbitrary HTTP POST to the app's own public webhook endpoint with attacker-chosen headers, which is standard unauthenticated internet access.

### Recommendation
Bind the tenant-identifying headers to the HMAC verification rather than trusting them independently. At minimum, include `shop`, `topic`, and `webhook_id` in the signable string (mirroring what `AuthQuery#to_signable_string` already does for OAuth), or otherwise cryptographically bind header values to the payload before `Registry.process` treats `request.shop` as an authoritative tenant identifier.

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker.myshopify.com` and lets Shopify send a legitimate webhook (e.g. `orders/create`), capturing the raw POST body `B` and its valid header `x-shopify-hmac-sha256: H` (computed as `HMAC-SHA256(api_secret_key, B)`).
2. Attacker crafts a new POST to the app's public webhook endpoint using the exact same body `B` and header `x-shopify-hmac-sha256: H`, but sets:
   - `x-shopify-shop-domain: victim.myshopify.com`
   - (optionally spoofs `x-shopify-topic`/`x-shopify-webhook-id` similarly)
3. `Registry.process` calls `Utils::HmacValidator.validate(request)` [5](#0-4)  — this passes because it only checks `HMAC(secret, B) == H`.
4. The handler receives `WebhookMetadata.new(topic: ..., shop: "victim.myshopify.com", body: parsed(B), ...)` [6](#0-5)  and processes attacker-controlled body content under the victim shop's identity.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
