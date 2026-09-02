This confirms the analog: `Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , while `shop`, `topic`, `webhook_id`, and `api_version` are all read directly from unauthenticated HTTP headers [2](#0-1) . `HmacValidator.validate` only checks that the HMAC matches `to_signable_string` (the raw body) [3](#0-2) , and `Registry.process` then trusts `request.shop`, `request.topic`, etc. and forwards them to the app's handler without any additional binding [4](#0-3) .

### Title
Webhook `shop-domain`/`topic`/`webhook_id` headers are not covered by the HMAC, allowing shop-spoofing of otherwise-authentic webhook deliveries - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
Shopify webhooks are signed using the app's single shared `client_secret` (`Context.api_secret_key`) — the same secret is used for every shop that installs the app, not a per-shop secret. This gem's `Webhooks::Request#to_signable_string` only returns the raw body [1](#0-0) , so the HMAC verification performed in `HmacValidator.validate`/`validate_signature` only proves "this body was signed with the app secret", not "this body came from shop X" [3](#0-2) . The `shop`, `topic`, `webhook_id`, and `api_version` values consumed by `Registry.process` are read straight from attacker-controllable HTTP headers and are never part of the signed payload [2](#0-1) .

### Finding Description
The identity binding that should hold is:
`shop attributed to webhook data == shop that actually generated/owns that HMAC-signed body`

Because only `@raw_body` is fed into the HMAC computation [1](#0-0) , and the app-wide `client_secret` used to sign webhooks is identical across all shops that installed the app, any actor who controls a shop that has installed the app (an "unprivileged" — from the app's perspective, not admin — tenant) receives real webhook deliveries with valid HMACs computed over bodies they at least partly control (e.g., product/order payloads containing attacker-editable text fields, or by replaying a previously captured body). That actor can then re-POST the exact same `raw_body` + valid `hmac-sha256` header to the app's webhook endpoint while substituting the `shopify-shop-domain`, `shopify-topic`, and `shopify-webhook-id` headers, since none of those are bound to the signature.

`Registry.process` validates only the HMAC over the body and then unconditionally trusts `request.shop`/`request.topic`/`request.webhook_id` when building `WebhookMetadata` for the app's handler [4](#0-3) . If the host application uses `data.shop` to route/attribute the payload to a tenant record (the documented, intended use of `WebhookMetadata#shop`), the attacker can make a validly-signed webhook (from their own shop) appear to originate from any other shop domain of their choosing.

### Impact Explanation
This breaks the tenant-identity binding at the point the gem hands verified data to the app: the gem asserts "this data is confirmed authentic and is attributed to shop X" when in fact only the body's authenticity (not its shop attribution) was verified. This enables cross-tenant data injection/confusion — a malicious merchant/app-installer can inject attacker-influenced, validly-"authenticated" webhook payloads attributed to a victim shop domain, since the gem provides no attribute other than the unauthenticated header to distinguish tenants. This matches the High-severity class of scope/expiry-style check bypass via an identity field not covered by the cryptographic proof.

### Likelihood Explanation
Any threat actor able to install the app on at least one shop (a normal, unprivileged path — installing a public Shopify app requires no special privilege) can receive genuine webhooks with valid signatures and replay them with modified identity headers, since HTTP headers on webhook deliveries are not authenticated by the gem's verification routine.

### Recommendation
Include `shop`, `topic`, and `webhook_id` in the signable string used by `Webhooks::Request#to_signable_string`, or otherwise cryptographically bind them (e.g., in the body) before verification, so that HMAC validation authenticates the shop/topic attribution, not just the raw body bytes.

### Proof of Concept
1. App has a shop `attacker.myshopify.com` installed; attacker triggers/receives a webhook for that shop with a body they can influence (e.g., a product-update webhook with a crafted title/description field) and a legitimately-computed `x-shopify-hmac-sha256` header (computed by Shopify using the app-wide `client_secret`).
2. Attacker resends this exact `raw_body` and `hmac-sha256` header to the app's webhook endpoint but replaces the `x-shopify-shop-domain` header value with `victim.myshopify.com` (and adjusts `topic`/`webhook-id` as desired).
3. `HmacValidator.validate` in `lib/shopify_api/utils/hmac_validator.rb` succeeds because it only checks the body bytes against the HMAC [3](#0-2) .
4. `Registry.process` in `lib/shopify_api/webhooks/registry.rb` proceeds and calls the app's handler with `shop: "victim.myshopify.com"` even though the payload actually originated from the attacker's shop [5](#0-4) .

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
