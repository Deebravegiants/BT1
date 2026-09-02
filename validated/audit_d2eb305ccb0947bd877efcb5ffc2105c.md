Confirmed: `ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , and `HmacValidator.validate` computes the signature over that string only [2](#0-1) . The `shop` (and `topic`, `webhook_id`, `api_version`) values come straight from unauthenticated HTTP headers and are never part of the signed content [3](#0-2) , yet `Registry.process` passes `request.shop` straight into `WebhookMetadata` given to the app's handler as the tenant identifier [4](#0-3) , and documentation explicitly tells developers to use `data.shop` to key merchant-specific work such as enqueuing jobs `shop_domain: data.shop` [5](#0-4) .

### Title
Webhook `shop-domain` header is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw JSON body, so `Utils::HmacValidator.validate` verifies exclusively the body bytes against the app's `api_secret_key`. The `shop-domain`, `topic`, `webhook-id`, and `api-version` values are read directly from HTTP headers and never enter the signed payload. `Registry.process` nonetheless treats `request.shop` as a trusted tenant identifier and forwards it unmodified to the app's `WebhookHandler` via `WebhookMetadata`.

### Finding Description
The identity binding that should hold is: `shop attributed to webhook event == shop whose data actually produced the signed body`. Before the attacker acts, a merchant on shop A receives a legitimately signed webhook: `hmac == HMAC(api_secret_key, body_A)` with header `shop-domain: A`. Because `to_signable_string` only encodes `@raw_body` [1](#0-0) , that same `(body_A, hmac)` pair remains a valid signature no matter what `shop-domain` header accompanies it — the HMAC computation never touches `shop`, `topic`, or `webhook_id` [6](#0-5) .

An attacker who has legitimate access to the app on their own shop (an "unprivileged" tenant with respect to any other merchant's data) receives real, validly-signed webhook deliveries for their own shop. They can resend that exact `raw_body` + `hmac-sha256` header to the app's webhook endpoint while substituting `shop-domain` (and optionally `webhook-id`) with another merchant's shop domain. `Utils::HmacValidator.validate(request)` still returns `true` because it only checks `body` against the secret [7](#0-6) , and `Registry.process` passes the forged `shop` straight through: `handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop, body: request.parsed_body, ...))` [8](#0-7) . After the request, the host application's handler — following the gem's own documented pattern of keying merchant-specific processing off `data.shop` [5](#0-4)  — believes the attacker's body originated from the victim shop and processes/attributes it accordingly.

### Impact Explanation
This breaks the tenant boundary the gem is supposed to enforce for webhook processing (`Registry.process` / `HmacValidator.validate`): a caller can get their own signed content accepted as if it belongs to a different, unrelated shop. Any host application that follows the gem's documented `data.shop` usage (as shown in the gem's own docs) to determine which merchant's records to create/update/delete from webhook payloads is exposed to cross-tenant data confusion/injection driven entirely by data controlled by an unprivileged caller with no need for the victim's credentials or the app's `client_secret`.

### Likelihood Explanation
Likelihood is moderate-to-high in any multi-tenant app: the attacker only needs to be a legitimate installed merchant of the app (i.e., possess at least one real, validly-signed webhook body from their own shop, which every installed merchant naturally receives), then replay that body to the app's public webhook endpoint with an altered `shop-domain` header. No secrets, tokens, or victim cooperation are required — only network access to the app's own webhook route, which is by design internet-reachable.

### Recommendation
Include `shop`, `topic`, and `webhook_id` in the HMAC-signed material (or otherwise cryptographically bind the header-derived identity to the body) inside `ShopifyAPI::Webhooks::Request#to_signable_string`, rather than signing the raw body alone. At minimum, document prominently that `data.shop` from `WebhookMetadata` is unauthenticated and must not be used to resolve merchant-tenant context without additional server-side verification (e.g., cross-checking against a known/registered shop list per `webhook_id`).

### Proof of Concept
1. App installs the gem's webhook processing and registers a handler that keys work off `data.shop`, mirroring the documented example `perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)` [5](#0-4) .
2. Attacker's own shop `attacker.myshopify.com` triggers a real webhook; attacker captures `raw_body` and the `X-Shopify-Hmac-Sha256` header from the legitimate delivery.
3. Attacker POSTs the exact same `raw_body` to the app's webhook endpoint but sets `X-Shopify-Shop-Domain: victim.myshopify.com` (keeping the same HMAC header value).
4. `ShopifyAPI::Webhooks::Request.new` parses headers/body normally; `Utils::HmacValidator.validate` recomputes `HMAC(api_secret_key, raw_body)` — identical to the original — and returns `true` [9](#0-8) .
5. `Registry.process` builds `WebhookMetadata` with `shop: "victim.myshopify.com"` and the attacker's body, invoking the app's handler as though the data came from the victim shop [8](#0-7) .

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

**File:** docs/usage/webhooks.md (L19-30)
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
```
