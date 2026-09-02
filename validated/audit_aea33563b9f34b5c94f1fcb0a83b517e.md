This confirms the finding: `WebhookMetadata.shop` (lib/shopify_api/webhooks/webhook_handler.rb:6-8) carries `request.shop` (lib/shopify_api/webhooks/request.rb:20-23), which is read from the unauthenticated `x-shopify-shop-domain`/`shopify-shop-domain` header, while `Utils::HmacValidator.validate` (lib/shopify_api/utils/hmac_validator.rb:12-22) only verifies `to_signable_string`, which is defined as `@raw_body` alone (lib/shopify_api/webhooks/request.rb:35-38). The shop identity delivered to the host app's handler is never part of the HMAC-verified bytes.

### Title
Webhook shop-domain identity is not bound to the HMAC signature, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable content solely from the raw request body, while the `shop` (tenant) identifier is read from an HTTP header that is completely outside the HMAC. `ShopifyAPI::Webhooks::Registry.process` validates only the body signature and then hands the unauthenticated header-derived `shop` value straight to the host application's `WebhookHandler` via `WebhookMetadata`. Any request bearing a previously-valid `(body, hmac)` pair, but with the `shop`/`shopify-shop-domain` header changed to a different merchant, will pass `HmacValidator.validate` and be dispatched to the handler labeled as coming from the attacker-chosen shop.

### Finding Description
The equality that should hold is: `shop authenticated by HMAC == shop delivered to the handler`. In this gem it does not:

- `Request#hmac` and `Request#to_signable_string` only cover `@raw_body`: [1](#0-0) [2](#0-1) 
- `Request#shop` is parsed straight from an attacker-controlled HTTP header, with no cross-check against the signed body: [3](#0-2) 
- `Registry.process` validates the HMAC of the body only, then forwards `request.shop` unchanged into `WebhookMetadata`, which is the only tenant-identifying field the host application's `handle(data:)` callback receives: [4](#0-3) [5](#0-4) 

Since the same `api_secret_key` (client secret) is shared across every shop that installs the app, `compute_signature`/`validate_signature` in `HmacValidator` produce/accept the exact same HMAC for the same body regardless of which shop the body actually originated from: [6](#0-5) 

An unprivileged attacker who controls their own installed shop (or who has captured/observed one legitimate webhook delivery) can obtain a valid `(raw_body, hmac)` pair for content they influence (e.g., by creating an order or product in their own store to trigger `orders/create` or similar), then replay that exact body and HMAC to the app's webhook endpoint while substituting the `x-shopify-shop-domain` (or `shopify-shop-domain`) header with a victim shop's domain. `HmacValidator.validate` still returns `true` because it never inspects the header, and `Registry.process` dispatches the payload to the handler as if it were verified data belonging to the victim shop.

### Impact Explanation
This breaks the tenant boundary the HMAC is supposed to enforce: a signature that only proves "this body was sent by someone who knows the app's `client_secret`" is treated by the library as also proving "this body belongs to shop X," which it does not. Downstream host applications that key their session/database lookups on `WebhookMetadata#shop` (the documented, expected usage of this API) will process or persist attacker-supplied data under another merchant's tenant record, i.e. cross-tenant data injection/corruption via a spoofed identity field that this gem asserts is authenticated by the HMAC check it performs.

### Likelihood Explanation
Medium-to-High: the attacker only needs their own Shopify installation (a normal unprivileged capability) to generate valid `(body, hmac)` pairs, then a single unauthenticated HTTP POST to the target app's public webhook endpoint with a modified shop header. No access token, `client_secret`, or victim credentials are required.

### Recommendation
Include the shop domain (and ideally topic/webhook-id) inside the HMAC-signable material, or require `Registry.process`/`HmacValidator` to validate the header-derived `shop` against a value embedded in the signed body/claims before constructing `WebhookMetadata`. At minimum, document that `request.shop` is not cryptographically authenticated and must not be trusted for tenant identification without an independent check (e.g., matching it against a shop already provisioned via OAuth for the current session).

### Proof of Concept
1. Attacker installs the app on their own dev shop `attacker.myshopify.com` and triggers a webhook (e.g. `orders/create`) with a body they control, capturing the real `x-shopify-hmac-sha256` value Shopify computed with the app's shared `client_secret`.
2. Attacker sends a POST to the app's webhook endpoint with the identical `raw_body` and `x-shopify-hmac-sha256`, but sets `x-shopify-shop-domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only recomputes the HMAC over `raw_body` — [2](#0-1)  — and this matches, so validation passes.
4. The handler receives `WebhookMetadata.new(topic:, shop: "victim.myshopify.com", body:, ...)` — [7](#0-6)  — and the host app processes attacker-controlled data as authenticated content for the victim's tenant.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-13)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
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

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L6-12)
```ruby
    class WebhookMetadata < T::Struct
      const :topic, String
      const :shop, String
      const :body, T::Hash[String, T.untyped]
      const :api_version, String
      const :webhook_id, String
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
