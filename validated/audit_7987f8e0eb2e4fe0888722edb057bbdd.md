This confirms the vulnerability: the webhook `topic`, `shop`, `webhook_id`, and `api_version` are all read from HTTP headers [1](#0-0) , while the HMAC signature only covers the raw request body via `to_signable_string` returning `@raw_body` [2](#0-1) . `Registry.process` validates the HMAC and then trusts `request.shop` (header-derived, unauthenticated) to build the `WebhookMetadata` passed to the handler [3](#0-2) .

### Title
Webhook `shop` (tenant identity) header is not covered by HMAC verification, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb, lib/shopify_api/webhooks/registry.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating an HMAC computed over the raw request body [2](#0-1) [4](#0-3) . However, the `shop` value handed to the app's webhook handler is read from the `shop-domain` HTTP header, which is never included in the signed content [5](#0-4) . Because the HMAC secret (`api_secret_key`) is the same for every merchant that has installed the app, a merchant who is a legitimate, unprivileged install of the app can capture a valid `(body, hmac)` pair from their own genuine webhook deliveries and replay it against the app's webhook endpoint with the `shop-domain` header changed to a victim shop, producing a request that still passes `Utils::HmacValidator.validate` while attributing the payload to an arbitrary, attacker-chosen tenant.

### Finding Description
The identity binding that should hold is: `shop that is cryptographically authenticated == shop the handler acts on`. In `Registry.process`, the only authentication check performed is:

```ruby
raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)
...
handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop, ...))
``` [6](#0-5) 

`Utils::HmacValidator.validate` calls `verifiable_query.to_signable_string`, which for `Webhooks::Request` returns only `@raw_body` [2](#0-1) . None of `topic`, `shop`, `webhook_id`, or `api_version` — all sourced from attacker-influenceable HTTP headers [1](#0-0)  — are part of the signed material. Consequently, HMAC validity proves only "this body was signed with the app's secret at some point"; it proves nothing about which shop, topic, or webhook ID the request is actually claiming.

Since the same `api_secret_key` is shared by the app across all its installed shops, any shop that has installed the app (an ordinary, unprivileged tenant) can obtain a genuine `(raw_body, hmac)` pair from a webhook Shopify delivered to it, then resend that exact body+HMAC to the app's public webhook endpoint while substituting the `shop-domain` header for a different, victim shop. The signature still validates because the header is not part of the signed string, and `Registry.process` passes the attacker-controlled `shop` value straight into `WebhookMetadata` for the handler to act on [7](#0-6) .

### Impact Explanation
This breaks the tenant boundary: `shop` is the identity binding that host applications use to key sessions, look up merchant records, and gate merchant-specific data/actions. An unprivileged shop can cause the app to process a webhook body as if it originated from a different merchant, resulting in cross-tenant data confusion (e.g., an `orders/create` or `app/uninstalled` payload being attributed to a shop that never sent it). This matches the Critical "cross-tenant access" impact category.

### Likelihood Explanation
Any merchant that installs the app is, by definition, capable of receiving genuine webhooks from Shopify for their own shop — this is not a privileged position. Capturing a valid `(raw_body, hmac)` pair requires no special access (it's simply what the app's own endpoint already receives for that shop), and replaying it with a modified header requires only the ability to send an HTTP request, which is exactly the capability this gem's webhook endpoint is designed to accept from the internet. No secrets, tokens, or elevated privileges are needed beyond having installed the app once.

### Recommendation
Bind `shop` (and ideally `topic`/`webhook_id`) into the signed material, or otherwise cryptographically tie the header values to the HMAC-covered body before trusting them. Since the wire format is controlled by Shopify's webhook delivery contract, the gem should treat header-sourced identity fields as unauthenticated unless it can independently corroborate them — e.g., by cross-checking `request.shop` against an expected/known shop for the delivery context, or by refusing to rely on `shop` unless it is deterministically derivable from the signed body payload itself (many webhook bodies do carry a shop identifier inside the JSON, which could be cross-verified against the header value before use).

### Proof of Concept
1. App has two merchants installed: Shop A (attacker-controlled) and Shop B (victim).
2. Shopify delivers a genuine webhook to the app for Shop A: `raw_body = B_A`, headers include `x-shopify-shop-domain: shop-a.myshopify.com`, `x-shopify-hmac-sha256: H(B_A)` computed with the app's shared `api_secret_key`.
3. Attacker (operator of Shop A) records this valid `(B_A, H(B_A))` pair.
4. Attacker sends a new HTTP request directly to the app's webhook endpoint with the same body `B_A` and same HMAC header `H(B_A)`, but sets `x-shopify-shop-domain: shop-b.myshopify.com`.
5. `Webhooks::Request.new` parses headers, `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes `HMAC(body)` and compares — it matches since the body and HMAC are untouched [4](#0-3) .
6. `handler.handle` is invoked with `shop: "shop-b.myshopify.com"` even though Shop B never sent this webhook and this data never originated from Shop B [7](#0-6) .

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
