Confirmed the root cause: `Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , while `topic`, `shop`, `api_version`, and `webhook_id` are all read straight from HTTP headers without being part of the HMAC-signed content [2](#0-1) . `Registry.process` validates only the raw-body HMAC and then trusts `request.shop`/`request.topic` to route and tag the event [3](#0-2) .

### Title
Webhook `shop`/`topic` headers are not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable content from the raw body alone, while the tenant-identifying `shop` header (and `topic`/`webhook_id`/`api_version`) are excluded from the signed payload. `Registry.process` validates the HMAC and then unconditionally forwards `request.shop` to the app's webhook handler as the authoritative tenant identity.

### Finding Description
The binding that should hold is: **HMAC-verified bytes == bytes the app trusts as tenant identity**. Here that equality is broken.

`Request#to_signable_string` is defined as:
```ruby
def to_signable_string
  @raw_body
end
``` [1](#0-0) 

but `shop`, `topic`, `webhook_id`, and `api_version` are all pulled from HTTP headers, which play no part in the signed string:
```ruby
def shop
  T.cast(shopify_header("shop-domain"), String)
end
``` [4](#0-3) 

`Utils::HmacValidator.validate` recomputes the HMAC purely over `to_signable_string` (i.e., the raw body) and compares it to the `X-Shopify-Hmac-Sha256` header [5](#0-4) . Because the same `app_secret_key`-derived signature is valid for the same body regardless of which shop or topic header accompanies it, an attacker who legitimately owns/installs the app on their **own** shop can:
1. Trigger a webhook event on their own shop (e.g., `orders/create`) and capture the genuine `raw_body` + valid `X-Shopify-Hmac-Sha256` header that Shopify sent to the app's endpoint.
2. Replay that exact `(raw_body, hmac)` pair to the app's webhook endpoint, but substitute the `X-Shopify-Shop-Domain` header with a victim shop's domain (and optionally change `X-Shopify-Topic`/`X-Shopify-Webhook-Id`, which are equally unauthenticated).
3. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only checks the raw body [6](#0-5) .
4. The handler receives `WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)` believing the event is authentically from the victim's shop [7](#0-6) .

This is the direct analog of the report's bug class: a value acted upon (`shop`, the tenant key) is not covered by the cryptographic check (`HMAC`) that is supposed to authenticate the entire request.

### Impact Explanation
This is a cross-tenant integrity break: the app's webhook handler (which typically keys data storage, order processing, or state transitions off `shop`) can be made to process attacker-supplied data under another merchant's shop identity, using nothing but a signature the attacker validly obtained for their own shop. This satisfies the "cross-tenant access" Critical category, since an unprivileged app-installing user can forge events attributed to a shop they do not control.

### Likelihood Explanation
Any developer who has installed the target app on their own store (a normal, unprivileged action) can capture real webhook deliveries their store receives (e.g., via a proxy on their own endpoint, or any logging they control) and replay them with a modified `shop`/`topic` header. No access to `api_secret_key` or the victim's tokens is required — likelihood is high for any app relying on this gem's webhook verification for shop attribution.

### Recommendation
Include the identifying headers (`shop`, `topic`, `webhook_id`, `api_version`) in the signed content the app trusts, or otherwise cryptographically bind them to the raw body before verification — e.g., re-derive/verify the shop's known secret per shop rather than trusting the header, or require `to_signable_string` to canonicalize header+body together to match what Shopify actually signs, and reject any mismatch between the header-declared shop and any shop obtainable from a pre-established shop-to-secret mapping.

### Proof of Concept
1. Install the app on `attacker-shop.myshopify.com`; trigger an `orders/create` webhook and capture the raw POST body plus the `X-Shopify-Hmac-Sha256`, `X-Shopify-Topic`, `X-Shopify-Shop-Domain: attacker-shop.myshopify.com` headers Shopify sent.
2. Replay the identical body and HMAC header to the app's webhook endpoint, but set `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)` [6](#0-5) ; since validation only hashes `@raw_body` [1](#0-0) , it succeeds.
4. The registered handler receives `WebhookMetadata` with `shop: "victim-shop.myshopify.com"` [7](#0-6) , processing attacker-controlled data under the victim's tenant identity.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
