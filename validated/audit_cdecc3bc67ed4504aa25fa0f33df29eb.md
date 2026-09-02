Found a solid analog: the Shopify webhook HMAC signature in this gem covers only the raw request body, not the `shop-domain` (or `topic`/`webhook-id`) header that the registry later treats as the tenant identity of the webhook.### Title
Webhook `topic`/`shop-domain`/`webhook-id`/`api-version` headers are trusted without being covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, so the HMAC verification performed by `Utils::HmacValidator.validate` in `ShopifyAPI::Webhooks::Registry.process` proves only that the *body bytes* were signed with `Context.api_secret_key`. The identity fields the registry actually acts on — `topic`, `shop`, `webhook_id`, `api_version` — come from unauthenticated HTTP headers that are never included in the signed string, so they can be freely rewritten by anyone who can reach the app's public webhook endpoint together with a validly-signed body.

### Finding Description
`Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-200`) does:
```ruby
raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)
handler = @registry[request.topic]&.handler
handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop,
  body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))
```
`Utils::HmacValidator.validate` computes an HMAC-SHA256 over `verifiable_query.to_signable_string` using `Context.api_secret_key` (`lib/shopify_api/utils/hmac_validator.rb:12-31`), and for a webhook `Request` that signable string is defined as just the raw body:
```ruby
sig { override.returns(String) }
def to_signable_string
  @raw_body
end
```
(`lib/shopify_api/webhooks/request.rb:35-38`)

Meanwhile `topic`, `shop`, `webhook_id`, and `api_version` are all read straight from HTTP headers (`lib/shopify_api/webhooks/request.rb:15-33`) with no cryptographic binding to the body or to each other:
```ruby
def shop
  T.cast(shopify_header("shop-domain"), String)
end
```

The equality the code implicitly assumes is:
`HMAC(body, api_secret_key) valid ⇒ (topic, shop, webhook_id) in headers are the ones Shopify actually sent for this body`

but the real guarantee is only:
`HMAC(body, api_secret_key) valid ⇒ body bytes were signed by api_secret_key at some point`

Since `api_secret_key` is the app's single client secret shared across every shop that installs the app, any merchant who installs the app receives legitimate, validly-HMAC-signed webhook deliveries for their own shop. That merchant can capture a `(raw_body, X-Shopify-Hmac-SHA256)` pair from a webhook triggered on their own store (e.g., by creating an order to get a signed `orders/create` payload) and replay that exact body+HMAC to the app's shared webhook endpoint while substituting the `X-Shopify-Shop-Domain` header (and/or `X-Shopify-Topic`, `X-Shopify-Webhook-Id`) with a victim shop's domain. `HmacValidator.validate` still passes because it only checks the body bytes, and `Registry.process` hands the host application a `WebhookMetadata` claiming `shop: <victim-domain>` with attacker-controlled body content.

### Impact Explanation
This is a cross-tenant data injection: the host application's webhook handler (keyed by `data.shop`) will process attacker-supplied event data as if it originated from a different merchant's store. Depending on how the host app uses webhook data (e.g., to sync orders/inventory, trigger fulfillment, or update per-shop state), this lets one merchant forge events attributed to another tenant, corrupting cross-tenant state or triggering unintended actions under another shop's identity — a cross-tenant access violation per the Critical impact bucket (cross-tenant access via a broken identity binding).

### Likelihood Explanation
Exploitation requires only: (1) being a legitimate installer of the target app on at least one shop (an "unprivileged internet user" from the perspective of any other tenant), (2) the ability to trigger and capture one legitimate webhook (a routine, self-service action), and (3) sending a replayed HTTP POST with a modified `shop-domain`/`topic` header to the app's public webhook URL. No access to `api_secret_key`, tokens, or victim credentials is needed — the gem's own HMAC check is bypassed by design because it never covers the header fields the registry trusts.

### Recommendation
Bind the trust-relevant headers into the signed material, or otherwise verify them out-of-band per shop:
- Include `topic`, `shop-domain`, and `webhook-id` in `Webhooks::Request#to_signable_string` (or otherwise authenticate them), so `HmacValidator.validate` fails if any of these headers are altered relative to what Shopify actually signed.
- Alternatively/additionally, cross-check the `shop` extracted from the webhook against a shop the app actually has an active session/registration for before invoking the handler, rather than trusting the header value implicitly.

### Proof of Concept
1. App `X` is installed on shop `attacker.myshopify.com` (attacker-controlled) and shop `victim.myshopify.com`.
2. Attacker triggers an `orders/create` event on their own shop, capturing the exact `raw_body` and `X-Shopify-Hmac-SHA256` value Shopify sent to `X`'s webhook endpoint for that event — this signature is valid because `Context.api_secret_key` is shared by all shops of app `X`.
3. Attacker POSTs the same `raw_body` and same `X-Shopify-Hmac-SHA256` header to `X`'s public webhook endpoint, but sets `X-Shopify-Shop-Domain: victim.myshopify.com` (and optionally forges `X-Shopify-Topic`/`X-Shopify-Webhook-Id`).
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only hashes `@raw_body` (`lib/shopify_api/webhooks/request.rb:36-38`, `lib/shopify_api/utils/hmac_validator.rb:26-31`).
5. `Registry.process` invokes the registered handler with `WebhookMetadata.new(shop: "victim.myshopify.com", body: <attacker's order payload>, ...)` (`lib/shopify_api/webhooks/registry.rb:198-199`), so the host application processes attacker-controlled webhook content as if it belongs to `victim.myshopify.com`. [1](#0-0) [2](#0-1) [3](#0-2)

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-38)
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
