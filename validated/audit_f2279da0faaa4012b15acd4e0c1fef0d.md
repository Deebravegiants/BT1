This confirms the vulnerability. `Request#to_signable_string` (in `lib/shopify_api/webhooks/request.rb:36-38`) returns only `@raw_body`, so the HMAC computed by `HmacValidator.validate` (in `lib/shopify_api/utils/hmac_validator.rb:26-31`) authenticates only the request body bytes. The `shop`, `topic`, `webhook_id`, and `api_version` fields are read straight from unauthenticated HTTP headers (`lib/shopify_api/webhooks/request.rb:16-33`) and passed unchecked into `WebhookMetadata` by `Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-199`), which is what host apps use to attribute the event to a tenant.

### Title
Webhook shop/topic identity headers are not covered by HMAC, allowing cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` only returns the raw body, so the HMAC verified by `Utils::HmacValidator.validate` binds solely to the payload bytes. The `shop-domain`, `topic`, `webhook-id`, and `api-version` headers used to build `WebhookMetadata` (the tenant/event identity trusted by the host app's handler) are never part of the signed content.

### Finding Description
`Registry.process` enforces `raise ... unless Utils::HmacValidator.validate(request)` [1](#0-0)  before dispatching to the handler with `WebhookMetadata.new(topic: request.topic, shop: request.shop, body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id)` [2](#0-1) .

`HmacValidator.validate_signature` computes `compute_signature(verifiable_query.to_signable_string, secret)` and compares it against the `hmac` header [3](#0-2) . For `Request`, `to_signable_string` returns only `@raw_body` [4](#0-3) , while `shop`, `topic`, `webhook_id`, and `api_version` are all pulled from separate, unsigned headers [5](#0-4) .

This breaks the intended binding: `hmac == HMAC(secret, body)` should equal `hmac == HMAC(secret, body ‖ shop ‖ topic)` for the identity fields the app actually trusts, but it does not. Concretely: an unprivileged internet user who operates their own (e.g., free/dev) Shopify store can register the target app's webhook endpoint to receive their own store's legitimately-signed webhooks. Because the signature covers only the JSON body, that same `(raw_body, hmac)` pair remains valid no matter what `x-shopify-shop-domain`, `x-shopify-topic`, `x-shopify-webhook-id`, or `x-shopify-api-version` headers are sent alongside it. The attacker can therefore replay the captured, validly-signed body while substituting the `shop-domain` header for an arbitrary victim shop and/or swapping the `topic`/`webhook-id`, and `Registry.process` will pass HMAC validation and hand the forged identity straight to the app's handler as if it originated from the victim shop.

### Impact Explanation
Any host application that uses `data.shop` from `WebhookMetadata` to select which merchant's records/session to act on (the documented and expected usage pattern, per `docs/usage/webhooks.md`) will process attacker-supplied data under a victim shop's identity. Depending on the handler's logic this enables cross-tenant data injection/corruption (e.g., writing attacker-controlled order/product data against a victim's stored session or database keyed by shop), and can also be used to spoof mandatory compliance-webhook topics (`customers/redact`, `shop/redact`, `customers/data_request`) against a shop the attacker doesn't own. This crosses a tenant boundary using only a body/HMAC pair the attacker legitimately obtained for their own shop, which qualifies as cross-tenant access.

### Likelihood Explanation
Requires only owning any Shopify store subscribed to a webhook that the target app registers, then being able to send arbitrary HTTP requests to the app's public webhook endpoint (unprivileged internet capability, no app credentials or secrets needed). The rest of the SDK offers no additional binding to prevent this.

### Recommendation
Include `shop`, `topic`, `webhook_id`, and `api_version` header values in the string that is HMAC-verified (or otherwise cryptographically bind them to the payload before use), so that the shop/topic used to construct `WebhookMetadata` cannot diverge from the identity attested to by the HMAC-protected bytes.

### Proof of Concept
1. Attacker owns `attacker-shop.myshopify.com` and configures the target app to receive its `orders/create` webhook.
2. Shopify sends a request with body `B` and header `x-shopify-hmac-sha256: HMAC(secret, B)` and `x-shopify-shop-domain: attacker-shop.myshopify.com`.
3. Attacker replays this exact `(B, hmac)` pair to the app's webhook endpoint but changes the header to `x-shopify-shop-domain: victim-shop.myshopify.com` (and/or a different `x-shopify-topic`, e.g. `customers/redact`).
4. `Request#to_signable_string` only hashes `B`; `HmacValidator.validate` succeeds because the signature was never computed over the shop/topic headers [4](#0-3) .
5. `Registry.process` builds `WebhookMetadata` with `shop: "victim-shop.myshopify.com"` and dispatches it to the app's handler, which processes attacker-controlled data as if it came from the victim shop [2](#0-1) .

### Citations

**File:** lib/shopify_api/webhooks/registry.rb (L188-190)
```ruby
        sig { params(request: Request).void }
        def process(request)
          raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)
```

**File:** lib/shopify_api/webhooks/registry.rb (L198-199)
```ruby
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
