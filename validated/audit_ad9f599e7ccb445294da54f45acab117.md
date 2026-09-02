This confirms the identity binding gap: `WebhookMetadata.shop` (used by every `WebhookHandler#handle` implementation to identify the tenant) comes straight from `Request#shop`, which reads the `X-Shopify-Shop-Domain` header, while `Request#to_signable_string` — the only thing the HMAC actually covers — is just `@raw_body`. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) 

### Title
Webhook `shop` identity is not covered by the HMAC, allowing shop-domain spoofing on genuinely-signed webhook bodies - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes the HMAC-verifiable signable string solely from the raw HTTP body, while the `shop` (tenant identity) is read from the `X-Shopify-Shop-Domain` header, which plays no part in the HMAC computation or verification.

### Finding Description
`Request#to_signable_string` returns only `@raw_body` [5](#0-4) , and `HmacValidator.validate` verifies the HMAC exclusively against this signable string using the app-wide `Context.api_secret_key` [6](#0-5) . Meanwhile `Request#shop` is read directly from the (unauthenticated) `shopify-shop-domain` / `x-shopify-shop-domain` header [7](#0-6) , and this is exactly what `Registry.process` forwards to the app's `WebhookHandler#handle` as the tenant-identifying `WebhookMetadata.shop` field once `HmacValidator.validate(request)` passes [2](#0-1) .

The identity binding that should hold is: `shop header value == shop bound inside the HMAC-signed bytes`. It does not — the header is never included in `to_signable_string`, so it is "bytes verified versus bytes parsed": the bytes cryptographically verified (raw body) are a strict subset of the bytes the application actually parses and trusts (raw body + shop header).

Because Shopify signs webhooks for *every* installed shop of an app using the *same* app-wide `client_secret`/`api_secret_key` (not a per-shop secret), a merchant who has legitimately installed the app on their own store (an "unprivileged internet user" relative to any other tenant) receives real webhook deliveries with valid HMACs for their own shop. That attacker-controlled shop can trigger webhook topics (e.g. by performing actions in their own store that Shopify will webhook out), capture the `(raw_body, X-Shopify-Hmac-Sha256)` pair, and replay it to the app's webhook endpoint with the `X-Shopify-Shop-Domain` header rewritten to a victim shop's domain. `HmacValidator.validate` will still pass because it only checks the raw body, and `Registry.process` will dispatch a `WebhookMetadata` claiming to be from the victim shop.

### Impact Explanation
Any host application that uses `WebhookMetadata#shop` (or `Request#shop`) as the tenant key to look up sessions, write data, or gate access — the intended and documented use of this field — can be made to process attacker-supplied webhook payloads under a victim shop's identity. This is a cross-tenant identity spoofing primitive delivered by the gem's own trusted API surface (`Registry.process`/`WebhookMetadata`), matching the Critical "cross-tenant access" impact category, since the gem itself asserts the HMAC-validated request is authentically from `request.shop` when it has not verified that binding at all.

### Likelihood Explanation
Likelihood is bounded by the practical difficulty of getting Shopify to emit a webhook with attacker-chosen body content for a topic useful to spoof, and by whether the consuming application actually keys sensitive logic off `WebhookMetadata.shop` without cross-checking the topic/body's own shop-scoped identifiers. Any app that follows the documented pattern of trusting `data.shop` from `Registry.process` is exposed as soon as an attacker owns any single shop with the app installed.

### Recommendation
Include the shop domain (and ideally topic/webhook-id) in the HMAC-covered signable string, or independently verify that the `shop-domain` header matches a shop-specific value that Shopify has authenticated (Shopify does not offer this natively for webhooks, so the safer fix is to document/enforce that consuming apps must not trust `request.shop`/`WebhookMetadata.shop` alone for cross-tenant-sensitive decisions, and to cross-validate it against the webhook body's own `myshopify_domain`/`admin_graphql_api_id` fields for topics that carry shop identity in the payload).

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com`.
2. Attacker triggers a webhook topic (e.g. `products/update`) on their own shop; Shopify sends a POST with a valid `X-Shopify-Hmac-Sha256` computed over the raw body using the app's shared `client_secret`.
3. Attacker captures `raw_body` and the valid `hmac` header, then re-sends the same body/HMAC to the app's webhook endpoint but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only checks `raw_body` against the HMAC [8](#0-7) .
5. The handler receives `WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...)` and, if it uses `shop` to look up/act on tenant data, performs the attacker's forged webhook body under the victim's identity.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-38)
```ruby
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
