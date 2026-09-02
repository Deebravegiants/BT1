### Title
Webhook HMAC signature does not cover the `shop-domain` header, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable content from the raw request body only, while the `shop`, `topic`, `webhook_id`, and `api_version` values used by webhook handlers are read directly from unauthenticated HTTP headers. `ShopifyAPI::Webhooks::Registry.process` validates the HMAC and then passes these header-derived, unverified values straight to the app's handler, breaking the binding between "HMAC-verified bytes" and "the shop the data is attributed to."

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

Meanwhile `Request#shop`, `#topic`, `#webhook_id`, and `#api_version` are all read from HTTP headers that are never included in the signable string: [2](#0-1) 

`Utils::HmacValidator.validate` only ever calls `verifiable_query.to_signable_string`/`hmac`, so it only proves that the body bytes match a signature computed with `Context.api_secret_key`; it says nothing about the header values: [3](#0-2) 

`Registry.process` uses exactly this validation, then forwards the unauthenticated `request.shop`, `request.topic`, and `request.webhook_id` to the app-supplied handler as if they were verified: [4](#0-3) 

Because a single app's `api_secret_key` is shared across every merchant/tenant that installs it, any holder of one legitimate `(raw_body, hmac)` pair — e.g., a merchant who receives their own genuine webhook — can resend that exact body and HMAC to the app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` (and/or `X-Shopify-Topic`/`X-Shopify-Webhook-Id`) header with a victim shop's domain. `Utils::HmacValidator.validate` still returns `true` because it never inspected those headers, and the handler receives `WebhookMetadata` claiming the body originated from the victim shop.

This is the exact class of bug described in the report: a field the application acts on (`shop`, used as the tenant/session key for webhook processing) is not covered by the integrity check (the HMAC, which binds only the raw body).

### Impact Explanation
If a host application's webhook handler uses `WebhookMetadata#shop` to key any per-tenant state (uninstall handling, data deletion/GDPR requests, order/customer sync, feature toggles, etc.), an attacker who controls one legitimate shop can inject attacker-controlled payloads that the app will process as if they came from an arbitrary other shop. This is a cross-tenant data injection/impersonation issue — data or actions attributed to one merchant can be forged under another merchant's identity without ever needing that merchant's or the app's credentials.

### Likelihood Explanation
Exploitation only requires the attacker to be an ordinary (non-privileged) user of the shared app — i.e., install the app on their own store to receive at least one genuine `(body, hmac)` pair for a topic they control, then replay it against the app's public webhook endpoint with a forged `shop-domain` header. No access to `api_secret_key`, tokens, or TLS interception is needed, matching the "unprivileged internet user" threat model.

### Recommendation
Include the identifying headers (`shopify-shop-domain`, `shopify-topic`, and ideally `shopify-webhook-id`/`shopify-api-version`) as part of the HMAC-signable payload verified by `Utils::HmacValidator`, or otherwise cryptographically bind the `shop` value to the signed body before it is trusted by `Registry.process`/handed to handlers. At minimum, document/require that the host application not treat `WebhookMetadata#shop` (or `#topic`/`#webhook_id`) as verified unless it independently corroborates it (e.g., cross-checks against an expected shop for that endpoint).

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and receives a real webhook: body `B` with header `X-Shopify-Hmac-Sha256: H` (valid for `B` under the shared `api_secret_key`) and `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`.
2. Attacker resends the same `B`/`H` to the app's webhook endpoint but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: {...})` is built; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which only checks `HMAC(api_secret_key, B) == H` — this still passes.
4. The handler is invoked with `WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: parsed(B), ...)`, i.e., attacker-controlled data is processed under the victim shop's identity. [5](#0-4) [6](#0-5)

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
