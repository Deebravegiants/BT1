This confirms the vulnerability. `Webhooks::Request#to_signable_string` returns only `@raw_body`, and `hmac` is validated only against that body via `Utils::HmacValidator.validate(request)` in `Registry.process`. The `shop` (and `topic`) fields come solely from unauthenticated headers (`shopify-shop-domain` / `x-shopify-shop-domain`) that are never part of the signed content, yet `Registry.process` passes `request.shop` straight into `WebhookMetadata` for the handler to act on as the tenant identity.

### Title
Webhook shop-domain header is not covered by HMAC verification, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable content from the raw body alone, while the `shop` attribute used to attribute webhook data to a tenant is read from an unauthenticated header. Since the app's `client_secret` (and thus the resulting HMAC) is identical for every shop that installs the app, a legitimately-signed webhook body captured from one shop can be replayed to the app's webhook endpoint with a forged `shop-domain` header pointing at a different, unrelated shop, and it will pass HMAC verification.

### Finding Description
`Request#to_signable_string` only returns `@raw_body`: [1](#0-0) 
while `shop` is read directly from the `shopify-shop-domain`/`x-shopify-shop-domain` header, which is never included in the signed string: [2](#0-1) 

`Registry.process` verifies only this body-derived HMAC, then hands `request.shop` (the unauthenticated header value) straight to the registered handler as the tenant identity: [3](#0-2) 

`HmacValidator.validate` in turn calls `verifiable_query.to_signable_string`, which for `Request` never includes `shop`, so its equality check is: `HMAC(body, client_secret) == received_hmac`, completely independent of the `shop` value: [4](#0-3) 

Because a single app's `client_secret` (the same `Context.api_secret_key`) is used to compute the HMAC for webhooks sent from *every* shop that has installed the app, any party who can observe one valid `(raw_body, hmac)` pair from any shop — e.g., a merchant who installed the app on their own store and captured the webhook their store received, or any actor with visibility into webhook traffic (e.g., a webhook proxy, logging pipeline, or a shared endpoint) — can replay that exact body with a forged `x-shopify-shop-domain` header naming a *different* shop. The signature still validates because the shop is not part of what is signed. The binding broken is: **shop authenticated (header, unauthenticated) ≠ shop covered by the HMAC (body only)**.

### Impact Explanation
This is a cross-tenant data confusion vector: the app will process attacker-controlled/replayed webhook payloads as if they originated from a victim shop, since `WebhookMetadata.shop` is populated from the forged header and the HMAC check cannot detect the mismatch. Depending on the handler's logic (e.g., handlers that write incoming webhook data keyed by `shop`, or that trigger shop-scoped side effects such as data sync, billing changes, or GDPR-topic handling), this allows an unprivileged actor who merely needs one legitimately-signed webhook body (obtainable by installing the app themselves) to inject/attribute that payload to an arbitrary other shop known to use the app. This satisfies the "cross-tenant access" criterion.

### Likelihood Explanation
Any developer using the app has a `client_secret` shared across all installs; a malicious or compromised merchant with the app installed can capture one valid signed webhook (this requires no special privilege — merely installing the app, a normal unprivileged flow) and replay it against the app's public webhook endpoint with a different `shop-domain` header. No access token, secret key, or privileged access is required beyond app-normal usage.

### Recommendation
Bind the `shop` (and `topic`) to the HMAC verification, or otherwise cross-check the header-derived `shop` against an authenticated source. At minimum, `Request#to_signable_string` should incorporate the shop/topic headers into the signed content used for comparison, or the library should document/enforce that the caller must independently ensure `shop-domain` is trusted (e.g., only accept webhooks for shop domains present in the caller's own session store), since currently there is no such binding enforced by the gem itself.

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker.myshopify.com` and receives a legitimate webhook (e.g., `orders/create`) with raw body `B` and header `x-shopify-hmac-sha256: H`, where `H = Base64(HMAC-SHA256(client_secret, B))`.
2. Attacker sends a request to the app's webhook endpoint with the same body `B`, the same `x-shopify-hmac-sha256: H` header, but with `x-shopify-shop-domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes `HMAC(client_secret, B)` and compares to `H` — this succeeds since `B` and `H` are unchanged, per [5](#0-4) .
4. The handler receives `WebhookMetadata` with `shop: "victim.myshopify.com"` despite the payload never having been produced for that shop, per [6](#0-5) .

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
