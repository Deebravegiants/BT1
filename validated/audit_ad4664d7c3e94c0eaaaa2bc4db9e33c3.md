This confirms the vulnerability. The `shop-domain` header (`x-shopify-shop-domain` / `shopify-shop-domain`) is **read but not covered by the HMAC** — the webhook signature (`ShopifyAPI::Webhooks::Request#to_signable_string`) only signs `@raw_body`, while `shop` is pulled from a separate, unsigned HTTP header [1](#0-0) . `Registry.process` validates only the body HMAC and then passes the unauthenticated `request.shop` straight into the tenant-identifying `WebhookMetadata` object handed to the app's handler [2](#0-1) . The gem's own documentation instructs host apps to treat `data.shop` as the trusted shop identifier for the webhook [3](#0-2) .

Because Shopify webhook HMACs are computed with the app's single shared `api_secret_key` (the same key across all shops that install the app) rather than a per-shop secret [4](#0-3) , any unprivileged merchant who installs the app can legitimately trigger a webhook for their own store, capture the (valid) body + HMAC pair, and then replay it to the app's callback endpoint with the `x-shopify-shop-domain` header swapped to a victim shop's domain. The signature still validates (it only covers the body), so `Registry.process` accepts it and the handler executes under `data.shop == victim shop` with attacker-controlled body content — a tenant-identity forgery.

### Title
Webhook `shop` field is trusted from an unauthenticated header not covered by the HMAC, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` derives the `shop` (and `topic`, `webhook_id`, `api_version`) fields from raw HTTP headers, while `Utils::HmacValidator.validate` (invoked by `Registry.process`) only verifies the HMAC over the raw request body via `to_signable_string`. The `shop-domain` header is never included in the signed material, so its authenticity is never actually checked, even though the gem passes it to the app's webhook handler as the trusted tenant identifier.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [5](#0-4) 

`Request#shop` reads the `shop-domain` header independently of the signed body: [6](#0-5) 

`Registry.process` validates the HMAC of the request, then immediately builds `WebhookMetadata` using `request.shop`, `request.topic`, etc., which are unauthenticated header values, and dispatches it to the registered handler: [2](#0-1) 

The library's documentation tells app developers that `data.shop` is "The shop domain of the webhook" and shows it being used directly to route/attribute data (e.g., `perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)`): [7](#0-6) 

The HMAC secret is the app's single `api_secret_key`/`old_api_secret_key`, shared across every shop that installs the app — it is not shop-specific: [4](#0-3) 

This breaks the intended binding: `shop header == shop that produced the signed body`. Any merchant who has installed the app (an unprivileged, non-credentialed attacker with respect to *other* tenants) can obtain a genuinely-signed webhook body+HMAC from their own store, then resend it to the app's webhook endpoint with the `shop-domain` header changed to a victim shop's domain. `HmacValidator.validate` only checks the body signature, which is still valid (body unchanged), so the forged request passes verification and the handler executes believing it originated from the victim shop.

### Impact Explanation
This qualifies as cross-tenant access: an attacker can cause the host application to process attacker-controlled webhook payloads under the identity of a different merchant/tenant. Depending on how the host app uses `data.shop` (e.g., looking up the tenant's session/access token, updating tenant-scoped records, billing, deduplication keys), this can lead to cross-tenant data corruption, incorrect authorization decisions, or triggering actions against the wrong merchant's data — all without possessing the victim's credentials or access token.

### Likelihood Explanation
Likelihood is high for any app that installs on more than one shop: the attacker only needs to be a legitimate (even free-trial) installer of the app to generate a validly-signed webhook of their choosing, then trivially forge the `shop-domain` header value on replay, since the signature never covers headers.

### Recommendation
Include the shop domain (and ideally topic/webhook id) in the HMAC-covered material, or independently verify that the shop asserted in the header matches a shop actually known/registered for this app (e.g., cross-check against the merchant's stored session) before trusting `request.shop` in `WebhookMetadata`. At minimum, document prominently that `data.shop` is unauthenticated and must be independently validated by the host application before being used for any tenant-scoped action.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com`.
2. Attacker triggers a webhook event (e.g., `orders/create`) on their own store; Shopify sends the app `POST /callback` with body `B` and header `X-Shopify-Hmac-Sha256: H`, where `H = HMAC-SHA256(api_secret_key, B)` and `X-Shopify-Shop-Domain: attacker.myshopify.com`.
3. Attacker intercepts/replays this request to the app's webhook endpoint, changing only `X-Shopify-Shop-Domain` to `victim.myshopify.com` (body `B` and `H` unchanged).
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes `HMAC-SHA256(api_secret_key, B)` and finds it matches `H` — validation succeeds [8](#0-7) .
5. `WebhookMetadata.new(topic: request.topic, shop: request.shop, body: request.parsed_body, ...)` is built with `shop == "victim.myshopify.com"` and dispatched to the app's handler, which trusts it per the gem's documented contract.

### Citations

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

**File:** docs/usage/webhooks.md (L10-26)
```markdown
If you want to register for an http webhook you need to implement a webhook handler which the `shopify_api` gem can use to determine how to process your webhook. You can make multiple implementations (one per topic) or you can make one implementation capable of handling all the topics you want to subscribe to. To do this simply make a module or class that includes or extends `ShopifyAPI::Webhooks::WebhookHandler` and implement the `handle` method which accepts the following named parameters: data: `WebhookMetadata`. An example implementation is shown below:

`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
- `api_version`, `String` - The api version of the webhook

```ruby
module WebhookHandler
  extend ShopifyAPI::Webhooks::WebhookHandler

  class << self
    def handle(data:)
      puts "Received webhook! topic: #{data.topic} shop: #{data.shop} body: #{data.body} webhook_id: #{data.webhook_id} api_version: #{data.api_version}"
      perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)
```

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-22)
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
```
