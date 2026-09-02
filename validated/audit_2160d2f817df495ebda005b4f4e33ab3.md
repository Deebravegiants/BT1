## Analysis

The bug-class hint from the LayerZero report ("a field is used by the application logic but not actually covered by the message's authentication check") maps cleanly onto how `ShopifyAPI::Webhooks::Request` builds its HMAC-signable string. [1](#0-0) 

`to_signable_string` returns only `@raw_body`, so the HMAC (`X-Shopify-Hmac-Sha256`) signs the body bytes exclusively: [2](#0-1) 

But the `shop` (and `topic`, `webhook_id`, `api_version`) values consumed by the library are pulled straight from HTTP headers, which are **not** part of the signed payload: [3](#0-2) [4](#0-3) 

`Registry.process` validates the HMAC and then trusts `request.shop` (and `request.topic`) to build the `WebhookMetadata` handed to the app's handler, with no separate binding check between the signed body and the shop-identifying header: [5](#0-4) 

### Binding that is broken

The equality that should hold is:

`shop_that_signed_the_body == shop_field_the_handler_receives`

Because `shop` lives in an unauthenticated header while only the body is HMAC-covered, this equality is not enforced by the gem. Any attacker who can obtain **one** legitimately-signed webhook body+HMAC pair for their own shop (trivial — install a free/dev app instance and receive any webhook) can:

1. Capture the raw body and its valid `X-Shopify-Hmac-Sha256` value from a webhook Shopify sent for *their own* shop.
2. Replay the exact same `raw_body`/`hmac-sha256` header to the app's webhook endpoint, but substitute `X-Shopify-Shop-Domain` with a victim shop's domain.
3. `HmacValidator.validate` only recomputes the HMAC over `raw_body`, so it still passes.
4. `Registry.process` builds `WebhookMetadata.new(shop: request.shop, ...)` using the attacker-chosen `shop` value and dispatches it to the app's handler as if it were a real event from the victim shop.

Downstream host applications (this is the intended integration point, e.g. `ShopifyApp`) commonly use `WebhookMetadata#shop` to select which merchant's session/data to act on. Since this gem provides no assurance that the `shop` header is bound to the signed content, cross-tenant confusion is possible purely through this gem's own verification logic — not because the host app violates any documented contract.

### Title
Webhook `shop` (and other Shopify headers) are not covered by HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` signs only the raw body, while `shop`, `topic`, `webhook_id`, and `api_version` are read from unauthenticated HTTP headers and trusted by `Registry.process` after HMAC validation succeeds.

### Finding Description
`Request#hmac` and `Request#to_signable_string` are used by `Utils::HmacValidator.validate` to verify authenticity of a webhook. The signable string is `@raw_body` only [1](#0-0) . Meanwhile `shop`, `topic`, `api_version`, and `webhook_id` are parsed directly from headers with no cryptographic link to the body [6](#0-5) . `Registry.process` performs the HMAC check and then immediately trusts `request.shop`/`request.topic` to route and construct `WebhookMetadata` for the handler [5](#0-4) . Because the header fields are outside the authenticated boundary, an attacker controlling any valid (body, hmac) pair — obtainable from a webhook legitimately delivered to their own shop — can freely relabel which shop the event is attributed to.

### Impact Explanation
This breaks the identity binding `shop_that_signed_body == shop_delivered_to_handler`, enabling cross-tenant webhook spoofing: a handler that trusts `WebhookMetadata#shop` to select per-merchant state (sessions, local records, redact/data-request compliance flows, etc.) can be tricked into acting on/for a victim shop using an attacker-obtained signature. This qualifies as Critical (cross-tenant access) per the impact taxonomy.

### Likelihood Explanation
Moderate-to-high: any developer/attacker can install the app (even a free plan or dev store) to legitimately receive at least one signed webhook, then replay its body+HMAC with a forged `shop-domain` header. No access token, `client_secret`, or privileged credential is required — only observation of one legitimate webhook delivery to an account the attacker controls.

### Recommendation
Include the shop domain (and ideally topic/webhook id) in the HMAC-signable material, or otherwise verify server-side that the `shop` header corresponds to a shop with an active, matching installation/session before dispatching to handlers. At minimum, document/enforce that `WebhookMetadata#shop` must be cross-checked against known installed shops by the consuming application before being trusted for tenant-scoped operations.

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker.myshopify.com` and receives a legitimate webhook, e.g. body `{"id":123}` with header `X-Shopify-Hmac-Sha256: <valid-hmac-for-body>`.
2. Attacker POSTs to the app's webhook endpoint with the same body and HMAC header but sets `X-Shopify-Shop-Domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `raw_body` only and succeeds [7](#0-6) .
4. The handler is invoked with `WebhookMetadata.new(topic: ..., shop: "victim.myshopify.com", body: ..., ...)` [8](#0-7) , causing the host application to process the event as belonging to `victim.myshopify.com` despite it never having sent or signed this event for that shop.

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

**File:** lib/shopify_api/webhooks/request.rb (L67-70)
```ruby
      sig { params(name: String).returns(T.untyped) }
      def shopify_header(name)
        @headers["shopify-#{name}"] || @headers["x-shopify-#{name}"]
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
