### Title
Webhook Shop Domain Not Covered by HMAC Allows Cross-Tenant Webhook Spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
The webhook `Request` object's HMAC verification only authenticates the raw request body, while the `shop` (tenant) attribution is read from an HTTP header that is never included in the signed payload. Any bytes an attacker can pair with a validly-signed body (e.g. from their own installed shop) can be re-submitted with an arbitrary `shopify-shop-domain` / `x-shopify-shop-domain` header, and `ShopifyAPI::Webhooks::Registry.process` will accept it as authentic and route it to the handler under the attacker-chosen shop identity.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop` is derived purely from a header that participates in no cryptographic check: [2](#0-1) [3](#0-2) 

`Utils::HmacValidator.validate` computes and compares the HMAC solely against `verifiable_query.to_signable_string` (i.e., the body), never touching header fields: [4](#0-3) 

`Webhooks::Registry.process` gates on this body-only HMAC check and then trusts `request.shop` (and `request.topic`) to build the `WebhookMetadata` handed to the host application's handler, with no cross-check that the shop is bound to the signed bytes: [5](#0-4) 

The broken identity binding, stated as an equality that should hold but does not:
`HMAC_verified(raw_body) == identity_claim(shop_header)` — the gem enforces `HMAC_verified(raw_body) == true` but never asserts any relationship between the verified bytes and the `shop` value used for tenant routing. Because `hmac-sha256` is computed only over `@raw_body`, an attacker who possesses any single valid `(raw_body, hmac)` pair — trivially obtainable by installing the app on their own free development store and capturing a legitimate webhook delivery — can resubmit that exact body/HMAC pair to the app's webhook endpoint while substituting the `shopify-shop-domain` header with a victim merchant's domain. `HmacValidator.validate` will still return `true` because it only recomputes/compares the HMAC of `raw_body`, and `Registry.process` will proceed to invoke the handler with `shop: <victim-domain>`.

### Impact Explanation
This is a cross-tenant identity confusion: the host application's webhook handler receives attacker-controlled body content falsely attributed to a victim shop it never came from. Any application logic that uses `WebhookMetadata#shop` to select which merchant's data store to write to, update, or delete will act on the wrong tenant using data that was never actually sent by (or about) that tenant, satisfying the Critical "cross-tenant access" impact criterion.

### Likelihood Explanation
The prerequisite is only the ability to send arbitrary HTTP requests to the app's public webhook endpoint plus one legitimate signed body/HMAC pair, which any unprivileged internet user can generate by installing the target app on a free Shopify development store and capturing its own outgoing webhook. No access to `api_secret_key`, tokens, or the victim's credentials is required, and no host-application misuse of undocumented behavior is needed — the gem's public `Registry.process`/`Utils::HmacValidator.validate` API is used exactly as documented.

### Recommendation
Bind the shop identity to the HMAC-verified payload rather than trusting an unauthenticated header for routing decisions:
- Extend `to_signable_string` (or add a companion check in `HmacValidator`/`Registry.process`) to include the `shop-domain` header value (and ideally `topic`/`webhook-id`) in the bytes that are HMAC-verified, or
- Require host applications to independently verify that the `shop` on the request corresponds to an actual installed/known session before invoking any handler, and document this requirement prominently since the gem currently provides no such check itself.

### Proof of Concept
1. Attacker installs the target Shopify app on their own (free) development store `attacker-shop.myshopify.com` and triggers any subscribed webhook topic (e.g. `orders/create`), capturing the raw POST body and the `x-shopify-hmac-sha256` header Shopify sends — this HMAC is valid because it is computed only over the body with the app's shared secret.
2. Attacker resends the exact same body and `x-shopify-hmac-sha256` value to the same webhook endpoint, but sets `x-shopify-shop-domain: victim-shop.myshopify.com` and, if desired, a different `x-shopify-webhook-id`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks `OpenSSL::HMAC.hexdigest(..., @raw_body)` against the supplied HMAC — see [4](#0-3) .
4. The handler registered for that topic is invoked with `WebhookMetadata.new(topic:, shop: "victim-shop.myshopify.com", body: <attacker-controlled JSON>, ...)` — see [5](#0-4) , causing the host app to process attacker data under the victim's tenant context.

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

**File:** lib/shopify_api/webhooks/request.rb (L67-70)
```ruby
      sig { params(name: String).returns(T.untyped) }
      def shopify_header(name)
        @headers["shopify-#{name}"] || @headers["x-shopify-#{name}"]
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
