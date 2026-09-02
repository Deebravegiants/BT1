### Title
Webhook `shop`/`topic` headers are trusted for tenant identification without being covered by the HMAC signature - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw body [1](#0-0) , so `Utils::HmacValidator.validate` in `Webhooks::Registry.process` authenticates nothing but the byte content of the body [2](#0-1) . The `shop`, `topic`, and `webhook_id` values, read straight from attacker-writable HTTP headers [3](#0-2) , are then handed to the app's handler as if they were authenticated tenant identity [4](#0-3) .

### Finding Description
This mirrors the reported bug class: a field that is *acted on* (the `shop`/`topic` used to identify the tenant/event) is not covered by the cryptographic check (the HMAC), while a different, unrelated field (the raw body bytes) is the only thing verified. The broken identity binding is:

`verified(body) == valid` should imply `shop_header == shop_that_produced(body, hmac)` — but it does not, because `hmac = HMAC(secret, body)` is computed by Shopify with the app's single, app-wide `api_secret_key`, independent of shop, topic, or webhook id.

Because the same `api_secret_key` is used to sign webhooks for every shop that has the app installed, any authenticated merchant of the app (an "unprivileged" caller relative to other tenants) can:
1. Trigger a real webhook event on their own store (e.g., an event whose body is predictable/minimal, such as `app/uninstalled`, which typically has an empty or near-empty JSON body `{}`), capturing a valid `(raw_body, hmac)` pair signed by Shopify.
2. Replay that exact `raw_body` and `hmac` to the app's webhook endpoint, but substitute the `X-Shopify-Shop-Domain` and `X-Shopify-Topic` headers to name a *different* victim shop and topic.
3. `Utils::HmacValidator.validate` in `Registry.process` only recomputes the HMAC over `raw_body` [5](#0-4)  and succeeds, because the headers were never part of the signed material.
4. `Registry.process` then dispatches to the handler with `shop: request.shop` set to the forged victim shop and `topic: request.topic` set to the forged topic [2](#0-1) .

This lets an attacker who merely installed the app on their own store forge a webhook that the app's handler will process as though it came from a shop the attacker does not control — a cross-tenant identity binding break entirely within this gem's own verification path (`Request` + `HmacValidator` + `Registry.process`), not dependent on the host app misusing the API.

### Impact Explanation
Depending on the app's webhook handlers (which trust `WebhookMetadata#shop`/`#topic` as authenticated, per the gem's documented contract of "HMAC-validated webhook"), this can drive cross-tenant actions: e.g. forging `app/uninstalled` to trigger cleanup/session-revocation logic for a shop that never uninstalled, or forging other low/no-payload topics to trigger tenant-scoped side effects for a victim shop the attacker does not own. This satisfies the Critical "cross-tenant access" impact category, since the trust boundary broken is the shop-tenant identity that `Registry.process` asserts is authenticated once `HmacValidator.validate` passes.

### Likelihood Explanation
Requires only that the attacker be a legitimate (if malicious) installer of the app on their own shop — no leaked secrets, no privileged account, and no TLS interception is needed. The attacker fully controls the headers of the HTTP POST reaching the app's public webhook endpoint; only the (body, hmac) pair needs to come from a genuine Shopify-signed delivery, which any installer can obtain for their own store. Feasibility is highest for topics with fixed/empty bodies (`{}`), lowering to topics whose body content the attacker doesn't control or need to match anything shop-specific.

### Recommendation
Do not treat `Request#shop` / `Request#topic` / `Request#webhook_id` as authenticated solely because `HmacValidator.validate` passed. Either:
- Bind the shop identity cryptographically, e.g. by cross-checking `request.shop` against the shop associated with the session/credentials the app already trusts (reject if it doesn't match a known, previously-provisioned shop for this specific webhook subscription), or
- Extend `to_signable_string` (or add a secondary check) so header-derived identity used for dispatch is verified against an out-of-band, per-shop expectation before handler dispatch in `Registry.process`.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and triggers a webhook topic with an empty/minimal, predictable body (e.g. `app/uninstalled` → body `{}`), capturing the raw POST including headers `X-Shopify-Hmac-Sha256`, `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`, `X-Shopify-Topic: app/uninstalled`.
2. Attacker resends the identical `raw_body` (`{}`) and identical `X-Shopify-Hmac-Sha256` value to the app's webhook endpoint, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes `HMAC(api_secret_key, "{}")` and matches the supplied HMAC — validation passes [6](#0-5) .
4. The handler is invoked with `WebhookMetadata.new(topic: "app/uninstalled", shop: "victim-shop.myshopify.com", ...)` [4](#0-3) , causing the app to act on behalf of `victim-shop.myshopify.com` despite that shop never sending this webhook.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L16-33)
```ruby
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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
