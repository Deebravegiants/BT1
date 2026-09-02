Confirmed: the `WebhookMetadata.shop` field passed to the app's handler is documented as "the shop domain of the webhook" [1](#0-0)  and is exactly the header-derived value, never included in the HMAC-signed content.

### Title
Webhook shop-domain attribution is not bound to the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating an HMAC over the raw request body, then hands the caller-supplied `shop-domain` header to the app's handler as the trusted tenant identifier. Because the `shop` field is never part of the signed content, any actor who possesses one valid `(body, hmac)` pair signed with the app's client secret can replay it with an arbitrary `shop-domain` header and have it processed as if it originated from a different merchant.

### Finding Description
`ShopifyAPI::Webhooks::Request` implements `Utils::VerifiableQuery`. Its `to_signable_string` returns only the raw body: [2](#0-1) 

while `shop` is read straight from an unauthenticated header with no cryptographic binding to the signature: [3](#0-2) 

`HmacValidator.validate` (used by `Registry.process`) only checks that `HMAC(client_secret, raw_body) == received_hmac`; it never touches `shop`: [4](#0-3) [5](#0-4) 

`Registry.process` then forwards the unauthenticated `request.shop` directly into `WebhookMetadata`, which is passed to the app-provided handler as the trusted tenant key: [6](#0-5) [7](#0-6) 

Critically, the `hmac-sha256` secret used to sign Shopify webhooks is the app's single `client_secret` (`Context.api_secret_key`), shared across every shop that has the app installed — it is not per-shop. This means the same `(topic, body, hmac)` tuple that Shopify sends for a webhook belonging to shop A is a value the merchant who owns shop A (or anyone who can observe traffic to shop A's webhook endpoint) can capture and replay to the app's webhook endpoint with the `shopify-shop-domain` header changed to shop B. The signature still validates because it was never over the shop field — it was only ever over the body. The app's documented contract tells integrators to trust `data.shop` as the identity of the emitting merchant: [1](#0-0) 

This breaks the identity binding: `shop authenticated by HMAC` ≠ `shop attributed to the processed webhook`. Before the attack, `request.shop` (header) happens to equal the shop whose secret signed the body (because Shopify itself sent it correctly). After the attack, the HMAC still validates (same body/secret), but `request.shop` no longer equals the actual origin of the body — an attacker-chosen value is substituted, and the handler cannot tell the difference since it only sees the `WebhookMetadata` struct.

### Impact Explanation
This is a cross-tenant data confusion vector (Critical category: cross-tenant access). Any app that uses `data.shop` from `WebhookMetadata` to route the webhook body to per-shop application state (e.g., "look up shop B's session/settings, then apply the received order/product/customer payload") can have another tenant's captured webhook replayed and misattributed to shop B, causing shop B's application data to be updated/corrupted with shop A's payload, or triggering shop-B-scoped side effects (order fulfillment, inventory changes, notifications) using attacker-controlled body content that was never generated for shop B.

### Likelihood Explanation
Any merchant that has the app installed legitimately receives valid `(raw_body, hmac)` pairs for their own webhooks — no secret extraction or brute force is required. Replaying that captured pair to the app's public webhook endpoint with a modified `shopify-shop-domain` header is trivial and passes `Registry.process`'s only authentication check.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` (any shop can install a public app) and lets Shopify send it a normal webhook, e.g. `orders/create`, to the app's webhook endpoint. Attacker captures the raw POST body and the `X-Shopify-Hmac-Sha256` header from that request (e.g., via a proxy they control since it's their own shop's traffic).
2. Attacker resends the exact same body and `X-Shopify-Hmac-Sha256` value to the app's webhook endpoint, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` computes `Utils::HmacValidator.validate(request)`, which passes because it only hashes `raw_body` against `Context.api_secret_key` — the same secret used for every shop of this app:
```ruby
# lib/shopify_api/utils/hmac_validator.rb
result = validate_signature(verifiable_query, Context.api_secret_key)
```
4. `Registry.process` builds `WebhookMetadata.new(topic: request.topic, shop: request.shop, body: request.parsed_body, ...)` with `shop == "victim-shop.myshopify.com"` and dispatches it to the app's handler, which believes the payload originated from `victim-shop.myshopify.com`.

### Recommendation
Include the `shop-domain` (and ideally `webhook-id`/`api-version`) header in the HMAC-signed material, or otherwise cryptographically bind the shop identity to the signed payload before trusting it. At minimum, `Registry.process`/`WebhookMetadata` should not treat the `shop` header as authenticated data unless it is verified against a value derived from a signed source (e.g., cross-checked against the destination the webhook was registered for, via `webhook_id` lookup, or by including it in the signable string as Shopify's own broader webhook verification guidance recommends for multi-tenant correctness).

### Citations

**File:** docs/usage/webhooks.md (L12-17)
```markdown
`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
- `api_version`, `String` - The api version of the webhook
```

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

**File:** lib/shopify_api/utils/verifiable_query.rb (L10-16)
```ruby

      sig { abstract.returns(T.nilable(String)) }
      def hmac; end

      sig { abstract.returns(String) }
      def to_signable_string; end
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

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L6-12)
```ruby
    class WebhookMetadata < T::Struct
      const :topic, String
      const :shop, String
      const :body, T::Hash[String, T.untyped]
      const :api_version, String
      const :webhook_id, String
    end
```
