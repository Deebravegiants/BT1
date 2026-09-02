### Title
Webhook shop identity (`x-shopify-shop-domain`) is not covered by the HMAC signature, allowing cross-tenant shop spoofing - ([File: lib/shopify_api/webhooks/request.rb](lib/shopify_api/webhooks/request.rb))

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body [1](#0-0) , so `Utils::HmacValidator.validate` only authenticates the payload bytes, never the `shop`, `topic`, `webhook_id`, or `api_version` values that are read straight out of unauthenticated HTTP headers [2](#0-1) . `Registry.process` still trusts `request.shop` to build the `WebhookMetadata` passed to the host app's handler after only checking the HMAC over the body [3](#0-2) .

### Finding Description
The bug-class hint from the external report — a component terminating/acting on data whose identity binding was never actually enforced — maps here to: **the "shop" the HMAC implicitly authenticates (i.e., "some request signed with the app's shared `api_secret_key`") is not equal to the "shop" used by the host application for tenant routing/authorization ("`x-shopify-shop-domain` header value")**.

`HmacValidator.validate` computes the signature purely from `verifiable_query.to_signable_string` and the app's `api_secret_key`/`old_api_secret_key` [4](#0-3) . For webhooks, `to_signable_string` is defined as just `@raw_body` [1](#0-0) . The `shop`, `topic`, `webhook_id`, and `api_version` fields are pulled from HTTP headers with no cryptographic linkage to the signature [2](#0-1) .

Crucially, `api_secret_key` (the app's `client_secret`) is a single secret shared across **every shop that has installed the app** — it is not a per-shop secret. This means any merchant who has legitimately installed the app can obtain HMAC-valid webhook bodies computed with that same shared secret (e.g., by triggering a webhook for their own store, since the body-only signature does not bind to their shop). That merchant, acting as an unprivileged consumer of their own webhook feed, can then replay the same body + valid signature to the app's webhook endpoint while substituting the `x-shopify-shop-domain` (and/or `x-shopify-topic`) header with a victim shop's domain. `Registry.process` only re-checks `Utils::HmacValidator.validate(request)` [5](#0-4) , which still passes because it never inspected the header values, and then dispatches to the handler with `shop: request.shop` set to the attacker-chosen value [6](#0-5) .

Equality that should hold but doesn't:
`shop authenticated by HMAC` (nothing — HMAC covers only body bytes) ≠ `shop used by host app to key tenant state` (`request.shop`, taken from an unauthenticated header).

### Impact Explanation
If the host application uses `WebhookMetadata#shop` to decide which tenant's session/data the webhook payload applies to (this is the intended and documented usage — see `docs/getting_started.md`'s webhook guidance and the `handler.handle(data: WebhookMetadata.new(..., shop: request.shop, ...))` call), an attacker who is a legitimate (but unprivileged relative to other tenants) app-installer can forge webhook deliveries that the app will process as if they came from a different, victim shop. This is a cross-tenant access primitive: attacker-controlled body content (e.g., a fake order-paid or app-uninstalled event) gets attributed to another merchant's shop record purely because the shop field lives outside the signed portion of the request.

### Likelihood Explanation
Exploitation only requires: (1) installing the app on any store (or otherwise obtaining one HMAC-valid webhook body/signature pair, which Shopify itself will send to any installer), and (2) sending a crafted HTTP request to the app's public webhook endpoint with the same body/HMAC header but a different `x-shopify-shop-domain` header. No access to `api_secret_key`, tokens, or the victim's credentials is required, satisfying the unprivileged-internet-user bar.

### Recommendation
Bind the shop (and ideally topic/webhook id) into the value that is actually verified, not just left as trusted headers:
- Include `shop-domain` (and `topic`) in the signable string/HMAC computation, or
- Require the host application (and this library's `Registry.process`) to independently verify that `request.shop` corresponds to a shop that this specific webhook subscription was registered against (e.g., cross-check against the session store) before invoking the handler, rather than trusting the header value implicitly authenticated only by a shared, cross-tenant secret.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com`, causing Shopify to deliver a legitimate webhook with headers:
   ```
   x-shopify-topic: orders/paid
   x-shopify-hmac-sha256: <valid-hmac-of-body>
   x-shopify-shop-domain: attacker.myshopify.com
   ```
2. Attacker captures the raw body and the valid `x-shopify-hmac-sha256` value (both are visible to them since it's their own tenant's webhook).
3. Attacker replays the identical body and HMAC header to the app's public webhook endpoint, but sets `x-shopify-shop-domain: victim.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new` parses headers, `Registry.process` validates HMAC successfully (`Utils::HmacValidator.validate`, based only on `@raw_body`) [5](#0-4) , and calls the handler with `shop: "victim.myshopify.com"` [6](#0-5) , even though the payload/signature never originated from or was authorized for that shop.

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
