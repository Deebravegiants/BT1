Confirmed: `Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , while `shop`, `topic`, `webhook_id`, and `api_version` are all read from unauthenticated headers [2](#0-1) . `Registry.process` validates only the HMAC of the body, then forwards `request.shop` straight into the tenant-scoped `WebhookMetadata` passed to the host app's handler [3](#0-2) . Since `api_secret_key` is a single per-app secret shared across every installing shop (not a per-shop secret), any shop that installs the app can legitimately obtain valid `(raw_body, hmac)` pairs for its own webhooks, then replay that same body/HMAC pair while swapping the `shopify-shop-domain` header to a victim shop — `Registry.process` will accept it as authentic for the victim tenant.

### Title
Webhook shop-domain header is not covered by HMAC, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` binds the HMAC to `@raw_body` only, while `shop`, `topic`, `webhook_id`, and `api_version` are read from HTTP headers that are never part of the signed content. `Registry.process` treats a valid body HMAC as proof of the entire request's authenticity, including the `shop` value it hands to the host application's handler.

### Finding Description
The equality the gem should enforce is: `shop authenticated by HMAC == shop delivered to handler`. In reality: `to_signable_string` = `@raw_body` [1](#0-0) , and `shop` is pulled independently from `shopify-shop-domain`/`x-shopify-shop-domain` headers via `shopify_header` [4](#0-3) . `HmacValidator.validate` only ever calls `verifiable_query.to_signable_string`, so it validates the body bytes, never the shop header [5](#0-4) . `Registry.process` raises only if the body HMAC is invalid, then immediately trusts `request.shop` to build `WebhookMetadata` for the handler [3](#0-2) .

Because `Context.api_secret_key` is one shared secret used for every shop that installs the app (it is not shop-specific), a shop that has legitimately installed the app can capture a real `(raw_body, hmac)` pair delivered to its own webhook endpoint, then resend that identical body and HMAC to the app with the `shopify-shop-domain` header changed to any other installed shop. The signature still validates (it only covers the body), so `Registry.process` calls the handler with `WebhookMetadata(shop: "<victim-shop>", body: <attacker-controlled-but-previously-signed-body>, ...)`, causing the host app to act on/store data as if it originated from the victim tenant.

### Impact Explanation
This breaks the tenant boundary the gem is expected to enforce for webhook delivery: an attacker who is merely a shop owner that installed the app (unprivileged w.r.t. other tenants) can inject spoofed webhook events attributed to a different shop, since `shop` is not bound to the signature that authenticates the payload. Depending on the handler's semantics, this can lead to cross-tenant data corruption or triggering of tenant-specific business logic under a victim's identity, matching the "cross-tenant access" impact class.

### Likelihood Explanation
Exploitation requires the attacker to control at least one shop with the app installed (a normal unprivileged capability), capture one legitimate webhook delivery (trivial, they receive their own webhooks), and replay it to the public webhook endpoint with one header changed. No secret material or elevated access is required.

### Recommendation
Include `shop` (and ideally `topic`/`webhook_id`) in the signable content, or independently verify that the `shopify-shop-domain` header corresponds to a shop the app has a legitimate, current installation/session for before dispatching to the handler. Document/enforce that handlers must not trust `data.shop` without cross-checking against known installed shops.

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com`; app registers webhook subscriptions with Shopify.
2. Shopify sends a legitimate webhook to the app for `attacker-shop.myshopify.com`: body `{"id":1}"`, header `x-shopify-hmac-sha256: <valid-hmac-of-body>`, `x-shopify-shop-domain: attacker-shop.myshopify.com`.
3. Attacker replays the exact same body and HMAC to the app's webhook endpoint, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new` parses headers, `Registry.process` calls `Utils::HmacValidator.validate(request)` which only checks the body-based HMAC — it passes [6](#0-5) .
5. Handler receives `WebhookMetadata(shop: "victim-shop.myshopify.com", body: {"id":1}, ...)` and processes it as a legitimate event for the victim tenant.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
