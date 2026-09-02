## Analysis: Webhook shop-domain header is not covered by the HMAC signature

The external report describes a class of bug where a value that is *checked* differs from the value that is actually *used/trusted*. The strongest analog in this gem is in the webhook-processing path, where the HMAC signature only covers the request body, while the `shop` value used to attribute/dispatch the webhook is read from an unauthenticated header and is never included in what's verified.

### Root cause

`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw body: [1](#0-0) 

`shop` is derived from the `shopify-shop-domain`/`x-shopify-shop-domain` HTTP header, which is attacker-controllable and not part of the signed content: [2](#0-1) 

`HmacValidator.validate` computes the signature over `to_signable_string` (the body only) and compares it against the `hmac` header — it never incorporates `shop`: [3](#0-2) 

`Registry.process` validates the HMAC of the request, then dispatches to the handler using `request.shop` taken directly from the unauthenticated header — the exact field that was never covered by the signature check: [4](#0-3) 

### The broken identity binding

The intended invariant is: `shop attributed to webhook == shop that the HMAC over the payload was actually signed for`. In practice the code enforces: `HMAC(secret, body) == received_hmac` while using `shop = header value`, which is a completely independent, unauthenticated channel. Since Shopify apps use a single `api_secret_key` shared across all shops that install the app (not a per-shop secret), this is exactly the pattern called out in the rules: "a field acted on but not covered by the HMAC."

### Exploitability

Because the secret is shared across all installs of the same app, a malicious merchant who has installed the app on their own shop (Shop A) will legitimately receive webhooks (valid `body` + `hmac` pairs) from Shopify. That attacker can then replay the same body/HMAC pair to the app's webhook endpoint while rewriting the `shopify-shop-domain` header to a victim shop's domain (Shop B). `HmacValidator.validate` still returns `true` (the body and secret are unchanged), and `Registry.process` will hand `WebhookMetadata` down to the app's handler with `shop: "shop-b.myshopify.com"` even though the payload was never signed in relation to Shop B. Any host application that trusts `WebhookMetadata#shop` to select which tenant's data/session to act on (a well-documented and expected usage pattern for this gem, per `docs/`) will process/attribute data cross-tenant.

This matches the required impact bar: cross-tenant access achieved purely through this gem's own verification logic, without needing the app's `client_secret`, an access token, or any privileged account — only the ability to install the app on one's own store (an "unprivileged internet user" from the perspective of the victim shop).

### Title
Webhook shop attribution is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` derives the `shop` identity solely from the unauthenticated `shopify-shop-domain`/`x-shopify-shop-domain` header, while `to_signable_string` (the value the HMAC is verified against) only encodes the raw body. `Registry.process` verifies the HMAC and then trusts `request.shop` for dispatch, so the value that's checked (body integrity for the app's shared secret) is not the value that's used to identify the tenant (the shop header).

### Finding Description
- `Request#shop` reads `shopify-shop-domain` from request headers with no cryptographic binding: `lib/shopify_api/webhooks/request.rb:20-23`.
- `Request#to_signable_string` returns only `@raw_body`, excluding `shop`, `topic`, and other headers from the signed content: `lib/shopify_api/webhooks/request.rb:35-38`.
- `Utils::HmacValidator.validate` computes `HMAC(secret, to_signable_string)` and compares to the `hmac` header, using the app's single `api_secret_key` shared by all shop installs: `lib/shopify_api/utils/hmac_validator.rb:12-31`.
- `Registry.process` validates only the HMAC of the body, then constructs `WebhookMetadata` using `request.shop` taken straight from the header, handing it to the app's handler as trusted tenant identity: `lib/shopify_api/webhooks/registry.rb:188-199`.

The equality that should hold is: `shop_bound_by_hmac == shop_used_for_dispatch`. Instead the code enforces `hmac_is_valid_for(body)` and separately uses `shop_from_header` for dispatch — these are two unrelated values.

### Impact Explanation
Because `api_secret_key` is shared across all merchants who install the same app (not scoped per shop), any merchant who installs the app can obtain a valid `(body, hmac)` pair for their own shop and then forge a webhook request for a different shop by only changing the `shop-domain` header. Any host application built on top of this gem's documented `WebhookMetadata#shop` value (the intended, supported way to identify the webhook's originating tenant) will process the forged payload as though it belongs to the victim shop — a cross-tenant confusion/spoofing condition, meeting the "Critical - cross-tenant access" bar.

### Likelihood Explanation
The only prerequisite is installing the target app on an attacker-controlled shop (a normal, unprivileged action for any Shopify merchant) and being able to send HTTP requests to the app's public webhook endpoint with custom headers — no access token, `client_secret`, or privileged account is required.

### Proof of Concept
1. Attacker installs the app on their own store `attacker.myshopify.com` and triggers any webhook (e.g. `orders/create`), capturing the legitimate request: `raw_body`, and the `shopify-hmac-sha256` header.
2. Attacker replays this exact `raw_body`/HMAC pair to the app's webhook endpoint but replaces the `shopify-shop-domain` header with `victim.myshopify.com`.
3. `HmacValidator.validate` recomputes `HMAC(api_secret_key, raw_body)` — unchanged — and returns `true`: `lib/shopify_api/utils/hmac_validator.rb:12-22`.
4. `Registry.process` proceeds and builds `WebhookMetadata.new(topic: ..., shop: "victim.myshopify.com", body: ..., ...)`, invoking the app's handler as if the data came from the victim shop: `lib/shopify_api/webhooks/registry.rb:190-199`.

### Recommendation
Bind the `shop` (and other dispatch-relevant fields) into the value that is actually verified — e.g., include the shop domain in the signable content, or independently verify that the `shop-domain` header corresponds to a shop with an active, previously-established session/webhook registration before trusting it for dispatch.

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
