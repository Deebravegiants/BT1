### Title
Webhook shop identity is not covered by the HMAC signature, enabling cross‑tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb](lib/shopify_api/webhooks/request.rb))

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant identity (`shop`) from an HTTP header that is never included in the HMAC-signed payload. The signature only covers the raw request body, so any attacker who can obtain one *validly signed* webhook (e.g. by installing the app on their own store and triggering an event) can replay that exact body/HMAC pair while substituting the `shop-domain` header for any other shop. `Registry.process` accepts the request because `HmacValidator.validate` only checks the body against the HMAC, then trusts the unauthenticated `shop` header when building `WebhookMetadata`, which app code uses to key data to a tenant.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

But `shop`, `topic`, `api_version`, and `webhook_id` are all read from HTTP headers that are **not** part of that signable string: [2](#0-1) 

`HmacValidator.validate` computes the signature only over `to_signable_string` (i.e. the raw body) and compares it to the `hmac-sha256` header: [3](#0-2) 

`Registry.process` relies on this validation, then trusts `request.shop` (from the unauthenticated header) to build the `WebhookMetadata` that is handed to the app's business logic: [4](#0-3) 

The identity binding that should hold is: `shop domain verified by HMAC == shop domain the handler acts on`. In reality: the HMAC only binds the body bytes, while the `shop` (and `topic`/`webhook_id`) used by the handler come from a header that is completely outside the signed content. Since the `api_secret_key` used to sign webhooks is shared across every shop that has the app installed, any attacker who installs the app on their own store can capture a real, validly-signed webhook (raw body + `x-shopify-hmac-sha256`) for actions they perform themselves, then resend the identical body/HMAC pair to the app's webhook endpoint with the `x-shopify-shop-domain` header changed to a victim shop's domain. `Utils::HmacValidator.validate(request)` still succeeds because the signature check never looked at the header, and `Registry.process` forwards `shop: request.shop` (now the forged victim domain) to the handler.

### Impact Explanation
This breaks the tenant/identity boundary the HMAC is supposed to guarantee. An attacker-controlled webhook body (from their own store's legitimate events) can be attributed to an arbitrary victim shop domain in the data passed to the app's webhook handler. Per the gem's own documented usage pattern, host applications key persisted data and background jobs off `data.shop`: [5](#0-4) 

This enables cross-tenant data injection/corruption — the classic "trusted field not covered by the authentication tag" bug class — since the app has no way to distinguish a spoofed shop label from an authentic one.

### Likelihood Explanation
Requires only an unprivileged attacker able to install the target app on a store they control (a normal, permission-less action for any Shopify merchant/developer) and the ability to send arbitrary HTTP requests to the app's public webhook endpoint. No access token, `client_secret`, or privileged credentials are needed — only a genuine webhook once received from Shopify for the attacker's own shop.

### Recommendation
Include `shop`, `topic`, and `webhook_id`/`api_version` in the HMAC-signed content (or otherwise cryptographically bind them to the raw body) so that `HmacValidator.validate` fails if any of these headers are altered independently of the body. At minimum, document that host apps must not treat `Request#shop` as trusted/authenticated on its own, or have `Registry.process` derive/cross-check the shop from an authenticated source (e.g., the corresponding session) rather than solely from the unauthenticated header.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com`.
2. Attacker triggers a real event (e.g., `orders/create`) on their own store; Shopify sends a webhook to the app with body `B` and header `x-shopify-hmac-sha256: H` (valid HMAC of `B` with the app's shared `api_secret_key`), plus `x-shopify-shop-domain: attacker-shop.myshopify.com`.
3. Attacker resends the exact same `B` and `H` to the app's webhook endpoint, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `HmacValidator.validate` (only checking `B` vs `H`) succeeds: [6](#0-5) 
5. `request.shop` now returns `victim-shop.myshopify.com`, and the handler receives `WebhookMetadata` claiming this attacker-crafted body originated from the victim shop, exactly as shown in `Registry#process`: [7](#0-6)

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

**File:** docs/usage/webhooks.md (L19-29)
```markdown
```ruby
module WebhookHandler
  extend ShopifyAPI::Webhooks::WebhookHandler

  class << self
    def handle(data:)
      puts "Received webhook! topic: #{data.topic} shop: #{data.shop} body: #{data.body} webhook_id: #{data.webhook_id} api_version: #{data.api_version}"
      perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)
    end
  end
end
```
