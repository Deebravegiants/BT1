Confirmed root cause: the webhook HMAC signature in this gem is computed exclusively over the raw HTTP body via `Webhooks::Request#to_signable_string` (`@raw_body`), while the `shop` (and `topic`, `api_version`, `webhook_id`) values consumed by `Registry.process` are taken straight from unauthenticated HTTP headers (`shopify-shop-domain` / `x-shopify-shop-domain`) that are never included in the signed bytes.

### Title
Webhook `shop` identity is taken from an HMAC-uncovered header, breaking the "bytes verified == bytes trusted" binding - (File: `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` validates a webhook by calling `Utils::HmacValidator.validate(request)`, which only verifies the HMAC over `request.to_signable_string`, i.e. the raw request body. The `shop` identity used to build `WebhookMetadata` for the handler comes from `Webhooks::Request#shop`, which reads the `shopify-shop-domain`/`x-shopify-shop-domain` HTTP header — a value that is never part of the signed payload.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , and `#shop` is read from a header that is unrelated to that body [2](#0-1) . `Registry.process` validates only the HMAC of the body, then immediately uses `request.shop` to construct the data handed to the app's webhook handler, without any additional binding between the verified bytes and the shop header [3](#0-2) .

This breaks the equality the HMAC is supposed to enforce: `HMAC_valid(raw_body) == true` is treated as if it implied `shop_header == shop_that_sent(raw_body)`, but those are two independent, unrelated fields. Any party that can deliver an HTTP request to the app's webhook endpoint with *any* valid previously-observed `(raw_body, hmac)` pair (e.g., a replayed/legitimate webhook payload from their own shop, or one captured via normal traffic) can freely resend it with an arbitrary `x-shopify-shop-domain` header value, because that header is not covered by the signature at all.

### Impact Explanation
This allows cross-tenant confusion in the app's webhook handler: an attacker-controlled request with a validly-signed body (from the attacker's own shop's genuine webhook, since anyone can install the app and receive real webhooks/HMACs for their own shop) can be replayed with a forged `shop` header pointing at a victim shop. Since `Registry.process` passes this unauthenticated `shop` value straight to `WebhookMetadata`/the app's handler, host applications that key persistence, data updates, or session/token lookups by this `shop` field (which is the gem's own documented API surface, `WebhookMetadata#shop`) will act on the wrong tenant — a cross-tenant impact.

### Likelihood Explanation
Likelihood is high for any app that installs on multiple merchants: every legitimately installed shop can generate its own validly-HMAC'd webhook bodies (e.g. by triggering an event Shopify sends a webhook for), and the attacker fully controls all HTTP headers of their own request replay, including the shop-domain header — no secret material is needed since the header is simply unauthenticated input parsed by the gem.

### Recommendation
Include the `shop` domain (and ideally `topic`/`webhook_id`) inside the HMAC-covered signable string, or otherwise cryptographically bind the header values to the verified payload before trusting them (e.g. require the shop domain to appear inside the verified JSON body, or maintain a webhook-id/shop mapping validated server-side) rather than trusting the raw header value directly in `Webhooks::Request#shop`.

### Proof of Concept
1. Install the app on shop `attacker.myshopify.com`; trigger any webhook event so Shopify sends a genuine, validly-signed webhook body+HMAC to the app.
2. Capture that `(raw_body, x-shopify-hmac-sha256)` pair.
3. Replay the same body/HMAC to the app's webhook endpoint, but set `x-shopify-shop-domain: victim.myshopify.com`.
4. `HmacValidator.validate(request)` succeeds because it only checks `raw_body` against the HMAC [4](#0-3) ; `Registry.process` then dispatches to the handler with `data.shop == "victim.myshopify.com"` [3](#0-2) , causing the app to act on the victim tenant using attacker-supplied body content.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-22)
```ruby
        sig { params(verifiable_query: VerifiableQuery).returns(T::Boolean) }
        def validate(verifiable_query)
          return false unless verifiable_query.hmac

          result = validate_signature(verifiable_query, Context.api_secret_key)
          if result || Context.old_api_secret_key.nil? || T.must(Context.old_api_secret_key).empty?
            result
          else
            validate_signature(verifiable_query, T.must(Context.old_api_secret_key))
          end
        end
```
