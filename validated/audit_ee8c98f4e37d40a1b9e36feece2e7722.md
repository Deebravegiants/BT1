### Title
Webhook `shop` identity is not covered by the HMAC signature, allowing the shop-domain field to be spoofed on an otherwise validly-signed webhook payload - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by verifying the HMAC over the raw request body, then dispatches to the app's handler using a `shop` value taken from an HTTP header that is never included in that signature. The equality the gem should guarantee — "the shop the HMAC authenticates" == "the shop the handler is told the event belongs to" — does not hold.

### Finding Description
`ShopifyAPI::Webhooks::Request` implements `Utils::VerifiableQuery`: [1](#0-0) 

`to_signable_string` returns only `@raw_body`, and `hmac` is read from the `hmac-sha256` header. `shop` (line 21-23) is read from a completely separate, unsigned header (`shopify-shop-domain` / `x-shopify-shop-domain`).

`Utils::HmacValidator.validate` computes the signature purely over `verifiable_query.to_signable_string` (i.e., the body) and compares it to the received `hmac`: [2](#0-1) 

`Registry.process` uses exactly this validation, and if it passes, immediately builds the event metadata using the unauthenticated `request.shop`: [3](#0-2) 

So the binding the library actually enforces is:
`HMAC(body, api_secret_key) == received_hmac`

but the binding the handler is implicitly given (and that host applications built on this gem's documented API rely on, e.g. to look up the shop's session/config) is:

`shop_header == "the shop this event is about"`

These two are never tied together. Anyone who can obtain one legitimately-signed `(raw_body, hmac)` pair for their own shop (e.g., because they installed the app and simply captured a webhook delivered to their own endpoint, or replayed it against a different endpoint) can resubmit the exact same body/HMAC pair while substituting a different value in the `shop-domain` header. `HmacValidator.validate` will still return `true`, because the header is not part of the signed material, and `Registry.process` will hand the handler a `WebhookMetadata` claiming the event is for the attacker-chosen shop.

### Impact Explanation
This breaks the tenant boundary the gem is expected to enforce for webhook authenticity. A typical downstream consumer (as documented for this gem and mirrored by `shopify_app`) uses `WebhookMetadata#shop` to select which shop's session/settings to act on when processing the event body. Because the shop identity is forgeable independent of a valid signature, an attacker who possesses any one valid `(body, hmac)` pair can cause the host application to process attacker-supplied webhook content under a victim shop's identity — a cross-tenant data-integrity violation. This meets the Critical bar of "cross-tenant access" defined in scope.

### Likelihood Explanation
Exploitation requires only a single genuine webhook delivery to any shop the attacker controls (trivially obtainable by installing the app on their own store, which is the normal, unprivileged usage flow for any Shopify app) and the ability to POST directly to the app's webhook endpoint with a modified header, which is standard HTTP client capability. No possession of `api_secret_key`, access tokens, or any privileged credential is required — likelihood is high for any app that trusts `WebhookMetadata#shop` (the exact field this gem exposes for that purpose).

### Recommendation
Bind the shop identity into the verified material instead of treating it as ambient header data:
- Extend `VerifiableQuery#to_signable_string` for webhooks to incorporate the shop-domain (and ideally topic/webhook-id) alongside the body, or
- Have `HmacValidator`/`Registry.process` cross-check `request.shop` against an expected/registered set of shop domains for the API version/topic before dispatch, or at minimum document prominently (and enforce in the library) that `WebhookMetadata#shop` must never be trusted for authorization decisions without an independent, out-of-band verification (e.g., confirming the shop has an active offline session) before it is used to select which tenant's data to mutate.

### Proof of Concept
1. App receives a legitimate webhook for `attacker-shop.myshopify.com`:
   ```
   POST /webhooks
   X-Shopify-Topic: orders/create
   X-Shopify-Hmac-Sha256: <valid-hmac-of-body>
   X-Shopify-Shop-Domain: attacker-shop.myshopify.com
   Body: {"id": 1, "note": "malicious payload"}
   ```
   Attacker captures `Body` and `X-Shopify-Hmac-Sha256` exactly as delivered.

2. Attacker resends the identical body and HMAC, only changing the shop header:
   ```
   POST /webhooks
   X-Shopify-Topic: orders/create
   X-Shopify-Hmac-Sha256: <same-hmac-as-above>
   X-Shopify-Shop-Domain: victim-shop.myshopify.com
   Body: {"id": 1, "note": "malicious payload"}
   ```
3. `ShopifyAPI::Utils::HmacValidator.validate(request)` returns `true` (line `lib/shopify_api/utils/hmac_validator.rb:26-31`) because it only checks the body against the HMAC.
4. `ShopifyAPI::Webhooks::Registry.process` (line `lib/shopify_api/webhooks/registry.rb:190-199`) dispatches to the handler with `shop: "victim-shop.myshopify.com"`, causing the app to process attacker-controlled content as if it originated from `victim-shop`.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-38)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end

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
