This confirms the vulnerability. `Request#to_signable_string` returns only `@raw_body` (webhooks/request.rb:35-38), while `Request#shop` reads directly from the unsigned `x-shopify-shop-domain`/`shopify-shop-domain` header (webhooks/request.rb:20-23). `HmacValidator.validate` in `Registry.process` only checks the HMAC over that signable string (the body) (webhooks/registry.rb:189-190), so the tenant-identifying `shop` header is never covered by the signature and is passed straight into `WebhookMetadata.new(shop: request.shop, ...)` for the handler (webhooks/registry.rb:198-199).

### Title
Webhook shop-domain header is excluded from HMAC coverage, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` signs only the raw request body for HMAC verification, while the `shop` (tenant) identifier is read from an HTTP header that is never included in the signed content. Any user who can obtain one valid `(body, hmac)` pair signed by the app's shared `api_secret_key` — e.g. by installing the app on their own store and receiving a legitimate webhook — can replay that exact body/HMAC pair to the app's public webhook endpoint while substituting an arbitrary `x-shopify-shop-domain` header. `Registry.process` validates only the HMAC-over-body and then trusts the spoofed shop value for all downstream handler logic.

### Finding Description
`Request#to_signable_string` returns `@raw_body` only [1](#0-0) , while `Request#shop` is derived from the `shopify-shop-domain`/`x-shopify-shop-domain` header, which is not part of that signable string [2](#0-1) .

`Utils::HmacValidator.validate` computes and compares the HMAC strictly against `verifiable_query.to_signable_string` (i.e., the body) [3](#0-2) . `Registry.process` gates entirely on this check and then forwards `request.shop` — the unauthenticated header value — directly into the handler's `WebhookMetadata` [4](#0-3) .

Because the same app `api_secret_key` is used to sign webhooks for every shop that installs the app, any merchant (an unprivileged actor with respect to other tenants) can install the app on their own store, capture a legitimate `(raw_body, x-shopify-hmac-sha256)` pair delivered to their own endpoint, and then re-POST that identical body/HMAC to the app's webhook endpoint with the `x-shopify-shop-domain` header changed to a victim shop's domain. The HMAC check passes (it only verifies the body, which is unmodified), but the handler now believes the event originated from the victim shop. This breaks the binding: `shop authenticated == shop the handler acts on`.

### Impact Explanation
This is a cross-tenant integrity/authentication violation: an attacker-controlled webhook payload can be attributed to an arbitrary victim shop domain. Depending on how the host application's `WebhookHandler` implementations use `shop`/`WebhookMetadata#shop` (e.g., to look up sessions, write records, trigger side effects, or invalidate/redact data for "customers/redact", "shop/redact"), this allows an unprivileged actor to inject fabricated, attacker-chosen data into another tenant's records — a cross-tenant access impact under the Critical severity bucket.

### Likelihood Explanation
Likelihood is high: the webhook HTTP endpoint is by design internet-reachable and unauthenticated aside from the HMAC header. Any developer/customer who can install the target app on their own store (a normal, unprivileged interaction with a public app) can obtain a valid signed `(body, hmac)` pair for a topic of their choosing and replay it with a forged shop header. No access token, `client_secret`, or privileged account is required — only observation of one's own legitimately received webhook.

### Recommendation
Include the tenant-identifying header (`shop-domain`, and ideally `topic`/`api-version`/`webhook-id`) in the HMAC-signed content, or otherwise cryptographically bind the shop domain to the signature (Shopify's actual delivery already computes the HMAC over the body per shop, so on the verification side the library should also verify that `request.shop` matches an expected/allow-listed shop associated with the session or app installation before dispatching to the handler, rather than trusting the header outright). At minimum, document/require that handler implementations cannot treat `request.shop` as authenticated, and update `to_signable_string` so the shop-domain header cannot be swapped without invalidating the HMAC.

### Proof of Concept
1. Install the target Shopify app on an attacker-owned store `attacker.myshopify.com`; the app registers a webhook (e.g. `customers/create`).
2. Shopify delivers a webhook to the app's endpoint with headers `x-shopify-shop-domain: attacker.myshopify.com`, `x-shopify-hmac-sha256: <hmac>` and some `raw_body`, where `<hmac>` = `HMAC-SHA256(api_secret_key, raw_body)`.
3. Attacker captures `raw_body` and `x-shopify-hmac-sha256` from step 2 (they own this delivery, no secret needed).
4. Attacker crafts a new HTTP POST to the same webhook endpoint with the identical `raw_body` and `x-shopify-hmac-sha256`, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
5. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only validates `raw_body` against the unchanged HMAC [5](#0-4) .
6. The handler executes with `data.shop == "victim-shop.myshopify.com"` even though the body content and event actually originated from the attacker's own store [6](#0-5) .

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
