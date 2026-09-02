## Title
Webhook HMAC signs only the raw body, not the `shop-domain`/`topic` headers — breaks the shop-authentication binding and enables cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
The `flashProof` report describes a security check bound to the wrong identity (`tx.origin` instead of the actual caller), so the check doesn't actually protect the resource it's meant to protect. The same class of bug exists in `ShopifyAPI::Webhooks::Request`/`Registry`: the webhook HMAC signature only covers the raw request body, while the `shop` and `topic` values used to route and attribute the webhook to a tenant are taken from unauthenticated HTTP headers that are never included in the signed payload.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Utils::HmacValidator.validate_signature` computes the HMAC over exactly that signable string and compares it against the received `hmac-sha256` header: [2](#0-1) 

`Registry.process` validates only this body-only HMAC, then immediately trusts `request.topic` and `request.shop` — both read straight from unauthenticated headers via `shopify_header` — to route to a handler and to build the tenant-identifying `WebhookMetadata`: [3](#0-2) [4](#0-3) [5](#0-4) 

The binding the HMAC is supposed to enforce is: `hmac == HMAC(secret, body ∧ shop ∧ topic)`. In reality it only enforces `hmac == HMAC(secret, body)`; `shop` and `topic` are unauthenticated bytes that the handler nonetheless treats as verified. This is exactly the pattern called out in the rules: "a field acted on but not covered by the HMAC."

### Impact Explanation
Because `shop` (and `topic`) are not part of the signed content, any raw body/HMAC pair that is valid for one shop is also valid for any other `shop-domain`/`topic` header combination. An unprivileged user who legitimately installs the target app on their own store (a normal, unprivileged action any merchant can perform) will receive genuine Shopify webhook deliveries with a real, secret-derived HMAC over their own body content. That exact `(raw_body, hmac)` pair can be replayed directly to the app's webhook endpoint with an arbitrary `x-shopify-shop-domain` (and `x-shopify-topic`) header, since `Registry.process` never checks that the signed body actually belongs to the shop claimed in the header. The host application's handler will then process the payload as if it originated from the spoofed shop — a cross-tenant confusion/impersonation that lets a merchant inject fabricated business events (order/customer/app-uninstalled, etc.) attributed to a different, victim tenant.

### Likelihood Explanation
Likelihood is high for any body content that is static, predictable, or reusable across shops (e.g., topics with fixed/empty JSON bodies, or bodies whose merchant-identifying fields live only in the JSON, not enforced separately) — the attacker only needs one genuine signed delivery from their own store to obtain a working `(body, hmac)` pair, then can freely vary the `shop`/`topic` headers when replaying it to the target endpoint.

### Recommendation
Include the `shop` (and ideally `topic`) values in the signed content, or otherwise cryptographically bind the header-derived `shop`/`topic` to the HMAC-verified body before they are used for routing/tenant attribution in `Registry.process` and `WebhookMetadata`.

### Proof of Concept
1. Install the target app on shop `attacker.myshopify.com`; subscribe to a webhook topic whose payload is static/predictable (e.g. `"{}"`).
2. Receive the genuine Shopify-delivered webhook request with headers `x-shopify-hmac-sha256: <valid hmac for "{}">`, `x-shopify-shop-domain: attacker.myshopify.com`.
3. Replay the identical raw body and `x-shopify-hmac-sha256` value to the app's webhook endpoint, but set `x-shopify-shop-domain: victim.myshopify.com` (and any registered `x-shopify-topic`).
4. `Utils::HmacValidator.validate` succeeds (it only checks the body against the secret) as shown in [6](#0-5) , and the handler processes the event believing it came from `victim.myshopify.com`.

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

**File:** lib/shopify_api/webhooks/request.rb (L67-70)
```ruby
      sig { params(name: String).returns(T.untyped) }
      def shopify_header(name)
        @headers["shopify-#{name}"] || @headers["x-shopify-#{name}"]
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
