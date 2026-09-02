This confirms the finding: `Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , while `shop`, `topic`, `api_version`, and `webhook_id` are read directly from HTTP headers without any cryptographic binding to the HMAC [2](#0-1) . `Registry.process` only checks `Utils::HmacValidator.validate(request)`, which recomputes the signature over `to_signable_string` (i.e., raw body only) and then unconditionally trusts `request.shop` to build `WebhookMetadata` [3](#0-2) .

### Title
Webhook shop-domain header is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` binds the HMAC verification exclusively to the raw request body. The `shop` (and `topic`/`webhook_id`/`api_version`) values, which are read straight from the `X-Shopify-Shop-Domain` header, are never included in the signed material. Any actor who can obtain one validly-signed webhook body for the shared app secret can replay it with an arbitrary `shop` header value and still pass `Utils::HmacValidator.validate`.

### Finding Description
`Utils::HmacValidator.validate` computes `HMAC(secret, verifiable_query.to_signable_string)` and compares it to the `hmac` field via `OpenSSL.secure_compare` [4](#0-3) . For `Webhooks::Request`, `to_signable_string` returns only `@raw_body` [1](#0-0) , while `shop`, `topic`, `webhook_id`, and `api_version` are pulled unauthenticated from headers [2](#0-1) .

The identity binding that should hold is:
`shop asserted in the processed webhook == shop that the HMAC signature actually authenticates`

Because the signature covers only the body bytes and not the shop header, this equality does not hold. `Registry.process` validates the HMAC and then trusts `request.shop` (and `request.topic`) to build the `WebhookMetadata` handed to the app's handler [3](#0-2) . Since all shops installed on a given app share the same `api_secret_key`, any request whose body was legitimately HMAC-signed for the app (e.g. a genuine webhook the attacker's own shop received) can be replayed to the app's public webhook endpoint with the `X-Shopify-Shop-Domain` header rewritten to a victim shop, and it will pass verification unchanged.

### Impact Explanation
This breaks the shop/tenant identity boundary that `Utils::HmacValidator.validate` is supposed to enforce for webhook authenticity. A malicious merchant of the app can forge webhook events that the app's handler code will process as if they originated from a different shop, since `request.shop` is not authenticated by the signature. Depending on what the host application's webhook handler does with `WebhookMetadata#shop` (e.g. looking up or acting on a session/access token keyed by that shop, writing data attributed to that shop), this enables cross-tenant data injection or state corruption without possessing the victim's credentials — a High-severity break of a tenant/authentication boundary.

### Likelihood Explanation
Any shop that installs the app has legitimate, valid (body, hmac) pairs delivered to the app's endpoint under the shared `api_secret_key`. The webhook HTTP endpoint is public-facing by design (Shopify posts to it over the internet), so an attacker who is simply a customer/merchant of the app (unprivileged relative to other tenants) can capture such a pair and replay it with a modified shop header with no additional secrets required.

### Recommendation
Include `shop` (and ideally `topic`/`webhook_id`) in the HMAC-signed material for webhook requests, or otherwise cryptographically bind the shop identity to the payload before trusting `request.shop` in `Registry.process`. At minimum, document/require that host applications independently verify the shop domain via the API-key/session context rather than the raw header.

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker.myshopify.com` and receives a real webhook, e.g. for `orders/create`, with headers `X-Shopify-Hmac-Sha256: <validHmac>`, `X-Shopify-Shop-Domain: attacker.myshopify.com`, and some `raw_body`.
2. Attacker resends the exact same `raw_body` and `X-Shopify-Hmac-Sha256` value to the app's webhook endpoint, but sets `X-Shopify-Shop-Domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses the forged headers; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only hashes `@raw_body`, unaffected by the header change [5](#0-4) .
4. The registered handler is invoked with `WebhookMetadata.new(topic: request.topic, shop: "victim.myshopify.com", body: request.parsed_body, ...)`, causing the app to process attacker-controlled data as an authenticated event from the victim shop [6](#0-5) .

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-13)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
