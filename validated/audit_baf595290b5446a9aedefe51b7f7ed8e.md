## Title
Webhook `shop`, `topic`, and `webhook_id` fields are not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
The gem's webhook verification only authenticates the raw request body via HMAC; the `shop-domain`, `topic`, `api-version`, and `webhook-id` headers that identify *which tenant and event* the payload belongs to are read straight off unauthenticated HTTP headers and passed to the app's handler untouched. An attacker who can obtain one genuinely-signed webhook body (e.g., from their own test shop, which legitimately receives Shopify-signed webhooks for the same app) can replay that body against the victim app's webhook endpoint while forging the `shop-domain`/`topic` headers to point at a different, victim shop. `HmacValidator.validate` will accept it because it never examines those headers.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw body: [1](#0-0) 

Meanwhile `shop`, `topic`, `api_version`, and `webhook_id` are read verbatim from client-controlled headers with no cryptographic binding to the signed content: [2](#0-1) 

`HmacValidator.validate` computes/compares the signature only over `to_signable_string` (the raw body), so it never verifies that the `shop-domain`/`topic` headers correspond to the body that was actually signed by Shopify: [3](#0-2) 

`Registry.process` performs exactly this check-then-trust pattern: it validates the HMAC of the body, then immediately hands the *unauthenticated* `request.shop`/`request.topic` to the app's webhook handler as if they were verified: [4](#0-3) 

This breaks the intended identity binding:
`HMAC(shared_secret, raw_body)` should authenticate `(shop, topic, raw_body)` as a unit, but it actually only proves `raw_body` was signed by *some* legitimate Shopify webhook to *this app* (any installed shop) — not that it was signed *for the shop or topic claimed in the headers*.

Concretely: `shop == request.shop` (trusted downstream by the handler) is not equal to `shop-that-actually-produced-this-signed-body` (the only fact the HMAC check proves). An attacker who operates or compromises one shop that has installed the app can capture a validly-signed webhook body (raw_body + valid `x-shopify-hmac-sha256`) from their own shop, then resend it to the victim app's webhook endpoint with the `x-shopify-shop-domain` header rewritten to a different, target merchant's domain (and/or `x-shopify-topic` rewritten to an arbitrary registered topic whose handler happens to accept that body shape, e.g. reusing an `orders/create` body against an `app/uninstalled` handler is not possible since topic changes body semantics, but same-topic cross-tenant replay is fully viable). The signature still validates because it is body-only.

### Impact Explanation
This crosses a tenant boundary using only unprivileged internet access to the app's public webhook endpoint (no access token or `client_secret` required) — the attacker only needs one shop that has legitimately installed the target app (a completely unprivileged path any developer can achieve by installing their own test app instance). The forged request causes the host application to process attacker-supplied webhook data under a spoofed `shop` identity, which is squarely the "cross-tenant access" impact class: an app might use the (spoofed) `shop` field to route to per-tenant business logic (e.g., disable/enable features, mark orders, invalidate sessions) for a shop the attacker does not control.

### Likelihood Explanation
Moderate-to-high: exploitation requires the attacker to install the same app on a shop they control (a normal, permission-less action any developer/merchant can take), capture one legitimately-signed webhook, and replay it with modified headers to the app's public HTTPS webhook endpoint. No secrets, tokens, or privileged access are needed beyond installing the target app on an attacker-owned shop.

### Recommendation
Include the identity-relevant headers (`shop-domain`, `topic`, and ideally `webhook-id`/`api-version`) in the HMAC-signed material, or otherwise cryptographically bind them to the payload before trusting them downstream — mirroring how `Auth::Oauth::AuthQuery#to_signable_string` binds `shop` into the OAuth HMAC computation. At minimum, `Registry.process` should not forward `request.shop`/`request.topic` to handlers as trusted values unless they are provably part of the signed content.

### Proof of Concept
1. Install the target app on an attacker-controlled shop `attacker-shop.myshopify.com`; capture a real Shopify-issued webhook, e.g. body `{"id":123}` with headers:
   - `x-shopify-hmac-sha256: <valid signature over the body, computed with the app's client_secret>`
   - `x-shopify-shop-domain: attacker-shop.myshopify.com`
   - `x-shopify-topic: orders/create`
2. Replay the exact same raw body and HMAC header to the victim app's public webhook endpoint, but change:
   - `x-shopify-shop-domain: victim-shop.myshopify.com`
3. Because `HmacValidator.validate` (`lib/shopify_api/utils/hmac_validator.rb:26-31`) only checks the body against the HMAC, the request passes verification.
4. `Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-199`) invokes the registered `orders/create` handler with `shop: "victim-shop.myshopify.com"`, even though the payload was never produced for that shop, causing the app to act on attacker-controlled data under the victim shop's identity.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-23)
```ruby
      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

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
