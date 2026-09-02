## Title
Webhook `shop` (and `topic`/`webhook_id`/`api_version`) headers are not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, so `Utils::HmacValidator.validate` verifies solely that the *body* bytes are authentic. The `shop`, `topic`, `webhook_id`, and `api_version` values are all read from unauthenticated HTTP headers and are never mixed into the signed string, yet `Registry.process` passes `request.shop` straight to the app's webhook handler as the tenant identifier.

### Finding Description
`Request#to_signable_string` is defined as: [1](#0-0) 

while `shop` is derived from the `shopify-shop-domain`/`x-shopify-shop-domain` header: [2](#0-1) 

`Utils::HmacValidator.validate` computes and compares the HMAC only over `to_signable_string` (i.e., the raw body): [3](#0-2) 

`Registry.process` treats a passing HMAC check as sufficient proof of authenticity for the whole request, then forwards the unauthenticated `shop` header directly to the app's handler: [4](#0-3) 

The gem's own documentation instructs app developers to treat `data.shop` as the trusted tenant identifier for downstream processing (e.g., enqueuing per-shop jobs): [5](#0-4) 

This breaks the intended identity binding: `hmac_valid(raw_body) == true` is treated as if it implied `shop_header == originating_shop`, but the signature never covers `shop_header`. Any (body, hmac) pair that was genuinely produced by Shopify for one shop remains valid when replayed with a different `shopify-shop-domain` header value, because the signature check is blind to that header.

### Impact Explanation
An attacker who operates their own store installed on the same app (an ordinary, unprivileged merchant of the app — not requiring `api_secret_key`, access tokens, or any privileged account) can capture a legitimate webhook Shopify sends to the app for their own shop (valid `raw_body` + valid `hmac-sha256`), then resend that exact `(raw_body, hmac)` pair directly to the app's public webhook endpoint while substituting the `shopify-shop-domain` header with a victim shop's domain. `Registry.process` will pass HMAC validation (since the body/hmac pair is genuinely valid) and hand the handler a `WebhookMetadata` claiming the data belongs to the victim shop. Any app that scopes state changes, cache writes, or job attribution by `data.shop` (exactly as the gem's docs recommend) will attribute attacker-controlled data to a victim tenant — a cross-tenant data injection / cross-tenant access impact.

### Likelihood Explanation
Webhook endpoints are public HTTP routes by design (per the documented Rails controller example), so no special network position is needed. The only prerequisite is that the attacker has (or can obtain) a legitimately-signed webhook for *any* shop using the app — trivially satisfied by installing the app on a store the attacker controls and observing its own inbound webhook traffic. Replaying it with a modified header requires no cryptographic secret. This makes the attack straightforward for any external, unprivileged actor with an installed instance of the app.

### Recommendation
Include `shop`, `topic`, `webhook_id`, and `api_version` in the value that is HMAC-verified, or otherwise cryptographically bind them to the body (e.g., verify that `shop` is consistent with an out-of-band trusted channel, or require Shopify's newer signed webhook headers that cover these fields). At minimum, document prominently that `data.shop` is unauthenticated and must not be used for tenant-scoping decisions without an independent authenticity check.

### Proof of Concept
1. Install the target app on attacker-owned shop `attacker.myshopify.com`; capture a real webhook POST from Shopify, noting `raw_body` and the `x-shopify-hmac-sha256` header (`hmac`).
2. Replay `POST /callback/orders/create` to the app's webhook endpoint with the same `raw_body` and same `hmac`, but set `x-shopify-shop-domain: victim.myshopify.com`.
3. `ShopifyAPI::Utils::HmacValidator.validate` returns `true` (only `raw_body` is checked, per `Request#to_signable_string` at [1](#0-0) ).
4. `Registry.process` invokes the app handler with `WebhookMetadata(shop: "victim.myshopify.com", body: <attacker's own order data>, ...)` per [6](#0-5) , causing the app to process attacker data as if it belonged to the victim shop.

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

**File:** docs/usage/webhooks.md (L10-29)
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
    end
  end
end
```
