### Title
Webhook shop-domain header is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature over the raw request body only, while the `shop` attribute the gem hands to the app's webhook handler is taken from an unsigned HTTP header. An attacker who can obtain any single valid `(body, hmac)` pair for a webhook topic with a static/predictable body (e.g. a compliance topic fired against a shop they control) can replay that body/hmac pair to the app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` header for a victim shop. `Registry.process` will accept it as valid and dispatch it to the handler tagged with the victim's `shop`, breaking the binding between "HMAC-verified bytes" and "shop the payload is attributed to."

### Finding Description
`Request#to_signable_string` returns only the raw body: [1](#0-0) 

`Request#shop` (and `topic`, `webhook_id`, `api_version`) are read straight from HTTP headers that are never included in the signable string: [2](#0-1) 

`Registry.process` validates only `Utils::HmacValidator.validate(request)` — i.e. only the body — and then trusts `request.shop` (the header) to build the `WebhookMetadata` passed to the app's handler: [3](#0-2) 

`HmacValidator.validate` in turn calls `verifiable_query.to_signable_string`, so whatever the `VerifiableQuery` implementation excludes from that string is never covered by the signature: [4](#0-3) 

The broken binding, expressed as an equality that should hold but doesn't:
`shop attributed to the processed webhook (header, unauthenticated)` ≠ `shop bound by the HMAC signature (body only)`.

Any topic whose body doesn't itself carry an HMAC-covered, unforgeable shop identifier (or whose body is static/near-static, such as `app/uninstalled`, `shop/redact`, or other topics with minimal payloads) lets an attacker who legitimately triggers that webhook for their own store capture a valid `(raw_body, hmac)` pair, then replay it against the app's webhook endpoint with the `shopify-shop-domain` (or `x-shopify-shop-domain`) header changed to a target shop domain. `Utils::HmacValidator.validate` still succeeds because it only recomputes the HMAC over `@raw_body`, and `Registry.process` forwards the attacker-chosen `shop` header value into the handler unchecked.

### Impact Explanation
This is a cross-tenant confusion: the host application's webhook handler is invoked believing the event pertains to shop B while the cryptographically-verified content actually originated from (and was authorized for) shop A. Depending on which topic is abused, this can trigger privileged, tenant-scoped side effects (e.g., data deletion/redaction routines, uninstall/cleanup logic, cache invalidation) against a shop the attacker does not control, using a signature that was never issued for that shop. This matches the Critical "cross-tenant access" impact category, since the gem's own trust boundary — "HMAC-verified request implies the claimed shop is authentic" — is violated by design.

### Likelihood Explanation
Exploitation requires the attacker to have (or create) an app installation on a shop they control so a real webhook fires with a valid HMAC, and requires a topic/body pair that is static or attacker-influenced enough to be replayed against any target shop. This is a realistic scenario for any app owner/tester account, and Shopify's own webhook payloads for several topics are minimal JSON (as reflected in the gem's own tests using `raw_body: "{}"`), making capture-and-replay straightforward once one legitimate delivery is observed.

### Recommendation
Include the shop-domain (and ideally topic/webhook-id) header values in the signable content that is authenticated, or otherwise cryptographically bind the header-derived `shop`/`topic` to the HMAC-verified body before constructing `WebhookMetadata`. At minimum, document that consuming applications must not treat `WebhookMetadata#shop` as trusted without independently reconciling it against shop-identifying content inside the verified body, or reject webhook processing when body content and header-derived shop diverge.

### Proof of Concept
1. Install the app on attacker-controlled shop A and trigger a webhook topic with a minimal/static body (e.g. `app/uninstalled`), capturing the raw HTTP request Shopify sends, including the valid `X-Shopify-Hmac-Sha256` header and body.
2. Replay that exact body and HMAC header to the app's webhook endpoint, but replace `X-Shopify-Shop-Domain` with victim shop B's domain.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC solely over `@raw_body` [1](#0-0)  — it matches, so validation passes.
4. `Registry.process` builds `WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)` using the attacker-supplied `shop` header [5](#0-4)  and invokes the app's handler as if shop B sent the event, despite the signature only ever having been issued for shop A's payload.

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
