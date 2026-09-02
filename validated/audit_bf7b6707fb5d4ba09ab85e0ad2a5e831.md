### Title
Webhook `shop`, `topic`, and `webhook-id` are trusted from unsigned HTTP headers while the HMAC only covers the raw body - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`, so `HmacValidator.validate` authenticates nothing but the JSON body. The `shop`, `topic`, `api_version`, and `webhook_id` values that `Registry.process` hands to the app's `WebhookHandler` are read straight from HTTP headers (`shopify-shop-domain`, `shopify-topic`, etc.) that are never included in the signed material.

### Finding Description
`Request#hmac` is computed from `shopify-hmac-sha256`, and `Request#to_signable_string` is defined as: [1](#0-0) 
i.e. it signs only the raw JSON body. `HmacValidator.validate_signature` compares this signable string's HMAC against the header value: [2](#0-1) 

`Registry.process` treats a passing HMAC check as proof of the entire request's authenticity, then reads `request.shop`, `request.topic`, and `request.webhook_id` — all sourced from headers, none of which are part of the signed bytes — and forwards them unmodified to the app's handler: [3](#0-2) [4](#0-3) 

The binding that should hold is: `shop authenticated by HMAC == shop delivered to WebhookMetadata`. In this implementation that equality is never enforced — the HMAC authenticates `raw_body` only, while `shop` (and `topic`/`webhook_id`) come from headers outside the signed scope. Any two webhooks with byte-identical bodies (which is common — Shopify webhook payloads for the same topic/shop-independent fields, or simply an app receiving the same generic event body across shops) produce the same valid HMAC regardless of which shop or topic header is attached.

Concretely: an attacker who operates their own (unprivileged) development/trial shop can trigger a genuine webhook delivery from Shopify to the app's endpoint, capture the valid `x-shopify-hmac-sha256` value together with the raw body, and then re-POST that exact body with an *arbitrary* `x-shopify-shop-domain` header (and/or `x-shopify-topic`) pointing at a victim shop. `HmacValidator.validate` still passes because it only checks the untouched body against the signature, and `Registry.process` will hand the handler a `WebhookMetadata` claiming the event belongs to the victim shop.

### Impact Explanation
This breaks the tenant/shop identity binding the app relies on to route webhook data per-merchant. Any app logic that uses `WebhookMetadata#shop` to look up per-shop state, credentials, or trigger shop-scoped side effects (e.g., "look up this shop's session/access token and act on their store", GDPR/mandatory topic handling, billing events, order processing) can be made to act as if the event came from a different, victim shop while the attacker fully controls the (replayed) body content indirectly by choosing which of their own webhook types/bodies to capture. This is a cross-tenant confusion primitive reachable by any internet-accessible party with control of their own trial/dev shop and knowledge of the target app's public webhook URL — no access token, secret, or privileged account required.

### Likelihood Explanation
High reachability: webhook endpoints are public HTTP endpoints designed to receive unauthenticated internet traffic; the only gate is the HMAC. Obtaining one's own valid `(body, hmac)` pair requires only owning a Shopify development store and subscribing the app (or observing) a webhook — this is available to any unprivileged user. Swapping the `shop-domain`/`topic` header requires no cryptographic material at all since those fields sit entirely outside the signed scope.

### Recommendation
Include the shop domain (and ideally topic/webhook-id/api-version) as part of the signed material verified against Shopify's canonical value, or independently verify that the `shop-domain` header corresponds to a shop this app has actually installed/authorized before trusting it in `WebhookMetadata`. At minimum, `to_signable_string` should incorporate all values used for authorization decisions, or `Registry.process` should cross-check `request.shop` against an app-side installed-shops registry before dispatching to handlers.

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker-shop.myshopify.com` and lets Shopify deliver a genuine webhook (e.g. `orders/create`) to the app's endpoint, capturing the raw body `B` and the valid header `x-shopify-hmac-sha256: H` (computed by Shopify using the app's real `client_secret`).
2. Attacker replays a POST to the same webhook endpoint with:
   - body = `B` (byte-identical)
   - `x-shopify-hmac-sha256: H` (unchanged, still valid because only body is signed)
   - `x-shopify-shop-domain: victim-shop.myshopify.com` (or `x-shopify-topic` changed to a different registered topic)
3. `Utils::HmacValidator.validate(request)` in [5](#0-4) 
returns `true` since `to_signable_string` only checks `B`.
4. `Registry.process` invokes the app's handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...)`, causing the app to process attacker-supplied data under the victim's shop identity.

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
