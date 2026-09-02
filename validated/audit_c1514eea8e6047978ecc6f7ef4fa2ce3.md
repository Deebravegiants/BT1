### Title
Webhook `shop` (and `topic`/`webhook_id`/`api_version`) Identity Is Not Bound by the HMAC, Allowing Cross-Tenant Webhook Forgery - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-verifiable payload from the raw HTTP body only, while the `shop`, `topic`, `webhook_id`, and `api_version` fields that `ShopifyAPI::Webhooks::Registry.process` uses to route and attribute the webhook to a tenant are taken from unauthenticated HTTP headers. This breaks the equality that should hold between "the shop the HMAC proves the payload came from" and "the shop the payload is attributed/dispatched to," enabling cross-tenant webhook forgery.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop`, `#topic`, `#webhook_id`, and `#api_version` are read directly from HTTP headers, which are never fed into the HMAC signable string: [2](#0-1) 

`Registry.process` validates the HMAC (which only proves the body's integrity/authenticity) and then trusts `request.shop` and `request.topic` — taken straight from headers — to route the webhook and populate `WebhookMetadata`, which is the tenant identifier passed to the app's handler: [3](#0-2) 

The `HmacValidator.validate` call only recomputes the HMAC over `verifiable_query.to_signable_string`, i.e., the raw body — it has no visibility into headers at all: [4](#0-3) 

The broken binding, expressed as an equality that should hold but doesn't:
`shop_that_HMAC_authenticates == shop_used_for_tenant_dispatch`

Because the HMAC covers only the body, an attacker who can obtain any genuine `(raw_body, hmac)` pair signed by the app's secret (e.g., by triggering real Shopify webhook deliveries to the app for their own shop) can resend that exact body+HMAC to the app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` (and/or `X-Shopify-Topic`/`Webhook-Id`) header with a different shop's domain. The signature still validates because the header content is not part of the signed material, so the forged webhook is accepted and dispatched as if it belongs to the victim shop.

### Impact Explanation
This is a cross-tenant identity confusion: an app relying on `WebhookMetadata#shop` (or `#topic`) to look up/update per-tenant state will process attacker-controlled data under a victim's tenant identity, since the field that establishes "who this webhook is about" is not covered by the same authentication mechanism the library exposes as its integrity guarantee. This matches the Critical impact category of cross-tenant access.

### Likelihood Explanation
Any entity that can install the app on their own store (a normal, unprivileged action for a public/embeddable Shopify app) can obtain genuine `(body, hmac)` pairs signed with the app's secret via real webhook deliveries, then replay them with a modified `shop-domain` header value against the app's public webhook endpoint. No access to `api_secret_key`, access tokens, or the app's `client_secret` is required — only observation of legitimate webhook traffic to one's own tenant.

### Recommendation
Bind the shop (and ideally topic/webhook id) into the material verified by the HMAC, or independently authenticate that the header-derived `shop` matches a shop known to be an actual recipient of the webhook (e.g., cross-check against Shopify's TLS-terminated request source or reject header-only shop attribution). At minimum, `to_signable_string` should not be the sole trust anchor for identity fields consumed downstream in `Registry.process`/`WebhookMetadata`.

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker.myshopify.com` and receives a genuine webhook delivery with body `B` and valid header `X-Shopify-Hmac-Sha256: H` (computed by Shopify over `B` using the app's secret) and `X-Shopify-Shop-Domain: attacker.myshopify.com`.
2. Attacker crafts a raw HTTP POST to the app's webhook endpoint reusing `raw_body = B` and `X-Shopify-Hmac-Sha256: H`, but sets `X-Shopify-Shop-Domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: {...shop-domain: "victim.myshopify.com", hmac-sha256: H...})` is constructed; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks `HMAC(B)` against `H`. [5](#0-4) 
4. The handler receives `WebhookMetadata` with `shop: "victim.myshopify.com"` and body `B`, even though `B` was never sent by Shopify on behalf of `victim.myshopify.com` — demonstrating the forged cross-tenant attribution.

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
