Confirmed: `to_signable_string` for the webhook `Request` class only covers `@raw_body` [1](#0-0) , while `shop`, `topic`, `api_version`, and `webhook_id` are all read directly from unauthenticated HTTP headers [2](#0-1) . `Registry.process` validates only the HMAC of the body, then passes `request.shop` straight to the handler as the tenant identity [3](#0-2) .

### Title
Webhook shop identity spoofing via unauthenticated `shop-domain` header not covered by HMAC - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request#shop` is read from the `x-shopify-shop-domain`/`shopify-shop-domain` HTTP header, but `HmacValidator.validate` only verifies `request.to_signable_string`, which returns the raw request body only [1](#0-0) . The shop identity attribute that the host app relies on to attribute the event to a tenant is not part of the signed material.

### Finding Description
`Registry.process` enforces `Utils::HmacValidator.validate(request)` before dispatching the webhook to the app's handler [4](#0-3) . `HmacValidator.validate_signature` computes the HMAC over `verifiable_query.to_signable_string` and compares it with the received `hmac` [5](#0-4) . For `Webhooks::Request`, `to_signable_string` returns only `@raw_body` [1](#0-0) , while `shop` is derived independently from the `shop-domain` header, which is not included in the HMAC-covered bytes [6](#0-5) . The equality the code implicitly assumes is: `shop used by handler == shop that produced the signed body`. In reality the gem only proves `hmac == HMAC(secret, raw_body)`; it proves nothing about which shop header accompanied that body. Since all shops installed under the same app share the same `api_secret_key`, any merchant who installs the app (an unprivileged, arbitrary internet user relative to other tenants) can capture one of their own genuine webhook deliveries (valid body + valid HMAC), then resend that exact body/HMAC pair to the app's webhook endpoint while substituting an arbitrary victim shop domain in the `shop-domain` header. `Request.new` never checks the header value against anything derived from the signed bytes, and `Registry.process` forwards `request.shop` (attacker-controlled) straight into `WebhookMetadata` for the handler [7](#0-6) .

### Impact Explanation
This breaks a cross-tenant identity binding: a merchant/attacker can make the host application believe a forged event body originated from a different, victim shop. Depending on how the host app's `WebhookHandler#handle` uses `data.shop` (e.g., to look up/update per-shop records, cancel orders, alter settings, or trigger downstream automation), this enables cross-tenant data manipulation or spoofed application state changes attributed to a shop the attacker does not control — matching the "cross-tenant access" impact class.

### Likelihood Explanation
Requires only that the attacker be able to install the target app on their own store (a normal, unprivileged action for any merchant) to obtain one legitimately-signed webhook body/HMAC pair, then replay it to the public webhook endpoint with a modified header. No access token, `client_secret`, or privileged credentials are required — only observation of one's own webhook traffic.

### Recommendation
Bind the shop identity to the signed material, e.g., include `shop`, `topic`, and `webhook_id` (or verify them against a per-shop record established at install time) in the HMAC-covered signable string, or otherwise cryptographically bind the header-derived `shop` to the signed body before trusting it as the event's tenant.

### Proof of Concept
1. Install the app on `attacker.myshopify.com`; capture a real webhook delivery: raw body `B` and header `x-shopify-hmac-sha256: H` where `H = HMAC-SHA256(api_secret_key, B)`, along with `x-shopify-shop-domain: attacker.myshopify.com`.
2. Replay to the app's webhook endpoint with identical `B`/`H` but `x-shopify-shop-domain: victim.myshopify.com`.
3. `HmacValidator.validate` succeeds because it only checks `B` against `H` [8](#0-7) ; `Registry.process` dispatches the handler with `data.shop == "victim.myshopify.com"` [7](#0-6) , causing the app to process attacker-controlled data as belonging to the victim tenant.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-33)
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
```

**File:** lib/shopify_api/webhooks/request.rb (L35-38)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
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
