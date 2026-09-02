This confirms the vulnerability. The gem explicitly documents `shop` as a trusted field from webhook processing (`docs/usage/webhooks.md:14`) that the handler should use to identify which tenant the payload belongs to (e.g. `perform_later(topic: data.topic, shop_domain: data.shop, ...)`), yet this value is read straight from an HTTP header that is never covered by the HMAC signature computed in `ShopifyAPI::Utils::HmacValidator.validate`.

### Title
Webhook `shop` (and `topic`/`webhook_id`/`api_version`) header is trusted but not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant-identifying `shop` attribute solely from the `shopify-shop-domain`/`x-shopify-shop-domain` HTTP header [1](#0-0) , while `to_signable_string`, which is what actually gets HMAC-verified, only returns the raw request body [2](#0-1) . `HmacValidator.validate` computes and compares the signature exclusively against `to_signable_string` [3](#0-2) . This means an attacker who possesses one valid `(raw_body, hmac)` pair (for example, from a webhook legitimately delivered to their own shop after installing the app) can replay that exact body/hmac pair to the app's webhook endpoint while substituting an arbitrary `shop-domain` header value, and `Registry.process` will accept it because it only checks `Utils::HmacValidator.validate(request)` before dispatching to the handler with the attacker-chosen `shop` [4](#0-3) .

### Finding Description
The `shop` field acted upon by the handler (`WebhookMetadata#shop`, documented as "The shop domain of the webhook" [5](#0-4) ) is not bound to the cryptographic proof of authenticity. The equality that should hold is:

`shop asserted in the signed payload == shop the handler acts on`

but in this implementation the signed payload is only the JSON body, and `shop` (as well as `topic`, `webhook_id`, `api_version`) come from unauthenticated headers [6](#0-5) . Because HMAC verification never reads these headers, any request with a body+hmac pair that once validated for shop A will also validate when the `shop-domain` header is changed to shop B — the `OpenSSL.secure_compare` check in `validate_signature` only ever sees the body [3](#0-2) .

### Impact Explanation
This breaks the tenant boundary enforced by the webhook signature: an unprivileged internet user who has installed the app under their own (attacker-controlled) shop can capture one legitimate webhook delivery (body + hmac) and replay it directly to the app's public webhook endpoint with a forged `shop-domain`/`topic`/`webhook_id` header pointing at a victim shop. Because the gem's documented flow instructs handlers to key off `data.shop` for the shop identity used for storage, job dispatch, or session/token lookups [7](#0-6) , this can lead to attacker-controlled data being processed and stored under another merchant's tenant record — cross-tenant data injection/corruption. This matches the "cross-tenant access" impact category.

### Likelihood Explanation
Likelihood is moderate-to-high: any attacker can obtain a valid `(body, hmac)` pair for free by simply installing the app on their own development/trial shop and receiving one real webhook from Shopify (no `api_secret_key` or access token needed, since Shopify computes the HMAC using the app's shared secret and delivers it directly to the attacker's own registered endpoint). No server compromise or credential theft is required — only observation of traffic they are already the legitimate recipient of.

### Recommendation
Bind the `shop` (and ideally `topic`/`webhook_id`/`api_version`) to the HMAC-verified material, or otherwise independently authenticate it — e.g. compute/verify the HMAC over a canonical string that includes these header values, or cross-check the `shop` header against a shop known to have subscribed to this specific `webhook_id`/topic (as tracked internally in `Registry`) before dispatching to the handler. At minimum, document prominently that `data.shop` is unauthenticated and must be revalidated by the host application against a trusted session/shop record before being used for any tenant-sensitive operation.

### Proof of Concept
1. Install the target app on attacker-controlled shop `attacker.myshopify.com`; trigger any subscribed webhook topic (e.g. `orders/create`) so Shopify delivers a legitimately-signed webhook to the app's endpoint, e.g.:
```
POST /callback/orders/create
x-shopify-topic: orders/create
x-shopify-hmac-sha256: <valid-hmac-for-body>
x-shopify-shop-domain: attacker.myshopify.com
x-shopify-webhook-id: <id>
<raw JSON body B>
```
2. Attacker records `(B, valid-hmac-for-body)`.
3. Attacker (or anyone, since no secret is required) resends the identical raw body and hmac header, but with the `x-shopify-shop-domain` header changed to `victim.myshopify.com`:
```
POST /callback/orders/create
x-shopify-topic: orders/create
x-shopify-hmac-sha256: <same-valid-hmac-for-body>
x-shopify-shop-domain: victim.myshopify.com
x-shopify-webhook-id: <id>
<raw JSON body B>
```
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)` which passes (it only checks the body against the hmac) [8](#0-7) , then dispatches `WebhookMetadata.new(... shop: "victim.myshopify.com" ...)` to the app's handler [9](#0-8) , causing attacker-controlled body content to be processed/stored as if it belonged to `victim.myshopify.com`.

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

**File:** docs/usage/webhooks.md (L12-17)
```markdown
`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
- `api_version`, `String` - The api version of the webhook
```

**File:** docs/usage/webhooks.md (L24-27)
```markdown
    def handle(data:)
      puts "Received webhook! topic: #{data.topic} shop: #{data.shop} body: #{data.body} webhook_id: #{data.webhook_id} api_version: #{data.api_version}"
      perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)
    end
```
