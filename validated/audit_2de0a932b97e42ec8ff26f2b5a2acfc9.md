### Title
Webhook shop-domain identity is not bound to the HMAC, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signable string from the raw body only, while the `shop` (and `topic`, `webhook_id`, `api_version`) values used by the registry/handler are taken from separate, unsigned HTTP headers. Any party who can obtain one valid `(raw_body, hmac)` pair signed with the app's shared `client_secret` (e.g. the operator of any shop that has installed the app, receiving their own legitimate webhook) can replay that exact body/HMAC pair while substituting the `x-shopify-shop-domain` header for a different, victim shop that also uses the same app. `HmacValidator.validate` will still pass because it only checks `to_signable_string` (the raw body), so the handler will process attacker-controlled data attributed to the victim shop's identity.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop`, `#topic`, `#webhook_id`, and `#api_version` are all read directly from headers that are not part of the signed content: [2](#0-1) 

`Registry.process` validates the HMAC via `Utils::HmacValidator.validate(request)`, which internally calls `validate_signature`, comparing the computed HMAC of `to_signable_string` (i.e. the body only) against the supplied `hmac` header — the `shop` header is never covered: [3](#0-2) [4](#0-3) 

Once the HMAC check passes, `Registry.process` passes `request.shop` straight into `WebhookMetadata` and into the app's handler, unchecked against any registry of shops known to have installed the app: [5](#0-4) 

The binding that should hold is:
`shop_the_HMAC_was_computed_for == shop_the_handler_acts_on`

But in this implementation:
`signable_string = raw_body` (shop-independent) while `handler acts on request.shop` (header-controlled, unsigned)

Because Shopify signs webhooks with the single `client_secret` shared across all shops that install a given app (not a per-shop secret), a valid `(body, hmac)` pair generated for shop A's webhook remains a valid signature regardless of which `shop-domain` header accompanies it. An attacker who legitimately operates (or has installed the app on) shop A can capture a real webhook delivery for shop A and resend the identical body+HMAC to the app's webhook endpoint with the `x-shopify-shop-domain` header rewritten to shop B (a different tenant of the same app), and the request will still pass `HmacValidator.validate`.

### Impact Explanation
This breaks the tenant identity binding relied on by any downstream handler that trusts `data.shop` after `Registry.process` succeeds (as documented and exemplified in `docs/usage/webhooks.md`, where handlers use `data.shop` to key storage/queue operations). An attacker with a legitimate installation of the app on their own shop can inject arbitrary attacker-chosen webhook bodies (topic-appropriate JSON) that the host application will process as if they originated from a victim shop, since the identity check performed by this gem (`HmacValidator.validate`) provides no assurance about the shop field. This is a cross-tenant data-integrity/confusion issue — the impact bucket is cross-tenant access, since data belonging to one tenant's context can be forged for another tenant's identity through this gem's webhook verification.

### Likelihood Explanation
Likelihood is moderate: exploitation requires the attacker to have at least one installation of the target app (a normal, low-privilege state achievable by any merchant/developer who installs a public or unlisted Shopify app), from which they can capture one valid signed webhook and replay it with a modified shop header against the same publicly reachable webhook endpoint. No access token, `client_secret`, or other privileged credential is required — only observation of traffic the attacker's own tenant legitimately receives.

### Recommendation
Bind the shop identity into the verified signable content, or otherwise validate `request.shop` independently before trusting it:
- Where possible, verify that the `shop` in the webhook request corresponds to a shop for which the app holds an active session/access token (i.e., cross-check against the app's own installed-shop store) before invoking the handler.
- Consider including the shop-domain header (or another value cryptographically bound per-shop) in the material verified by `HmacValidator`, or require the host application to perform this cross-check, and document this requirement prominently since `Request#to_signable_string` currently only covers the body.

### Proof of Concept
1. App merchant "Attacker" installs the target Shopify app on `attacker-shop.myshopify.com` and triggers an event (e.g., `orders/create`) that causes Shopify to send a legitimate webhook to the app's endpoint with headers:
   - `x-shopify-shop-domain: attacker-shop.myshopify.com`
   - `x-shopify-hmac-sha256: <valid HMAC of raw_body computed with the app's shared client_secret>`
   - raw body: `{"id": 1, ...}`
2. Attacker captures this exact `(raw_body, hmac)` pair.
3. Attacker resends an HTTP POST to the same webhook endpoint, keeping `raw_body` and `x-shopify-hmac-sha256` identical, but sets:
   - `x-shopify-shop-domain: victim-shop.myshopify.com`
4. `ShopifyAPI::Webhooks::Request.new(raw_body:, headers:)` builds a request object where `to_signable_string` still equals the original `raw_body`.
5. `ShopifyAPI::Webhooks::Registry.process(request)` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC of `raw_body` with `Context.api_secret_key` and compares it to the (still-valid) `hmac` header — validation succeeds.
6. The registered handler is invoked with `WebhookMetadata.new(topic:, shop: "victim-shop.myshopify.com", body: <attacker-controlled JSON>, ...)`, causing the host application to process attacker-supplied data under the victim shop's identity. [6](#0-5)

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
