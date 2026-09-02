### Title
Webhook HMAC Validation Covers Only the Request Body, Not the `shop-domain` Header — Allows Cross-Tenant Webhook Spoofing (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating an HMAC over the raw request body, then dispatches the handler using the shop identity taken from an HTTP header that is *not* covered by that HMAC. An attacker who legitimately receives one authentic webhook for their own shop can keep the body and its valid HMAC unchanged, but swap the `shop-domain` header to a victim shop, causing the app to process attacker-controlled webhook data under a victim tenant's identity.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw body: [1](#0-0) 

The `shop` (and `topic`) values used to identify the tenant are pulled from separate, unsigned HTTP headers: [2](#0-1) [3](#0-2) 

`Utils::HmacValidator.validate` computes the signature over `verifiable_query.to_signable_string` (i.e., the body only) and compares it against the `hmac-sha256` header: [4](#0-3) 

`Registry.process` treats a passing HMAC check as full authentication of the request, then immediately forwards `request.shop` (the unsigned header) to the handler as the tenant identity: [5](#0-4) 

The identity binding the app relies on is:
`shop authenticated by HMAC == shop the webhook payload is attributed to`

But the HMAC only binds `body ⇄ signature`; it says nothing about `shop-domain header ⇄ signature`. Concretely:
1. Attacker's own store triggers a legitimate webhook. Shopify computes `hmac = HMAC-SHA256(secret, raw_body)` and sends headers including `x-shopify-shop-domain: attacker-shop.myshopify.com`.
2. Attacker captures this request, changes only `x-shopify-shop-domain` to `victim-shop.myshopify.com` (and optionally the topic), keeping `raw_body` and `x-shopify-hmac-sha256` unchanged.
3. Replays it to the app's webhook endpoint.
4. `HmacValidator.validate` recomputes the HMAC over the identical `raw_body` — it still matches, so validation passes.
5. `Registry.process` calls `handler.handle(data: WebhookMetadata.new(topic:, shop: request.shop, ...))` with `shop == "victim-shop.myshopify.com"`, even though that shop never sent or authorized this data.

Any handler that uses `shop` from `WebhookMetadata` to look up/update per-tenant records (the documented and expected usage pattern) will process attacker-supplied data as if it originated from the victim tenant.

### Impact Explanation
This breaks the tenant/shop identity boundary that the HMAC check is meant to enforce: an attacker who legitimately controls one installed shop can forge webhook events attributed to any other shop, injecting fabricated data (e.g., fake `orders/paid`, `app/uninstalled`, or `customers/data_request` payloads) into a different merchant's tenant context. This is a cross-tenant integrity violation reachable by any unprivileged party that can obtain a single genuine webhook delivery for their own store — no access token, `client_secret`, or privileged access is required.

### Likelihood Explanation
Likelihood is high for any app author who follows the library's documented pattern of trusting `WebhookMetadata#shop` to select the tenant record to act on, since `Registry.process` provides no cross-check between the authenticated payload and the claimed shop. The only prerequisite is the attacker owning (or controlling) any single shop that installs the app, which is trivial to obtain since Shopify app installation is open to any developer/store.

### Recommendation
Bind the shop identity into the authenticated material instead of trusting an unsigned header:
- Include the `shop-domain` (and `topic`/`webhook-id`) in the HMAC input (`to_signable_string`) so any tampering invalidates the signature, or
- Independently verify that `request.shop` matches a shop the app has an active, previously-established session/installation for before dispatching to handlers, rather than accepting any value from the unauthenticated header once the body-only HMAC passes.

### Proof of Concept
```ruby
# Attacker owns "attacker-shop.myshopify.com" and receives a real webhook delivery,
# e.g. orders/paid, with body B and header hmac H = HMAC-SHA256(secret, B).

headers = {
  "x-shopify-topic" => "orders/paid",
  "x-shopify-hmac-sha256" => H,                     # unchanged, still valid for body B
  "x-shopify-shop-domain" => "victim-shop.myshopify.com", # swapped from attacker's own domain
}

# Replayed to the merchant app's webhook endpoint with unchanged raw body B:
request = ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: headers)
ShopifyAPI::Webhooks::Registry.process(request)
# => HmacValidator.validate(request) still returns true (HMAC only covers B)
# => handler.handle(data: WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...))
# The app processes attacker-controlled data as belonging to victim-shop.
```

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

**File:** lib/shopify_api/webhooks/request.rb (L67-70)
```ruby
      sig { params(name: String).returns(T.untyped) }
      def shopify_header(name)
        @headers["shopify-#{name}"] || @headers["x-shopify-#{name}"]
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
