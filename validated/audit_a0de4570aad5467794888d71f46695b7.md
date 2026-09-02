### Title
Webhook `shop` (tenant) identity is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by verifying an HMAC over the raw request body. The `shop` value that is later used to attribute the event to a specific merchant/tenant is read from the `X-Shopify-Shop-Domain` header, which is **not** part of the signed payload. Because the signing secret (`api_secret_key`/`client_secret`) is shared by every shop that has installed the same app, anyone who controls one legitimate installation of the app can obtain a validly-signed `(body, hmac)` pair from their own store and replay it against the app's webhook endpoint with the `shop-domain` header rewritten to a victim shop, causing the handler to process/act on the payload as if it belonged to the victim tenant.

### Finding Description
The signable string for a webhook request is defined as only the raw body: [1](#0-0) 

The `shop` accessor, by contrast, is derived purely from an unauthenticated header: [2](#0-1) 

`Registry.process` validates the request using `Utils::HmacValidator.validate(request)`, which only checks `request.hmac` against `compute_signature(request.to_signable_string, secret)` — i.e., against the raw body — and then immediately trusts `request.shop` to build the metadata handed to the app's handler: [3](#0-2) [4](#0-3) 

The equality this breaks: `verified(hmac, body) == authorized(shop)`. The HMAC only proves *"this body was signed with this app's `client_secret`"* — it does **not** prove *"this body came from shop X"*. Since `client_secret` is a single value shared across every shop that has installed a given app (not shop-specific), an attacker who legitimately installs the target app on their own store can trigger any webhook topic they choose on their own store, capture the resulting `(raw_body, X-Shopify-Hmac-Sha256)` pair — both fully valid — and then send that exact body/HMAC pair to the app's webhook endpoint with `X-Shopify-Shop-Domain` rewritten to the victim's domain. `HmacValidator.validate` will still return `true` because it never looks at the shop header, and `Registry.process` will dispatch the handler with `WebhookMetadata.new(..., shop: request.shop, ...)` pointing at the victim shop.

### Impact Explanation
This breaks the tenant isolation the gem's webhook API is supposed to provide to consuming apps: `WebhookMetadata#shop` is the field host applications are expected to use to key their per-merchant data (session lookup, data updates, GDPR redaction flows for `customers/redact`/`shop/redact`, etc., which are also handled through this same path). An attacker can spoof cross-tenant events for any shop domain of their choosing carrying attacker-controlled body content signed with a validly-obtained HMAC, enabling cross-tenant data corruption/injection — a Critical-impact issue under the stated rubric (cross-tenant access).

### Likelihood Explanation
Any actor who can install the target app on a store they control (which is the normal, low-privilege way to become an app user) can generate an arbitrary number of validly-signed `(body, hmac)` pairs for any webhook topic subscribed by the app, then replay them with a forged `shop-domain` header at the app's public webhook endpoint. No access token, `client_secret` knowledge, or privileged account is required beyond a self-service app install, which is well within the "unprivileged internet user" threat model.

### Recommendation
Bind the tenant identity to the signature verification step rather than trusting an unauthenticated header. At minimum, `to_signable_string` in `lib/shopify_api/webhooks/request.rb` should incorporate the `shop` header (and ideally `topic`/`webhook_id`) into the HMAC-covered string, or the gem should document/require that consuming apps additionally verify `shop` is one of their own known/installed shops before trusting the payload's contents. Shopify's own webhook signing does not include headers in the HMAC, so this really needs to be mitigated at the "known installed shop" verification layer inside `Registry.process`/`WebhookMetadata`, rejecting shops that are not recognized installs of the app.

### Proof of Concept
1. Attacker installs Target App on `attacker-shop.myshopify.com` (self-service, no special privilege).
2. Attacker triggers a webhook (e.g. `orders/create`) on their own shop, capturing the exact raw body `B` and the resulting `X-Shopify-Hmac-Sha256: H` sent by Shopify (both are valid because they're signed with the app's shared `client_secret`).
3. Attacker POSTs `B` to the app's public webhook endpoint with headers:
   - `X-Shopify-Hmac-Sha256: H` (unchanged, still valid for body `B`)
   - `X-Shopify-Shop-Domain: victim-shop.myshopify.com` (forged)
   - `X-Shopify-Topic: orders/create`
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only checks `H` against `B`.
5. The app's registered handler is invoked with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: <attacker-controlled>, ...)`, and any app that keys tenant data lookups/writes off `data.shop` now processes attacker-controlled data under the victim tenant's identity.

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
