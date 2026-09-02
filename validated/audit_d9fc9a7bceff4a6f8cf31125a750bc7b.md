### Title
Webhook shop identity is not covered by the HMAC signature, enabling cross-tenant shop-domain spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` implements `VerifiableQuery#to_signable_string` by returning only `@raw_body`, so `Utils::HmacValidator.validate` proves nothing about the `shop-domain` header. `Webhooks::Registry.process` accepts the request once the body's HMAC checks out, then unconditionally trusts `request.shop` (parsed straight from the unauthenticated header) to route the event to a tenant.

### Finding Description
`Request#to_signable_string` returns only the raw body [1](#0-0) , while `shop` is read verbatim from the `shopify-shop-domain`/`x-shopify-shop-domain` header without any cryptographic binding to the signed content [2](#0-1) . `HmacValidator.validate` only ever calls `verifiable_query.to_signable_string`/`verifiable_query.hmac`, so it validates the body against the app's `client_secret` but never touches the shop header [3](#0-2) . `Registry.process` then gates only on that body-HMAC check and immediately forwards the unauthenticated `request.shop` to the handler as the tenant identity for the event [4](#0-3) .

This is structurally the same bug class as the report: a value that is *acted on* (`shop`, used as the tenant/session key for webhook processing) is not covered by the field that is *cryptographically verified* (the HMAC over the raw body). In the Curve/Convex case, `_fetchRewards` updated `lastUpdate`/`periodFinish` using a timestamp that bypassed the integral update that should have preceded it, silently decoupling "what was verified/accounted for" from "what was actually acted on." Here, the equality that should hold — `shop used for routing == shop bound into the HMAC` — is broken: `shop_acted_on != shop_covered_by_hmac`.

Because Shopify computes webhook HMACs using the app's single shared `client_secret` for every shop that installs the app (not a per-shop secret), any merchant who installs the app can legitimately trigger events in their own store and receive a validly HMAC-signed webhook body from Shopify for their own shop. If that request is replayed to the app's webhook endpoint with the `X-Shopify-Shop-Domain` header rewritten to a different (victim) shop that also uses the same app, `HmacValidator.validate` still returns `true` (the body/HMAC pair is genuinely valid for the shared secret), and `Registry.process` will dispatch the attacker-controlled body to the handler tagged as the victim's shop.

### Impact Explanation
This crosses a tenant boundary: an attacker-controlled webhook body (e.g., fabricated `orders/create`, `app/uninstalled`, `customers/data_request`, etc., generated from the attacker's own store) can be attributed to a different merchant's shop domain purely by changing an HTTP header, since that header is never part of the signed payload. Any host application that uses `WebhookMetadata#shop` to select which merchant/session/database row to write to or act on (the intended, documented use of this field) can be made to apply attacker data under another tenant's identity — this is cross-tenant access/data injection, matching the Critical-impact category (cross-tenant access) called out in scope.

### Likelihood Explanation
Exploitation requires only: (1) the attacker be a legitimate, unprivileged installer of the same app (a normal, low-privilege capability — anyone can install a public Shopify app on their own store), and (2) the ability to replay an HTTP request to the app's public webhook endpoint with a modified header, which requires no secret, no TLS interception, and no elevated access. This is entirely within the "unprivileged internet user" threat model.

### Recommendation
Bind the shop identity into the signed payload before trusting it, mirroring the report's fix of restoring the missing binding before acting on state:
- Do not treat `shop-domain` (or `topic`) as verified merely because the body HMAC passed; if the host application needs a trustworthy shop identifier, it should be cross-checked against a value embedded inside the HMAC-covered body itself (Shopify webhook payloads include the shop's `id`/`domain` in the JSON body for most topics), or the gem should expose a method that only returns `shop` after confirming it matches an authenticated source (e.g., a value recorded from `_updateIntegrals`-equivalent state, such as a previously stored session keyed by shop).
- At minimum, document prominently (and ideally enforce in `Webhooks::Registry.process`) that `request.shop`/`request.topic` header values are unauthenticated relative to the HMAC and must not be used by host applications as an authorization or tenant-selection key without additional verification.

### Proof of Concept
1. App `A` is installed on `shop-attacker.myshopify.com` and `shop-victim.myshopify.com` (both are legitimate, unprivileged app installs — no elevated access needed).
2. Attacker performs an action on their own store that triggers a webhook (e.g., creates an order), and captures the resulting POST request Shopify sends to the app's webhook endpoint, including the valid `X-Shopify-Hmac-Sha256` header computed over the raw body using the app's single shared `client_secret`.
3. Attacker resends the identical raw body and HMAC header to the same endpoint, but replaces `X-Shopify-Shop-Domain: shop-attacker.myshopify.com` with `X-Shopify-Shop-Domain: shop-victim.myshopify.com`.
4. `Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes HMAC over `request.to_signable_string` (the unchanged raw body) and succeeds [5](#0-4) .
5. The handler receives `WebhookMetadata.new(topic: request.topic, shop: request.shop, body: request.parsed_body, ...)` with `shop` equal to `shop-victim.myshopify.com` and `body` containing attacker-controlled data, even though the request never touched the victim's store [6](#0-5) .

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
