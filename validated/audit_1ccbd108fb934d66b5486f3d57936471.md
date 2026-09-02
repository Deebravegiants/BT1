This confirms the finding. The documentation explicitly states in `docs/usage/webhooks.md:125` that `Registry.process` "will verify the request did indeed come from Shopify" — but the verification only covers the raw body, not the `shop` field that the gem passes as the tenant identifier to the handler.

### Title
Webhook `shop` domain is not covered by HMAC verification, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` validates a webhook solely via `Utils::HmacValidator.validate(request)`, which signs/verifies only the raw request body. The `shop` (and `topic`/`webhook_id`/`api_version`) values are read directly from HTTP headers and are never included in the signed bytes, yet `shop` is passed to the application's webhook handler as the authoritative tenant identifier.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0)  while `shop` is derived from the unauthenticated `shopify-shop-domain`/`x-shopify-shop-domain` header: [2](#0-1) .

`Registry.process` validates the HMAC and, if it passes, immediately trusts `request.shop` to build the `WebhookMetadata` passed to the app's handler: [3](#0-2) .

`HmacValidator.validate` computes the HMAC purely from `verifiable_query.to_signable_string` (the raw body) against the app's `api_secret_key`, with no binding to `shop`, `topic`, or any header: [4](#0-3) .

Since a single Shopify app uses one `api_secret_key` shared across all merchant installs, any merchant who installs the app receives genuinely-signed webhooks for their own store. The HMAC over the body is therefore valid for that shop's traffic, but it says nothing about which shop the body belongs to. An attacker who has installed the app (an unprivileged internet user relative to other tenants) can capture one of their own valid webhook deliveries (raw body + valid `hmac-sha256` header) and replay it to the app's shared webhook endpoint with a forged `x-shopify-shop-domain` header naming a victim shop. `HmacValidator.validate` will accept it because it never inspects the `shop` header, and `Registry.process` will hand the handler `shop: <victim-domain>` alongside the attacker's payload.

This breaks the intended identity binding: `shop authenticated-by-HMAC == shop delivered-to-handler`. The gem authenticates only the body's provenance from *some* shop under the app, not the specific shop claimed in the header that host applications rely on for tenant-scoped processing (as documented and exemplified in `docs/usage/webhooks.md:14,25-26`, where `data.shop` is used directly to route/store data per-tenant).

### Impact Explanation
This is a cross-tenant access vector: an attacker-controlled or attacker-owned shop install can inject spoofed webhook events attributed to any other merchant using the same app (e.g., forging `orders/create`, `app/uninstalled`, `shop/redact`, or other business-critical webhook data under a victim's `shop` domain), corrupting or exfiltrating data across tenant boundaries in host applications that trust `data.shop` as returned by this gem (as its own documentation instructs).

### Likelihood Explanation
Any user who can install the app (a normal, unprivileged Shopify merchant) automatically receives valid HMAC-signed webhook traffic for their own shop and can replay it with a modified `shop-domain` header to the same public webhook endpoint. No secrets, tokens, or elevated privileges are required — only the ability to install the target app once and observe/replay one legitimate webhook request.

### Recommendation
Bind `shop` (and ideally `topic`) into the value verified by HMAC, or otherwise cryptographically associate the verified body with the claimed shop before handing it to the handler — e.g., by requiring the caller to supply the expected shop (from the route/session context) and rejecting the webhook if it doesn't match `request.shop`, or by validating `request.shop` against per-shop registration state rather than trusting an unauthenticated header outright.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker.myshopify.com`, gets `Registry.register_all` to enable e.g. `orders/create`.
2. Shopify delivers a legitimate webhook to the app's callback URL:
   - Headers: `x-shopify-hmac-sha256: <valid-hmac-of-body>`, `x-shopify-shop-domain: attacker.myshopify.com`, `x-shopify-topic: orders/create`.
   - Attacker captures this raw body and its valid `hmac-sha256` value.
3. Attacker replays the same body/HMAC to the same endpoint but changes only the header: `x-shopify-shop-domain: victim.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new` parses headers/body normally; `HmacValidator.validate` recomputes the HMAC over the raw body only and it matches (since the body/HMAC pair is unchanged) — see `lib/shopify_api/utils/hmac_validator.rb:26-31` and `lib/shopify_api/webhooks/request.rb:35-38`.
5. `Registry.process` invokes the app's handler with `shop: "victim.myshopify.com"` and the attacker's body, as shown in `lib/shopify_api/webhooks/registry.rb:198-199`, causing the host application to process/store attacker data under the victim's tenant.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-23)
```ruby
      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L35-38)
```ruby
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
