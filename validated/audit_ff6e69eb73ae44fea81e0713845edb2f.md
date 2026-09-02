## Title
Webhook HMAC only binds the request body, not the `shop-domain` header — enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes/validates the HMAC signature over the raw request body only, while the `shop` identity that the library hands to application webhook handlers is read from the unsigned `X-Shopify-Shop-Domain` header. Any actor that legitimately controls a single shop instance of the app (an "unprivileged" tenant relative to other merchants) can capture one valid `(body, hmac)` pair from their own webhook deliveries — since all shops share the same app `client_secret` — and replay it against the app's webhook endpoint with the `shop-domain` header changed to a victim shop. `HmacValidator.validate` will accept it because the signature never covered the shop field, and the handler will process the forged payload as if it originated from the victim tenant.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop` is parsed straight from a header that is never part of the signed material: [2](#0-1) 

`Registry.process` validates the HMAC and then immediately trusts `request.shop` to construct the `WebhookMetadata` passed to the application handler, without any additional binding between the verified bytes and the shop identity: [3](#0-2) 

`HmacValidator.validate` / `validate_signature` only ever compares `verifiable_query.hmac` against a signature computed from `to_signable_string`, i.e. the body — never the shop header: [4](#0-3) 

The identity binding that should hold is:
`shop authenticated by the HMAC == shop attributed to the processed webhook data`

but in this implementation:
`shop covered by the HMAC (none — only body is signed) != shop used to build WebhookMetadata (attacker-controlled header)`

Because the app's `client_secret` (and therefore the HMAC secret) is shared across every shop that installs the app, any tenant that has installed the app can obtain a genuinely valid `(body, hmac)` pair for their own store's webhook deliveries, then resend that exact body/HMAC pair to the app's webhook endpoint with the `X-Shopify-Shop-Domain` (or `Shopify-Shop-Domain`) header swapped to a victim shop's domain. `Registry.process` will pass HMAC validation (since the body/HMAC pair is untouched) and will dispatch the handler with `shop: <victim shop>`, causing the application to record/act on fabricated data as if it came from a different tenant.

### Impact Explanation
This breaks the tenant boundary that the webhook processing pipeline is supposed to enforce: a merchant/tenant with no access to another tenant's install can inject fabricated webhook events attributed to that other tenant, letting them corrupt or manipulate the victim shop's application state via any webhook-driven business logic (order/inventory sync, billing state, GDPR/compliance topics, etc.). This is a cross-tenant access issue stemming directly from a code construct in this gem (`Webhooks::Request`/`Webhooks::Registry`), matching the report's identity-binding bug class ("a field acted on but not covered by the HMAC").

### Likelihood Explanation
Exploitation requires only: (1) the attacker be a legitimate installer of the target app on their own store (no special privilege, no access to `api_secret_key`), and (2) the ability to observe one of their own webhook deliveries' raw body + HMAC (feasible via a proxy/logging endpoint they control, since it's their own traffic) and resend it to the app's public webhook endpoint with a modified shop header. No secrets need to be stolen from the victim or from Shopify.

### Recommendation
Bind the `shop` identity into the value that is actually authenticated, e.g., require the webhook consumer to cross-check `request.shop` against the shop tied to the delivery via a channel that is authenticated (for instance, verifying the target endpoint/shop mapping registered at subscription time, or including the shop in the signed payload/verification if the platform ever exposes such a mechanism) rather than trusting the raw `shop-domain` header once body-HMAC validation succeeds. At minimum, document and enforce that `WebhookMetadata.shop` must be revalidated by the host application against the shop that the specific webhook subscription (`webhook_id`) belongs to, since neither the shop nor webhook id are covered by the signature.

### Proof of Concept
1. App is installed on Attacker's shop `attacker.myshopify.com` and Victim's shop `victim.myshopify.com` (same app, same `client_secret`).
2. Attacker's own store triggers a webhook delivery; Attacker captures the raw HTTP request at their reverse proxy: body `B` and header `X-Shopify-Hmac-Sha256: H` (valid, computed with the shared `client_secret` over `B`), and `X-Shopify-Shop-Domain: attacker.myshopify.com`.
3. Attacker resends the exact same request to the app's public webhook endpoint, changing only `X-Shopify-Shop-Domain` to `victim.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only recomputes the HMAC over `@raw_body` (unchanged): [1](#0-0) 
5. `Registry.process` builds `WebhookMetadata.new(... shop: request.shop ...)` using the attacker-controlled header value `victim.myshopify.com` and invokes the registered handler: [5](#0-4) 
6. The host application processes body `B` (attacker-controlled content within the topic's schema) as an authentic event for `victim.myshopify.com`.

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
