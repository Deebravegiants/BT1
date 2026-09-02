## Analysis

The bug class from the external report ("a value is trusted/acted upon without being covered by an integrity check, leading to incorrect binding of an identity") maps cleanly onto how this gem handles inbound Shopify webhooks.

### Root cause

`ShopifyAPI::Webhooks::Request#to_signable_string` — the value that is actually HMAC-verified — is the **raw HTTP body only**: [1](#0-0) 

```ruby
def to_signable_string
  @raw_body
end
```

But `shop`, `topic`, `api_version`, and `webhook_id` are all read straight from unauthenticated HTTP headers: [2](#0-1) 

`Registry.process` validates the HMAC against `to_signable_string` (i.e., the body only) and then hands `request.shop` — a header value that was never part of the signed payload — straight to the app's webhook handler as the tenant identity: [3](#0-2) 

```ruby
def process(request)
  raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)
  ...
  handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop,
    body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))
end
```

### The equality that should hold but doesn't

`shop_used_for_tenant_attribution == shop_covered_by_hmac`

In reality, `shop_covered_by_hmac` doesn't exist at all — the HMAC only binds the body bytes, not the `x-shopify-shop-domain` header. The gem's `Utils::HmacValidator.validate` call gives host applications false confidence that the *entire webhook request*, including tenant attribution, is authenticated, when in fact only the body content is.

### Attack scenario

1. An unprivileged internet user installs the target Shopify app on their **own** store (a store they control) and triggers a webhook event (e.g. `orders/create`) with a body they can craft/observe (order data they control).
2. Shopify sends the webhook to the app's endpoint with a valid HMAC computed over that body, plus headers `x-shopify-shop-domain: attacker-shop.myshopify.com`, `x-shopify-topic: orders/create`.
3. The attacker captures this valid `(raw_body, hmac)` pair — both fully visible to them — and replays the exact same request to the same endpoint, but substitutes the `x-shopify-shop-domain` header with a **victim** shop's domain.
4. `Utils::HmacValidator.validate(request)` still succeeds because it only checks the (unchanged) raw body against the (unchanged) HMAC. `Registry.process` then calls the app's handler with `shop: "victim-shop.myshopify.com"`, attributing the attacker-controlled payload to the victim tenant.

Since host applications are expected to trust the `shop` field returned by this gem's webhook processing (it is the gem's job to authenticate the request), this allows a forged cross-tenant webhook — an unprivileged user can inject fabricated webhook events attributed to a shop they do not control, without possessing that shop's or the app's credentials.

### Title
Webhook shop/topic/tenant identity is not covered by HMAC verification, enabling cross-tenant webhook forgery - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes the HMAC signature over the raw body only, while `shop`, `topic`, `webhook_id`, and `api_version` are sourced from unauthenticated headers and passed downstream as the trusted event/tenant identity after HMAC validation succeeds.

### Finding Description
`Request#to_signable_string` returns `@raw_body` exclusively (`lib/shopify_api/webhooks/request.rb:35-38`), and `Utils::HmacValidator.validate` only ever checks this signable string against the `hmac` header (`lib/shopify_api/utils/hmac_validator.rb:12-31`). Meanwhile `Registry.process` unconditionally trusts `request.shop`/`request.topic` (header-derived, unsigned) once the body HMAC check passes and forwards them as `WebhookMetadata` to the app's handler (`lib/shopify_api/webhooks/registry.rb:188-199`). This breaks the intended binding: the caller of `handler.handle` assumes `shop` was authenticated the same way the body was, but it wasn't.

### Impact Explanation
An attacker who owns/controls one legitimate installation of the target app can obtain arbitrarily many valid `(body, hmac)` pairs for bodies they fully control, then replay them with a forged `shop-domain` header pointing at any other shop. Any app logic keyed off `WebhookMetadata#shop` (e.g., "update order X for shop Y", cache invalidation, triggering merchant-visible side effects) can be made to act on a victim tenant using attacker-supplied data — a cross-tenant integrity/confused-deputy issue.

### Likelihood Explanation
Moderate: it requires the attacker to control at least one legitimate app installation (trivial for a public app: anyone can install it on a free dev/test store) and to know or guess a target shop's domain (which is often public, e.g., `victimshop.myshopify.com`). No secrets or privileged access are required.

### Recommendation
Include `shop`, `topic`, `webhook_id`, and `api_version` in the value that is HMAC-verified (or otherwise validate them out-of-band, e.g. against the caller-supplied expected shop), rather than only signing the raw body, so that the gem's `Errors::InvalidWebhookError` check reflects the full set of trusted fields it hands to the app.

### Proof of Concept
```ruby
# 1. Attacker installs app on their own store and triggers a webhook, capturing:
raw_body = '{"id": 1, "note": "attacker controlled"}'
hmac = OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), api_secret_key, raw_body)

# 2. Attacker replays the exact same body+hmac but swaps the shop header:
forged_headers = {
  "x-shopify-topic" => "orders/create",
  "x-shopify-hmac-sha256" => Base64.encode64(hmac),
  "x-shopify-shop-domain" => "victim-shop.myshopify.com", # not covered by HMAC
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: forged_headers)
ShopifyAPI::Webhooks::Registry.process(request)
# => handler.handle is invoked with shop: "victim-shop.myshopify.com"
#    even though the payload/hmac only proves the body, not the shop.
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
