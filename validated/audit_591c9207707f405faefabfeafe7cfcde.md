Confirmed: no sanitization occurs anywhere for the webhook `shop` value — it flows directly from an unauthenticated header into the handler.

### Title
Webhook shop-domain header is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` signs only the raw request body for HMAC validation, while the shop identity (`shopify-shop-domain` header) that is handed to the webhook handler as the authoritative tenant is never included in that signature. An attacker who can obtain any validly-signed webhook body (e.g., by installing the app on their own, attacker-controlled shop and capturing a real webhook delivery) can replay that exact body/HMAC pair to the app's public webhook endpoint while substituting the `shop-domain` header with a victim shop's domain, causing the app to process attacker-controlled data under the victim's tenant identity.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

The `shop` accessor is read straight from the `shopify-shop-domain`/`x-shopify-shop-domain` header with no cryptographic binding to the body or the HMAC: [2](#0-1) 

`ShopifyAPI::Webhooks::Registry.process` validates the request purely via `Utils::HmacValidator.validate(request)`, which only compares the HMAC of `to_signable_string` (i.e., the body) against the secret-derived signature: [3](#0-2) [4](#0-3) 

After that check passes, `request.shop` (the unauthenticated header value) is passed straight through as the tenant identifier to the app's handler: [5](#0-4) 

The identity binding that should hold is: `hmac_signed_bytes == bytes_the_handler_trusts_as_this_shop's_data`. In this implementation, `hmac_signed_bytes == raw_body` only, while `bytes_the_handler_trusts_as_this_shop's_data == (shop header, raw_body)`. Because `shop` is outside the signed scope, the two sides diverge: a byte-for-byte valid, secret-signed body can be paired with any attacker-chosen `shop` header and still pass validation.

### Impact Explanation
This breaks the tenant (shop) boundary that host applications built on this gem rely on to route and attribute webhook data. An unprivileged internet user who can install the target app on any shop they control (trivial for public apps distributed via the Shopify App Store, including free development stores) can:
1. Trigger a real webhook (e.g., a product/order update) on their own shop, producing a body they substantially control and a valid HMAC signed with the app's real `api_secret_key`.
2. Replay that exact `raw_body` + `hmac-sha256` header pair to the app's public webhook endpoint, changing only the `shopify-shop-domain` (and `webhook-id`/`api-version`, which are equally unsigned) header to name a victim shop.
3. `HmacValidator.validate` passes (body/signature unchanged), and the handler receives `WebhookMetadata` believing the payload originated from the victim shop.

Depending on how the host app's handler uses `shop` (e.g., to key database writes, trigger app actions, or invalidate/update per-tenant state), this enables cross-tenant data injection/corruption attributed to a shop the attacker does not control — a cross-tenant boundary violation stemming directly from this gem's webhook verification design.

### Likelihood Explanation
Exploitability requires only: (a) the ability to install the app on an attacker-controlled shop (routine, unprivileged, and free for many app distribution models), and (b) capturing one legitimately delivered webhook body for that shop, both readily achievable without any leaked secrets or privileged access. The webhook endpoint is public-facing by design (it must receive unauthenticated HTTP POSTs from "Shopify"), and this gem provides no other binding (e.g., signing headers, nonce/timestamp-bound shop claim) to prevent header substitution.

### Recommendation
Include the shop domain (and ideally `webhook-id`/`topic`/`api-version`) inside the HMAC-signed material, or otherwise cryptographically bind the claimed shop to the verified payload, instead of trusting an unsigned header. If Shopify's wire format only signs the body (matching real Shopify webhook behavior), the gem should document this limitation prominently and/or offer an opt-in mechanism for callers to assert the expected shop for a given webhook context, rather than silently exposing `request.shop` as if it were verified.

### Proof of Concept
1. Attacker signs up as a Shopify Partner and creates/installs the vulnerable app on `attacker-shop.myshopify.com` (no special privilege needed).
2. Attacker triggers a webhook event on their own shop (e.g., updates a product with attacker-chosen JSON content) and captures the resulting HTTP POST, including the `X-Shopify-Hmac-Sha256` header and raw body — both validly signed with the app's real `api_secret_key`.
3. Attacker replays the identical raw body and `X-Shopify-Hmac-Sha256` header to the app's webhook endpoint, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks the (unchanged) raw body against the (unchanged) signature: [6](#0-5) 
5. The handler is invoked with `WebhookMetadata.new(topic: request.topic, shop: request.shop, body: request.parsed_body, ...)` where `shop` is `"victim-shop.myshopify.com"` and `body` is attacker-controlled — the app now processes attacker data as if it belongs to the victim tenant: [5](#0-4)

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-38)
```ruby
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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-22)
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
