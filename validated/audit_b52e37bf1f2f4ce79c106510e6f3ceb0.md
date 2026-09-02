This confirms the vulnerability. The `VerifiableQuery` interface requires `to_signable_string`, and for webhook `Request` objects, that method returns only `@raw_body`, meaning the `shop-domain` header is never included in the HMAC computation.I have sufficient evidence to complete the analysis.### Title
Webhook `shop-domain` header is not covered by the HMAC signature, allowing cross-tenant shop spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
### Finding Description
The bug class in the external report is a broken identity binding: a value the system acts on (`required_validators`) is not covered by the same verification mechanism used to authorize the actor. The same pattern exists in this gem's webhook processing path.

`ShopifyAPI::Webhooks::Registry.process` verifies a webhook request solely via `Utils::HmacValidator.validate(request)`: [1](#0-0) 

`HmacValidator.validate` computes the signature over `verifiable_query.to_signable_string` and compares it to the `hmac` header using a constant-time comparison: [2](#0-1) 

For webhook requests, `to_signable_string` returns **only the raw body** — it does not include any headers: [3](#0-2) 

Yet `Request#shop` is read straight from the unauthenticated `shopify-shop-domain` / `x-shopify-shop-domain` header and is never checked against anything HMAC-covered: [4](#0-3) 

This `shop` value is then passed downstream, unverified, as the tenant identity for the webhook event: [5](#0-4) [6](#0-5) 

The equality that should hold but does not:
`shop authenticated by HMAC` == `shop the handler treats as the event's tenant`.

In reality: `hmac covers raw_body only` ≠ `shop header value used for tenant attribution`. The `hmac-sha256` header only proves that *someone possessing `api_secret_key` produced this exact body* at some point; it proves nothing about which `shop-domain` header should accompany that body.

### Impact Explanation
Because the documented handler pattern uses `data.shop` directly to key downstream persistence/enqueueing logic (as shown in the gem's own webhook docs — `perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)`), an attacker who can obtain any single valid `(raw_body, hmac)` pair for a topic (e.g., because they run their own trial/dev shop installed on the same app, or because a legitimate webhook payload is otherwise observed) can replay that exact body/HMAC pair to the app's webhook endpoint while substituting an arbitrary victim `shop-domain` header. Since HMAC verification never touches this header, `Registry.process` accepts the request as fully valid and dispatches it to the handler tagged with the attacker-chosen shop identity — i.e., cross-tenant event injection. Depending on the app's handler logic (which is standard/documented usage of this gem), this can lead to another merchant's data queue being populated with forged records, or a target shop's records being mutated/read based on attacker-controlled body content under the attacker's chosen `shop`. This satisfies the Critical bar of "cross-tenant access" because the tenant boundary (`shop`) that the app is meant to enforce is not authenticated by the gem despite being exposed as an authenticated field to consumers.

### Likelihood Explanation
Medium-to-High. An attacker needs one valid `(body, hmac)` pair for the target app (trivially obtainable if the attacker runs a free/dev installation of the same app on their own shop, since HMAC uses the single global `api_secret_key`, not a per-shop secret). No access token, TLS interception, or privileged credential is required — this fits the unprivileged-internet-user threat model, since the attacker only needs to send a normal HTTP POST with a forged `x-shopify-shop-domain` header and a body/HMAC pair they legitimately received for their own shop.

### Recommendation
Do not treat the `shop-domain` header as a trusted tenant identifier unless it is itself covered by the signed payload. Options:
1. Include the `shop-domain` header (and other identity headers such as `topic`, `webhook-id`) in `to_signable_string` used for HMAC verification, matching them against the signed content.
2. Alternatively, require/document that consuming apps independently verify `request.shop` corresponds to a shop that has an active, installed session before trusting it, rather than relying on the gem's `HmacValidator.validate` to have authenticated the header.

### Proof of Concept
1. Install the target app on an attacker-controlled shop `attacker.myshopify.com`; trigger any webhook topic the app subscribes to and capture the raw POST body and its `x-shopify-hmac-sha256` value (valid because it was computed with the app's real, shared `api_secret_key`).
2. Replay the exact same raw body and `x-shopify-hmac-sha256` value to the app's webhook endpoint, but set `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `Utils::HmacValidator.validate` at [7](#0-6)  passes because it only re-hashes `raw_body`.
4. `Registry.process` dispatches `WebhookMetadata.new(..., shop: request.shop, ...)` with `shop == "victim-shop.myshopify.com"` to the app's handler, even though that body/HMAC pair was never produced for that shop, causing the app to act on forged data under the victim's tenant identity.

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

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L6-12)
```ruby
    class WebhookMetadata < T::Struct
      const :topic, String
      const :shop, String
      const :body, T::Hash[String, T.untyped]
      const :api_version, String
      const :webhook_id, String
    end
```
