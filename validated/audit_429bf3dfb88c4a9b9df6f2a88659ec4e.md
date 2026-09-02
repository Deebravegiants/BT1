I found a strong analog. In `ShopifyAPI::Webhooks::Request` (`lib/shopify_api/webhooks/request.rb`), the HMAC signature only covers the raw request body, while the `shop` identity used by webhook handlers is read directly from an unauthenticated header.This confirms the finding. `Registry.process` trusts `request.shop`, `request.topic`, `request.webhook_id`, and `request.api_version` — all sourced from HTTP headers — while `Utils::HmacValidator.validate` only checks the HMAC against `request.to_signable_string`, which returns solely `@raw_body`. The `shop` identity handed to every app's `WebhookHandler#handle` is therefore never covered by the cryptographic signature.

### Title
Webhook `shop` (and `topic`/`webhook_id`) identity is not covered by HMAC verification, enabling cross-tenant webhook forgery via signature replay - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , while `shop`, `topic`, `webhook_id`, and `api_version` are all read from unauthenticated HTTP headers [2](#0-1) . `Registry.process` validates the HMAC over that body-only signable string and then dispatches to the handler using the header-derived `shop` value without any additional check binding `shop` to the signed content [3](#0-2) .

### Finding Description
The identity binding that should hold is: `shop` value trusted by the app == `shop` value cryptographically covered by the HMAC signature. In this gem, that equality does not hold, because:
- `HmacValidator.validate` computes/compares HMAC solely over `verifiable_query.to_signable_string` [4](#0-3) .
- For webhook requests, `to_signable_string` is just the raw body [1](#0-0) ; the `shop-domain` header is completely outside the signed payload [5](#0-4) .
- `Registry.process` uses this unauthenticated `request.shop` to build the `WebhookMetadata` passed straight to the app-provided `WebhookHandler#handle` [3](#0-2) , and the gem's own documentation instructs apps to key business logic (e.g., `shop_domain: data.shop`) directly off this value [6](#0-5) .

This is a direct structural analog to CVE-2023-27535: a piece of connection/request state that determines *whose* identity a downstream action is attributed to (there: FTP account; here: `shop`) is not covered by the same authentication check (there: connection reuse cache key; here: HMAC signature) that is otherwise trusted to authenticate the request.

### Impact Explanation
An unprivileged internet user who legitimately controls one Shopify store (trivially obtainable, e.g. a free development store) can trigger a real webhook to their own app endpoint and obtain a validly-signed `(raw_body, hmac)` pair signed with the app's real `api_secret_key`. Because the HMAC never covers the `X-Shopify-Shop-Domain` header, the attacker can resend that exact same body+HMAC to the app's webhook endpoint while substituting an arbitrary victim shop domain in the header. `HmacValidator.validate` still returns `true` (the body is unchanged), and `Registry.process` will invoke the app's handler with `data.shop` set to the victim's domain and attacker-controlled `data.body`. Any app that uses `data.shop` to scope database writes, cache keys, session lookups, or triggers side effects (as the gem's own documentation recommends) will process attacker data under the victim tenant's identity — a cross-tenant integrity/confidentiality breach.

### Likelihood Explanation
Likelihood is high for any app that installs on more than one shop and relies on `shopify_api`'s webhook signature verification as the sole authenticity check for `data.shop`, which is the documented/expected usage pattern in `docs/usage/webhooks.md`. No secret material is required by the attacker beyond installing the app on a shop they control.

### Recommendation
Include the `shop-domain` (and ideally `topic`, `webhook_id`, `api_version`) header values as part of the HMAC-signable content in `Webhooks::Request#to_signable_string`, or otherwise cryptographically bind them to the verified body (e.g., signing a canonical string containing the headers plus body) so `Registry.process` cannot be fed a validly-signed body under an attacker-chosen shop identity.

### Proof of Concept
1. Attacker installs the target app on their own dev store `attacker.myshopify.com` and lets a real webhook fire, capturing raw body `B` and its valid `X-Shopify-Hmac-Sha256` header `H` (computed by Shopify using the app's real secret).
2. Attacker POSTs to the app's webhook endpoint with:
   - Body: `B` (unchanged)
   - `X-Shopify-Hmac-Sha256: H` (unchanged, still valid since HMAC only covers body)
   - `X-Shopify-Shop-Domain: victim.myshopify.com` (forged)
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only checks `request.to_signable_string` (`== B`) against `H` [7](#0-6) .
4. The registered handler is invoked with `WebhookMetadata.new(shop: "victim.myshopify.com", body: parsed_body_of_B, ...)` [8](#0-7) , causing the app to process attacker-controlled data under the victim shop's tenant identity.

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

**File:** docs/usage/webhooks.md (L19-29)
```markdown
```ruby
module WebhookHandler
  extend ShopifyAPI::Webhooks::WebhookHandler

  class << self
    def handle(data:)
      puts "Received webhook! topic: #{data.topic} shop: #{data.shop} body: #{data.body} webhook_id: #{data.webhook_id} api_version: #{data.api_version}"
      perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)
    end
  end
end
```
