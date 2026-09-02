This confirms the vulnerability pattern: `ShopifyAPI::Webhooks::Request#to_signable_string` (line 36-38) returns only `@raw_body`, while `shop` (line 20-23), `topic`, `webhook_id`, and `api_version` are all pulled unauthenticated from HTTP headers and are never part of the HMAC-signed string. `Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-199`) validates the HMAC against the body alone, then trusts `request.shop` to build `WebhookMetadata` handed to the app's handler. [1](#0-0) [2](#0-1) 

### Title
Webhook `shop` identity is not bound to the HMAC signature, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` only returns the raw JSON body; the `shop` (and `topic`/`webhook_id`/`api_version`) fields come from unauthenticated HTTP headers and are excluded from what is HMAC-verified. `Registry.process` validates the HMAC over the body alone and then trusts `request.shop` to construct the `WebhookMetadata` object dispatched to the app's handler, so the equality "shop authenticated by HMAC" == "shop delivered to the handler" does not hold.

### Finding Description
`HmacValidator.validate` computes `compute_signature(verifiable_query.to_signable_string, secret)` and compares it to the `hmac` field. [3](#0-2) 
For `Webhooks::Request`, `to_signable_string` is just `@raw_body` — no header, including `shop-domain`, is included in the signable content. [4](#0-3) 
`shop`, `topic`, `webhook_id`, and `api_version` are all read straight from HTTP headers, with no cryptographic binding to the HMAC that only covers the body. [5](#0-4) 
`Registry.process` treats a valid HMAC-over-body as sufficient proof of authenticity, then immediately trusts `request.shop`/`request.topic`/etc. to build the `WebhookMetadata` passed to the app-defined handler, which frequently uses `shop` as a tenant key to look up records or store data (per `docs/usage/webhooks.md`'s example of `perform_later(shop_domain: data.shop, ...)`). [2](#0-1) 

This mirrors the report's bug class: an "update schema" (here, the shop-binding schema) treats a field (`shop`) as trusted based on an unrelated verification (HMAC over body only) instead of covering it in the signed material — a field acted on but not covered by the HMAC.

### Impact Explanation
Because the request-body/HMAC pair is not bound to a specific shop, any body+HMAC pair observed for one shop's webhook (e.g. an attacker who legitimately controls or observes their own store's webhook traffic, or a body that happens to match another shop's payload, such as `{}` bodies or predictable/duplicated bodies) can be replayed to the app's webhook endpoint with an arbitrary `X-Shopify-Shop-Domain`/`Shopify-Shop-Domain` header. The receiving handler will process it as if it legitimately originated from the spoofed shop, since the gem exposes `request.shop` from the header without any signature coverage. This crosses the tenant boundary (cross-tenant access) in applications that key persistence, authorization, or business logic off `WebhookMetadata#shop` — matching the Critical "cross-tenant access" category.

### Likelihood Explanation
Exploitation does not require the app's `api_secret_key`: an attacker needs to obtain any single valid `(raw_body, hmac)` pair (trivial for identical/common payloads such as `{}` or predictable mandatory-compliance topics, or for a body an attacker fully controls in their own store's webhook), then POST it directly to the app's public webhook endpoint with a spoofed shop header. No TLS interception or credential theft is needed, satisfying the "unprivileged internet user" threat model.

### Recommendation
- Short term: include `shop`, `topic`, `webhook_id`, and `api_version` in the material verified against the HMAC, or at minimum require the receiving application to independently authenticate `shop` against a known/allow-listed value (e.g., matching an existing session) before trusting it — document this prominently since `to_signable_string` currently silently omits headers.
- Long term: since Shopify's real HMAC computation covers only the body by design, update the gem's documentation/API to make clear that `WebhookMetadata#shop` is unauthenticated and must be cross-checked by the app (e.g., against a stored session for that shop) before being used as a tenant key.

### Proof of Concept
1. Attacker's own store `attacker-shop.myshopify.com` triggers a webhook with body `{}` (or any body an attacker can arrange to have delivered), and attacker observes the resulting `X-Shopify-Hmac-Sha256` header value, which the app's secret produces deterministically for a known body.
2. Attacker crafts a raw HTTP request to the victim app's public webhook endpoint with:
   - `raw_body`: the exact same `{}` (or reused) body
   - `X-Shopify-Hmac-Sha256`: the previously observed valid HMAC for that body
   - `X-Shopify-Shop-Domain`: `victim-shop.myshopify.com` (any target tenant)
   - `X-Shopify-Topic`: any registered topic
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks the body against the HMAC (`lib/shopify_api/webhooks/request.rb:35-38`, `lib/shopify_api/utils/hmac_validator.rb:26-31`).
4. The handler receives `WebhookMetadata` with `shop: "victim-shop.myshopify.com"` even though the payload's true "hmac-shop" binding was never established, allowing the attacker to inject data/events attributed to a shop they do not control.

### Citations

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
