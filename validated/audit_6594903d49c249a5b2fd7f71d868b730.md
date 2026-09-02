This confirms the finding. `WebhookMetadata.shop` (and `topic`, `webhook_id`) are handed directly to the app's `WebhookHandler#handle` as trusted tenant identity, but they originate purely from HTTP headers that are never covered by the HMAC signature. [1](#0-0) [2](#0-1) [3](#0-2) 

### Title
Webhook `shop` (tenant) identity is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating an HMAC computed over the raw request body. The `shop` (and `topic`, `webhook_id`) fields that are handed to the app's handler as the identified tenant come from HTTP headers that are completely outside the scope of what the HMAC signs, breaking the binding `shop authenticated == shop the handler acts on`.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [4](#0-3) 

Meanwhile `shop`, `topic`, and `webhook_id` are read straight from attacker-controllable headers (`shopify-shop-domain`, `shopify-topic`, `shopify-webhook-id`) with no cryptographic tie to the signed body: [5](#0-4) 

`Registry.process` validates only the HMAC over the body via `Utils::HmacValidator.validate(request)`, and then unconditionally forwards the unauthenticated `request.shop`, `request.topic`, and `request.webhook_id` to the app-defined handler inside a `WebhookMetadata` struct that carries no cryptographic provenance: [2](#0-1) [3](#0-2) 

The `HmacValidator` itself is generic and only checks `to_signable_string` against `Context.api_secret_key`, so it has no visibility into headers at all: [6](#0-5) 

Critically, the secret used to compute/verify the HMAC is the single app-level `Context.api_secret_key`, shared across every shop/tenant that has the app installed — it is not shop-specific. Any legitimate merchant who has installed the app receives real webhook deliveries to their own publicly reachable endpoint, each with a body and a valid HMAC computed with that same shared secret. Because the `shop` header carrying tenant identity is never included in the signed bytes, that same `(raw_body, hmac)` pair remains valid no matter what `shopify-shop-domain` header value accompanies it. A malicious merchant (an "unprivileged" party with respect to other tenants of the same app) can capture one of their own genuine webhook deliveries and replay it against the app's webhook endpoint with the `shopify-shop-domain` header changed to a victim shop's domain. `Registry.process` will accept it as authentic (the HMAC still matches the unmodified body) and dispatch it to the handler labeled as coming from the victim shop.

### Impact Explanation
This breaks the identity binding "shop verified by HMAC" == "shop the handler trusts and acts on," letting one tenant inject fabricated, apparently-authentic events (e.g. `orders/create`, `app/uninstalled`, `shop/redact`, `customers/data_request`) attributed to a different, victim shop. Any app logic that uses `WebhookMetadata#shop` to look up/update per-tenant records, revoke sessions, trigger data deletion, or otherwise branch on tenant identity can be manipulated cross-tenant, which is a Critical-impact cross-tenant access issue per the given classification.

### Likelihood Explanation
Likelihood is high for any app exposing a webhook endpoint reachable from the internet (the standard, documented usage pattern for this gem): the attacker need only be a legitimate, unprivileged merchant of the same app to obtain one genuine `(body, hmac)` sample from their own store, then replay it with a modified `shop` header — no access to `api_secret_key`, access tokens, or any other privileged credential is required.

### Recommendation
Bind the tenant/topic identity into what is actually verified: either include `shop`, `topic`, and `webhook_id` in the HMAC-signable content, or perform an independent authenticated lookup (e.g., re-derive/verify shop membership from a signed source, such as fetching the shop via the app's own registered webhook/subscription records) before trusting the `shop` header, rather than passing the raw header value straight into `WebhookMetadata` after only a body-only HMAC check.

### Proof of Concept
1. Merchant M installs the app and legitimately receives a webhook: body `{"id":1}`, header `x-shopify-shop-domain: m-shop.myshopify.com`, and `x-shopify-hmac-sha256: <valid-hmac-of-body>` (computed by Shopify using the app's shared `client_secret`).
2. M crafts a new HTTP POST to the app's webhook endpoint reusing the exact same body and `x-shopify-hmac-sha256` value, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new(raw_body: body, headers: headers)` parses this, and `Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only checks the body against the HMAC: [7](#0-6) 
4. The registered handler receives `WebhookMetadata.new(shop: "victim-shop.myshopify.com", topic: ..., body: {"id":1}, ...)` and performs whatever tenant-scoped action it associates with that topic against `victim-shop.myshopify.com`, even though the request never originated from Shopify on behalf of that shop.

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
