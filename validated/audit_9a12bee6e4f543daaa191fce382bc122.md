### Title
Webhook `shop` identity is trusted from an unauthenticated header while `hmac` only covers the raw body, allowing cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates a webhook exclusively by validating the HMAC of the raw request body, but the `shop` value that the gem hands to the app's handler is read from an HTTP header that is never included in that HMAC computation. This breaks the intended binding "HMAC-authenticated bytes == the shop the app acts on," letting an attacker who legitimately receives a validly-signed webhook for their own store replay it while claiming to be a different (victim) shop.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

The `shop` accessor, however, is derived purely from the `shopify-shop-domain`/`x-shopify-shop-domain` HTTP header, which is not part of the signed material at all: [2](#0-1) 

`Utils::HmacValidator.validate` recomputes the HMAC over `verifiable_query.to_signable_string` (i.e., the raw body only) and compares it to the `hmac` header using `OpenSSL.secure_compare`: [3](#0-2) 

`Registry.process` only checks this body HMAC before dispatching to the app-registered handler, and it forwards `request.shop` (the unauthenticated header value) straight into the `WebhookMetadata` struct that the handler trusts as the tenant identity: [4](#0-3) 

`WebhookMetadata.shop` is documented and consumed by app code as "The shop domain of the webhook" with no further verification expected from the app: [5](#0-4) [6](#0-5) 

**Broken binding (as an equality):**
`hmac_header == HMAC(secret, signable_string)` is verified, but the gem then asserts `metadata.shop == shop-domain header`, which is an *entirely separate, unauthenticated* value. The intended invariant should be `metadata.shop == the tenant whose secret actually produced this HMAC`, but nothing in the code enforces that the `shop-domain` header corresponds to the body/HMAC pair that was validated.

Because Shopify signs webhooks with the single shared `client_secret` for the whole app (not a per-shop secret), any merchant who has legitimately installed the app receives real webhooks with a valid HMAC for their own shop. That attacker-controlled tenant can capture one such `(raw_body, hmac)` pair and replay it to the app's webhook endpoint while substituting an arbitrary `x-shopify-shop-domain` header (e.g., a victim's shop). `HmacValidator.validate` still passes, because it only checks the body bytes, and `Registry.process` will hand the handler a `WebhookMetadata` claiming the payload belongs to the victim shop.

### Impact Explanation
This is a cross-tenant integrity break: an unprivileged, unauthenticated actor (with respect to the victim shop — they only need their own valid installation) can make an app process attacker-supplied JSON as if it originated from a different merchant's store. Any host application that keys off `data.shop` to select which tenant's records to update/create (a documented and expected usage pattern per `docs/usage/webhooks.md`) can be tricked into writing attacker-controlled data into another shop's records, or into triggering shop-scoped side effects (e.g. billing, inventory sync, order creation) under the wrong tenant identifier. This matches the "cross-tenant access" criterion for a Critical-severity finding.

### Likelihood Explanation
Likelihood is high for any app that has at least one other (even low-trust) merchant installation, since:
- Obtaining a validly HMAC-signed webhook body only requires operating your own store with the app installed — no secret key, TLS interception, or privileged account needed.
- The `shop-domain` header is fully attacker-controlled in the replayed request; the gem performs no cross-check between it and the HMAC-covered bytes.
- The vulnerable code path (`Registry.process` → `HmacValidator.validate` → handler dispatch) is the sole, documented way this gem authenticates inbound webhooks, so every app that follows the gem's documented usage is exposed.

### Recommendation
Include the shop-identifying header (or better, the value returned by Shopify's `X-Shopify-Shop-Domain` combined with body-embedded shop identifiers where available) in the HMAC-signed material, or independently verify that the header-derived shop actually owns the webhook subscription (e.g., cross-reference `webhook_id`/shop pairing via a lookup that was itself established through an authenticated channel) before constructing `WebhookMetadata`. At minimum, update `VerifiableQuery`/`Request#to_signable_string` so the signable string is bound to the specific shop header value, and update `HmacValidator` accordingly so a body signed for shop A cannot be replayed while claiming to be shop B.

### Proof of Concept
1. Attacker registers/installs the target app on their own store `attacker-shop.myshopify.com` and enables a webhook topic (e.g., `orders/create`).
2. Shopify sends a legitimately signed webhook to the app: body `B`, header `x-shopify-hmac-sha256: HMAC(secret, B)`, header `x-shopify-shop-domain: attacker-shop.myshopify.com`.
3. Attacker intercepts/replays this exact request to the app's webhook endpoint but changes only the `x-shopify-shop-domain` header to `victim-shop.myshopify.com` (body and HMAC header untouched).
4. `ShopifyAPI::Webhooks::Request.new` parses the forged header successfully; `Utils::HmacValidator.validate` recomputes the HMAC over `B` only, which still matches, so validation passes: [4](#0-3) 
5. `Registry.process` calls `handler.handle(data: WebhookMetadata.new(... shop: "victim-shop.myshopify.com" ...))`, and the app processes attacker-controlled body `B` as data belonging to `victim-shop.myshopify.com`.

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

**File:** docs/usage/webhooks.md (L12-30)
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
    end
  end
end
```
```
