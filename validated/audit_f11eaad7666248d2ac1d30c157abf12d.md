Confirmed root cause with exact code.

### Title
Webhook `shop-domain` header is trusted for tenant routing without being covered by the HMAC signature - (File: `lib/shopify_api/webhooks/registry.rb`, `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/utils/hmac_validator.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authorizes a webhook solely by validating an HMAC that only covers the raw request body, then dispatches the handler using the shop identity taken from an unauthenticated header field. This breaks the binding `HMAC-verified-bytes == data-acted-upon`, allowing the shop identity attached to a webhook payload to be forged while the HMAC still validates.

### Finding Description
`Registry.process` accepts a `Request` object and only checks the HMAC before invoking the handler with `request.shop`: [1](#0-0) 

The HMAC check delegates to `Utils::HmacValidator.validate`, which computes the signature over `verifiable_query.to_signable_string`: [2](#0-1) 

For a webhook `Request`, `to_signable_string` returns only the raw HTTP body (`@raw_body`), never the headers: [3](#0-2) 

Meanwhile `shop` (and `topic`, `webhook_id`, `api_version`) are read directly from HTTP headers that are not part of the signed material: [4](#0-3) 

`Registry.process` then hands `request.shop` straight to the host application's handler as the tenant identity for the event, with no cross-check that this shop matches the body or the HMAC: [1](#0-0) 

Because the HMAC secret (`Context.api_secret_key`) is a single app-level secret shared across every shop that installs the app (not a per-shop secret), any two webhook deliveries with an identical body produce an identical valid HMAC regardless of which shop they originated from. An attacker who operates (or has ever installed the app on) shop A can capture a legitimate `(raw_body, hmac)` pair that Shopify sent for a webhook topic whose body is shop-independent or attacker-influenced (e.g. `app/uninstalled`, `shop/redact`, or any topic whose JSON body the attacker can reproduce/predict), then replay that exact body and HMAC to the app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` header with a victim shop's domain. `HmacValidator.validate` still passes because it only checks the body, and `Registry.process` will invoke the handler with `WebhookMetadata.shop` set to the attacker-chosen victim shop: [5](#0-4) 

This is the equality that should hold but doesn't: `hmac_signed_bytes == bytes_that_determine_the_tenant`. The signed bytes are `@raw_body` only; the tenant-determining byte is the unauthenticated `shop-domain` header.

### Impact Explanation
If the host application trusts `WebhookMetadata.shop` (as the gem's own `WebhookMetadata` and handler contract expects) to look up or update per-shop state — e.g., marking a shop as uninstalled/redacted, invalidating a session, or writing customer-redaction data keyed by shop — an attacker can cause that action to be attributed to and executed against a shop they do not own, purely by forging the header. This is a cross-tenant integrity violation: one merchant's webhook traffic can be used to inject events tied to a different merchant's shop identity.

### Likelihood Explanation
The attack requires an attacker who controls at least one shop with the app installed (so they can observe genuine `(body, hmac)` pairs delivered to their own endpoint) and the ability to POST directly to the app's public webhook endpoint (which is inherently internet-reachable, as it must accept unauthenticated deliveries from Shopify). No access to `api_secret_key` or any privileged credential is needed — the exploit works precisely because the shared secret's coverage (body only) does not extend to the identity field the application relies on. This satisfies the "field acted on but not covered by the HMAC" analog directly.

### Recommendation
Bind the shop identity into the signed material, or otherwise independently verify it. Concretely: extend `VerifiableQuery`/`Request#to_signable_string` (or add a secondary check in `Registry.process`) so the HMAC computation, or an additional verification step, incorporates the `shop-domain` header value, and reject the webhook if that header cannot be corroborated (e.g., via a registered/expected shop list, or a per-shop verification callback exposed to the host app) before invoking `handler.handle`.

### Proof of Concept
1. App owner installs the app on `attacker-shop.myshopify.com`; attacker observes a real webhook delivery to their endpoint with body `B` and header `X-Shopify-Hmac-Sha256: H` (computed by Shopify using the app's shared `client_secret`, per `lib/shopify_api/utils/hmac_validator.rb`).
2. Attacker crafts a new HTTP POST to the app's webhook endpoint containing the identical body `B` and identical `X-Shopify-Hmac-Sha256: H`, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate`, which recomputes HMAC over `to_signable_string` (i.e., `B` only) and finds it matches `H` — validation passes (`lib/shopify_api/utils/hmac_validator.rb:13-22`, `lib/shopify_api/webhooks/request.rb:36-38`).
4. `Registry.process` invokes `handler.handle(data: WebhookMetadata.new(topic:, shop: request.shop, ...))` with `shop == "victim-shop.myshopify.com"`, even though the payload was never sent by Shopify on behalf of that shop (`lib/shopify_api/webhooks/registry.rb:198-199`).

### Citations

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
