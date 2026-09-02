## Title
Webhook `shop`/`topic` identity fields are not covered by the HMAC signature, enabling cross-tenant webhook spoofing via replay - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating an HMAC over the raw request body, while the `shop`, `topic`, and `webhook_id` fields that are handed to the app's handler as trusted, tenant-identifying data are taken from unauthenticated HTTP headers.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) . `Registry.process` calls `Utils::HmacValidator.validate(request)`, which computes `HMAC(secret, request.to_signable_string)` and compares it to the `hmac` header [2](#0-1) . Once that check passes, `process` builds `WebhookMetadata` directly from unauthenticated headers: `shop: request.shop`, `topic: request.topic`, `webhook_id: request.webhook_id` [3](#0-2) , and `Request#shop`/`#topic`/`#webhook_id` are read straight from the `shopify-shop-domain`/`shopify-topic`/`shopify-webhook-id` headers with no cryptographic binding to the body or the HMAC [4](#0-3) .

The equality this breaks: **shop authenticated by the HMAC ≠ shop delivered to the handler as the session/tenant key.** Shopify signs webhooks with the app's single `client_secret`/`api_secret_key`, which is identical for every shop that has installed the app — the signature never binds the specific `shop-domain` header value. Consequently, any legitimate merchant who installs the app on their own store (an "unprivileged internet user" from the app's perspective) legitimately receives real webhook deliveries with a valid HMAC computed over a body they fully control the content and timing of (e.g. by triggering `orders/create` on their own store). That attacker can capture the `{raw_body, hmac_header}` pair and replay it to the app's webhook endpoint while substituting the `shopify-shop-domain` header with a victim shop's domain. `HmacValidator.validate` still passes because it never inspects headers, and `Registry.process` hands the handler a `WebhookMetadata` claiming `shop: <victim-shop>` with attacker-controlled `body`/`topic`. Any host application that uses `data.shop` as a session/tenant lookup key (exactly as the gem's own documentation instructs — `perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)` [5](#0-4) ) will process attacker-supplied data as if it originated from the victim's store.

### Impact Explanation
This is a cross-tenant access vulnerability: an attacker with only a legitimate, low-privilege installation of the app on their own shop can inject forged webhook events attributed to another merchant's shop, since the gem's own verification primitive (`HmacValidator`/`Webhooks::Request`) never binds `shop`/`topic` to the signature. Any app that follows the documented pattern of keying webhook processing off `WebhookMetadata#shop` is exposed to cross-tenant data corruption/injection without needing the app's `api_secret_key`, an access token, or any credential belonging to the victim.

### Likelihood Explanation
High. The attack requires no privileged access to the target — only a real (attacker-owned) shop installation of the vulnerable app and the ability to replay/craft HTTP requests to the app's public webhook endpoint, both trivially available to any developer/merchant. The affected code path (`Registry.process` → `HmacValidator.validate` → `Request#shop`) is on by design in every app using this gem's webhook feature, and the documented usage pattern actively encourages trusting `data.shop`.

### Recommendation
Include the identity-relevant headers (`shop`, `topic`, `webhook_id`, `api_version`) in the signed material, or otherwise cryptographically bind them to the HMAC — e.g. change `Request#to_signable_string` to sign a canonical concatenation of these headers plus the raw body, and update `HmacValidator`/documentation accordingly. At minimum, document loudly that `data.shop`/`data.topic` are unauthenticated and must not be trusted as a tenant key without independently confirming the shop against the app's own webhook subscription/session state.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker-shop.myshopify.com` and triggers, e.g., an `orders/create` event so Shopify delivers a webhook `POST` with a valid `X-Shopify-Hmac-Sha256` header computed over the raw JSON body using the app's shared `client_secret`.
2. Attacker captures `{raw_body, X-Shopify-Hmac-Sha256}` from that legitimate delivery.
3. Attacker crafts a new request to the same app's webhook endpoint, reusing the identical `raw_body` and `X-Shopify-Hmac-Sha256` header, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only checks `HMAC(secret, raw_body) == hmac_header` — this still matches, so the request is accepted.
5. The app's handler receives `WebhookMetadata(shop: "victim-shop.myshopify.com", topic: ..., body: ...)` and processes/stores it as data belonging to the victim shop, per the gem's documented handler pattern (`shop_domain: data.shop`).

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

**File:** docs/usage/webhooks.md (L24-27)
```markdown
    def handle(data:)
      puts "Received webhook! topic: #{data.topic} shop: #{data.shop} body: #{data.body} webhook_id: #{data.webhook_id} api_version: #{data.api_version}"
      perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)
    end
```
