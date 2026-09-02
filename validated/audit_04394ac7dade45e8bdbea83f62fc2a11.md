This confirms the finding. The webhook HMAC only signs `@raw_body` (the JSON body) via `Request#to_signable_string`, while `topic`, `shop`, `api_version`, and `webhook_id` are all read directly from HTTP headers that are never included in the signed bytes.This confirms the full data path: `Registry.process` validates only the HMAC over the raw body, then constructs `WebhookMetadata` with `shop: request.shop` taken straight from an unauthenticated header, and passes it to the host app's `WebhookHandler#handle`, which apps use as the tenant/shop identity to route the webhook data.### Title
Webhook `shop` (and `topic`/`api_version`/`webhook_id`) identity fields are not covered by the HMAC, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by verifying the HMAC over the raw JSON body, but the tenant-identifying `shop` field (along with `topic`, `webhook_id`, and `api_version`) is read directly from HTTP headers that are never included in the HMAC's signed bytes. This breaks the identity binding `shop authenticated == shop delivered to handler`.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

Meanwhile `shop`, `topic`, `webhook_id`, and `api_version` are all pulled straight from HTTP headers with no cryptographic binding to the body or to each other: [2](#0-1) 

`Registry.process` validates only this body-only HMAC via `Utils::HmacValidator.validate(request)`, and then immediately builds `WebhookMetadata` using the unauthenticated `request.shop` header value, handing it to the host application's registered handler as the trusted tenant identity: [3](#0-2) 

`Utils::HmacValidator.validate_signature` computes the signature purely from `verifiable_query.to_signable_string` (i.e., the raw body for webhooks) and the app's `api_secret_key`: [4](#0-3) 

The documented usage pattern instructs handlers to use `data.shop` as the tenant key to route/process webhook payloads (e.g., `perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)`), reinforcing that `shop` is treated as an authenticated tenant identifier by consumers of this gem even though the gem itself never binds it cryptographically: [5](#0-4) 

Since a single Shopify app shares one `api_secret_key` across every shop that has installed it, any body+HMAC pair that is valid for shop A (e.g., a legitimate webhook the attacker's own store received) remains a valid HMAC pair regardless of which `shop-domain` header is attached to the replayed request — the signature check has no dependency on that header at all. An attacker who controls (or intercepts) one legitimate webhook delivery for their own shop can replay that exact raw body/HMAC pair to the app's webhook endpoint while substituting an arbitrary `x-shopify-shop-domain` header value, and `Registry.process` will accept it as authentic and dispatch it to the handler labeled with the attacker-chosen shop.

### Impact Explanation
This is a cross-tenant identity-binding break: the field the handler uses to determine *which merchant's data this is* (`shop`) is disjoint from the bytes that are actually authenticated. Depending on how the host application's handler uses `data.shop` (e.g., to select which merchant's DB row/session to update, or to attribute an order/webhook event to a specific store), this allows an attacker to inject data or trigger side effects attributed to a shop they do not control — a cross-tenant access/confusion vulnerability. This qualifies under the "Critical - cross-tenant access" impact category, since it is a data-integrity/tenant-isolation failure enabled entirely by this gem's request-authentication design, not by host-application misuse of a documented API.

### Likelihood Explanation
Exploitation requires the attacker to possess at least one legitimate `(raw_body, hmac)` pair — most straightforwardly by being a merchant who has installed the app themselves and thus legitimately receives webhooks with valid HMACs signed by the shared `api_secret_key`. No access to `api_secret_key`, access tokens, or TLS interception is required; the attacker only needs to replay an HTTP POST with modified headers to the app's public webhook endpoint. This is a realistic, low-effort attack path for any unprivileged merchant/installer of a multi-tenant app.

### Recommendation
Bind the tenant-identifying headers into the HMAC-verified material, e.g., by including `shop`, `topic`, and `webhook_id` in `Request#to_signable_string` (or by having `Registry.process` independently verify that the `shop` in the metadata corresponds to a shop with a currently valid webhook registration/session before dispatching), so that a valid signature for one shop's payload cannot be replayed under a different shop's identity.

### Proof of Concept
1. App `MyApp` is installed on `attacker-shop.myshopify.com` and `victim-shop.myshopify.com`, sharing one `api_secret_key`.
2. Shopify sends the attacker a genuine webhook for their own shop:
   - Headers: `x-shopify-shop-domain: attacker-shop.myshopify.com`, `x-shopify-topic: orders/create`, `x-shopify-hmac-sha256: <valid HMAC of raw_body>`
   - Body: `{"id": 123, ...}`
3. The attacker POSTs the identical `raw_body` and `x-shopify-hmac-sha256` to the app's webhook endpoint, but changes the header to `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request#to_signable_string` returns the unchanged `raw_body`; `Utils::HmacValidator.validate` recomputes the same valid HMAC (headers play no role), so `Registry.process` (`lib/shopify_api/webhooks/registry.rb:190`) does not raise `InvalidWebhookError`.
5. `WebhookMetadata.new(shop: "victim-shop.myshopify.com", topic: "orders/create", body: {...}, ...)` is passed to the app's handler, which processes/attributes the attacker's forged order data to `victim-shop.myshopify.com`.

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
