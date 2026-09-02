Confirmed root cause: `Registry.process` treats a webhook request as authenticated for a specific shop purely because `HmacValidator.validate(request)` returned true, but that validation only proves the raw body bytes match the app's secret — it never binds `request.shop` (read straight from the `X-Shopify-Shop-Domain` header) to that signature.

### Title
Webhook shop identity is not bound by the HMAC signature, allowing cross-tenant webhook spoofing via header substitution - (File: `lib/shopify_api/webhooks/registry.rb`, `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authorizes a webhook purely on `Utils::HmacValidator.validate(request)` succeeding, then trusts `request.shop` (and `topic`/`webhook_id`) when building `WebhookMetadata` for the host app's handler. But the HMAC in `Request#to_signable_string` is computed only over `@raw_body`; the `shop`, `topic`, `webhook_id`, and `api_version` values are parsed straight from HTTP headers that are never included in the signed bytes.

### Finding Description
`Request#to_signable_string` returns `@raw_body` alone: [1](#0-0) 
while `shop` is read independently from the `shopify-shop-domain`/`x-shopify-shop-domain` header with no cryptographic tie to that body: [2](#0-1) 

`HmacValidator.validate` only recomputes the HMAC over `to_signable_string` (the body) and compares it to the `hmac` header value; it never incorporates `shop`, `topic`, or `webhook_id` into the signed material: [3](#0-2) 

`Registry.process` then gates entirely on that body-only check and forwards the unauthenticated `request.shop` to the app's handler as the trusted tenant identifier: [4](#0-3) 

The binding that should hold is:
`HMAC-verified(bytes) == (body, shop, topic)` bound together

but what is actually verified is:
`HMAC-verified(bytes) == body` only, while `shop`/`topic`/`webhook_id` are parsed out-of-band and asserted as authentic without being part of the verified bytes.

Any party who can obtain a single legitimate `(raw_body, hmac-sha256 header)` pair emitted by Shopify for the app (e.g., by installing the app on their own store and inspecting the webhook delivery they receive, which is normal, unprivileged usage — no `client_secret` or `api_secret_key` is ever needed) can replay that exact body and HMAC header to the app's public webhook endpoint while substituting the `X-Shopify-Shop-Domain` header for any victim shop domain. `HmacValidator.validate` still returns `true` because it only checks the untouched body bytes, so `Registry.process` proceeds and calls the host app's handler with `WebhookMetadata#shop` set to the attacker-chosen victim domain and `WebhookMetadata#body` containing the attacker's own (or arbitrary replayed) payload.

### Impact Explanation
This is a cross-tenant identity-confusion vector: the shop value that host applications use as the tenant/session key for storing webhook-driven state (order updates, GDPR redact events, inventory changes, uninstall events, etc.) is trusted by this gem without any signature binding to the payload it accompanies. An attacker can cause the app to process attacker-controlled webhook data under a victim shop's identity, i.e., cross-tenant access/data injection, which maps to the Critical "cross-tenant access" impact category.

### Likelihood Explanation
Likelihood is High: no secrets, tokens, or privileged access are required — only a single genuine `(body, hmac)` pair obtainable by anyone who installs the app on any store (including a free/dev store) and observes their own webhook deliveries (e.g. via a debug endpoint), plus the ability to send an arbitrary HTTP POST to the app's publicly reachable webhook endpoint with a forged `X-Shopify-Shop-Domain` header. This is exactly the class of "field acted on but not covered by the HMAC" identity-binding failure highlighted by the analog bug class.

### Recommendation
Include the identity-bearing headers (`shop`, `topic`, `webhook_id`, `api_version`) in the signed material verified by `HmacValidator`, or otherwise cryptographically bind `request.shop`/`topic` to the HMAC-verified body (e.g., require the app-side validator to compare `request.shop` against an app-known/allow-listed installed-shop registry before trusting `WebhookMetadata#shop`, and document that host apps must never treat header-derived `shop` as authenticated unless it is independently cross-checked). At minimum, `to_signable_string` should incorporate the header values that `Registry.process` relies on before delegating to `HmacValidator.validate`.

### Proof of Concept
1. Attacker installs the target public Shopify app on their own (attacker-controlled) development store and registers a webhook topic the app subscribes to.
2. Shopify delivers a legitimate webhook POST to the app's endpoint with body `B` and header `X-Shopify-Hmac-Sha256: H` (valid for secret known only to Shopify/app) and `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`.
3. Attacker captures `(B, H)` from their own webhook receiver/logs (no secret needed — this is data delivered to them as the shop owner).
4. Attacker sends a new HTTP POST directly to the same public webhook endpoint URL with body `B`, header `X-Shopify-Hmac-Sha256: H` unchanged, but `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
5. `Utils::HmacValidator.validate(request)` at [5](#0-4)  returns `true` because it only checks `B` against the secret; `Registry.process` at [6](#0-5)  then invokes the host app's handler with `WebhookMetadata#shop == "victim-shop.myshopify.com"` and the attacker's `body`, demonstrating that shop identity is not bound by the HMAC signature.

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
