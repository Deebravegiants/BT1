### Title
Webhook `shop-domain` header is not covered by the Shopify HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes and verifies the webhook HMAC over the raw request body only, while the `shop` (tenant identifier) is read from a separate, unsigned HTTP header. Because the shop attribution is not bound to the HMAC-covered bytes, an attacker who owns a legitimate installation of the app (their own shop) can capture one genuine webhook (valid body + valid HMAC for their own tenant) and replay it against the app's webhook endpoint with the `X-Shopify-Shop-Domain` header rewritten to a victim shop. `HmacValidator.validate` still passes because it only checks the body, so the forged request is dispatched to the handler labeled as coming from the victim tenant.

### Finding Description
`Utils::HmacValidator.validate` verifies a `VerifiableQuery` by recomputing an HMAC over `to_signable_string` and comparing it to the `hmac` value supplied by the caller: [1](#0-0) 

For webhooks, `ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body — it does not include the shop domain, topic, or any other header: [2](#0-1) 

However, `#shop` (and `#topic`, `#webhook_id`) are pulled directly from unauthenticated HTTP headers: [3](#0-2) 

`Webhooks::Registry.process` validates the HMAC and then dispatches to the handler using `request.shop`, which is never checked against the signed payload: [4](#0-3) 

This breaks the intended binding: `shop-domain header == tenant the signed body belongs to`. In reality the equality that holds is only `HMAC(body) == valid-for-this-app-secret`; the shop value is completely detached from what was actually signed. Any bytes that produced a valid HMAC for *some* legitimate webhook (obtainable by any developer who installs the app on a shop they control, since Shopify signs every real webhook it sends) can be replayed with an arbitrary `shop` header, and the gem will treat the body as belonging to that arbitrary tenant.

### Impact Explanation
This is a cross-tenant access primitive: an attacker who is a legitimate merchant/installer of the app can forge webhook deliveries that the host application will attribute to a victim shop of their choosing. Depending on how the host's `WebhookHandler` uses `WebhookMetadata#shop` (e.g., looking up/updating tenant records, writing order/customer data, triggering per-shop side effects), this allows injecting attacker-controlled body data into another tenant's context — a cross-tenant integrity/confidentiality violation, matching the Critical "cross-tenant access" impact category in scope.

### Likelihood Explanation
Likelihood is meaningful, not merely theoretical: obtaining a validly-signed webhook body is trivial for any attacker with their own free/dev shop and an installed instance of the target app (e.g., trigger `orders/create` in their own store). The webhook endpoint is by design internet-reachable and unauthenticated aside from the HMAC. Rewriting the `X-Shopify-Shop-Domain` (or `Shopify-Shop-Domain`) header on replay requires no cryptographic material beyond what the attacker already legitimately possesses.

### Recommendation
Include the shop domain (and ideally topic/webhook id) as part of the HMAC-verified material, or otherwise cryptographically bind the shop header to the signed body before trusting it — mirroring how `Auth::Oauth::AuthQuery#to_signable_string` includes `shop` in the signed string. At minimum, `Webhooks::Request#to_signable_string` should incorporate the shop-domain header so that `HmacValidator.validate` fails if the header is altered after the fact:
```ruby
sig { override.returns(String) }
def to_signable_string
  "#{shop}\n#{@raw_body}"
end
```
(with a corresponding compatible change on the signing/verification side, coordinated with how Shopify signs webhook payloads).

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com` and triggers a real webhook (e.g., `orders/create`). Shopify sends:
   - Headers: `X-Shopify-Topic: orders/create`, `X-Shopify-Hmac-Sha256: <valid-hmac-of-body>`, `X-Shopify-Shop-Domain: attacker.myshopify.com`
   - Body: `{"id":1,...}` (attacker fully controls the contents of their own order/resources, so the body itself can be crafted).
2. Attacker replays the identical body and `X-Shopify-Hmac-Sha256` value to the app's webhook endpoint, but sets `X-Shopify-Shop-Domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks `HMAC(raw_body)` — see [5](#0-4) .
4. The handler receives `WebhookMetadata.new(topic:, shop: "victim.myshopify.com", body: attacker_controlled_body, ...)` and processes attacker-controlled data under the victim's tenant identity — see [6](#0-5) .

### Citations

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

**File:** lib/shopify_api/webhooks/request.rb (L20-33)
```ruby
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
