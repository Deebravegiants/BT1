### Title
Webhook `shop` tenant identifier is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant identity (`shop`) from the `X-Shopify-Shop-Domain` HTTP header, but the HMAC signature that `ShopifyAPI::Webhooks::Registry.process` verifies covers only the raw request body — never the shop header. An unprivileged holder of any single genuine, validly-signed webhook (e.g. one delivered to their own installed shop) can replay that exact body/HMAC pair while substituting an arbitrary `shop-domain` header, and the library will accept it as authentic and hand the forged shop identity to the host application's webhook handler.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop` is read straight from a header that plays no part in that signable string: [2](#0-1) 

`Registry.process` validates the HMAC using `Utils::HmacValidator.validate(request)`, which calls `verifiable_query.to_signable_string` (i.e. body-only) and compares against `Context.api_secret_key`: [3](#0-2) 

Once that body-only HMAC check passes, `process` immediately trusts `request.shop` as the tenant identity and forwards it to the handler: [4](#0-3) 

The equality the library implicitly relies on is: **"HMAC-authenticated bytes" == "bytes used to determine which shop the event belongs to."** In reality the HMAC only authenticates the JSON body; the `shop-domain` header is a completely separate, unauthenticated channel. Because Shopify signs webhooks with the *app's* `client_secret` (shared across every shop that installs the app, not per-shop), any legitimate recipient of one webhook for their own store already possesses a body+HMAC pair that is valid for that secret. That pair remains valid no matter what `shop-domain` value accompanies it, since the header is never hashed.

### Impact Explanation
This breaks the tenant/shop identity binding used throughout `Webhooks::Registry.process` → `handler.handle(data: WebhookMetadata.new(..., shop: request.shop, ...))`. A merchant/attacker who legitimately installed the app on their own store (an unprivileged internet user relative to other tenants) can capture one authentic webhook delivery (topic/body/HMAC), then re-POST the identical body and HMAC to the app's public webhook endpoint with the `shop-domain` header changed to a victim shop. The library reports the payload as authentic and passes the attacker-chosen shop string into the handler, letting the attacker inject/spoof events attributed to a shop they do not control — a cross-tenant confusion/injection that can corrupt or exfiltrate state keyed by shop domain in the host application. No `api_secret_key`, access token, or credential leak is required; only a single normal webhook a merchant already legitimately receives.

### Likelihood Explanation
Likelihood is high for any app that (a) allows self-serve installs (so an attacker can be a legitimate merchant of their own store) and (b) exposes its webhook endpoint publicly, which is the standard and expected deployment configuration for this gem. Triggering a webhook for one's own shop (e.g. `app/uninstalled`, `orders/create`) is trivial and entirely within an ordinary merchant's control.

### Recommendation
Bind the `shop` (and `topic`/`api_version`/`webhook_id` if they influence handler behavior) into the HMAC-signable representation, or otherwise cryptographically bind the header values to the signed body, so that the shop identity cannot be altered independently of the signature. At minimum, `Request#to_signable_string` should incorporate the `shop-domain` header, and `HmacValidator`/`Registry.process` should re-verify that the "authenticated" request corresponds to the specific shop it claims to be for (e.g. by cross-checking against an expected/known shop when one is already known to the host app).

### Proof of Concept
1. App is installed on `attacker-shop.myshopify.com`; attacker triggers any webhook topic on their own store and captures the raw POST: headers include `x-shopify-hmac-sha256: <valid-hmac-of-body>` and `x-shopify-shop-domain: attacker-shop.myshopify.com`, with some JSON `raw_body`.
2. Attacker resends the exact same `raw_body` and `x-shopify-hmac-sha256` value to the app's webhook endpoint, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new(raw_body:, headers:)` parses `shop` as `victim-shop.myshopify.com`.
4. `Registry.process` calls `Utils::HmacValidator.validate(request)` — this only hashes `raw_body`, which is unchanged, so validation succeeds (`lib/shopify_api/utils/hmac_validator.rb:12-31`, `lib/shopify_api/webhooks/request.rb:35-38`).
5. `handler.handle(data: WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: ..., ...))` runs with the forged shop, causing the host application to process/store the attacker's payload as if it came from the victim shop.

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
