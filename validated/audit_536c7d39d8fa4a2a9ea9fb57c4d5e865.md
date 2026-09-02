### Title
Webhook shop-domain identity spoofing due to HMAC covering only the raw body — ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-verifiable signable string from the raw body only, while the `shop` (tenant identifier) that is later trusted by application handlers is taken from an unauthenticated HTTP header. This breaks the intended identity binding: `HMAC(secret, raw_body) == received_hmac` says nothing about which shop the payload belongs to, yet `Registry.process` hands the header-derived `shop` value straight to the webhook handler as ground truth.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

The `shop`, `topic`, and `webhook_id` are read straight from HTTP headers with no cryptographic binding to the signed content: [2](#0-1) 

`HmacValidator.validate` only checks `verifiable_query.to_signable_string` (i.e., the raw body) against the app's secret: [3](#0-2) 

`Registry.process` calls this validator and, on success, forwards the *header-derived* `request.shop` (along with topic/body/webhook_id) to the handler as trusted metadata, with no re-check that this shop is the one that actually produced the signed body: [4](#0-3) 

The equality the code should enforce is `shop_authenticated_by_hmac == shop_delivered_to_handler`. Instead, only `hmac(raw_body) == received_hmac` is checked, and `shop_delivered_to_handler` is read from an out-of-band header that carries no signature coverage.

Because the app's `client_secret`/HMAC key is shared across every shop that installs the app (it's per-app, not per-shop), any merchant who has legitimately installed the app receives genuine `(raw_body, hmac)` pairs signed with that same secret for their own shop's events. Nothing in `Request`/`Registry` binds the `shop` header to the specific `hmac`/`raw_body` pair that was actually delivered for that shop, so a captured `(raw_body, hmac)` pair from Shop A remains valid when replayed with a different `X-Shopify-Shop-Domain: shop-b.myshopify.com` header.

### Impact Explanation
This enables cross-tenant data injection: a malicious merchant (Shop A) can capture a legitimately-signed webhook body/HMAC pair from their own store and replay it against the app's webhook endpoint while spoofing the `shop-domain` header to point at a victim shop (Shop B). `Registry.process` will pass HMAC validation and invoke the app's handler with `WebhookMetadata.shop == "shop-b.myshopify.com"` and attacker-chosen `body`/`topic`, causing the host application to attribute attacker-controlled data (e.g., fake `orders/create`, `app/uninstalled`, GDPR `customers/redact`, etc.) to a different tenant. This matches the "cross-tenant access" impact category, since the tenant identity that gates per-shop data/handlers is forged.

### Likelihood Explanation
Moderate-to-high: any actor who can install the app on a shop they control (a normal, unprivileged path — no leaked secret, TLS interception, or privileged account required) automatically obtains valid `(raw_body, hmac)` pairs for events they can trigger themselves (e.g., creating an order or product update in their own store, or receiving mandatory GDPR webhooks). Replaying that request with a forged `shop-domain` header against the public webhook endpoint requires no credentials beyond the ability to send an HTTP POST.

### Recommendation
Bind the delivered `shop` (and ideally `topic`/`webhook_id`) into the value that is cryptographically verified, or otherwise reject header-derived tenant identifiers that aren't part of the signed payload. Concretely: fail validation unless the caller supplies (or the library independently confirms) the shop domain associated with the specific webhook subscription/`webhook_id`, rather than trusting the `X-Shopify-Shop-Domain` header purely because the body's HMAC matches. At minimum, document that consumers of `WebhookMetadata.shop` must not treat it as authenticated and must cross-check it against their own webhook registration records (e.g., by webhook_id) before trusting it for tenant-scoped operations.

### Proof of Concept
1. Malicious actor installs the app on `attacker-shop.myshopify.com` and configures a webhook (e.g., `products/update`).
2. Actor triggers the event, causing Shopify to POST a legitimately-signed webhook: `raw_body = B`, headers include `X-Shopify-Hmac-Sha256: H = HMAC(secret, B)` and `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`.
3. Actor replays the exact same `raw_body = B` and `X-Shopify-Hmac-Sha256: H` to the app's public webhook endpoint, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
4. `Utils::HmacValidator.validate` recomputes `HMAC(secret, B)`, which still equals `H`, so validation passes: [5](#0-4) 
5. `Registry.process` invokes the handler with `WebhookMetadata.shop == "victim-shop.myshopify.com"` and the attacker's body `B`, even though the payload never originated from `victim-shop`: [4](#0-3)

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-33)
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
