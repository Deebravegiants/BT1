### Title
Webhook `shop-domain` header is not covered by the HMAC signature, allowing a shop-identity mismatch on replay - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature over the raw body only, while the `shop` (tenant identifier) is read from a separate, unsigned HTTP header. `Registry.process` verifies only that the body matches the HMAC, then hands the unauthenticated `shop` value straight to the app's handler as the trusted tenant identity.

### Finding Description
`Request#to_signable_string` returns `@raw_body` only: [1](#0-0) 

`Request#shop` is derived purely from the `shopify-shop-domain`/`x-shopify-shop-domain` header, independent of the signed content: [2](#0-1) 

`Registry.process` verifies the HMAC via `Utils::HmacValidator.validate(request)`, which internally calls `compute_signature(verifiable_query.to_signable_string, secret)` i.e. HMAC(body) — it never incorporates `request.shop` into the signature check — and then immediately forwards `request.shop` to the handler as the authenticated tenant id: [3](#0-2) [4](#0-3) 

The binding that is broken: `authenticated_bytes == HMAC(secret, raw_body)` is checked, but the identity binding host applications rely on is `authenticated_shop == shop_used_for_tenant_routing`. Since `shop` is not part of `to_signable_string`, an attacker who has captured any one legitimate webhook delivery (raw body + valid `hmac-sha256` header — trivially obtainable by installing the app on the attacker's own shop and triggering an event, since Shopify webhooks are unauthenticated public POSTs to the app's endpoint) can replay that exact `raw_body`/`hmac` pair to the app's webhook endpoint while substituting an arbitrary `shopify-shop-domain` header value. `HmacValidator.validate` will still return `true` (the body/HMAC pair is unchanged and valid), and `Registry.process` will call the handler with `WebhookMetadata#shop` set to the attacker-chosen value, even though the merchant identified by that value never sent this event.

Because `shopify_api` gem's documentation and the `WebhookMetadata#shop` field are the officially recommended way for host apps to determine which shop's data/session to act on (per `docs/usage/webhooks.md`), an app built per this gem's contract will process/attribute this replayed event under the wrong tenant, i.e. cross-tenant confusion originating purely from a gap in this gem's own verification logic (not from the host app ignoring documented behavior — the gem promises "This will verify the request did indeed come from Shopify" but that verification does not cover the shop identity).

### Impact Explanation
This crosses a tenant boundary: an unprivileged internet user (only needing their own installed test shop to obtain one valid raw_body+hmac pair) can cause a host application, following this gem's documented API exactly, to process webhook data under an arbitrary victim shop's identity. Depending on the topic subscribed to (e.g. `customers/data_request`, `orders/create`, `shop/redact`) this can trigger tenant-scoped side effects (data writes, deletion flows, notifications, session-scoped background jobs) keyed to the attacker's chosen shop, rather than the shop that actually sent the data. This matches the "cross-tenant access" Critical impact category, since the shop identity binding that the gem is supposed to authenticate is not actually authenticated.

### Likelihood Explanation
Moderate-to-high: the attacker needs only (1) a development/test Shopify store they control (freely obtainable), (2) the app installed there so they receive one legitimate webhook with a known/predictable body and valid HMAC for a chosen topic, and (3) knowledge of the app's webhook endpoint path (usually documented/predictable, e.g. `/webhooks/orders_create`). No access to `api_secret_key`, tokens, or victim credentials is required — the HMAC check passes because the body is unmodified; only the extraneous `shop-domain` header is swapped.

### Recommendation
Bind the shop identity into the verified payload before trusting it. Options:
- Include `shopify-shop-domain` (and ideally `webhook-id`) in `to_signable_string`, or otherwise verify the header against a value embedded in/derivable from the HMAC-covered body if Shopify's payload includes shop info.
- At minimum, document loudly (and enforce, where possible) that `WebhookMetadata#shop` must not be treated as a verified merchant identity by itself — but preferably fix at the gem level, since the gem is what performs and reports the "verified" HMAC check.
- Cross-check that the resolved shop is a shop the app is actually installed on / has an active webhook subscription/session for before acting on payload data.

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker.myshopify.com` and subscribes/triggers a webhook (e.g. `orders/create`).
2. Attacker's endpoint (or a sniff of their own webhook log) captures the raw POST body `B` and the valid `X-Shopify-Hmac-Sha256: H` header, where `H = Base64(HMAC-SHA256(app_secret, B))`.
3. Attacker sends a new POST to the app's webhook endpoint with the same body `B` and header `H`, but sets `X-Shopify-Shop-Domain: victim.myshopify.com` and any other topic/webhook-id headers desired.
4. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: {...})` is constructed by the host app exactly per the documented pattern: [5](#0-4) 
5. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes `HMAC(app_secret, B)` and compares to `H` — this succeeds since `B` and `H` are unmodified.
6. The handler is invoked with `WebhookMetadata.new(shop: "victim.myshopify.com", body: parsed(B), ...)`, causing the host app to process attacker-controlled data attributed to `victim.myshopify.com`.

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

**File:** docs/usage/webhooks.md (L127-135)
```markdown
```ruby
class WebhookController < ApplicationController
  def webhook
    ShopifyAPI::Webhooks::Registry.process(
      ShopifyAPI::Webhooks::Request.new(raw_body: request.raw_post, headers: request.headers.to_h)
    )
    render json: {success: true}.to_json
  end
end
```
