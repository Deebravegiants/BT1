### Title
Webhook shop-domain (and topic/webhook-id/api-version) are not covered by the HMAC signature, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, so `HmacValidator.validate` authenticates nothing but the body bytes. The `shop`, `topic`, `webhook_id`, and `api_version` values—each read straight from unauthenticated HTTP headers—are never part of the signed material, yet they are trusted downstream to identify which merchant/tenant a webhook belongs to.

### Finding Description
`Utils::HmacValidator.validate` computes an HMAC over `verifiable_query.to_signable_string` and compares it to the `hmac` field: [1](#0-0) 

For webhooks, `to_signable_string` is defined as just the raw body: [2](#0-1) 

Meanwhile `shop`, `topic`, `webhook_id`, and `api_version` are all pulled directly from HTTP headers with no cryptographic binding to the HMAC at all: [3](#0-2) 

`Registry.process` validates only the body-HMAC, then forwards the attacker-controllable `request.shop`, `request.topic`, and `request.webhook_id` straight into `WebhookMetadata`, which is handed to the app's registered handler as trusted tenant-identifying data: [4](#0-3) 

The equality that should hold is: `shop_bound_by_hmac == shop_used_for_tenant_routing`. Here that equality is broken — the HMAC binds only the body bytes, while the shop (tenant identity) used by the handler comes from a header outside the signed scope.

### Impact Explanation
Any unprivileged internet user who can observe one legitimate `(raw_body, hmac)` pair — trivially obtainable by installing a free/dev app on their own store and capturing their own store's real webhook deliveries — can replay that exact body+HMAC to the target app's public webhook endpoint while substituting an arbitrary `shop-domain` (and `topic`/`webhook-id`) header. `HmacValidator.validate` still returns `true` because it only checks the body, so `Registry.process` accepts the request and dispatches it to the handler tagged with the attacker-chosen `shop`. If the host application uses `WebhookMetadata#shop` to select which tenant's data to update/create/delete (the documented and expected usage pattern), this allows cross-tenant data injection/confusion — one merchant's genuine webhook payload can be replayed under another merchant's identity.

### Likelihood Explanation
The webhook HTTP endpoint is, by design, a public, unauthenticated endpoint that must accept POSTs from Shopify's servers; nothing prevents any client from POSTing directly to it with arbitrary headers. No secret (`api_secret_key`) is required by the attacker — a body/hmac pair legitimately produced for their own shop is sufficient. This is a low-effort, directly reachable exploit path.

### Recommendation
Bind the tenant-identifying fields into the signed material, or otherwise cryptographically tie `shop`, `topic`, and `webhook_id` to the HMAC before trusting them:
- Include `shop-domain` (and ideally `topic`/`webhook-id`) in the string that is HMAC-verified, not just the raw body, or
- Require host applications to cross-check `request.shop` against the session/shop the webhook was registered for before acting on it, and document this requirement clearly, or
- Reject/flag webhook deliveries where the header-derived shop does not match an expected registered shop for that specific webhook subscription id.

### Proof of Concept
1. Attacker installs a (free/dev) app on `attacker-shop.myshopify.com` and triggers a real webhook (e.g. `orders/create`), capturing the genuine `raw_body` and `x-shopify-hmac-sha256` value sent by Shopify to the app's webhook endpoint.
2. Attacker sends this exact `raw_body` and `hmac` to the same app's public webhook endpoint, but sets `x-shopify-shop-domain: victim-shop.myshopify.com` and any desired `x-shopify-topic`/`x-shopify-webhook-id`.
3. `ShopifyAPI::Webhooks::Request.new` parses these headers, `Utils::HmacValidator.validate` succeeds because it only hashes `raw_body` (`request.rb:35-38`, `hmac_validator.rb:26-31`).
4. `Registry.process` builds `WebhookMetadata` with `shop: "victim-shop.myshopify.com"` and dispatches to the app's handler (`registry.rb:188-200`), which processes attacker-supplied body content under the victim tenant's identity.

### Citations

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

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
