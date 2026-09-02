### Title
Webhook shop identity is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes the HMAC signature only over the raw request body, while the shop identity (`shop-domain` header) that the app trusts to attribute the webhook to a tenant is taken from an HTTP header that is never included in the signed content. This breaks the identity binding: `shop (header, used for dispatch)` ≠ `shop (bytes covered by HMAC)`.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop`, `#topic`, `#webhook_id`, and `#api_version` are all read straight from HTTP headers, none of which are part of the signable string: [2](#0-1) 

`Utils::HmacValidator.validate` verifies the HMAC exclusively against `verifiable_query.to_signable_string`, i.e. the body: [3](#0-2) 

`Registry.process` gates only on this body-only HMAC check, then forwards the header-derived, unauthenticated `shop` value straight into `WebhookMetadata`, which is what the app's `WebhookHandler#handle` uses to attribute the webhook to a specific merchant: [4](#0-3) [5](#0-4) 

Because the `shop-domain` (and `topic`/`webhook_id`) header is never part of the signed payload, any request whose body+HMAC pair is valid for the app's secret will pass validation regardless of which shop-domain header accompanies it. The shop value that is actually authenticated by `Utils::HmacValidator` is the empty set — it authenticates nothing about tenant identity, yet `Registry.process` treats `request.shop` as trusted tenant context for the handler.

### Impact Explanation
This is a cross-tenant identity-binding gap: an attacker who legitimately installs the target app on their own store (or otherwise obtains one valid `(raw_body, hmac)` pair signed by the app's secret for any topic) can resend that exact body and HMAC to the app's webhook endpoint while substituting an arbitrary victim `X-Shopify-Shop-Domain` header. `HmacValidator.validate` still succeeds (it only checks the body), and `Registry.process` dispatches the attacker-chosen body to the handler tagged with the victim's shop. Any app that uses `WebhookMetadata#shop` to look up/update per-tenant records (the documented and expected usage pattern) will apply attacker-controlled webhook content under another merchant's identity — a cross-tenant access/data-integrity issue.

### Likelihood Explanation
Obtaining one valid `(body, hmac)` pair is trivial for anyone who installs the app on their own store (no special privilege required, and no `api_secret_key`/access token is needed by the attacker) — genuine webhooks the app receives for the attacker's own shop already contain a body and a correctly computed HMAC. Replaying them with a modified shop header requires only sending an HTTP request to the app's public webhook endpoint.

### Recommendation
Include the shop domain (and ideally topic/webhook id) as part of the signed material verified against the HMAC, or otherwise cryptographically bind the header-derived shop to the payload before it is treated as trusted tenant context in `WebhookMetadata`/`Registry.process`.

### Proof of Concept
1. Install the app on attacker-owned shop `attacker.myshopify.com`; trigger any webhook topic the app subscribes to. Capture the resulting request: raw body `B` and header `X-Shopify-Hmac-Sha256: H` (valid for `B` under the app's secret), computed via `lib/shopify_api/webhooks/request.rb`/`hmac_validator.rb`.
2. Send a new POST to the app's webhook endpoint reusing body `B` and header `X-Shopify-Hmac-Sha256: H`, but set `X-Shopify-Shop-Domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only checks `B` against `H` — this passes.
4. The handler receives `WebhookMetadata.new(shop: "victim.myshopify.com", body: parsed B, ...)`, causing the app to process attacker-supplied content as if it originated from `victim.myshopify.com`.

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
