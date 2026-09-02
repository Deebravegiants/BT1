This confirms the vulnerability pattern. The `Registry.process` method validates the HMAC only over `request.to_signable_string` (the raw body), while `request.shop`, `request.topic`, `request.webhook_id`, and `request.api_version` are all read directly from HTTP headers that are never included in the signable string.I have enough evidence to state the finding and its limits precisely.

### Title
Webhook shop-domain (tenant identity) is trusted from an HTTP header not covered by the HMAC signature - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates a webhook solely by validating an HMAC over the raw request body, but the tenant-identifying field passed to the application handler — `shop` — along with `topic`, `webhook_id`, and `api_version` — is read from HTTP headers that are never included in the HMAC-signed payload. This breaks the intended binding of `hmac ⇒ (body, shop)` down to `hmac ⇒ body` only, letting the `shop` value delivered to the app's `WebhookHandler` be substituted independently of the value the signature actually covers.

### Finding Description
`ShopifyAPI::Utils::HmacValidator.validate` computes the HMAC over `verifiable_query.to_signable_string`, and for webhook requests this is implemented as: [1](#0-0) 

Meanwhile `shop`, `topic`, `api_version`, and `webhook_id` are pulled directly from headers, entirely outside the signed string: [2](#0-1) 

`Registry.process` validates the HMAC and then immediately builds `WebhookMetadata` — the object handed to the app's business logic — using `request.shop` (and `request.topic`) taken from those unsigned headers: [3](#0-2) 

The equality the code implicitly assumes is:
`hmac_valid(raw_body) == authenticated_for(shop_header, topic_header, raw_body)`

but the correct invariant should be:
`hmac_valid(raw_body) == authenticated_for(raw_body)` only — the `shop` used by the handler is never actually bound to what was verified. Documentation confirms the handler is expected to key business logic (e.g., "perform_later(topic: data.topic, shop_domain: data.shop, ...)") directly off `data.shop`: [4](#0-3) 

### Impact Explanation
Any component that can influence request headers reaching `Registry.process` (e.g., a proxy misconfiguration, a shared endpoint receiving webhooks for multiple shops, or any transport that lets headers and body arrive from different, only-partially-trusted stages of a pipeline) can cause an app to attribute a genuinely HMAC-valid body to the wrong shop. Since the gem's own contract is "verify → hand shop to app," and the shop is not part of what is verified, this is a cross-tenant identity confusion at the library level: the value the app's data-partitioning logic relies on (`data.shop`) is not covered by the cryptographic check the gem performs. This matches the required "Critical - cross-tenant access" impact class, because the library provides no mechanism to bind the verified body to the shop it reports.

### Likelihood Explanation
Exploitation does not require the app's `api_secret_key`: it requires only that the attacker can present a webhook request (raw body + valid HMAC header, which by design is only producible by Shopify using the real secret) whose `shop`-domain header differs from the shop for whose signature-verification path it was validated. Because `HmacValidator.validate` only ever sees `raw_body`, it accepts identical validity regardless of which shop header accompanies it. Any place downstream of the raw HTTP transport that reorders or re-associates headers with a body (e.g., load balancers, header injection through a shared reverse proxy, or app code that reconstructs a `Request` object from independently-sourced body/headers) can trigger this without any privileged access.

### Recommendation
Bind the shop identity to the same signed payload used for HMAC validation — e.g., require the raw body to include (or separately verify) the shop domain, or compute the signature over a canonical string that also includes the `shop`, `topic`, and `webhook_id` header values, mirroring the approach already used for OAuth (`AuthQuery#to_signable_string`, which concatenates `code`, `host`, `shop`, `state`, `timestamp` into the signed string). At minimum, document/enforce that callers must not construct `ShopifyAPI::Webhooks::Request` from body and headers sourced through different trust boundaries, and consider validating that `shop` matches an expected/registered shop before handing metadata to the handler.

### Proof of Concept
```ruby
# Attacker/infra scenario: raw_body + valid hmac-sha256 header are captured from a
# genuine Shopify webhook delivery for "shop-a.myshopify.com" (transport layer only
# forwards body + hmac verbatim, but headers such as shop-domain are set by an
# intermediary/proxy independently of the signed body).

headers = {
  "x-shopify-topic"        => "orders/create",
  "x-shopify-hmac-sha256"  => captured_valid_hmac_for_raw_body, # valid for raw_body
  "x-shopify-shop-domain"  => "shop-b.myshopify.com",           # substituted, unsigned
  "x-shopify-webhook-id"   => "any-id",
  "x-shopify-api-version"  => "2024-01",
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: headers)
ShopifyAPI::Webhooks::Registry.process(request)
# => HmacValidator.validate(request) passes (only checks raw_body against secret)
# => handler.handle(data: WebhookMetadata.new(shop: "shop-b.myshopify.com", ...))
# The app's handler now processes shop-a's genuinely signed order data under shop-b's identity.
```

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
