Confirmed: the vulnerability path is fully supported by the gem's own code with no host-app dependency beyond documented usage.

### Title
Cross-Tenant Webhook Spoofing via Unauthenticated Shop-Domain Header - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating an HMAC computed over the raw request body, while the `shop-domain` header used to attribute the event to a tenant is never included in that signature.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , and `Registry.process` accepts the request as authentic once `Utils::HmacValidator.validate(request)` passes against that signable string [2](#0-1) . `HmacValidator.validate_signature` computes the HMAC purely from `to_signable_string`, i.e. the body, using the app's `api_secret_key` [3](#0-2) . The `shop` attribute read for tenant attribution comes straight from the `shop-domain` header, which is not part of the signed material [4](#0-3) . `Registry.process` then dispatches to the app's handler using this unauthenticated header value as the tenant identifier: `handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop, body: request.parsed_body, ...))` [5](#0-4) .

This breaks the identity binding `shop authenticated by HMAC == shop used to key the tenant's data`. Because the same `api_secret_key` is shared by the app across every installed shop, any merchant who has installed the app can obtain a validly-HMAC-signed webhook body for their own store (by triggering a real event, e.g. `app/uninstalled` or `orders/create`), then replay that exact body to the app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` header with a victim shop's domain. `HmacValidator.validate` still returns `true` because only the body is checked, and `Registry.process` forwards `shop: <victim-domain>` to the handler together with the attacker-controlled body.

### Impact Explanation
This yields cross-tenant data/event injection: the host application — following the gem's documented pattern of trusting `data.shop` from `WebhookMetadata` as returned by `Registry.process` (see `docs/usage/webhooks.md`) — will process attacker-supplied webhook content as if it originated from the victim's shop. Depending on the topic subscribed, this can corrupt another tenant's stored data, trigger uninstall/cleanup logic (e.g., revoking the victim's stored access token) for a shop the attacker doesn't control, or otherwise cross tenant boundaries using only the attacker's own legitimate webhook traffic. No access token, `api_secret_key`, or privileged access is required — only the ability to install the app on one's own store and trigger events on it.

### Likelihood Explanation
Any unprivileged user who can install the app (a standard, unprivileged onboarding action for any public/multi-tenant Shopify app) can generate a validly-signed webhook body from their own shop and replay it with a forged shop header at will; the required signature is always reproducible for their own events, and the header substitution requires no cryptographic material.

### Recommendation
Include the `shop-domain` (and ideally `topic`/`webhook-id`) header values in the signed material verified by `HmacValidator`, or otherwise cross-check the resolved `shop` against a shop known to be associated with the specific webhook subscription/API version before dispatching to the handler, so that HMAC validity is bound to the tenant claim, not just the payload bytes.

### Proof of Concept
```ruby
# Attacker installs the app on their own shop "attacker.myshopify.com" and
# triggers a real event, e.g. app/uninstalled, capturing the genuine
# Shopify-signed body and headers sent to their app's webhook endpoint:
#
#   X-Shopify-Topic: app/uninstalled
#   X-Shopify-Hmac-Sha256: <valid HMAC of raw_body computed with the app's api_secret_key>
#   X-Shopify-Shop-Domain: attacker.myshopify.com
#   raw_body: '{"id":123,...}'   # or any attacker-influenced payload for other topics

# Attacker replays the identical body/HMAC to the same endpoint but swaps only
# the shop header:
headers = {
  "x-shopify-topic"        => "app/uninstalled",
  "x-shopify-hmac-sha256"  => captured_valid_hmac,   # unchanged, still valid for raw_body
  "x-shopify-shop-domain"  => "victim-shop.myshopify.com", # forged
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: captured_raw_body, headers: headers)

# HmacValidator only checks captured_raw_body, so this succeeds:
ShopifyAPI::Webhooks::Registry.process(request)
# => handler.handle(data: WebhookMetadata(shop: "victim-shop.myshopify.com", topic: "app/uninstalled", body: captured_raw_body, ...))
# The host app now believes the victim shop uninstalled the app / sent this data.
```

### Citations

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

**File:** lib/shopify_api/webhooks/registry.rb (L188-190)
```ruby
        sig { params(request: Request).void }
        def process(request)
          raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)
```

**File:** lib/shopify_api/webhooks/registry.rb (L198-199)
```ruby
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
