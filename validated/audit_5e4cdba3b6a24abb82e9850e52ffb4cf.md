### Title
Webhook `shop`, `topic`, `webhook-id` and `api-version` fields are accepted from unauthenticated HTTP headers while the HMAC only covers the raw body, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , so `Utils::HmacValidator.validate` only proves that the body was signed with the app's `api_secret_key` [2](#0-1) . However, `Request#shop`, `#topic`, `#webhook_id` and `#api_version` are read straight from HTTP headers that are never part of that signed value [3](#0-2) , and `Registry.process` passes `request.shop` unmodified into the handler after only checking the HMAC over the body [4](#0-3) .

### Finding Description
This is the same bug class as the reported CVE: something is validated (the HMAC over a byte sequence) while a different, unverified value (here, the `shop-domain`/`topic`/`webhook-id`/`api-version` headers) is what the application actually trusts and acts on — an identity binding is broken between "what was verified" and "what was used."

Concretely:
- `Utils::HmacValidator.validate_signature` computes `compute_signature(verifiable_query.to_signable_string, secret)` and compares it to the received HMAC using `OpenSSL.secure_compare` [5](#0-4) .
- For webhooks, `to_signable_string` is defined as `@raw_body` only [1](#0-0) .
- `Registry.process` uses this validation as the sole authenticity check, then immediately builds `WebhookMetadata.new(topic: request.topic, shop: request.shop, ..., webhook_id: request.webhook_id)` from the header-derived accessors, and dispatches it to the registered handler [4](#0-3) .

Because Shopify apps use a single `api_secret_key` for the whole app across all shops that install it (not a per-shop secret), any merchant who has installed the app receives genuine webhooks whose body+HMAC pair is valid under that one shared secret. Such a merchant (an unprivileged actor relative to other tenants of the same app) can capture a legitimate `raw_body`/`x-shopify-hmac-sha256` pair from their own webhook deliveries and replay it to the app's public webhook endpoint with the `x-shopify-shop-domain` (and/or `x-shopify-topic`, `x-shopify-webhook-id`) header rewritten to point at a different, victim shop. `HmacValidator.validate` still returns `true`, because it never inspects those headers — only the body. The handler then executes business logic believing the event legitimately originated from the victim shop.

Equality that should hold but doesn't:
`verified(raw_body) == true` while `shop_used_by_handler == request.shop` is **not** bound by that verification — i.e. `HMAC-authenticity(raw_body) ⇏ authenticity(shop, topic, webhook_id)`.

### Impact Explanation
This crosses a tenant boundary: an app that uses `WebhookMetadata#shop` to select which merchant's data to create/update/delete (a common and expected use documented for this gem) can be made to act on a shop it never actually received an event for, using attacker-supplied body content signed under the app's own legitimately-obtained (but shared) secret. That is cross-tenant access / data confusion, which meets the Critical/High bar in the rubric (cross-tenant access via a broken identity binding), without requiring the attacker to know `api_secret_key`, an access token, or any credential beyond installing the app once as an ordinary merchant.

### Likelihood Explanation
Moderate-to-high: exploitation only requires the attacker to be an app-installing merchant (unprivileged relative to other tenants), capture one legitimate webhook delivery to their own endpoint, and replay it with a modified `shop-domain`/`topic` header to the same publicly reachable webhook URL — no cryptographic secret needs to be known or brute-forced, since the HMAC never covers the header being forged.

### Recommendation
Bind the header-derived identity to the verified content, e.g.:
- Include `shop`, `topic`, and `webhook_id`/`api_version` in the signable string used by `HmacValidator`, or
- Cross-check `request.shop` against an independently trusted source (e.g., the shop associated with the specific webhook subscription/session that the app registered), rejecting the event if it doesn't match, before constructing `WebhookMetadata` and invoking the handler in `Registry.process`.

### Proof of Concept
1. Install the target app on attacker-controlled shop `attacker.myshopify.com`; Shopify delivers a legitimate webhook:
   - Headers: `x-shopify-shop-domain: attacker.myshopify.com`, `x-shopify-topic: orders/create`, `x-shopify-hmac-sha256: <valid HMAC of raw_body>`
   - Body: attacker-controlled order payload (attacker can shape it via their own store activity).
2. Attacker captures `raw_body` and the `x-shopify-hmac-sha256` value.
3. Attacker POSTs the identical `raw_body` and HMAC header to the app's webhook endpoint again, but replaces `x-shopify-shop-domain` with `victim-shop.myshopify.com`.
4. `Utils::HmacValidator.validate` recomputes the HMAC over `raw_body` only [1](#0-0)  and it matches (secret is shared across the app, not per-shop), so `Registry.process` proceeds and calls the handler with `shop: "victim-shop.myshopify.com"` and attacker-controlled `body` [4](#0-3) .

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-33)
```ruby
      sig { returns(String) }
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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-22)
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
