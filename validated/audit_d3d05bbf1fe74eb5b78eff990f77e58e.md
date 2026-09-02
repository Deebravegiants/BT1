## Title
Webhook shop/topic/api-version identity headers are not bound to the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw HTTP body, while `shop`, `topic`, `api_version`, and `webhook_id` are read directly from unauthenticated HTTP headers. `Utils::HmacValidator.validate` verifies the HMAC only against the raw body, so the tenant-identifying `shop` header is never cryptographically bound to the signature that the gem validates before dispatching the webhook to the host application's handler.

### Finding Description
`Request#to_signable_string` is defined to return `@raw_body` only: [1](#0-0) 

Meanwhile `shop`, `topic`, `api_version`, and `webhook_id` are pulled straight from HTTP headers with no HMAC coverage: [2](#0-1) 

`Utils::HmacValidator.validate_signature` computes the signature only from `verifiable_query.to_signable_string` (i.e. the raw body) and the shared `api_secret_key`: [3](#0-2) 

`Webhooks::Registry.process` validates the HMAC (body-only) and then unconditionally trusts `request.shop`/`request.topic` to build the `WebhookMetadata` handed to the host app's handler: [4](#0-3) 

Because the app's `api_secret_key` is a single shared secret for *all* shops that install the app, any merchant who legitimately installs the app can capture a genuine `(raw_body, x-shopify-hmac-sha256)` pair from their own real Shopify-delivered webhook. That pair remains cryptographically valid forever (it only depends on the secret and body, never on which shop it was delivered to). The attacker can then replay the exact same body+HMAC to the app's webhook endpoint while substituting the `x-shopify-shop-domain` (and/or `x-shopify-topic`, `x-shopify-webhook-id`) header to point at a victim shop. `HmacValidator.validate` still succeeds because it never inspects those headers, and `Registry.process` will happily dispatch `WebhookMetadata.new(shop: "victim.myshopify.com", ...)` to the host app's handler, which typically keys its data mutation/lookup logic off `data.shop`.

### Impact Explanation
This breaks the identity binding `hmac(secret, signed_bytes) == hmac_header` ⟺ `shop_header == actual_originating_shop`. The gem only proves the body's authenticity under the shared app secret; it does not prove which shop the body is "for." Host applications built on the documented `WebhookMetadata#shop` / `Request#shop` API therefore process attacker-chosen `shop` values as if they were verified, enabling cross-tenant confusion: an attacker can trigger any webhook handler's tenant-scoped side effects (order/product/customer updates, uninstall flows, GDPR data-request flows, etc.) against a victim shop's data using a payload they have no relationship to. Per the rules this is a Critical-impact class (cross-tenant access).

### Likelihood Explanation
Any user can create a free development/trial store and install a public app to legitimately receive at least one real signed webhook, satisfying the prerequisite. Replaying the body+HMAC with a swapped `shop-domain` (and other) header against the app's public webhook endpoint requires no secret knowledge and no privileged access — only the ability to send an HTTP POST, matching the "unprivileged internet user" threat model.

### Recommendation
Bind the tenant-identifying fields into the signed material, or otherwise assert that the header `shop` matches an independently known/authorized shop before acting on webhook data:
- Include `shop`, `topic`, and `webhook_id` in `to_signable_string` (this would be a breaking change vs. Shopify's current signing scheme), or
- Document prominently, and ideally enforce in `Registry.process`, that `WebhookMetadata#shop` must be cross-checked by the host app against a shop it already has an active session/installation record for before performing any mutating action, rejecting webhooks for shops that are not currently installed/authorized.

### Proof of Concept
1. Install the target app on an attacker-controlled shop `attacker.myshopify.com`; capture a real webhook delivery, e.g. raw body `{"id":123}` and header `x-shopify-hmac-sha256: <valid-hmac>` (valid because it's HMAC-SHA256 of the body under the app's shared `api_secret_key`).
2. Replay the identical body and `x-shopify-hmac-sha256` header to the same webhook endpoint, but set `x-shopify-shop-domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` accepts the headers, `Utils::HmacValidator.validate` succeeds (it only checks the raw body against the secret) — see [5](#0-4) .
4. `Registry.process` builds `WebhookMetadata.new(shop: "victim.myshopify.com", ...)` and invokes the registered handler, which the host application will treat as an authenticated event from `victim.myshopify.com`.

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
