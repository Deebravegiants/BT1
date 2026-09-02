### Title
Webhook `topic` and `shop-domain` are trusted from unauthenticated headers while the HMAC only covers the raw body, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, so the HMAC verification performed by `HmacValidator.validate` never binds the `shop`, `topic`, `webhook-id`, or `api-version` header values to the signature. `Registry.process` nonetheless treats these header-derived values as authoritative when constructing `WebhookMetadata` and dispatching it to the app's handler, breaking the identity binding `hmac-signed content == data acted upon`.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` is defined as: [1](#0-0) 

Meanwhile `shop`, `topic`, `webhook_id`, and `api_version` are all pulled straight from request headers with no cryptographic binding to the body: [2](#0-1) 

`HmacValidator.validate` computes the HMAC purely over `to_signable_string` (the body) and compares it to the `hmac` header: [3](#0-2) 

`Registry.process` validates only this body HMAC and then constructs `WebhookMetadata` directly from the unauthenticated `request.topic` and `request.shop` header values, dispatching it to the app-registered handler as if fully verified: [4](#0-3) [5](#0-4) 

The `api_secret_key` used to compute this HMAC is the app's single global client secret — it is identical for every shop that installs the app, not a per-shop secret. Consequently, any merchant who installs the app on their own (attacker-owned) shop receives Shopify webhooks whose body is HMAC-signed with the very same secret used for every other tenant. Because the signature covers only the body and not the `shop-domain`/`topic` headers, that attacker-controlled (body, hmac) pair remains valid even when replayed to the app's public webhook endpoint with the `shopify-shop-domain` and/or `shopify-topic` headers rewritten to name an arbitrary victim shop/topic.

### Impact Explanation
`Registry.process` forwards the forged `shop` (and `topic`) directly into `WebhookMetadata`, which downstream app handlers use to determine which merchant's records to update, e.g., mandatory compliance topics (`app/uninstalled`, `shop/redact`, `customers/redact`) or ordinary business webhooks. An attacker who legitimately installs the app on their own shop can trigger a webhook there, capture the valid `(raw_body, hmac)` pair, then submit an HTTP request straight to the app's webhook endpoint with the victim's `shop-domain` (and any registered `topic`) substituted in the headers. Because nothing in this gem binds `shop`/`topic` to the signed content, `Utils::HmacValidator.validate` accepts it, and the handler is invoked believing the attacker-supplied body legitimately originates from and pertains to the victim shop. This is a cross-tenant confusion: data/action intended for shop A can be attributed to shop B, letting an unprivileged attacker inject spoofed events (including uninstall/redact-style events) against a tenant they do not control.

### Likelihood Explanation
Exploitation requires no leaked credentials, no access token, and no interception — only that the attacker be a legitimate (if unprivileged) merchant able to install the target app on any shop they control, then replay one of their own valid webhook deliveries with forged headers directly against the app's public HTTP webhook endpoint. This is fully reachable through the gem's own `Webhooks::Request`/`Registry` code path, which is the officially documented way apps process webhooks with this SDK.

### Recommendation
Include the security-relevant header values (`shop-domain`, `topic`, `webhook-id`, `api-version`) in the HMAC signable string (or otherwise cryptographically bind them to the body), so `HmacValidator.validate` fails if any of these fields are altered relative to what Shopify actually signed. At minimum, `Registry.process` should not treat header-derived `shop`/`topic` as trustworthy unless they are covered by the same signature that validates the payload.

### Proof of Concept
1. Attacker installs the target Shopify app on `attacker-shop.myshopify.com` and triggers a webhook (e.g. `orders/create`) with a body they fully control (order fields, notes, metafields, etc.).
2. Shopify delivers the webhook to the app's endpoint with headers `x-shopify-shop-domain: attacker-shop.myshopify.com`, `x-shopify-topic: orders/create`, and `x-shopify-hmac-sha256: <hmac of body with the app's global api_secret_key>`.
3. Attacker captures `raw_body` and the valid `hmac` value.
4. Attacker sends a new HTTP POST directly to the app's public webhook endpoint with the identical `raw_body` and `hmac`, but sets `x-shopify-shop-domain: victim-shop.myshopify.com` (and optionally a different registered `x-shopify-topic`).
5. `ShopifyAPI::Webhooks::Request.new` parses these headers; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only hashes `raw_body` — unaffected by the header substitution: [1](#0-0) 
6. `Registry.process` invokes the app's handler with `WebhookMetadata(shop: "victim-shop.myshopify.com", topic: ..., body: <attacker-controlled body>)`, causing the app to process attacker data as if it belonged to the victim shop: [4](#0-3)

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

**File:** lib/shopify_api/webhooks/registry.rb (L188-199)
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
