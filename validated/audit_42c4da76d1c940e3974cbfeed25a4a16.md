This confirms the vulnerability. The `shop` field consumed by the app's webhook handler is completely outside the HMAC signature's coverage, since only the raw body bytes are signed.

### Title
Webhook shop-domain identity is unauthenticated and forgeable, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates a webhook solely by validating the HMAC over the raw request body, then trusts the unauthenticated `shop-domain` header as the tenant identity passed to the app's handler. Because the HMAC signature never covers the shop, topic, or webhook-id headers, any party capable of producing a validly-signed body for the app's shared `client_secret` (e.g., any merchant who has installed the app and can capture/replay one of their own legitimate webhook deliveries) can resubmit that same body with a forged `shop-domain` header pointing at a different, victim shop.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

while `shop` is read independently from an HTTP header that is never part of the signed content: [2](#0-1) 

`Utils::HmacValidator.validate` only checks `verifiable_query.hmac` against `to_signable_string`, i.e., the body bytes: [3](#0-2) 

`Registry.process` uses this same validation and then forwards `request.shop` — the unauthenticated header value — directly to the app's webhook handler as the trusted tenant identity: [4](#0-3) 

The gem's own documentation instructs apps to treat `data.shop` as an authoritative tenant identifier for dispatching work (e.g., `perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)`): [5](#0-4) 

The identity binding broken is: `hmac_valid(raw_body, client_secret) == true` should imply `shop == the tenant that actually generated raw_body`, but the code only proves `hmac_valid(raw_body, client_secret) == true`; `shop` is read from a header disjoint from the signed bytes, so the equality does not hold. Since `client_secret` is shared across all shops/installations of a given app (it is the app's secret, not a per-shop secret), any shop with the app installed can obtain a validly HMAC-signed body (from its own legitimate webhook deliveries) and replay it with an arbitrary `X-Shopify-Shop-Domain` header value, and the gem will report it as passing verification for that arbitrary shop.

### Impact Explanation
This breaks the tenant boundary the gem is meant to enforce for webhook processing. An attacker (any merchant with the app installed) can make the app process webhook data while asserting it came from a different, victim shop. If the host app uses `data.shop` to route webhook effects (e.g., write to the victim shop's tenant record, trigger actions scoped to a shop, invalidate/replace data keyed by shop), this results in cross-tenant data corruption or cross-tenant action — a Critical-class impact per this gem's authentication boundary (cross-tenant access), since the false trust originates directly from this gem's `Request`/`Registry` implementation rather than any misuse of a documented API contract.

### Likelihood Explanation
Likelihood is high for any app that follows the documented pattern of trusting `data.shop`. The attacker needs only: (1) their own shop to have the app installed and receiving at least one real webhook (to obtain a validly-signed raw body), and (2) the ability to send an arbitrary HTTP request with that raw body but a modified `shop-domain` header to the app's public webhook endpoint. No access to `api_secret_key`, tokens, or any privileged account is required.

### Recommendation
Include `shop`, `topic`, and `webhook_id` in the signed material validated for a webhook, or otherwise independently bind the shop domain to the signature (e.g., verify that the recomputed HMAC used the specific shop's own signature material if per-shop signing is available), so that mutating the `shop-domain` header invalidates the signature. At minimum, document prominently that `data.shop` from `WebhookMetadata` is unauthenticated and must not be trusted as tenant identity without an independent, session-bound cross-check.

### Proof of Concept
1. App has installed on `attacker-shop.myshopify.com`, has webhook registered for `orders/create`, and receives a legitimately signed webhook with `raw_body = '{"id":1}'` and header `X-Shopify-Hmac-Sha256: <valid signature over raw_body computed by Shopify using the app's client_secret>`.
2. Attacker captures this request and replays it to the app's webhook endpoint, changing only the header `X-Shopify-Shop-Domain: victim-shop.myshopify.com` (topic and hmac headers unchanged).
3. `ShopifyAPI::Webhooks::Request#hmac` and `#to_signable_string` are unaffected by the header change (body untouched), so `Utils::HmacValidator.validate` returns `true`.
4. `Registry.process` invokes the app's handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: {"id" => 1}, ...)`, causing the app to process data as if it originated from `victim-shop.myshopify.com`, even though it never sent this webhook.

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
