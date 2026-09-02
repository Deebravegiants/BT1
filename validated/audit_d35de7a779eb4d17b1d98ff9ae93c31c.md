### Title
Webhook `shop` identity is trusted for tenant routing while only the raw body is HMAC-covered, allowing cross-tenant webhook spoofing via replay - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant identifier (`shop`) from the `x-shopify-shop-domain`/`shopify-shop-domain` HTTP header, but the HMAC signature that `Utils::HmacValidator` verifies is computed only over the raw request body. The `shop` field that the host application relies on to know *which merchant* the webhook belongs to is never bound to the HMAC, so it can be swapped without invalidating the signature.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: ` [1](#0-0) `, and `HmacValidator.validate_signature` computes/compares the HMAC solely against that signable string: ` [2](#0-1) `. Meanwhile `Request#shop` is read directly from a header that is not part of that signed string: ` [3](#0-2) `.

`Registry.process` validates the HMAC and then forwards `request.shop` straight into the handler payload as the trusted tenant identity, with no independent check that this header actually corresponds to the body that was signed: ` [4](#0-3) `.

Binding that should hold but doesn't:
`HMAC(raw_body) == received_hmac` is treated by the library/host as equivalent to `shop_header == originating_shop`, but the equality actually proven is only over the body bytes, not over `(shop_header, raw_body)` jointly.

### Impact Explanation
An unprivileged internet user who can install the app on their own store (a legitimate, unprivileged action) receives genuine, correctly-HMAC'd webhooks for their own shop. Because the header carrying tenant identity is excluded from the signed payload, that attacker can replay the same body/HMAC pair to the app's webhook endpoint while substituting the `x-shopify-shop-domain` header with a victim shop's domain. `HmacValidator.validate` still returns `true` (it never inspects the header), and `Registry.process` will invoke the handler believing the event (e.g., `app/uninstalled`, `shop/redact`, `customers/data_request`, or any mandatory/compliance topic) originated from the victim tenant. This is a cross-tenant identity confusion: the host application's per-shop state (installation status, customer redaction, order data, etc., keyed off `WebhookMetadata#shop`) can be manipulated for a shop the attacker does not control, using only their own legitimately-issued webhook secret material — no leaked credentials or privileged account are required.

### Likelihood Explanation
Exploitation only requires: (1) installing the app on an attacker-owned/free-trial shop to receive a real signed webhook, and (2) replaying that request to the app's public webhook endpoint with a modified shop header — both are actions available to any unprivileged internet user with no access to the app's `client_secret` or any merchant's access token. The relevant code path (`Request#shop`, `HmacValidator.validate`, `Registry.process`) is exercised on every webhook processed by any app using this gem's `Webhooks::Registry`, making the vulnerable code unavoidable rather than opt-in.

### Recommendation
Bind the shop identity to the signed content: either include the `shop` (and ideally `topic`/`webhook_id`) header values in the HMAC-signable string used by `to_signable_string`, or require the caller to reconcile `request.shop` against a shop known to be legitimately installed (e.g., cross-check with the app's own session/shop store) before trusting it as the event's tenant in `Registry.process`. At minimum, document prominently that `request.shop` is not authenticated by the HMAC and must not be used as a sole tenant boundary.

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com`, receiving a legitimate webhook, e.g. topic `app/uninstalled`, with body `B` and header `x-shopify-hmac-sha256: HMAC(secret, B)`.
2. Attacker resends the identical body `B` and HMAC header to the app's webhook endpoint, but changes `x-shopify-shop-domain` to `victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses headers/body normally (`lib/shopify_api/webhooks/request.rb:45-63`).
4. `Utils::HmacValidator.validate` recomputes HMAC over `@raw_body` only and it matches, since the body was never altered (`lib/shopify_api/utils/hmac_validator.rb:26-31`, `lib/shopify_api/webhooks/request.rb:35-38`).
5. `Registry.process` proceeds and calls the host's handler with `shop: "victim-shop.myshopify.com"` (`lib/shopify_api/webhooks/registry.rb:198-199`), causing the host app to act on data attributed to the victim tenant it does not control.

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
