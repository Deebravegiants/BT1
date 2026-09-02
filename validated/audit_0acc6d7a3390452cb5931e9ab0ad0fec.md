### Title
Webhook `shop-domain` header is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` derives the `shop` (and `topic`, `webhook_id`, `api_version`) values directly from unauthenticated HTTP headers, while the HMAC signature that `HmacValidator` verifies is computed over the raw request body only. This breaks the binding: `shop == shop-domain header value` is trusted, but the header is never covered by `HMAC(client_secret, ...)`.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop` is read verbatim from the `shopify-shop-domain`/`x-shopify-shop-domain` header: [2](#0-1) 

`Webhooks::Registry.process` validates the webhook solely via `Utils::HmacValidator.validate(request)`, which calls `validate_signature` comparing `HMAC(secret, to_signable_string)` — i.e., HMAC over the body — against the `hmac` header, and then dispatches the handler using `request.shop` taken from the unauthenticated header: [3](#0-2) [4](#0-3) 

Because the shop-domain header is never included in the signable string, the equality the code implicitly trusts — "the shop whose data the HMAC vouches for" == "`request.shop` header value" — does not hold. A legitimately-signed webhook payload (obtained by an attacker for their own shop, since anyone can install the app on their own development/test store and trigger events such as `orders/create`, `customers/data_request`, etc.) has a valid HMAC that only binds the body content. The attacker can replay that exact `raw_body` + `hmac` pair while substituting an arbitrary `shop-domain` header, and `HmacValidator.validate` will still return `true`, because the shop value never entered the signature computation.

### Impact Explanation
`Registry.process` forwards `request.shop` to the host application's `WebhookHandler` unauthenticated: [5](#0-4) 

Apps built on this gem are documented to treat a processed webhook as authoritative for the named shop (registering/handling webhooks "for a shop"), so a forged `shop-domain` header lets an unprivileged attacker (who only needs their own, legitimately installed instance of the app) inject data or trigger side effects (e.g. GDPR redact/data-request handlers, order/customer processing, cache invalidation, billing state changes) attributed to a victim shop chosen by the attacker — a cross-tenant integrity/confidentiality violation that does not require the victim's access token or any credential leak, only network access to the app's public webhook endpoint.

### Likelihood Explanation
Any developer/attacker can install the target app on a shop they control, capture one legitimately Shopify-signed webhook (body + HMAC) for any topic exposed by the app, and replay it to the app's webhook endpoint with an arbitrary `shopify-shop-domain` header value. No secret material, tokens, or elevated privileges are required — only the ability to send an HTTP POST to the app's own publicly reachable webhook route, which is a standard unauthenticated endpoint by design (protected only by HMAC). This is a low-effort, high-likelihood exploitation path for any app relying on this gem's webhook shop attribution.

### Recommendation
Include the shop domain (and ideally topic/webhook id/api version) as part of the value verified against the HMAC, or otherwise cryptographically bind the shop identity to the signed payload before trusting `request.shop`. At minimum, update `Webhooks::Request#to_signable_string` (or `HmacValidator`) so that the `shop-domain` header cannot be altered independently of the HMAC-covered body, and document that host applications must not treat `request.shop`/`WebhookMetadata#shop` as trusted unless it participates in signature verification.

### Proof of Concept
1. Install the target Shopify app on an attacker-controlled development store; trigger a webhook (e.g., `orders/create`) so Shopify sends a POST with a valid `x-shopify-hmac-sha256` computed over the JSON body using the app's real `client_secret`.
2. Capture the raw request body and the `x-shopify-hmac-sha256` value.
3. Replay the same body and HMAC header to the app's webhook endpoint, but replace `x-shopify-shop-domain` with `victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new(raw_body:, headers:)` builds a `Request` whose `hmac` still matches (`HmacValidator.validate` only checks the body), and `shop` now reports `victim-shop.myshopify.com`.
5. `ShopifyAPI::Webhooks::Registry.process(request)` succeeds and invokes the app's handler with `WebhookMetadata.new(..., shop: "victim-shop.myshopify.com", ...)`, causing the host application to process attacker-supplied data as if it originated from the victim shop.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
