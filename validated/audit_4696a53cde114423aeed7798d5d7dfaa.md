### Title
Webhook `shop-domain` header is trusted for tenant identification without being covered by the HMAC signature - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature exclusively over the raw request body, while the `shop` (tenant identifier), `topic`, `api_version`, and `webhook_id` values are read directly from unauthenticated HTTP headers and handed to the app's webhook handler as trusted metadata. This breaks the equality `shop authenticated by HMAC == shop used to route/attribute the webhook`, allowing a request with a validly-signed body to be delivered with a forged `shop-domain` header and be processed as if it belonged to a different (victim) tenant.

### Finding Description
`HmacValidator.validate` verifies the signature against `verifiable_query.to_signable_string`: [1](#0-0) 

For webhooks, `to_signable_string` returns only the raw HTTP body: [2](#0-1) 

But the `shop`, `topic`, `api_version`, and `webhook_id` fields are parsed straight from HTTP headers, which are not part of the signed payload: [3](#0-2) 

`Registry.process` validates the HMAC (over the body only) and then constructs `WebhookMetadata` using the unauthenticated `request.shop` value, which is passed to the app's handler as the tenant identity for the event: [4](#0-3) 

Because the HMAC only binds the body, `shop-domain == request.shop` is never verified against anything cryptographically tied to the signature. Any request whose body has a valid HMAC (e.g., a body causing an intended per-app secret computation) can be delivered with an attacker-chosen `shop-domain` header, and the gem will hand that forged shop identity to the host application's webhook handler as if it were authentic. This is the same identity-binding defect pattern as the reported bug: a field (`shop`) that is acted upon (tenant attribution) is not covered by the authentication check (HMAC over body only).

### Impact Explanation
This enables cross-tenant misattribution of webhook data: the app's business logic keys webhook processing (session/tenant lookup, data writes, idempotency keys, mandatory-webhook handling such as `customers/redact` or `shop/redact`) on `WebhookMetadata#shop`, which is fully attacker-controllable independent of the signature. An attacker who can produce or replay a body/HMAC pair (e.g., from their own shop's legitimately delivered webhook) can relabel it to a victim shop's domain, causing the host app to process/store data under the wrong tenant — a cross-tenant access impact.

### Likelihood Explanation
Webhook endpoints are public HTTP(S) endpoints by design, and the header manipulation requires no possession of the app's `api_secret_key` or access tokens — only a body/HMAC pair that is valid for the shared app secret, which any installed merchant can legitimately obtain from their own webhook deliveries and then replay with a modified `shop-domain` header value.

### Recommendation
Include the `shop` (and ideally `topic`, `webhook_id`) values in the signed payload used for signature computation, or otherwise cryptographically bind the header-derived tenant identity to the signature (e.g., require the app to independently confirm the shop has valid credentials/session before trusting `WebhookMetadata#shop`, or compute the signature over headers + body rather than body alone).

### Proof of Concept
1. App exposes webhook endpoint `/webhooks` wired to `ShopifyAPI::Webhooks::Registry.process`.
2. Attacker owns/operates Shop A with the app installed; Shopify delivers a legitimate webhook to the endpoint with headers `x-shopify-shop-domain: shop-a.myshopify.com`, `x-shopify-hmac-sha256: <valid hmac of body B>`, body `B`.
3. Attacker captures this exact `(headers, body B, hmac)` combination (e.g., via their own logging/proxy in front of their webhook receiver) and resends the same body `B` with the same valid `hmac` but with `x-shopify-shop-domain` changed to `shop-victim.myshopify.com`.
4. `Utils::HmacValidator.validate` in [1](#0-0)  succeeds because it only checks `body` integrity.
5. `Registry.process` builds `WebhookMetadata.new(... shop: request.shop ...)` with `shop == "shop-victim.myshopify.com"` [5](#0-4) , and the app's handler processes the event as belonging to the victim shop despite the payload actually originating from the attacker's own shop.

### Citations

**File:** lib/shopify_api/utils/hmac_validator.rb (L13-21)
```ruby
        def validate(verifiable_query)
          return false unless verifiable_query.hmac

          result = validate_signature(verifiable_query, Context.api_secret_key)
          if result || Context.old_api_secret_key.nil? || T.must(Context.old_api_secret_key).empty?
            result
          else
            validate_signature(verifiable_query, T.must(Context.old_api_secret_key))
          end
```

**File:** lib/shopify_api/webhooks/request.rb (L16-33)
```ruby
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
