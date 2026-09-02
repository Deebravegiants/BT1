## Finding

### Title
Webhook `shop` attribution is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-verifiable signable string from the raw body only, while the `shop` value used to attribute the webhook to a tenant is read from an unauthenticated header. An attacker who can obtain one genuine, validly-signed webhook payload (trivially available by installing the app on their own shop) can replay that exact body+HMAC pair against the app's public webhook endpoint while substituting the `shop-domain` header for a victim shop, and the gem will report the payload as belonging to the victim tenant.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

The `shop` accessor is derived independently from the `shopify-shop-domain`/`x-shopify-shop-domain` HTTP header, which is not part of the signed material: [2](#0-1) 

`ShopifyAPI::Utils::HmacValidator.validate` only checks `request.hmac` against `compute_signature(verifiable_query.to_signable_string, secret)`, i.e. against the body: [3](#0-2) 

`ShopifyAPI::Webhooks::Registry.process` validates the HMAC and then forwards `request.shop` (the unauthenticated header value) straight to the app's handler as the tenant identifier, with no cross-check against the signed body: [4](#0-3) 

This breaks the intended identity binding `hmac_over(body) == hmac_over(body, shop)`: the gem treats "HMAC valid" as equivalent to "this payload legitimately belongs to `request.shop`", but the `shop` field was never part of what was authenticated.

### Impact Explanation
An attacker who installs the target app on a shop they control receives real, correctly-HMAC-signed webhook deliveries for that shop (e.g. `orders/create`, `customers/data_request`, etc.). Because the shop attribution lives only in an unsigned header, the attacker can capture the raw body + `hmac-sha256` value from their own delivery and re-POST it to the app's public webhook endpoint with the `shopify-shop-domain` header rewritten to any victim shop domain the attacker chooses. `Registry.process` will pass HMAC validation (since the body/HMAC pair is genuinely valid) and hand the handler a `WebhookMetadata` object claiming the attacker-crafted body originated from the victim shop. Any app logic that trusts `WebhookMetadata#shop` to write/update per-tenant records (common pattern: upsert order/customer data keyed by `shop`) can be tricked into writing attacker-controlled data into a victim tenant's records — a cross-tenant data integrity / injection issue reachable by any unprivileged internet user with no access token, secret, or privileged account.

### Likelihood Explanation
Likelihood is meaningful but not trivial: it requires the attacker to have (or create) their own valid installation of the target app to obtain a legitimately signed body/HMAC pair, and the app's webhook endpoint must be reachable directly (which it is, since Shopify webhook endpoints are public HTTPS URLs by design). No secrets, tokens, or privileged access are required — only the ability to install the app once as a normal merchant and then forge the destination header on a replayed request.

### Recommendation
Bind the `shop` (and ideally `topic`/`webhook_id`) into the value that is cryptographically verified before it is trusted, rather than relying solely on the raw body HMAC plus an out-of-band header. At minimum, applications should be advised (and the gem could enforce) that `WebhookMetadata#shop` must be cross-checked against a shop the app already has an active session/access token for, and that the `shop`/`topic` headers should not be treated as authenticated by `HmacValidator.validate`. Consider exposing a combined verification helper that ties header-derived identity fields into the signature check, or documenting explicitly that callers must independently authorize `request.shop` before using it to key any data writes.

### Proof of Concept
1. Install the target Shopify app on an attacker-controlled shop `attacker.myshopify.com`; trigger any webhook topic the app registers for (e.g. `orders/create`).
2. Capture the raw POST body and the `X-Shopify-Hmac-Sha256` header from that genuine delivery (this HMAC is valid because it is computed only over the body).
3. Replay the exact same body and `X-Shopify-Hmac-Sha256` header to the app's webhook endpoint, but set `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only checks the body against the HMAC: [4](#0-3) 
5. The handler receives `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: <attacker-controlled>, ...)` and, if the app persists this data keyed by `shop`, attacker-controlled content is now attributed to the victim tenant.

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
