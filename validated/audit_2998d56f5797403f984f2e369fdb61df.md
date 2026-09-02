### Title
Webhook `shop`, `topic`, and `webhook-id` are trusted from unauthenticated headers while the HMAC signs only the raw body - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely via `Utils::HmacValidator.validate(request)`, and that validator only signs/verifies `request.to_signable_string`, which is defined as the raw HTTP body. All other webhook identity fields—`shop`, `topic`, `webhook_id`, `api_version`—are read straight from HTTP headers and are never included in the signed material, yet they are passed unmodified into the handler as tenant/routing identity.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

The HMAC validator computes and compares the signature purely against that signable string: [2](#0-1) 

Meanwhile `shop`, `topic`, `webhook_id`, and `api_version` are parsed directly from HTTP headers with no cryptographic binding to the body or to each other: [3](#0-2) 

`Registry.process` validates only the HMAC and then dispatches the handler using the unauthenticated `request.topic` and forwards the unauthenticated `request.shop` directly into `WebhookMetadata` as the tenant identity for the handler to act on: [4](#0-3) 

The identity binding that is broken is:
`bytes cryptographically verified (raw request body only)` ≠ `bytes/headers actually parsed and trusted as tenant+event identity (shop-domain, topic, webhook-id headers)`.

Because the app's `client_secret` (used as the HMAC key via `Context.api_secret_key`) is a single shared secret across every shop that installs the app, any shop owner can legitimately install the app on their own store and receive real, validly-HMAC-signed webhook deliveries for that shop. Since the signature covers only the JSON body bytes—never the `x-shopify-shop-domain`, `x-shopify-topic`, or `x-shopify-webhook-id` headers—an attacker who controls a shop that has installed the target app can capture a genuine webhook delivery (with a valid HMAC over its body) and replay it to the app's public webhook endpoint with the `x-shopify-shop-domain` header rewritten to a different (victim) shop domain, and/or the `x-shopify-topic` header rewritten to a different topic. `HmacValidator.validate` will still pass because it only checks the untouched body bytes, and `Registry.process` will hand the forged shop/topic combination straight to the app's registered handler as if Shopify itself vouched for that shop and topic.

### Impact Explanation
This breaks the tenant boundary the whole webhook subsystem relies on: an unprivileged attacker who is merely a legitimate installer of the app on their own store can cause the host application to process attacker-controlled body content under an arbitrary victim shop identity (cross-tenant data injection/confusion), or cause a body meant for one topic to be dispatched under a different topic label of the attacker's choosing (topic confusion, e.g. tricking mandatory GDPR handlers like `customers/redact` or `shop/redact` into acting on the wrong tenant). This is a cross-tenant access issue, matching the Critical impact bucket in the rules (cross-tenant access via an identity field that is validated on one axis—body bytes—but trusted on another—header-derived shop/topic).

### Likelihood Explanation
The prerequisite is only that the attacker can install the target app on a shop they control (an ordinary, unprivileged action any merchant can perform) and can send arbitrary HTTP requests to the app's public webhook endpoint (which by design must be internet-reachable to receive Shopify's webhooks). No access token, `api_secret_key`, or privileged account is required—only observing/capturing one legitimately delivered webhook for their own shop and replaying it with modified headers.

### Recommendation
Include `shop`, `topic`, and `webhook_id` in the value that is HMAC-verified (or otherwise cryptographically bind them to the signed body), and reject any webhook whose header-derived identity fields do not match validated, expected values. At minimum, `Registry.process` should not trust `request.shop`/`request.topic` for tenant-critical actions unless they are corroborated by out-of-band means (e.g., cross-checking the shop against a known/expected shop for that delivery, or validating uniqueness/expected topic per registration).

### Proof of Concept
1. App is installed on `attacker-shop.myshopify.com`; Shopify sends a legitimate webhook, e.g.:
   ```
   POST /webhooks
   x-shopify-topic: orders/create
   x-shopify-hmac-sha256: <valid HMAC over raw body, keyed with the app's shared client_secret>
   x-shopify-shop-domain: attacker-shop.myshopify.com
   x-shopify-webhook-id: <id>
   Body: {"id": 1, ...attacker-controlled order payload...}
   ```
2. Attacker captures this request (they control the receiving traffic on their own shop's webhook delivery only insofar as they can intercept/replay it since it is just an HTTP POST to the app's endpoint; no encryption on headers is required to change them post-signature since headers aren't signed).
3. Attacker resends the identical body and HMAC value, but with:
   ```
   x-shopify-shop-domain: victim-shop.myshopify.com
   ```
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only checks the raw body against the HMAC — see `lib/shopify_api/utils/hmac_validator.rb:26-31` and `lib/shopify_api/webhooks/request.rb:35-38`.
5. The handler is invoked with `WebhookMetadata.new(topic: "orders/create", shop: "victim-shop.myshopify.com", body: <attacker payload>, ...)` — see `lib/shopify_api/webhooks/registry.rb:198-199` — causing the host application to process attacker-supplied data under the victim shop's tenant identity.

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
