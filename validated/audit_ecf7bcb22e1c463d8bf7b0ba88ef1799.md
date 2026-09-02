### Title
Webhook `shop`/`topic`/`webhook-id` identity fields are not covered by HMAC verification, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw HTTP body, so the HMAC signature validated by `Utils::HmacValidator.validate` only proves the integrity of the body — it says nothing about the `shop-domain`, `topic`, or `webhook-id` headers. `Registry.process` nevertheless trusts `request.shop` (taken straight from the unauthenticated header) as the tenant identity passed to the app's webhook handler. This breaks the binding "shop verified by HMAC == shop delivered to the handler."

### Finding Description
`Request#to_signable_string` is defined as: [1](#0-0) 
which returns only `@raw_body`. `HmacValidator.validate_signature` computes the HMAC over exactly that signable string: [2](#0-1) 
Meanwhile `request.shop`, `request.topic`, and `request.webhook_id` are read directly from HTTP headers with no cryptographic binding to the body or the HMAC: [3](#0-2) 
`Registry.process` validates only the HMAC of the body, then forwards `request.shop` unchanged as the tenant identifier to the app-supplied handler: [4](#0-3) 

Because Shopify apps share a single `client_secret` across every shop that installs the app, any shop owner (an "unprivileged internet user" relative to other tenants of the same app) that receives a legitimately signed webhook for their own store possesses a valid `(raw_body, hmac)` pair. Since the header carrying the tenant identity (`shop-domain`) is not part of the signed content, that attacker can resend the same body+HMAC to the app's webhook endpoint while substituting an arbitrary `shop-domain` (and `topic`/`webhook-id`) header. `HmacValidator.validate` will report success (the body/HMAC pair is genuine), and `Registry.process` will hand the handler a `WebhookMetadata` whose `shop` field names a victim tenant while `body` actually contains the attacker's own shop's data.

### Impact Explanation
This is a cross-tenant identity-binding failure inside the gem itself, not a misuse by the host app: the gem's own `process` method is the one that treats the unauthenticated `shop` header as trustworthy tenant identity after "verifying" the request. Any app that stores/dispatches webhook payloads keyed by `WebhookMetadata#shop` (the intended and documented use of this field) can be made to associate attacker-controlled webhook data with a different merchant's shop, i.e., cross-tenant data injection/confusion — a Critical-tier impact per the rules (cross-tenant access).

### Likelihood Explanation
Any merchant that has installed the vulnerable app on their own store can trivially capture a genuine `(raw_body, hmac)` pair from their own webhook deliveries (e.g., via a proxy) and replay it against the app's public webhook endpoint with a forged `shop-domain` header, since no other control (e.g., IP allow-listing of Shopify, mTLS) is enforced by this library. No access token, `client_secret`, or privileged access is required beyond operating one's own installed shop instance.

### Recommendation
Bind the `shop-domain` (and ideally `topic`, `webhook-id`) headers into the signed material verified against the HMAC, or independently verify that the shop in the header matches a shop with an active, previously-registered webhook/app installation before dispatching to the handler. At minimum, `Registry.process` should not trust `request.shop` unless it can be cryptographically tied to the same signature used to validate the payload.

### Proof of Concept
1. Attacker installs the target app on their own dev/test shop `attacker.myshopify.com` and lets Shopify deliver a legitimate webhook, capturing `raw_body` and the `X-Shopify-Hmac-SHA256` header value.
2. Attacker POSTs to the app's webhook endpoint with the same `raw_body`/HMAC but sets `X-Shopify-Shop-Domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks `raw_body` against the HMAC.
4. The handler receives `WebhookMetadata.new(shop: "victim.myshopify.com", body: <attacker's own data>, ...)`, causing the app to process/store attacker-controlled data under the victim shop's tenant identity.

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
