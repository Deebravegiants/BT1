### Title
Webhook shop-domain/topic/webhook-id headers are trusted but not covered by the HMAC, enabling cross-tenant webhook spoofing via replay - ([File: lib/shopify_api/webhooks/request.rb], [File: lib/shopify_api/webhooks/registry.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating an HMAC computed over the raw request body. The `shop`, `topic`, `webhook_id`, and `api_version` values that are handed to the app's handler come from HTTP headers that are never included in the signed payload, so they are not bound to the HMAC at all.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop`, `topic`, `webhook_id`, and `api_version` are all read straight from unauthenticated headers: [2](#0-1) 

`Registry.process` validates the HMAC (which only covers the body bytes) and then forwards the header-derived `shop`, `topic`, `webhook_id` and `api_version` to the registered handler as trusted, identifying metadata: [3](#0-2) 

The binding the code should enforce is:
`shop header == shop cryptographically bound to the signed body`

but the actual binding enforced is only:
`HMAC(raw_body, api_secret_key) == received_hmac`

with no cryptographic tie between that HMAC and the `shop-domain`/`topic`/`webhook-id` headers.

Any unprivileged internet user can install the app on their own development/test store, which causes Shopify to legitimately deliver a webhook to the app with a valid `x-shopify-hmac-sha256` for a body they fully control/observe (e.g. `shop/redact`, `app/uninstalled`, or any topic the app registers). They can then replay that exact `(body, hmac)` pair to the app's webhook endpoint while substituting a different `x-shopify-shop-domain` (a victim shop) and/or a different `x-shopify-topic`/`x-shopify-webhook-id`. `HmacValidator.validate` will still pass because it only checks the body against the same `api_secret_key`-derived signature, and `Registry.process` will dispatch the handler with `shop: <victim-shop>` and/or a topic/webhook-id chosen by the attacker.

### Impact Explanation
Because host applications are expected (and, per this gem's own docs/tests, encouraged) to use `WebhookMetadata#shop` to determine which merchant/tenant the payload applies to and `WebhookMetadata#topic` to decide what action to take, an attacker can trick the app into processing data as belonging to a shop it does not own, or into replaying a real payload under a forged topic. This is a cross-tenant identity confusion: the host app believes it received an authentic webhook for shop X, when in fact the payload/HMAC pair only proves the message came from Shopify for the attacker's own shop. Depending on how the app handler is written, this can lead to acting on/overwriting another merchant's data, mandatory-compliance webhooks (`shop/redact`, `customers/redact`) being triggered against the wrong shop, or state corruption across tenants — matching the "cross-tenant access" Critical impact category.

### Likelihood Explanation
Likelihood is high for any unprivileged attacker: installing an app on one's own store (a normal, unprivileged action) and observing its own inbound webhook traffic is trivial. No access token, `api_secret_key`, or privileged account is required — only the ability to replay an HTTP POST with modified headers to the app's public webhook endpoint.

### Recommendation
Bind the identifying metadata to the signed payload instead of trusting headers verbatim:
- Include `shop-domain`, `topic`, and `webhook-id` in the value that is HMAC-signed/verified (this requires coordination with Shopify's webhook delivery format, so at minimum the gem should document this residual trust boundary prominently), or
- Have `Registry.process`/`WebhookMetadata` cross-check the header-derived `shop` against an out-of-band trusted source (e.g. require the caller to supply the expected shop and assert equality) before dispatching the handler, and expose this as a supported, documented validation step rather than leaving host apps to trust `request.shop` implicitly.

### Proof of Concept
1. Install the target app on attacker-owned store `attacker.myshopify.com`; capture a legitimately delivered webhook request, e.g.:
   ```
   POST /webhooks HTTP/1.1
   x-shopify-topic: app/uninstalled
   x-shopify-hmac-sha256: <valid-hmac-for-body>
   x-shopify-shop-domain: attacker.myshopify.com
   x-shopify-webhook-id: <id>
   Body: {"id":123, ...}
   ```
2. Replay the identical body and `x-shopify-hmac-sha256` value, but change the header:
   ```
   x-shopify-shop-domain: victim.myshopify.com
   ```
3. `ShopifyAPI::Utils::HmacValidator.validate` in `lib/shopify_api/utils/hmac_validator.rb` recomputes the HMAC over the (unchanged) raw body and succeeds.
4. `ShopifyAPI::Webhooks::Registry.process` (`lib/shopify_api/webhooks/registry.rb` lines 188-200) dispatches the handler with `shop: "victim.myshopify.com"`, even though Shopify never sent this webhook for `victim.myshopify.com`.

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
