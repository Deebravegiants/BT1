### Title
Webhook `shop`, `topic`, `webhook_id`, and `api_version` Are Not Covered by the HMAC Signature, Enabling Cross-Tenant Webhook Spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable payload from the raw request body only, while the shop domain, topic, webhook id, and API version are read from separate, unsigned HTTP headers. `Webhooks::Registry.process` validates the HMAC and then unconditionally trusts these header-derived fields (in particular `shop`) when dispatching to the host application's handler, breaking the intended binding `hmac_verified_bytes == data_acted_upon`.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

Meanwhile, `shop`, `topic`, `webhook_id`, and `api_version` are all pulled straight from HTTP headers (`x-shopify-shop-domain`, `x-shopify-topic`, etc.) with no cryptographic binding to the signed body: [2](#0-1) 

`Webhooks::Registry.process` validates the HMAC of the request (i.e., of the raw body only) and then immediately trusts `request.shop` and `request.topic` — values that were never part of the signed material — to build `WebhookMetadata` passed to the app's handler: [3](#0-2) 

The gem's own `HmacValidator.validate` confirms the check is scoped strictly to `to_signable_string`: [4](#0-3) 

Because Shopify apps share a single `client_secret` across every shop that installs them (there is no per-shop HMAC key baked into this gem's validation), any merchant that has installed the app can capture a legitimate `(raw_body, x-shopify-hmac-sha256)` pair from their own store's webhook deliveries. That pair remains cryptographically valid for the app's `client_secret` regardless of which shop it is replayed for. An attacker can then replay that exact body+HMAC to the app's webhook endpoint while substituting an arbitrary `x-shopify-shop-domain` header (e.g., a victim merchant's domain). `Registry.process` will report a valid HMAC (since it only checks the body) and hand the handler a `WebhookMetadata` claiming the payload originated from the victim shop.

This is the same class of bug as the referral report's root cause: a value that is *acted upon* as an identity/tenant discriminator (`shop`) is disjoint from the value actually protected by the cryptographic check (`raw_body`), so `shop_verified == shop_used_for_tenant_routing` does not hold.

### Impact Explanation
Any host application that uses `WebhookMetadata#shop` from this gem to key data storage, trigger per-tenant side effects, or otherwise identify which merchant a webhook event belongs to can be made to process another merchant's webhook data under an attacker-chosen shop identity. This is a cross-tenant data-integrity/confusion issue: an attacker-controlled tenant can inject events attributed to a victim tenant, satisfying the "cross-tenant access" Critical-impact category, since the trust boundary between tenants sharing one app installation is broken by the gem's identity binding.

### Likelihood Explanation
Exploitation requires only that the attacker operate one legitimate installation of the target app (a normal, unprivileged merchant/user) — no access to `client_secret`, access tokens, or any privileged account is needed. Capturing a valid `(body, hmac)` pair is trivial (any real webhook delivery to their own store), and replaying it with a modified `shop` header is a simple unauthenticated HTTP request to the app's public webhook endpoint. Likelihood is Medium-High, gated only by the host app actually branching tenant logic on `WebhookMetadata#shop` — a very common integration pattern documented by this gem itself.

### Recommendation
Include `shop`, `topic`, `webhook_id`, and `api_version` in the HMAC-signable string (or otherwise cryptographically bind them to the raw body, e.g. by validating them against a previously-registered/expected shop for the current app installation) so that `HmacValidator.validate` fails whenever any of these header-derived identity fields is altered relative to what Shopify actually signed.

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com` and receives a real webhook, e.g.:
   ```
   POST /webhooks
   x-shopify-topic: orders/create
   x-shopify-hmac-sha256: <valid-hmac-for-body>
   x-shopify-shop-domain: attacker-shop.myshopify.com
   Body: {"id": 1, ...}
   ```
2. Attacker replays the identical body and `x-shopify-hmac-sha256` value, but changes the shop header:
   ```
   POST /webhooks
   x-shopify-topic: orders/create
   x-shopify-hmac-sha256: <same-valid-hmac-for-body>
   x-shopify-shop-domain: victim-shop.myshopify.com
   Body: {"id": 1, ...}
   ```
3. `Utils::HmacValidator.validate(request)` in `Webhooks::Registry.process` (`lib/shopify_api/webhooks/registry.rb:190`) succeeds because it only checks the (unmodified) body.
4. The handler receives `WebhookMetadata(shop: "victim-shop.myshopify.com", ...)` — as constructed in `lib/shopify_api/webhooks/registry.rb:198-199` — even though the request never actually originated from, nor was authorized for, `victim-shop.myshopify.com`.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
