## Finding

### Title
Webhook HMAC does not cover the `shop` (or `topic`/`webhook_id`) header, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` signs only the raw body for HMAC verification, while the shop domain that the gem hands to the app's webhook handler as the trusted tenant identifier comes from an unsigned HTTP header. An attacker who owns a legitimate installation of the app can replay a genuine, correctly-signed webhook body while swapping the `x-shopify-shop-domain` header to a victim shop, and `ShopifyAPI::Webhooks::Registry.process` will accept it as valid.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop`, `topic`, and `webhook_id` are read directly from HTTP headers and are never part of the signed content: [2](#0-1) 

`Utils::HmacValidator.validate` only checks `verifiable_query.to_signable_string` against the HMAC, so it never validates the headers: [3](#0-2) 

`Webhooks::Registry.process` calls this validator and then hands `request.shop` straight to the handler as the authenticated tenant identity, with no additional binding check: [4](#0-3) 

The documented usage pattern explicitly instructs apps to key business logic off `data.shop`: [5](#0-4) 

This breaks the intended identity binding: `shop the HMAC authenticates == shop the app acts upon`. In reality the HMAC authenticates only the byte content of `@raw_body`; the `shop` field the app is told to trust is attacker-controllable header data, not covered by the signature.

### Impact Explanation
Any party that can obtain one genuinely-signed webhook (e.g., by installing the app on their own store and triggering an event such as `orders/create`) can capture the `(raw_body, hmac)` pair from Shopify. Because the signature does not bind to `shop`, that exact pair remains valid when replayed at the app's public webhook endpoint with `x-shopify-shop-domain` (or `shopify-shop-domain`) rewritten to any other merchant's domain, and with `x-shopify-topic`/`webhook_id` altered too. `Registry.process` will pass HMAC validation and invoke the app's handler with `WebhookMetadata.shop` set to the victim shop while `body` is attacker-supplied content. Since apps are documented to use `data.shop` as the tenant key for storage, job dispatch, or Admin API lookups, this allows an unauthenticated attacker to inject fabricated events attributed to a shop they do not control — a cross-tenant data integrity/confusion issue.

### Likelihood Explanation
Any developer/attacker can install a public app on a shop they control (a normal, unprivileged action) and capture one legitimate webhook delivery for that shop. No secrets are needed; only replay/header-tampering of a message the attacker already legitimately possesses. This makes the attack straightforward to mount against any app using this gem's documented webhook processing flow.

### Recommendation
Bind the header-derived identity to the signed payload, e.g., include `shop`, `topic`, and `webhook_id` in the value that is HMAC-verified (or otherwise cryptographically bind them), or require the receiving app to cross-check `data.shop` against a shop it has an existing session/install record for before trusting webhook content for that shop.

### Proof of Concept
1. Install the app on attacker-controlled shop `attacker.myshopify.com`; trigger `orders/create` so Shopify sends a legitimate webhook: headers include `x-shopify-hmac-sha256: <H>` computed over raw body `B`, and `x-shopify-shop-domain: attacker.myshopify.com`.
2. Capture `(B, H)`.
3. POST to the app's webhook endpoint with body `B`, header `x-shopify-hmac-sha256: H` (unchanged) but `x-shopify-shop-domain: victim.myshopify.com`.
4. `HmacValidator.validate` succeeds because it only checks `B` against `H`; `Registry.process` calls the handler with `WebhookMetadata.new(shop: "victim.myshopify.com", body: <attacker's order data>, ...)`, causing the app to process attacker-controlled content as if it belonged to `victim.myshopify.com`.

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

**File:** lib/shopify_api/webhooks/request.rb (L35-43)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end

      sig { returns(T::Hash[String, T.untyped]) }
      def parsed_body
        JSON.parse(@raw_body)
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
