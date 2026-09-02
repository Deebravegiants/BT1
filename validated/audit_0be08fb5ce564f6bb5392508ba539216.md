### Title
Webhook `shop-domain` header is trusted without HMAC coverage, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable string from the raw request body only, while the `shop` (and `topic`/`webhook_id`) values are read directly from unauthenticated HTTP headers. `ShopifyAPI::Webhooks::Registry.process` validates the HMAC and then immediately trusts `request.shop` as the tenant identity passed to the app's handler, without that value ever being covered by the signature.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 
`Request#shop` is read straight from the `shopify-shop-domain`/`x-shopify-shop-domain` header with no relation to the signed bytes: [2](#0-1) 

`Utils::HmacValidator.validate` computes the HMAC purely over `to_signable_string` (i.e., the raw body) and compares it to the `hmac` header: [3](#0-2) 

`Registry.process` checks only this body HMAC, then passes `request.shop` straight to the app's handler as the authoritative tenant identifier: [4](#0-3) 

Because `shop` is never part of the signable string, the binding `HMAC-authenticated bytes == bytes acted on by the handler` is broken: the signature proves only "this body came from Shopify for *some* shop that has the app installed," not "this body belongs to the shop named in this header." Any unprivileged internet user who legitimately installs the app on their own store (no special privilege needed — any merchant can install any public app) will receive real webhook deliveries with a valid HMAC computed over their own event's body. That attacker can capture one such `(raw_body, hmac)` pair and replay it to the app's public webhook endpoint while substituting the `X-Shopify-Shop-Domain` header with a victim shop's domain. `HmacValidator.validate` still succeeds because it never inspects the header, so `Registry.process` dispatches the handler with `shop: "victim-shop.myshopify.com"` and the attacker-controlled body — a cross-tenant identity/data confusion the app cannot distinguish from a legitimate webhook for the victim.

### Impact Explanation
This breaks the tenant boundary the gem is supposed to provide via HMAC verification: apps that key persistence/business logic off `WebhookMetadata#shop` (the value produced from `request.shop`) can be made to apply attacker-supplied webhook bodies to another merchant's tenant record purely by header manipulation, with no credentials, tokens, or secrets required. This matches the "Critical – cross-tenant access" impact class, since the gem's own webhook-verification primitive is what silently permits the spoofed tenant assignment.

### Likelihood Explanation
High. Any internet user can install a public app for free on their own store to obtain a validly-signed `(body, hmac)` pair, then simply resend it with a different `shop-domain` header value to the app's already-public webhook receiver URL. No secret, access token, or elevated privilege is needed — only the ability to install the target app once as an ordinary merchant and to send an HTTP POST.

### Recommendation
Bind the shop identity into the signed payload verification path: e.g., require `Registry.process` (or `HmacValidator.validate`) to also verify that the `shop-domain` header corresponds to a shop associated with the delivered `webhook_id`/subscription (via a server-side registration lookup) or otherwise reject processing unless the `shop` value can be cross-checked against Shopify-controlled state rather than trusted from an unauthenticated header alone. At minimum, clearly document that host applications must not trust `WebhookMetadata#shop` as tenant-authoritative unless independently corroborated.

### Proof of Concept
1. Attacker installs the target public app on `attacker-shop.myshopify.com` (any unprivileged internet user can do this).
2. Shopify sends a legitimate webhook to the app's endpoint: body `B`, headers include `X-Shopify-Hmac-Sha256: H` (valid for secret `client_secret`) and `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`.
3. Attacker replays the exact same request to the app's webhook endpoint, changing only `X-Shopify-Shop-Domain` to `victim-shop.myshopify.com`.
4. `ShopifyAPI::Utils::HmacValidator.validate` recomputes HMAC over the raw body `B` only — matches `H` — validation passes (`lib/shopify_api/utils/hmac_validator.rb:26-31`).
5. `Registry.process` dispatches `handler.handle(data: WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: parsed(B), ...))` (`lib/shopify_api/webhooks/registry.rb:198-199`), causing the host app to treat attacker-controlled webhook content as belonging to the victim shop.

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
