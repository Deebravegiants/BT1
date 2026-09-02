### Title
Webhook `shop-domain` header is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` treats the `shop` value strictly as an unauthenticated HTTP header, while the HMAC signature that `ShopifyAPI::Webhooks::Registry.process` validates is computed only over the raw request body. Any attacker who can obtain one valid `(body, hmac)` pair for the app — trivially achievable by installing the app on their own store and receiving a legitimate webhook — can replay that exact body/HMAC pair to the app's webhook endpoint while substituting an arbitrary `X-Shopify-Shop-Domain` header. The signature still validates because the shop value is never part of the signed payload, letting the attacker impersonate any other merchant's shop in the resulting `WebhookMetadata`.

### Finding Description
`Registry.process` authenticates a webhook request purely through `Utils::HmacValidator.validate(request)`: [1](#0-0) 

`HmacValidator.validate` computes the HMAC over `verifiable_query.to_signable_string`: [2](#0-1) 

For `Webhooks::Request`, `to_signable_string` returns only the raw HTTP body — the `shop` field is read directly from the `shopify-shop-domain` / `x-shopify-shop-domain` header and is never included in the signed string: [3](#0-2) 

Yet `Registry.process` forwards this unauthenticated `request.shop` value straight into `WebhookMetadata`, which app code uses to identify the tenant the event belongs to: [4](#0-3) 

Because the app's `client_secret` (used to compute the HMAC) is the same across every shop that installs the app, a valid `(body, hmac)` pair generated from the attacker's own store's webhook traffic remains cryptographically valid no matter what shop-domain header is attached to the replayed request. This breaks the intended binding: `shop-domain header == HMAC-authenticated tenant identity`, since the equality actually enforced is only `body == HMAC(body)`, with `shop` left completely outside that guarantee.

### Impact Explanation
This is a cross-tenant identity confusion: an unprivileged attacker (any merchant who installs the app) can forge webhook events that the gem reports as coming from a victim shop of the attacker's choosing. Any host application that trusts `WebhookMetadata#shop` to select which merchant's session/data to act on (a documented and expected usage pattern for this field) can be tricked into processing attacker-controlled webhook bodies under a spoofed shop identity — satisfying the "cross-tenant access" criterion.

### Likelihood Explanation
High. Obtaining one legitimate `(body, hmac)` pair only requires the attacker to install the app on a store they control and observe one webhook delivery (e.g., `app/uninstalled`, `orders/create`). No access token, secret, or privileged account is required; only the ability to send an HTTP POST with attacker-chosen headers to the app's public webhook endpoint.

### Recommendation
Bind the `shop` (and ideally `topic`/`webhook-id`) values into the HMAC-signed payload verification, e.g., by validating them against Shopify's per-shop webhook secret behavior isn't applicable here, so instead the gem should require the caller to supply the expected shop (from an already-authenticated context) and compare it to `request.shop`, or otherwise document/enforce that `request.shop` must never be used as a trust boundary without an out-of-band verification (such as checking against a known, previously-established session for that shop) before it is used for any tenant-identifying decision in `WebhookMetadata`.

### Proof of Concept
1. Install the target app on an attacker-owned store `attacker.myshopify.com` and enable a webhook topic (e.g., `orders/create`).
2. Capture the raw POST body and the `X-Shopify-Hmac-Sha256` header Shopify sends for that webhook.
3. Replay the exact same body and HMAC header to the app's webhook endpoint, but set `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
4. `Utils::HmacValidator.validate` succeeds (it only checks the body against the secret), and `Registry.process` invokes the registered handler with `shop: "victim-shop.myshopify.com"` even though the payload is the attacker's own data — as shown in `Registry.process`'s use of `request.shop`: [5](#0-4)

### Citations

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

**File:** lib/shopify_api/webhooks/request.rb (L20-38)
```ruby
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

      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end
```
