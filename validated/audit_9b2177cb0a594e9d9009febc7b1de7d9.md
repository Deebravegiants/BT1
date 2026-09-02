Confirmed root cause. The finding stands: the gem's `Registry.process` verifies HMAC over `raw_body` only, then blindly trusts the unauthenticated `x-shopify-shop-domain` header to populate `WebhookMetadata#shop`, which is the tenant-identity field passed to the merchant app's handler.

### Title
Webhook shop identity is not bound to the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` treats a webhook as authentic solely based on whether the HMAC over the raw body matches, then forwards the `shop` value taken from the `x-shopify-shop-domain`/`shopify-shop-domain` header into `WebhookMetadata#shop`, which is not covered by that HMAC at all.

### Finding Description
`ShopifyAPI::Webhooks::Request` implements `Utils::VerifiableQuery` and defines `to_signable_string` as only the raw HTTP body: [1](#0-0) 

The `shop` accessor is read directly from an attacker-controlled header and is never included in the signed material: [2](#0-1) 

`HmacValidator.validate` computes and compares the HMAC purely against `to_signable_string` (i.e., the body): [3](#0-2) 

`Registry.process` only checks this body HMAC, then constructs `WebhookMetadata` using `request.shop` — the unauthenticated header value — and hands it to the app's handler as the trusted tenant identifier: [4](#0-3) [5](#0-4) 

The binding the gem is supposed to enforce is: `hmac == HMAC(secret, body)` AND `shop == the shop that produced/authorizes body`. In reality the gem only proves the first half. Because Shopify's HMAC signature is computed only over the payload bytes and not over the sending shop's domain, and because this library does not re-derive or independently authenticate `shop`, any two webhooks with identical bodies (which is common — e.g., `app/uninstalled`, `shop/update`, or any topic with a fixed/templated or attacker-influenced body across merchants) produce the same valid HMAC regardless of which shop header is attached to the request. A merchant who controls their own shop (an "unprivileged internet user" relative to other tenants) can capture a legitimately-signed webhook delivered to their own endpoint, then resend it to the same app's webhook endpoint with the `x-shopify-shop-domain` header rewritten to a victim shop's domain. The HMAC check still passes (it never looked at the header), and the app-level handler receives `WebhookMetadata#shop` = victim shop, believing the event legitimately originated from the victim's store.

### Impact Explanation
This breaks the tenant boundary the gem is responsible for enforcing on behalf of every embedding application: the `shop` field handed to `WebhookHandler#handle` is the sole tenant-scoping signal most apps use to look up sessions, credentials, and per-shop data before acting on webhook content. An attacker who can obtain one validly-signed webhook (trivial, since they can install the app on their own shop) can forge delivery "from" any other shop by replaying the identical body with a substituted shop header, causing the app to process attacker-supplied data under another tenant's identity — cross-tenant access/data confusion, matching the High-severity criteria for scope/identity check bypass in this class of finding.

### Likelihood Explanation
Any attacker with the ability to install the target Shopify app on their own store (a normal, unprivileged action) can trigger this: request their own valid webhook, capture body+HMAC, then POST it to the app's webhook endpoint with a forged `x-shopify-shop-domain` header. No secrets, tokens, or privileged access are required.

### Recommendation
Bind `shop` (and other actioned fields such as `topic`, `api_version`, `webhook_id`) into the material that is verified, or independently authenticate the shop identity — e.g., require the caller to additionally verify that the resolved `shop` corresponds to a shop with a currently valid installation/session before trusting `WebhookMetadata#shop`, and/or document to consumers that `shop` is unauthenticated and must not be trusted for authorization decisions without further verification.

### Proof of Concept
1. Install the target app on attacker-owned shop `attacker.myshopify.com`; trigger a webhook (e.g., `app/uninstalled`) whose body is identical/predictable across shops.
2. Capture the delivered request: raw body `B` and header `x-shopify-hmac-sha256: HMAC(secret, B)`.
3. Replay the exact same body `B` and HMAC header to the app's webhook endpoint, but replace `x-shopify-shop-domain` with `victim.myshopify.com`.
4. `Utils::HmacValidator.validate` succeeds because it only checks `HMAC(secret, B)` against the body, per [6](#0-5) .
5. `Registry.process` calls the handler with `WebhookMetadata.new(... shop: "victim.myshopify.com" ...)`, and the app processes the event as if it came from the victim's shop.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-23)
```ruby
      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L35-43)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end

      sig { returns(T::Hash[String, T.untyped]) }
      def parsed_body
        JSON.parse(@raw_body)
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
