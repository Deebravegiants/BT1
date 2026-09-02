### Title
Webhook `shop` (tenant) identity is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature only over the raw request body, while the `shop` (tenant identity) used by `Registry.process` to dispatch the webhook to the handler is taken from an unauthenticated HTTP header. An attacker who possesses one validly-signed webhook body (e.g., from their own shop) can replay it with a forged `shop-domain`/`x-shopify-shop-domain` header pointing at a victim shop, and the HMAC check will still pass, because that header is never part of the signed content.

### Finding Description
The vulnerability class mirrors M-9: a value that is *used* by downstream logic (`leverageAmount` there, `shop` here) is not derived from the same verified state that produced the check that is supposed to guarantee its correctness (the withdrawn amount there, the HMAC-protected payload here). Concretely:

- `to_signable_string` — the value that is HMAC-verified — returns only the raw body: [1](#0-0) 

- `shop` is read straight from an attacker-controlled header, entirely outside the signed content: [2](#0-1) 

- `HmacValidator.validate` only recomputes the HMAC over `verifiable_query.to_signable_string` (the body) and compares it to the `hmac` header — it never binds `shop`, `topic`, or `webhook_id` into the signature: [3](#0-2) 

- `Registry.process` validates the HMAC and then unconditionally trusts `request.shop` (and `request.topic`, `request.webhook_id`) to build the `WebhookMetadata` that is handed to the app's handler: [4](#0-3) 

The broken identity binding, stated as an equality that should hold but doesn't:
`shop that authorized/produced the HMAC-valid body == shop attributed to the processed webhook (request.shop)`

Because a single `api_secret_key` (the app's client secret) is shared across every shop that installs the app, any body that was genuinely HMAC-signed by Shopify for **shop A** remains a valid signature no matter which `shop-domain` header is attached to it. An attacker who controls (or has installed the app on) shop A can capture one such payload/HMAC pair and replay it against the app's webhook endpoint with the `shop-domain` header rewritten to **shop B** (a victim tenant). `HmacValidator.validate` returns `true` (body+HMAC pair matches), and `Registry.process` forwards `shop: "shop-B.myshopify.com"` to the app's handler as if the event genuinely originated from shop B.

### Impact Explanation
This breaks the tenant boundary the gem is supposed to enforce for webhook delivery: an app's webhook handler (which typically loads the shop's session/access token and applies the payload to that shop's local records, per `WebhookMetadata#shop`) can be made to act on attacker-chosen body content while attributing it to an arbitrary victim shop. This is a cross-tenant integrity issue — the library provides no mechanism to bind the reported `shop` to the cryptographically verified data, so it silently permits spoofed tenant attribution for any handler that relies on `WebhookMetadata#shop`/`#topic`/`#webhook_id` as trusted identifiers, which is exactly what the gem's documented API tells consumers to rely on.

### Likelihood Explanation
Exploitation requires only: (1) the attacker's own real, genuinely-delivered webhook body+HMAC from any shop that has installed the target app (attacker can trivially obtain this by installing the app to their own test store), and (2) the ability to send an HTTP request to the app's public webhook endpoint with a rewritten `shop-domain` header — both within reach of an unprivileged internet user, no access token, api_secret_key, or privileged account required.

### Recommendation
Bind the tenant/topic identity into the verified signature space, or independently corroborate it, before trusting `request.shop`/`topic`/`webhook_id`. For example, incorporate the `shop`, `topic`, and `webhook_id` headers into `to_signable_string` (if compatible with Shopify's signature scheme) or, at minimum, require callers to supply an out-of-band expected shop domain to `Registry.process` and reject processing when it doesn't match `request.shop`, rather than propagating an unauthenticated header value directly into `WebhookMetadata`.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com`, triggers a webhook (e.g. `orders/create`), and captures the raw body `B` and the corresponding `x-shopify-hmac-sha256` value `H` sent by Shopify (valid because `HMAC(api_secret_key, B) == H`).
2. Attacker POSTs to the app's webhook endpoint with:
   - body = `B`
   - `x-shopify-hmac-sha256` = `H`
   - `x-shopify-shop-domain` = `victim-shop.myshopify.com`
   - `x-shopify-topic`, `x-shopify-webhook-id` set as desired.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only checks `HMAC(api_secret_key, B) == H` — true — so validation passes: [5](#0-4) 
4. The handler is invoked with `WebhookMetadata.new(..., shop: "victim-shop.myshopify.com", body: <attacker-controlled parsed body>, ...)`, causing the app to process attacker-supplied data as if it belonged to the victim shop.

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
