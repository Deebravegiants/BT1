## Title
Webhook HMAC Validation Does Not Bind `shop-domain`/`topic` Headers, Enabling Cross-Tenant Webhook Spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable content from the raw body only, while `topic`, `shop`, `api_version`, and `webhook_id` are read straight from unauthenticated HTTP headers. `Webhooks::Registry.process` validates the HMAC over the body and then uses those unauthenticated header values to route the event and to identify which tenant (shop) the data belongs to, without any cryptographic link between the signed body and the header-derived shop/topic.

### Finding Description
`Utils::HmacValidator.validate` verifies that `computed_signature == verifiable_query.hmac`, where the signable content comes from `verifiable_query.to_signable_string`: [1](#0-0) 

For webhooks, `to_signable_string` returns only `@raw_body`; `shop`, `topic`, `api_version`, and `webhook_id` are pulled from headers that are never part of the signed content: [2](#0-1) 

`Registry.process` validates only that HMAC, then dispatches based on the unauthenticated `topic` header and forwards the unauthenticated `shop` header as the tenant identifier to the app's handler: [3](#0-2) 

The identity binding that should hold is: `shop header used to attribute data == shop that actually produced/owns the signed body`. Because the HMAC only covers `raw_body`, this equality is never checked — the gem authenticates *that a body was signed by the app's secret*, but not *which shop or topic it was signed for*.

### Impact Explanation
Because Shopify apps share a single `api_secret_key` across every installed shop, any HMAC-valid `(raw_body, hmac)` pair obtained from a real webhook delivery to one tenant remains cryptographically valid when replayed to the shared webhook endpoint with a forged `shopify-shop-domain` and/or `shopify-topic` header. This lets a merchant who has installed the app on their own store (an unprivileged, non-credentialed actor with respect to any other tenant) fabricate events attributed to a **different** shop, or relabel the topic to trigger a different handler than the one that legitimately produced the body (e.g., replaying a benign event's signed body but forging the `app/uninstalled` or `shop/redact` topic to trigger deauthorization/data-deletion logic against a victim tenant). This is a cross-tenant integrity/authentication issue in the identity binding the HMAC is expected to enforce.

### Likelihood Explanation
Exploitation requires only: (1) installing the app once as a normal merchant to obtain at least one genuinely HMAC-signed webhook body, and (2) POSTing that body with attacker-chosen `shop`/`topic` headers to the app's public webhook endpoint. No access to `api_secret_key`, access tokens, or any privileged account is needed — this is reachable by any unprivileged internet-facing merchant/attacker who can install the app.

### Recommendation
Bind the routing/tenant-identification headers into the HMAC-verified content (e.g., include `topic`, `shop`, and `webhook_id` in `to_signable_string`, or independently verify them against Shopify's per-webhook signature scheme/mandatory fields), so that the HMAC check enforces the full binding of `(body, topic, shop)` rather than `body` alone.

### Proof of Concept
1. Install the app on attacker-controlled shop `attacker.myshopify.com`; trigger any webhook event (e.g. `orders/create`) and capture the delivered `raw_body` and its valid `x-shopify-hmac-sha256` value.
2. Re-POST the exact same `raw_body` and `hmac` header to the app's webhook endpoint, but set `x-shopify-shop-domain: victim.myshopify.com` (and/or `x-shopify-topic: app/uninstalled`).
3. `Utils::HmacValidator.validate(request)` at [4](#0-3)  succeeds because the HMAC only ever covered `raw_body`, which is unchanged.
4. `Registry.process` dispatches the handler for the forged topic and passes `shop: "victim.myshopify.com"` into `WebhookMetadata`, causing the app to process attacker-supplied data as if it originated from and pertains to the victim's tenant.

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

**File:** lib/shopify_api/webhooks/registry.rb (L188-190)
```ruby
        sig { params(request: Request).void }
        def process(request)
          raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)
```
