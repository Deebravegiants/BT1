### Title
Webhook `shop-domain`, `topic`, and `webhook_id` headers are trusted for tenant identity but are not covered by the HMAC signature - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` treats a webhook request as authentic for a given shop once `Utils::HmacValidator.validate(request)` succeeds, then forwards `request.shop`, `request.topic`, and `request.webhook_id` to the app's handler as trusted tenant-identifying metadata. However, the HMAC is computed only over the raw request body — none of the `shop-domain`, `topic`, or `webhook-id` HTTP headers are included in the signed bytes. This is the same class of bug as the analog report: a field that is *acted on* (the shop identity used to route/attribute the event) is not the field that is *covered* by the cryptographic check.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

But `shop`, `topic`, `api_version`, and `webhook_id` are all read straight from unauthenticated headers: [2](#0-1) 

`Registry.process` validates the HMAC and then immediately uses those header-derived, unverified fields to build the `WebhookMetadata` passed to the app's handler: [3](#0-2) 

`HmacValidator.validate` only ever signs/verifies `verifiable_query.to_signable_string`, i.e., the body — it has no knowledge of headers at all: [4](#0-3) 

Because Shopify webhook HMACs are computed with the app's `client_secret`, which is identical for every shop that has the app installed, any shop that receives a genuine webhook for itself possesses a `(raw_body, hmac)` pair that will validate successfully regardless of which `shop-domain` header accompanies it. A malicious/curious installer of the app can capture one of their own store's real webhook deliveries and replay it to the app's webhook endpoint with the `x-shopify-shop-domain` header (and/or `x-shopify-topic`, `x-shopify-webhook-id`) rewritten to a victim shop's domain. `Utils::HmacValidator.validate` will still return `true` because it only checks the body bytes, and `Registry.process` will hand the handler a `WebhookMetadata` claiming the event belongs to the victim shop.

This is the precise "field acted on but not covered by the HMAC" identity-binding break called out in the task rules: the equality the code implicitly assumes is `verified(hmac, body) == verified(hmac, body+shop+topic+webhook_id)`, which is false.

### Impact Explanation
Any handler that uses `WebhookMetadata#shop` (the documented, intended way to determine which tenant a webhook belongs to) to look up, mutate, or delete shop-scoped state can be tricked into acting on the wrong tenant's data using an attacker-supplied shop identity, while the message body's authenticity check passes. Depending on which webhook topics an app registers (e.g. `app/uninstalled`, `customers/redact`, `shop/redact`, `orders/*`), this enables cross-tenant data corruption/exfiltration or forged lifecycle events attributed to a shop that never sent them — a cross-tenant boundary break, which maps to the Critical impact category (cross-tenant access).

### Likelihood Explanation
Exploitation only requires an attacker to be an ordinary merchant who has installed the app (a normal, unprivileged capability — no access token, `client_secret`, or leaked credential of a *victim* is needed). They need one genuine webhook delivery for their own shop (trivial to obtain by using the app normally) and the ability to send an HTTP POST with modified headers to the app's public webhook endpoint. No signing key of their own is needed since the HMAC never covers the header they are forging.

### Recommendation
Include the shop domain (and ideally topic/webhook id/api version) in the signable/verified material for webhooks, or otherwise cryptographically bind the header-derived shop identity to the signed payload before it is trusted — e.g., require the caller to separately re-verify `shop` against a known/expected value (such as the shop associated with the app's own webhook registration or a stored per-shop session) instead of accepting the raw `x-shopify-shop-domain` header as ground truth once only the body's HMAC has been checked.

### Proof of Concept
1. App is installed on `victim-shop.myshopify.com` and `attacker-shop.myshopify.com` (both use the same app `client_secret`).
2. Shopify sends a legitimate webhook to the app's endpoint for `attacker-shop.myshopify.com`, e.g. body `{"id":1}` with header `x-shopify-hmac-sha256: <valid-hmac-of-body>` and `x-shopify-shop-domain: attacker-shop.myshopify.com`.
3. Attacker captures this exact `(body, hmac)` pair and replays it to the same endpoint, only changing the header to `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `Utils::HmacValidator.validate` in `lib/shopify_api/utils/hmac_validator.rb` recomputes the HMAC over the unchanged body and it matches, so validation succeeds.
5. `Registry.process` in `lib/shopify_api/webhooks/registry.rb` (lines 188-200) builds `WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)` using the forged `shop` header value and invokes the app's handler as if the event genuinely originated from `victim-shop.myshopify.com`.

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
