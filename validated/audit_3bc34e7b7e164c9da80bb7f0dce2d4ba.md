This confirms the analog: the gem's docs explicitly describe `data.shop` as "The shop domain of the webhook" and it's the documented, trusted field that host apps are told to key their tenant logic on (`docs/usage/webhooks.md:12-26`), while `ShopifyAPI::Webhooks::Registry.process` only checks `Utils::HmacValidator.validate(request)` before forwarding it. [1](#0-0) [2](#0-1) 

### Title
Webhook shop-domain identity is not bound to the HMAC-verified body, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body` [3](#0-2) , while `shop`, `topic`, `webhook_id`, and `api_version` are all read from unauthenticated HTTP headers [4](#0-3) . `Utils::HmacValidator.validate` computes the HMAC purely from `to_signable_string` and compares it to the `hmac` header [5](#0-4) . `Registry.process` treats a passing HMAC check as proof the entire request — including `request.shop` — is authentic, and hands `shop` straight to the app's handler [1](#0-0) .

### Finding Description
The intended identity binding is: `shop header == tenant that produced the HMAC-signed body`. In reality the gem only verifies `HMAC(body) == received_hmac`; the `shop-domain` header is never part of the signed material. This is the same class of bug as the external report — code that validates one piece of state (the withdrawal at index `0`) but acts on a different, unverified piece of state (the withdrawal at index `i`). Here, the gem validates the *body* bytes but acts on (and forwards to the tenant-resolution logic) the *header* bytes, which are never covered by that validation.

Because `Registry.process` exposes `request.shop` to the handler as the trusted per-tenant identifier (and the gem's own documentation instructs integrators to key their `perform_later`/tenant lookup on `data.shop` [6](#0-5) ), any attacker capable of producing one valid `(raw_body, hmac)` pair for their own shop (trivial — install the app on an attacker-controlled shop and receive a legitimate webhook) can replay that identical body/HMAC to the app's webhook endpoint while substituting an arbitrary `X-Shopify-Shop-Domain` header value naming a victim shop. `HmacValidator.validate` will still return `true` because it never inspects the header, and `Registry.process` will invoke the handler with `shop: "<victim-shop>.myshopify.com"`.

### Impact Explanation
This breaks the tenant boundary: an app built per this gem's documented contract will process attacker-supplied webhook content under a victim shop's identity, since the field the gem treats as verified (`request.shop`) is not actually covered by the cryptographic check it performs. This is a cross-tenant access primitive — a Critical-severity outcome per the exploit categories listed (cross-tenant access via a credential/tenant-binding gap in the gem's own webhook-processing code, not a host-app misuse).

### Likelihood Explanation
Any developer following the shipped documentation (`docs/usage/webhooks.md`) is exposed automatically — no special host-app anti-pattern is required, since the doc itself instructs consumers to trust `data.shop`. The only prerequisite for the attacker is holding one legitimate app installation (their own store) to obtain a validly-HMAC'd payload, which is trivial for any public/embedded app.

### Recommendation
Include the `shop` (and ideally `topic`/`webhook_id`) header values in the material that is HMAC-verified, or otherwise cryptographically bind the header-derived `shop` to the signed body before exposing it to `WebhookMetadata`/handlers — mirroring the report's fix of using a single consistent, verified identifier instead of mixing verified and unverified state.

### Proof of Concept
1. Attacker installs the target app on `attacker.myshopify.com` and triggers a webhook (e.g. `orders/create`), capturing the real `raw_body` and the corresponding `X-Shopify-Hmac-Sha256` value that Shopify computed and sent.
2. Attacker POSTs to the app's webhook endpoint reusing that exact `raw_body`/HMAC pair, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses the forged headers; `Utils::HmacValidator.validate` recomputes HMAC over `raw_body` only and it matches, so `Registry.process` proceeds [7](#0-6) .
4. The registered handler receives `WebhookMetadata` with `shop: "victim-shop.myshopify.com"` and attacker-controlled `body`, and (per the gem's documented usage pattern) performs tenant-scoped work against the victim shop using attacker data.

### Citations

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

**File:** lib/shopify_api/webhooks/request.rb (L15-38)
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

**File:** docs/usage/webhooks.md (L12-26)
```markdown
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
