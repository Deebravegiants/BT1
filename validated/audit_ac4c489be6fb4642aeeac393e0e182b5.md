## Title
Webhook `shop` identity is never covered by the HMAC signature, allowing cross-tenant webhook attribution - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` binds the app-facing `shop` identity to a raw HTTP header (`X-Shopify-Shop-Domain`), while `Utils::HmacValidator.validate` only authenticates `@raw_body` via `to_signable_string`. `Registry.process` trusts `request.shop` to construct `WebhookMetadata` passed to the host app's handler, without that value ever being covered by the cryptographic check that gates processing.

### Finding Description
`Registry.process` gates webhook processing on a single check: [1](#0-0) 

The validation call is `Utils::HmacValidator.validate(request)`, which computes the signature purely over `to_signable_string`: [2](#0-1) 

And `Request#to_signable_string` returns only the raw body bytes: [3](#0-2) 

Meanwhile `Request#shop` is read straight from an attacker-controllable HTTP header, entirely outside the signed byte range: [4](#0-3) 

The equality this breaks is: `hmac_verified(bytes) == bytes_used_to_attribute_tenant`. The gem verifies `HMAC(secret, raw_body)` but then trusts `shop-domain header` — a field that is never part of the signed material — as the tenant identity handed to the host application's `handler.handle(data: WebhookMetadata.new(... shop: request.shop ...))`.

Because the app's `client_secret`/webhook secret is shared across every shop that installs the app, any merchant who installs the app can capture a legitimately-signed `(raw_body, hmac)` pair for their own shop, then replay that exact body+HMAC to the app's webhook endpoint while substituting a different value in the `X-Shopify-Shop-Domain` header. `HmacValidator.validate` still passes (it only checks the body bytes against the real secret), and `Registry.process` forwards the attacker-chosen `shop` value to the handler as if Shopify itself asserted that tenant, with body content (order/customer data, redact requests, etc.) originating from the attacker's own shop.

### Impact Explanation
This crosses a tenant boundary: an app relying solely on this gem's `Registry.process`/`Utils::HmacValidator.validate(request)` to authenticate webhook shop attribution will process attacker-controlled `(body, shop)` combinations as if verified end-to-end, potentially writing/mutating another merchant's tenant record with attacker-supplied data, or triggering shop-scoped side effects (e.g. GDPR redact flows, inventory/order sync) under the wrong tenant. This matches the High-severity "cross-tenant access" criterion, since the gem's own verification API (`HmacValidator.validate`) is the only binding offered and it does not cover the identity field the library itself exposes and recommends using (`request.shop`) — this is not the host app ignoring documented behavior, it's an intrinsic gap in what `validate` actually authenticates versus what `Request` exposes as verified-looking data.

### Likelihood Explanation
Requires only that the attacker be an installer of the same app (a normal, unprivileged merchant/dev-store operator) — no leaked secrets or privileged access needed. Capturing one's own legitimately delivered webhook `(body, hmac)` and replaying it with a forged `shop-domain` header is a standard HTTP request the attacker fully controls end-to-end.

### Recommendation
Include the shop/tenant identity in the signed material verified by `HmacValidator`, or have `Registry.process`/`Request` cross-check the `shop-domain` header against an independently-verified source (e.g., the topic/webhook subscription record fetched via the Admin API for that specific shop) rather than trusting the header purely because the body's HMAC validated. At minimum, document prominently that `request.shop` is unauthenticated and must not be used for tenant attribution without additional verification.

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker.myshopify.com`.
2. Shopify sends a legitimate webhook: body `B`, header `X-Shopify-Hmac-Sha256: H = HMAC(secret, B)`, header `X-Shopify-Shop-Domain: attacker.myshopify.com`.
3. Attacker resends the identical `B` and `H` to the app's webhook endpoint, but sets `X-Shopify-Shop-Domain: victim.myshopify.com`.
4. `Utils::HmacValidator.validate(request)` recomputes `HMAC(secret, B)` — matches `H`, validation passes (per `lib/shopify_api/utils/hmac_validator.rb:12-31`).
5. `Registry.process` builds `WebhookMetadata.new(topic:, shop: "victim.myshopify.com", body: parsed(B), ...)` (per `lib/shopify_api/webhooks/registry.rb:198-199`) and invokes the host handler as though Shopify verified this data belongs to `victim.myshopify.com`.

### Citations

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
