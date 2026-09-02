### Title
Webhook shop, topic, and webhook-id are not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, so the HMAC that `Utils::HmacValidator` verifies binds nothing but the payload bytes. The `shop-domain`, `topic`, and `webhook-id` headers — which `Registry.process` trusts and forwards unchanged into `WebhookMetadata` — are entirely outside that signature. Any merchant who has installed the app on their own store (an ordinary, unprivileged action) can capture one of their own genuinely-signed webhook deliveries and replay it to the app's webhook endpoint with a different `shop-domain` (and/or `topic`) header while keeping the same body and HMAC. `HmacValidator.validate` still returns `true` because it only checks the body, so the app processes attacker-controlled data under a victim shop's identity.

### Finding Description
The identity binding that should hold is:
`shop/topic/webhook_id used by the handler == shop/topic/webhook_id authenticated by the HMAC`

In this gem that equality does not hold. `HmacValidator.validate` verifies the signature exclusively against `verifiable_query.to_signable_string`: [1](#0-0) 

For webhooks, `to_signable_string` is defined as just the raw body: [2](#0-1) 

`Registry.process` then validates only that body-bound HMAC, and immediately trusts the unauthenticated `shop`, `topic`, and `webhook_id` header accessors to build the data handed to the app's handler: [3](#0-2) 

Because none of `shop`, `topic`, or `webhook_id` are part of the signed material, an attacker who has legitimately received one signed `(raw_body, hmac)` pair for their own shop (trivial — they just install the app on any store they control, which triggers Shopify to send them real, correctly-signed webhooks) can resend that exact body and HMAC to the app's webhook endpoint while substituting the `x-shopify-shop-domain` header for a victim shop's domain. `HmacValidator.validate` still returns `true`, and `Registry.process` calls the app's handler with `shop: "victim-shop.myshopify.com"` even though the body content was produced entirely by the attacker.

### Impact Explanation
This breaks the tenant boundary the whole webhook subsystem is meant to enforce: an attacker with no access token, no leaked secret, and no privileged account — merely their own legitimate app installation — can make the host application believe attacker-controlled event data originated from an arbitrary other shop that has the same app installed. Depending on how the host app uses `WebhookMetadata#shop`/`#topic` (e.g. updating per-shop billing/subscription state, processing `app/uninstalled` or GDPR `customers/redact`/`shop/redact` topics, syncing orders/inventory), this enables cross-tenant data injection/corruption using only this gem's documented API. This matches the Critical "cross-tenant access" impact category.

### Likelihood Explanation
Likelihood is high: the attacker only needs to be an ordinary merchant capable of installing the target app (a completely unprivileged, self-service action), trigger any webhook event on their own store, capture the body and its valid HMAC header, and replay it to the app's public webhook endpoint with a modified `shop-domain` (and/or `topic`/`webhook-id`) header. No credentials belonging to the app or to the victim shop are required.

### Recommendation
Include the shop domain (and ideally topic/webhook id) inside the value that gets HMAC-verified, or otherwise cryptographically bind them, e.g.:
- Compute/verify the signature over a canonical string that concatenates the raw body with the `shop-domain` and `topic` header values, or
- Require host applications to separately verify that `shop` corresponds to a shop with an active, previously-established session before processing, and document this explicitly as a hard requirement in `Registry.process`.

### Proof of Concept
```ruby
require "openssl"
require "base64"

secret = ShopifyAPI::Context.api_secret_key
body = '{"id":1,"note":"attacker-controlled"}'

# Attacker installs the app on their own shop and receives a real webhook,
# capturing a genuinely valid (body, hmac) pair.
hmac = Base64.encode64(OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), secret, body))

# Attacker replays the same body/hmac but swaps the shop-domain header.
headers = {
  "x-shopify-topic" => "orders/create",
  "x-shopify-hmac-sha256" => hmac,
  "x-shopify-shop-domain" => "victim-shop.myshopify.com", # not attacker's real shop
  "x-shopify-webhook-id" => "spoofed-id",
  "x-shopify-api-version" => "2024-01",
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: body, headers: headers)

# Still validates successfully because HMAC only covers `body`.
ShopifyAPI::Webhooks::Registry.process(request)
# => handler.handle is invoked with shop: "victim-shop.myshopify.com"
#    and attacker-controlled body content.
```

### Citations

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

**File:** lib/shopify_api/webhooks/request.rb (L20-38)
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
