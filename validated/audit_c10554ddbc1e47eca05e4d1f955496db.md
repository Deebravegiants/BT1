Based on my analysis, this is my final answer.

### Title
Webhook shop-domain identity spoofing via HMAC that only covers the request body - (File: lib/shopify_api/webhooks/request.rb)

### Summary
The gem's webhook verification computes and checks the HMAC over the raw request body only. The `shop-domain` header, which downstream code uses as the merchant/tenant identity for the webhook, is never included in the signed material. Any actor who possesses one valid `(body, hmac)` pair signed with the app's shared `client_secret` — trivially obtainable by installing the app on their own store and receiving a genuine webhook — can replay that exact body/HMAC pair while substituting an arbitrary `shop-domain` header. `Registry.process` accepts it because it only re-validates the HMAC against the body, then forwards the attacker-chosen shop value to the app's handler as trusted tenant identity.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop` is read straight from the `shopify-shop-domain` (or `x-shopify-shop-domain`) header with no cryptographic binding to the signed payload: [2](#0-1) 

`Registry.process` validates the HMAC of the body via `Utils::HmacValidator.validate(request)`, and — on success — immediately builds `WebhookMetadata` using the unauthenticated `request.shop` value, handing it to the app's `WebhookHandler#handle`: [3](#0-2) 

`HmacValidator.validate` / `validate_signature` only ever hash `verifiable_query.to_signable_string` (the body), never the shop header: [4](#0-3) 

`WebhookMetadata.shop` is a plain, unauthenticated string field consumed by every handler implementation: [5](#0-4) 

Because Shopify apps share one `client_secret` across every merchant/shop that installs them, "HMAC is valid" only proves "signed by this app's secret" — it does **not** prove "signed for shop X." The gem treats a valid body HMAC as sufficient authorization to trust `request.shop` as the tenant identity forwarded to the handler, breaking the equality that should hold: `shop authenticated by HMAC == shop attributed to the webhook payload`. This is precisely the "field acted on but not covered by the HMAC" class from the analog report, applied to the identity-binding boundary between HMAC verification and shop/tenant attribution.

### Impact Explanation
A malicious merchant (any unprivileged installer of the same app) can capture a genuine webhook Shopify sends them for their own store, then replay the identical body/HMAC to the app's webhook endpoint with the `shop-domain` header rewritten to a victim shop that also has the app installed. The app's handler receives `WebhookMetadata` claiming the victim shop originated the payload/topic, causing it to process/store attacker-supplied data under the victim's tenant record. Depending on the handler's logic (common patterns: upserting orders/customers/products keyed by `data.shop`, triggering side effects like emails, inventory changes, or GDPR compliance actions), this results in cross-tenant data corruption or injection — data being attributed to and acted upon within another merchant's tenant boundary without their consent, and without needing that merchant's own access token or credentials.

### Likelihood Explanation
Any app has at least one non-privileged merchant install that can generate a legitimate signed webhook at will (e.g., updating a product to trigger `products/update`). No secret, token, or privileged access is required beyond normal app installation. The attack is a straightforward byte-for-byte HTTP replay with one header changed.

### Recommendation
Bind the shop identity into the verified material: either include the shop domain in `to_signable_string`/HMAC computation, or require callers to cross-check `request.shop` against a shop that is independently known/registered for the app (e.g., verified against an existing session/installation record) before trusting the value passed into `WebhookMetadata`. At minimum, document prominently that `WebhookMetadata.shop` is not authenticated by the HMAC and must be independently verified by the host application against its own installed-shop records before being used for tenant attribution.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com` and triggers any webhook (e.g., updates a product), receiving a genuine POST with body `B` and header `X-Shopify-Hmac-Sha256: H` (valid for `B` under the app's shared `client_secret`).
2. Attacker replays the exact same request to the app's webhook endpoint, changing only `X-Shopify-Shop-Domain` to `victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `@raw_body` only — identical to `B` — and passes. [6](#0-5) 
4. The handler receives `WebhookMetadata.new(shop: "victim.myshopify.com", body: <attacker's data>, ...)` and processes it as if it originated from the victim shop.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-31)
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

        private

        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L6-12)
```ruby
    class WebhookMetadata < T::Struct
      const :topic, String
      const :shop, String
      const :body, T::Hash[String, T.untyped]
      const :api_version, String
      const :webhook_id, String
    end
```
