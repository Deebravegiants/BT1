### Title
Webhook `shop` Domain Not Covered by HMAC Signature Enables Cross-Tenant Webhook Spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant identifier (`shop`) exclusively from the `x-shopify-shop-domain` HTTP header, while `ShopifyAPI::Utils::HmacValidator` verifies the webhook HMAC only over the raw request body (`to_signable_string` returns `@raw_body`). Because the shop-domain header is never part of the signed material, an attacker holding one legitimately-signed webhook (e.g. from their own store, which they can freely trigger/receive) can resend the identical body+HMAC pair while substituting an arbitrary `x-shopify-shop-domain` value. `Registry.process` treats the HMAC check as sufficient proof of authenticity and hands the attacker-chosen `shop` straight to the app's webhook handler.

### Finding Description
`Request#shop` reads directly from the unauthenticated header: [1](#0-0) 

The signable string used for HMAC verification only includes the raw body, not any headers: [2](#0-1) 

`HmacValidator.validate` computes the signature purely from `to_signable_string` and compares it to the `hmac-sha256` header: [3](#0-2) 

`Registry.process` accepts any request that passes this body-only HMAC check, then forwards `request.shop` (the unauthenticated header value) as the tenant identifier to the handler: [4](#0-3) 

The identity binding that should hold is: `shop-domain header == the shop whose secret produced this HMAC`. Because the HMAC only signs the body, this equality is never checked — any body/HMAC pair valid for shop A can be replayed with the header changed to shop B, and the handler will process it as B's data with no cryptographic evidence that B ever sent it.

### Impact Explanation
This breaks the tenant boundary the gem is meant to enforce for webhook consumers: host applications rely on `WebhookMetadata#shop` (built directly from `request.shop`) to decide which merchant's session/data the payload applies to (e.g., `app/uninstalled`, `shop/redact`, `customers/redact`, or custom topics that don't embed the shop in the body). An attacker who controls a valid installation (their own store) can generate real, HMAC-signed webhook deliveries and then replay them against the app's webhook endpoint with the `shop-domain` header rewritten to a victim shop. Since the library asserts the request is authentic once `Utils::HmacValidator.validate` returns true, this qualifies as cross-tenant access — the strongest reachable impact for this bug class.

### Likelihood Explanation
Exploitation only requires network access to the app's public webhook endpoint and possession of one legitimately-signed webhook body (trivially obtainable by installing the app on an attacker-owned store or capturing any delivered webhook, since delivery is over plain HTTP POST and the header is not authenticated). No access token, `client_secret`, or privileged account is required — this is fully reachable by an unprivileged internet user who can install a test store.

### Recommendation
Include the shop domain (and other identity-relevant headers, such as `api-version`/`webhook-id` if relied upon by handlers) in the HMAC-signed material, or otherwise cryptographically bind the header to the payload before trusting it — e.g., have `to_signable_string` incorporate `shop` alongside the raw body, or require the host application to independently verify `request.shop` against a known-installed shop list before dispatching to the handler. At minimum, document that `request.shop` is unauthenticated and must not be used as a sole tenant-lookup key without additional verification.

### Proof of Concept
1. Attacker installs the app on `attacker.myshopify.com` and captures a real webhook delivery, e.g. `app/uninstalled`, with body `raw_body` and header `x-shopify-hmac-sha256: <valid_hmac>` (computed by Shopify using the app's real `client_secret`, which the attacker never sees).
2. Attacker resends the exact same body and `x-shopify-hmac-sha256` value to the app's webhook endpoint, but changes `x-shopify-shop-domain` to `victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request#hmac`/`#shop` parse the (now-forged) header as-is, and `HmacValidator.validate` succeeds because it only checks `raw_body` against the HMAC — the shop header is never part of the signed content (`lib/shopify_api/webhooks/request.rb:35-38`, `lib/shopify_api/utils/hmac_validator.rb:12-31`).
4. `Registry.process` invokes the handler with `WebhookMetadata(shop: "victim.myshopify.com", ...)` (`lib/shopify_api/webhooks/registry.rb:198`), causing the host application to act on `victim.myshopify.com`'s tenant context (e.g. mark it uninstalled, redact its data) using attacker-controlled/attacker-triggered webhook traffic.

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
