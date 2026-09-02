This confirms the vulnerability. The `shop` field passed to `WebhookMetadata` and consumed by handlers is taken directly from the `shopify-shop-domain`/`x-shopify-shop-domain` HTTP header, entirely outside the HMAC's coverage, which signs only `@raw_body`.

### Title
Webhook `shop` identity is not covered by HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant-identifying `shop` field from an HTTP header that is never included in the HMAC-signed payload, so the shop identity trusted by the webhook handler is not bound to the cryptographic proof of authenticity.

### Finding Description
`ShopifyAPI::Webhooks::Registry.process` validates a webhook by calling `Utils::HmacValidator.validate(request)`, which recomputes an HMAC over `request.to_signable_string` and compares it to `request.hmac`. In `Request`, `to_signable_string` returns only `@raw_body`, and `hmac` decodes the `shopify-hmac-sha256`/`x-shopify-hmac-sha256` header value: [1](#0-0) [2](#0-1) 

Separately, `shop` is read from a distinct header (`shopify-shop-domain`/`x-shopify-shop-domain`) with no cryptographic tie to the HMAC computation at all: [3](#0-2) 

`HmacValidator.validate_signature` only checks `verifiable_query.to_signable_string` (the raw body) against the secret-derived signature — it never incorporates the shop header into the signed material: [4](#0-3) 

`Registry.process` then trusts `request.shop` as the authenticated tenant identity and hands it straight to the app's handler via `WebhookMetadata`: [5](#0-4) [6](#0-5) 

The broken binding is: `shop_bound_by_hmac == shop_delivered_to_handler` does not hold. The HMAC only proves "this body+secret pair is valid, from some source that knows `api_secret_key`" (which, notably, is the app-wide `client_secret`, not per-shop) — it says nothing about which shop the payload belongs to. An attacker who controls any shop that has this app installed (e.g., their own free development/test store) can capture one of their own store's legitimate webhook deliveries (valid `raw_body` + valid HMAC over that body), then replay the exact same `raw_body`/HMAC pair to the app's webhook endpoint while substituting the `shopify-shop-domain` header with a victim shop's domain. `HmacValidator.validate` still returns `true` because it never looked at the shop header, and the handler receives `WebhookMetadata` claiming the payload is from the victim shop.

### Impact Explanation
This breaks the tenant boundary the gem is supposed to enforce for webhook delivery: any app relying on `request.shop` (as documented and as passed through `WebhookMetadata#shop`) to know which merchant a webhook body belongs to can be made to process attacker-controlled data under a victim shop's identity. Depending on the app's handler logic (e.g., updating shop-scoped records, uninstall/app-lifecycle side effects, order/customer sync), this enables cross-tenant data injection/corruption — a Critical-severity cross-tenant access issue, since the shop-binding guarantee the HMAC is supposed to provide is absent for this specific field.

### Likelihood Explanation
Any unprivileged internet user who can install the app on a shop they control (trivial with a free Shopify development store) can obtain a valid `raw_body`/HMAC pair for real webhook topics, then replay it against the same app's public webhook endpoint with a forged `shop` header. No access token, `client_secret`, or privileged access is required — only the ability to receive a legitimate webhook from their own installation and resend it with a different header.

### Recommendation
Bind the `shop` domain to the signed material, or otherwise verify it out-of-band before trusting it: at minimum, cross-check `request.shop` against the shop associated with the registered webhook subscription/session server-side, and/or include the shop domain in the HMAC-signed payload the gem verifies rather than trusting an unsigned header. Document clearly that `request.shop` from `ShopifyAPI::Webhooks::Request` is not cryptographically authenticated and must not be used as the sole tenant identifier without additional verification.

### Proof of Concept
1. Attacker installs the vulnerable app on their own shop `attacker.myshopify.com` and receives a legitimate webhook delivery, capturing the exact `raw_body` and the `shopify-hmac-sha256` header value Shopify sent.
2. Attacker sends a forged HTTP request to the app's webhook endpoint with the same `raw_body` and same `shopify-hmac-sha256`, but sets `shopify-shop-domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only checks `raw_body` against the HMAC [7](#0-6) .
4. The handler is invoked with `WebhookMetadata.new(topic:, shop: "victim.myshopify.com", body:, ...)` [8](#0-7) , causing the app to process attacker-supplied data as if it originated from the victim shop.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-13)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end
```

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
