Confirmed: `Webhooks::Request#to_signable_string` returns only `@raw_body`, meaning the HMAC covers exclusively the JSON body. The `shop`, `topic`, `webhook_id`, and `api_version` fields are all read directly from HTTP headers, which are outside the signed payload, yet `Registry.process` and `WebhookMetadata` pass this unauthenticated `shop` field straight to the host app's handler as the shop that identifies the tenant.

### Title
Webhook `shop` (and topic/webhook_id) fields are not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` derives its HMAC-signable content solely from the raw request body, while the `shop`, `topic`, `webhook_id`, and `api_version` attributes are parsed from unauthenticated HTTP headers. `ShopifyAPI::Webhooks::Registry.process` validates only the body-derived HMAC and then forwards these header-derived, unauthenticated values into `WebhookMetadata`, which the documented handler API instructs developers to trust as "the shop domain of the webhook."

### Finding Description
`Request#to_signable_string` is defined as: [1](#0-0) 
returning only `@raw_body`. Meanwhile `shop`, `topic`, `webhook_id`, and `api_version` are read from HTTP headers without any cryptographic binding to the signature: [2](#0-1) 

`Registry.process` validates the HMAC (which only proves the body integrity/authenticity) and then constructs `WebhookMetadata` directly from the unvalidated header fields, including `shop: request.shop`: [3](#0-2) 

The identity binding broken is: `shop asserted in HTTP header` ≠ `shop bound by the HMAC signature`. The signature proves "this body was produced with the app's `api_secret_key`," but not "this body belongs to shop X." Any actor who can trigger a legitimate webhook delivery from Shopify for one shop they control (e.g., their own installed instance of the app) obtains a validly-HMAC'd body. Because headers are unauthenticated, that same signed body can be replayed toward the app's webhook endpoint with a forged `X-Shopify-Shop-Domain` (or `shopify-shop-domain`) header naming a different, victim shop. `Registry.process` will accept it as valid (the HMAC check only inspects the body) and hand the handler a `WebhookMetadata` claiming the payload is for the victim shop.

The gem's own documentation instructs host applications to trust this exact unauthenticated field as the tenant identifier: [4](#0-3) [5](#0-4) 

So an app following the gem's documented API (using `data.shop` to route/enqueue work per-tenant) inherits the cross-tenant confusion directly from the gem's validation gap — this is not a case of the host app ignoring documented behaviour.

### Impact Explanation
This meets the Critical bar for cross-tenant access: an attacker-controlled shop can cause the app to process webhook data under a different, victim shop's tenant context. Depending on how the host app uses `data.shop` (e.g., to select which merchant's records to update, which job queue/tenant partition to enqueue into), this can lead to cross-tenant data corruption or information leakage tied to the wrong merchant, using only a request the attacker can trigger from their own (attacker-owned) shop instance of the app.

### Likelihood Explanation
The attacker needs: (1) their own shop with the target app installed (trivial — any developer/merchant can install a public app or already controls a shop that has it installed), (2) the ability to trigger a webhook event server-side (ordinary actions like creating an order), and (3) the ability to intercept/resend the delivered HTTP request with a modified header — achievable since delivery is a normal outbound HTTP POST from Shopify to the app's endpoint that the attacker can replay to the same endpoint. No access to the app's `api_secret_key` or an access token is required, since the attacker never needs to forge the HMAC — they only replay a body Shopify already signed for their own webhook and swap the unauthenticated shop header.

### Recommendation
Bind the identity fields into the HMAC-verifiable content rather than trusting headers independently. Since Shopify signs webhook payloads using HMAC-SHA256 over the raw body per official documentation, the fields transmitted purely via headers should not be treated as authenticated. Alternatives: (a) verify the `shop` header value against a webhook subscription/registration record maintained server-side (keyed by webhook id or a shop known via an established session) rather than trusting the header blindly in `WebhookMetadata`, or (b) update `to_signable_string`/validation to require an additional trusted correlation (e.g., matching the resolved `Session`/shop for the endpoint) before dispatching to the handler, and clearly document that `data.shop`/`data.topic`/`data.webhook_id` are NOT covered by the HMAC and must not be used as a sole tenant-authorization signal.

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker.myshopify.com` and registers/receives a webhook (e.g. `orders/create`).
2. Shopify delivers `POST /webhook_path` to the app with body `B` and headers including `X-Shopify-Hmac-Sha256: HMAC(secret, B)` and `X-Shopify-Shop-Domain: attacker.myshopify.com`.
3. Attacker intercepts/replays this exact request but changes only the header `X-Shopify-Shop-Domain` (or `shopify-shop-domain`) to `victim.myshopify.com`, keeping body `B` and the HMAC value unchanged.
4. The app calls `ShopifyAPI::Webhooks::Registry.process(ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: modified_headers))`.
5. `Utils::HmacValidator.validate(request)` succeeds because it only validates `to_signable_string` (`B`) against the unchanged HMAC: [6](#0-5) 
6. The handler is invoked with `WebhookMetadata.new(..., shop: "victim.myshopify.com", ...)`, and any host-app logic keyed on `data.shop` per the documented pattern now operates under the wrong tenant context.

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

**File:** docs/usage/webhooks.md (L12-16)
```markdown
`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
```

**File:** docs/usage/webhooks.md (L20-29)
```markdown
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
