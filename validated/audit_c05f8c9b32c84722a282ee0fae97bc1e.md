Confirmed: the webhook HMAC only signs the raw body, while the `shop`, `topic`, `api_version`, and `webhook_id` fields consumed by the app are taken from unsigned HTTP headers.I have enough to write the finding.

### Title
Cross-Tenant Webhook Spoofing via Unverified `shop` Header Not Bound to HMAC Signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating the HMAC over the raw request body, while the `shop` (and `topic`, `webhook_id`, `api_version`) values that the app's handler trusts to attribute the event to a specific merchant are read from unauthenticated, unsigned HTTP headers.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , and `Registry.process` validates the webhook exclusively via `Utils::HmacValidator.validate(request)` against that signable string before dispatching to the handler [2](#0-1) . `HmacValidator.validate` computes `OpenSSL::HMAC.hexdigest` over `to_signable_string` (i.e. the body only) using the app's single, shop-independent `Context.api_secret_key` [3](#0-2) . However, the `shop`, `topic`, `webhook_id`, and `api_version` values are pulled straight from HTTP headers (`x-shopify-shop-domain`, etc.) that are never included in the signed bytes: `shop` is defined as `shopify_header("shop-domain")` [4](#0-3) . `Registry.process` then forwards `request.shop` unchanged into `WebhookMetadata` passed to the app-supplied handler [5](#0-4) , and the documented handler pattern uses `data.shop` directly as the tenant key (e.g. `perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)`) [6](#0-5) .

The broken identity binding is:
`bytes cryptographically verified (raw_body only)` ≠ `bytes used to determine the tenant (shop header, unauthenticated)`

Because Shopify signs webhooks with the **app's single client secret**, not a per-shop secret, the HMAC over the body is identical in structure regardless of which shop sent it. This means any entity that can obtain one genuine, validly-signed webhook body+HMAC pair for *any* shop that has installed the app (e.g., by installing the app themselves on a shop they control, or a legitimate merchant simply forwarding/replaying webhook traffic they received) can replay that exact `raw_body`+`hmac-sha256` header pair to the app's webhook endpoint while substituting an arbitrary victim's `X-Shopify-Shop-Domain` header. `HmacValidator.validate` will still succeed because it only checks the raw body against the shared secret, and `Registry.process` will hand the handler a `WebhookMetadata` claiming the payload originated from the victim shop.

### Impact Explanation
This breaks the tenant-authentication boundary the gem is supposed to provide via webhook HMAC verification: an attacker (an unprivileged internet user who merely needs to be able to install the target app on any store, which is normal for public apps) can inject events attributed to an arbitrary victim shop into the app's processing pipeline. Depending on how the host app's handler consumes `data.shop` (as most documented handlers do — using it as the tenant/session key to look up or mutate per-shop state), this enables cross-tenant data corruption/injection: fake order/customer/GDPR events, poisoning of a victim shop's cached state, or bypass of shop-scoped authorization logic keyed off the webhook's claimed shop. This matches the Critical "cross-tenant access" impact category.

### Likelihood Explanation
Likelihood is high for any app relying on this gem's webhook processing exactly as documented: the attacker needs no special privileges beyond installing the app once on a shop they control (the normal, unprivileged flow for any public Shopify app) to harvest a valid `raw_body`/`hmac-sha256` pair, and then simply replays that body with a forged `X-Shopify-Shop-Domain` header to the app's public webhook endpoint. No access token, `client_secret`, or leaked credential is required — the entire class of protection (`HmacValidator.validate`) is bypassed by design because it was never binding the header-derived shop identity in the first place.

### Recommendation
Include the tenant-identifying fields (at minimum `shop`, and ideally `topic`/`webhook_id`) in the HMAC-covered signable string, or independently authenticate the `X-Shopify-Shop-Domain` header against a value bound to the raw body (e.g., verify the shop is a known/pre-registered installed shop and cross-check webhook delivery metadata via the Admin API `webhook_id` lookup) before constructing `WebhookMetadata`. At minimum, the documentation should explicitly warn implementers that `data.shop` is unauthenticated and must not be trusted as a tenant key without additional verification.

### Proof of Concept
1. Attacker installs the target public app on `attacker-shop.myshopify.com` (normal unprivileged flow) and registers a webhook, e.g. `orders/create`.
2. Shopify delivers a genuine webhook to the app's endpoint with body `B` and header `X-Shopify-Hmac-Sha256: H`, where `H = HMAC-SHA256(api_secret_key, B)` — computed with the app-wide secret, not a per-shop key.
3. Attacker captures `B` and `H` (e.g., via a proxy on their own server, or by using their own store to trigger a webhook).
4. Attacker crafts a request to the same webhook endpoint with:
   - Body: `B` (unchanged)
   - Header `X-Shopify-Hmac-Sha256`: `H` (unchanged)
   - Header `X-Shopify-Shop-Domain`: `victim-shop.myshopify.com` (forged)
   - Header `X-Shopify-Topic`/`X-Shopify-Webhook-Id`: unchanged/forged as needed
5. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes `HMAC-SHA256(api_secret_key, B)` and compares it to `H` — this succeeds because the signature never depended on `shop` [7](#0-6) .
6. `Registry.process` invokes the handler with `WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: parsed_body, ...)` [5](#0-4) , causing the app to process/attribute attacker-controlled webhook content as if it came from the victim shop.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery).returns(T::Boolean) }
        def validate(verifiable_query)
          return false unless verifiable_query.hmac

          result = validate_signature(verifiable_query, Context.api_secret_key)
          if result || Context.old_api_secret_key.nil? || T.must(Context.old_api_secret_key).empty?
            result
          else
            validate_signature(verifiable_query, T.must(Context.old_api_secret_key))
          end
        end

        private

        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

**File:** docs/usage/webhooks.md (L24-27)
```markdown
    def handle(data:)
      puts "Received webhook! topic: #{data.topic} shop: #{data.shop} body: #{data.body} webhook_id: #{data.webhook_id} api_version: #{data.api_version}"
      perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)
    end
```
