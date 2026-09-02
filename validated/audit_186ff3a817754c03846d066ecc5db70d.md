### Title
Webhook `shop` header is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, while `hmac`, `topic`, `shop`, `api_version`, and `webhook_id` are all read directly from unauthenticated HTTP headers. `Utils::HmacValidator.validate` only checks that the HMAC matches the raw body — it never binds the `shop-domain` header to the signature. `Webhooks::Registry.process` then forwards the unauthenticated `request.shop` value straight into `WebhookMetadata`, which host applications use to identify the tenant for the incoming webhook. This breaks the identity binding `HMAC-covered-body == (body, shop)`, letting an attacker replay a validly-signed body under an arbitrary victim shop domain.

### Finding Description
The webhook signature only protects the JSON payload: [1](#0-0) 

All identifying metadata, including `shop`, comes straight from attacker-controlled headers with no cryptographic binding to that value: [2](#0-1) 

The validator only recomputes and compares the HMAC over `to_signable_string` (i.e., the raw body), never incorporating `shop`, `topic`, or any header: [3](#0-2) 

`Registry.process` checks only that this body-only HMAC is valid, then hands `request.shop` (the unverified header) directly to the handler as the tenant identifier: [4](#0-3) 

`WebhookMetadata.shop` is the field host applications use to route/attribute webhook data to a specific merchant/tenant: [5](#0-4) 

Because `shop` is "a field acted on but not covered by the HMAC," any HTTP client that has obtained one validly-signed body/HMAC pair (e.g., from their own store's legitimate webhook traffic to a public endpoint) can resend the identical body and HMAC while substituting the `x-shopify-shop-domain` (or `shopify-shop-domain`) header for a different shop. The signature check still passes because it only verifies the body, and the handler processes the payload as if it belongs to the attacker-chosen shop.

### Impact Explanation
This breaks the tenant boundary the gem is supposed to enforce for webhook processing: the `shop` value that identifies which merchant's data store/session the payload applies to can be forged by an unauthenticated party while still passing HMAC verification. Host applications commonly use `WebhookMetadata#shop` (per the gem's own documented usage) to look up the merchant's session/store and write incoming data (orders, app/uninstalled, GDPR, etc.) keyed by that shop — an attacker can therefore inject data attributed to an arbitrary victim shop, or trigger app logic (e.g., `app/uninstalled` cleanup, data deletion) for a shop of their choosing. This is a cross-tenant access primitive rooted directly in the gem's verification logic, not merely a documentation/best-practice gap, since the gem itself constructs and passes the unauthenticated `shop` field into the trusted `WebhookMetadata` object after "successful" HMAC validation.

### Likelihood Explanation
Exploitation requires only: (1) capturing or generating one validly-signed webhook body+HMAC pair for any shop that uses the same app (trivially available to any developer/tester who installs the app on a test store, since webhook endpoints are public HTTP endpoints), and (2) resending that exact body/HMAC with a different `shop-domain` header value. No access token, `api_secret_key`, or privileged credential is required — this is reachable by any unprivileged internet user who can reach the app's public webhook endpoint.

### Recommendation
Include the `shop` (and ideally `topic`, `webhook_id`) header values in the signable content that the HMAC is computed over, or otherwise cryptographically bind them to the verified payload, so that `Utils::HmacValidator.validate` fails if any of these headers are altered relative to what Shopify actually signed. At minimum, `Webhooks::Request#to_signable_string` should not report a request as valid unless the `shop-domain` header is verified to be consistent with the signed body, matching the equality `HMAC-verified fields == fields the handler consumes`.

### Proof of Concept
1. Attacker installs the target app on their own test store `attacker-shop.myshopify.com` and receives a legitimate webhook: raw body `B`, header `x-shopify-hmac-sha256: H` (valid signature of `B` computed with the app's shared `api_secret_key`), and `x-shopify-shop-domain: attacker-shop.myshopify.com`.
2. Attacker sends a new HTTP request to the app's public webhook endpoint with the same raw body `B` and same `x-shopify-hmac-sha256: H`, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses the forged shop header without validation.
4. `Utils::HmacValidator.validate` recomputes HMAC over `B` only (per `to_signable_string`) and it matches `H`, so validation passes.
5. `Registry.process` invokes the handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: parsed(B), ...)`, causing the app to process attacker-controlled data as if it originated from the victim shop.

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

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L6-12)
```ruby
    class WebhookMetadata < T::Struct
      const :topic, String
      const :shop, String
      const :body, T::Hash[String, T.untyped]
      const :api_version, String
      const :webhook_id, String
    end
```
