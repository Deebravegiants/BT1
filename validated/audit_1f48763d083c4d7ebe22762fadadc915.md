### Title
Webhook `shop-domain` (and `topic`/`webhook-id`/`api-version`) headers are trusted by webhook handlers without being covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable payload from the raw body only, while the `shop`, `topic`, `webhook_id`, and `api_version` values that the registry hands to the app's webhook handler are taken from unsigned HTTP headers. Any caller who can produce one HMAC-valid `(raw_body, hmac)` pair for the app (e.g. a merchant who installed the app and receives their own legitimate webhooks) can replay that exact body/HMAC pair to the app's public webhook endpoint while substituting an arbitrary `shop-domain` header. The HMAC check still passes because it only verifies the body, but the handler is invoked believing the payload belongs to a different shop.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

The `shop`, `topic`, `webhook_id`, and `api_version` accessors are all derived from headers that are not part of the signed string: [2](#0-1) 

`HmacValidator.validate` verifies exactly `verifiable_query.to_signable_string` against the received HMAC using the app's shared `api_secret_key` — it has no knowledge of, or opinion on, the header values: [3](#0-2) 

`Registry.process` performs only this body-level HMAC check and then immediately trusts `request.shop`, `request.topic`, etc. to build the `WebhookMetadata` passed to the app's handler: [4](#0-3) 

Because the same `api_secret_key` is used to validate webhooks for every shop that installs the app, a valid `(raw_body, hmac)` pair obtained from a webhook for shop A (e.g. by an unprivileged user who installs the app on their own store, a normal, unprivileged action for any Shopify merchant) can be POSTed directly to the app's webhook endpoint with the `shopify-shop-domain` header changed to shop B. The signature check succeeds (it never covered the shop header), and the handler receives `WebhookMetadata` claiming the (attacker-controlled) body belongs to shop B. This breaks the identity binding: `shop attributed to payload` should equal `shop that authenticated/produced the payload`, but the gem only guarantees `HMAC(body) == HMAC(body)`, not `shop_header == shop_that_signed_body`.

### Impact Explanation
This is a cross-tenant data-integrity/impersonation issue: an attacker who legitimately installs the app on their own shop (which requires no special privilege — any Shopify merchant can install a public/dev app) can inject attacker-controlled webhook payloads that host applications will process as if they originated from a victim shop. Depending on how the host app's `WebhookHandler` implementations use `WebhookMetadata#shop` (e.g., to look up/mutate per-shop records), this can lead to cross-tenant data corruption or disclosure, matching the "cross-tenant access" impact category, since the gem's own API provides no protection against this — it only documents/implements body-level HMAC validation and hands the caller-supplied `shop` straight through.

### Likelihood Explanation
Exploitation only requires: (1) ability to install the target app on an attacker-owned shop to legitimately obtain one valid `(raw_body, hmac)` pair (or capture any repeated/predictable webhook body such as an empty-body/system webhook), and (2) the ability to send an arbitrary HTTP POST to the app's public webhook endpoint with custom headers, which is inherent to any HTTP server exposing that endpoint. No access token, `client_secret`, or other privileged credential is required — matching the "unprivileged internet user" bar. The main mitigating factor is that host applications may add their own additional shop-authorization logic downstream, but the gem itself performs and documents this as sufficient verification (`Errors::InvalidWebhookError, "Invalid webhook HMAC."` is the only integrity gate in `Registry.process`).

### Recommendation
Include the shop domain (and ideally topic/webhook id) in the HMAC-covered signable string, or otherwise cryptographically bind the header-derived `shop` value to the verified body (for example, by requiring the host app to cross-check `request.shop` against a known/allow-listed shop before dispatch). At minimum, document prominently that `Webhooks::Request#shop`/`#topic` are not covered by the signature and must not be trusted for authorization decisions without independent verification against the app's own session/shop records.

### Proof of Concept
1. Install the target Shopify app on attacker-owned shop `attacker.myshopify.com`; capture a real webhook delivery, recording `raw_body` and the valid `x-shopify-hmac-sha256` value (both are computed from the shared `api_secret_key`, which the attacker does not need to know).
2. Replay an HTTP POST to the app's webhook endpoint with the same `raw_body` and `x-shopify-hmac-sha256`, but set `x-shopify-shop-domain: victim.myshopify.com`.
3. `Utils::HmacValidator.validate` succeeds because it only checks `raw_body` against the HMAC: [5](#0-4) 
4. The registered handler is invoked with `WebhookMetadata.new(... shop: "victim.myshopify.com" ...)`, causing the host application to process attacker-controlled data under the victim shop's identity.

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
