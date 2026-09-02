### Title
Webhook `shop` (and `topic`/`webhook_id`) identity fields are not covered by the HMAC signature, allowing tenant-spoofed webhook delivery - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable content from the raw body only, while the tenant-identifying `shop-domain` header (plus `topic`/`webhook-id`) is read straight from unauthenticated HTTP headers and handed to the app's webhook handler unchanged. This breaks the equality that should hold for any signed request: `bytes verified == bytes acted on`. Here, `bytes verified = raw_body`, but `bytes acted on = raw_body + shop-domain header`, so the `shop` value used to attribute the event to a tenant is never bound by the signature.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop`, `#topic`, `#api_version`, and `#webhook_id` are all pulled from HTTP headers that are never included in the signable string: [2](#0-1) 

`HmacValidator.validate` only verifies `verifiable_query.to_signable_string` (i.e. the body) against `verifiable_query.hmac`: [3](#0-2) 

`Registry.process` validates the HMAC and then immediately dispatches the handler using the unauthenticated `request.shop` value as the tenant identifier, with no cross-check between `shop` and anything covered by the signature: [4](#0-3) 

Because the app's `api_secret_key` is shared across every shop that installs the app (it is not per-shop), any unprivileged internet user who obtains one legitimately-signed `(raw_body, hmac)` pair for the app (e.g. by installing the app on their own store and triggering an event, or capturing a webhook in transit/logs) can replay that exact body/HMAC to the app's public webhook endpoint while substituting an arbitrary `X-Shopify-Shop-Domain` header value. The HMAC check still passes because the header is not part of the signed content, and `WebhookMetadata` is constructed with the attacker-chosen `shop`: [5](#0-4) 

This is exactly the analog class called out: "a field acted on but not covered by the HMAC."

### Impact Explanation
Consuming applications are expected (per the gem's own `WebhookMetadata`/`Registry` API) to use `shop` as the tenant key to look up sessions/records and apply the webhook body's effects. Since `shop` is unauthenticated relative to the signature, an attacker can cause the body of a webhook they legitimately received for their own shop to be processed as if it belonged to a different (victim) shop — a cross-tenant data-integrity/access issue. This matches the Critical "cross-tenant access" impact bucket.

### Likelihood Explanation
Requires only network access to the app's public webhook endpoint plus one legitimately-signed webhook payload for the app (trivially obtainable by installing the app on an attacker-controlled shop, which requires no privileged credentials). No `api_secret_key`, access token, or social engineering is needed — only the ability to replay an HTTP POST with a modified header.

### Recommendation
Bind the tenant/topic identity into the signed content that is actually verified, e.g. compute/verify the HMAC over `shop-domain + topic + webhook-id + raw_body` (or otherwise cryptographically bind these header values), rather than over `raw_body` alone in `Request#to_signable_string`. At minimum, document and enforce in `Registry.process` that `shop` must be corroborated against a value derived from signed content (or a previously established session) before being trusted as the tenant key.

### Proof of Concept
1. Install the target app on attacker-owned shop `attacker.myshopify.com`; trigger a webhook (e.g. `orders/create`) and capture the raw body `B` and the resulting `X-Shopify-Hmac-Sha256` header value `H` — both valid because they are signed with the app's shared `api_secret_key`.
2. POST directly to the app's public webhook endpoint with:
   - `X-Shopify-Topic: orders/create`
   - `X-Shopify-Hmac-Sha256: H`
   - `X-Shopify-Shop-Domain: victim-shop.myshopify.com` (arbitrary victim tenant)
   - Body: `B`
3. `Utils::HmacValidator.validate` succeeds because it only checks `H` against `B`, per [6](#0-5) .
4. `Registry.process` invokes the app's handler with `WebhookMetadata.new(topic: "orders/create", shop: "victim-shop.myshopify.com", body: parsed_body_from_B, ...)`, causing attacker-controlled data to be processed under the victim tenant's identity.

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

**File:** lib/shopify_api/webhooks/request.rb (L35-43)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end

      sig { returns(T::Hash[String, T.untyped]) }
      def parsed_body
        JSON.parse(@raw_body)
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
