This confirms the vulnerability: the webhook HMAC only signs `@raw_body` (`to_signable_string` returns `@raw_body`, `lib/shopify_api/webhooks/request.rb:36-38`), while `shop` (the tenant identifier passed to the app's handler) is read straight from the unauthenticated `x-shopify-shop-domain`/`shopify-shop-domain` HTTP header (`lib/shopify_api/webhooks/request.rb:20-23`). `HmacValidator.validate` (`lib/shopify_api/utils/hmac_validator.rb:12-22`) only checks `verifiable_query.to_signable_string`, i.e., the raw body bytes, against the HMAC — it never binds the `shop` header into the signature. `Registry.process` then trusts `request.shop` and hands it straight to the app's webhook handler as the merchant identity (`lib/shopify_api/webhooks/registry.rb:189-199`, passing `shop: request.shop` into `WebhookMetadata`).

### Title
Webhook `shop` (tenant identity) is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, so the HMAC verified by `Utils::HmacValidator.validate` binds solely to the body bytes. The `shop` value that `Registry.process` forwards to the app's webhook handler as the authoritative tenant identifier is read from the `x-shopify-shop-domain`/`shopify-shop-domain` HTTP header, which is completely outside the HMAC's signed content.

### Finding Description
The binding that should hold is: `hmac == HMAC(secret, body ‖ shop ‖ topic)` such that the verified shop equals the shop the app acts on. Instead the gem implements `hmac == HMAC(secret, body)` (`lib/shopify_api/webhooks/request.rb:35-38`) and separately reads `shop` from a header (`lib/shopify_api/webhooks/request.rb:20-23`) that carries no cryptographic binding to that HMAC.

Any actor who is a legitimate merchant of even a single Shopify store (an "unprivileged internet user" with respect to any other merchant's data) can trigger a real webhook delivery for their own shop (e.g., `orders/create`), capturing a valid `(raw_body, hmac)` pair signed with the app's `client_secret`. Because the `shop-domain` header is not part of the signed content, the attacker can replay that exact body and HMAC to the app's webhook endpoint while substituting the `x-shopify-shop-domain` header with a victim shop's domain. `HmacValidator.validate` (`lib/shopify_api/utils/hmac_validator.rb:26-31`) will recompute the same signature from the same body and accept it, and `Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-200`) will invoke the app's handler with `shop: request.shop` set to the victim's domain, even though the payload was never authorized for or associated with that shop by Shopify.

### Impact Explanation
This breaks the tenant-isolation guarantee the gem is expected to provide to consuming applications: apps rely on the `shop` value from a successfully-HMAC-validated `Request`/`WebhookMetadata` to know which merchant's data to read or mutate. Since the signature does not bind `shop`, an attacker controlling one shop can forge webhook deliveries that the app's handler will process under an arbitrary victim shop identity — i.e., cross-tenant access/action within any host application that trusts `data.shop` from a `Registry.process` call (which is the gem's own documented usage pattern for webhook handlers).

### Likelihood Explanation
Likelihood is high for any app exposing a webhook endpoint: obtaining a valid signed webhook only requires operating (or having access to) any single Shopify development/trial store, which is trivial for any internet user to create. No access token, `client_secret`, or privileged account is required — only a normal webhook delivery the attacker receives for their own shop and then replays with a modified header.

### Recommendation
Bind `shop` (and ideally `topic`/`webhook-id`) into the signed content verified against the HMAC, or independently verify that the `shop-domain` header matches a value embedded in and covered by the signed payload, before trusting `request.shop` in `Registry.process`. At minimum, document and enforce that `shop` must never be treated as authenticated unless it is included in `to_signable_string`.

### Proof of Concept
1. Attacker owns `attacker-shop.myshopify.com` and configures the target app's webhook endpoint (or observes deliveries) to obtain a legitimate `(raw_body, x-shopify-hmac-sha256)` pair for a topic the app handles, generated with the app's real `client_secret` by Shopify itself.
2. Attacker sends the app's webhook endpoint a POST with:
   - Same `raw_body` and same `x-shopify-hmac-sha256` value captured in step 1.
   - `x-shopify-shop-domain: victim-shop.myshopify.com` (any value the attacker chooses).
3. `ShopifyAPI::Webhooks::Request.new` accepts the forged headers (`lib/shopify_api/webhooks/request.rb:45-63`).
4. `Utils::HmacValidator.validate(request)` calls `to_signable_string`, which returns only `@raw_body`; the recomputed HMAC matches, so validation passes (`lib/shopify_api/webhooks/request.rb:35-38`, `lib/shopify_api/utils/hmac_validator.rb:26-31`).
5. `Registry.process(request)` invokes the app's handler with `shop: request.shop` == `"victim-shop.myshopify.com"` (`lib/shopify_api/webhooks/registry.rb:198-199`), causing the app to act on the victim's tenant data using attacker-controlled body content. [1](#0-0) [2](#0-1) [3](#0-2)

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-38)
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
