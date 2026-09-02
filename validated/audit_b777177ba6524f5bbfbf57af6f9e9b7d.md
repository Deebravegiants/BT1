### Title
Webhook HMAC only signs the request body, allowing the `shop-domain` header to be spoofed for cross-tenant webhook injection - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, so the HMAC computed by `Utils::HmacValidator.validate` never covers the `shop`, `topic`, `webhook_id`, or `api_version` values that `Webhooks::Registry.process` extracts and hands to the app's handler. Any actor who can obtain one legitimately-signed `(raw_body, hmac)` pair for the app (e.g., by installing the app on their own store and capturing a real webhook delivery) can replay that exact body/HMAC pair while substituting an arbitrary `x-shopify-shop-domain` header, and the gem will report the forged shop as authenticated.

### Finding Description
The binding that should hold is: `HMAC_valid(raw_body, secret) == true` implies the whole authenticated context (including which shop the event is "for") is trustworthy. In this gem that equality is broken because the signable string used for verification is just the body: [1](#0-0) 

while `shop`, `topic`, `webhook_id`, and `api_version` are read straight from unauthenticated headers: [2](#0-1) 

`Registry.process` validates the HMAC (which only proves the body wasn't tampered with) and then forwards the attacker-controlled `shop` value verbatim into `WebhookMetadata`, which is the only tenant-identifying information the handler receives: [3](#0-2) 

`HmacValidator.validate` itself just compares `verifiable_query.to_signable_string` against the secret — it has no visibility into headers outside of whatever `to_signable_string` chooses to include: [4](#0-3) 

Because the app's `api_secret_key` is the same for every shop that installs the app, any merchant (an unprivileged internet user with respect to other tenants) can install the app on their own store, capture a real webhook (raw body + valid `x-shopify-hmac-sha256`), and then POST that exact same body/HMAC to the app's public webhook endpoint while changing only the `x-shopify-shop-domain` header to a victim shop. `Registry.process` will accept it as authentic and dispatch it to the handler labeled with the victim's shop.

### Impact Explanation
This breaks the shop-authentication boundary the gem is documented to provide: a webhook is only supposed to be attributable to the shop it's genuinely for. Since the handler receives a `shop` value that is not covered by the cryptographic signature, an attacker can inject data or trigger business logic (order/fulfillment updates, GDPR/mandatory topics, inventory changes, etc.) attributed to a shop they do not own, once the host app relies on `WebhookMetadata#shop` for tenant scoping — this is a cross-tenant access vector.

### Likelihood Explanation
High. Any developer/merchant can install the target app on their own store to obtain one valid `(body, hmac)` pair for a topic of their choosing, then simply resend that pair with a modified `shop-domain` header to the same publicly reachable webhook endpoint. No knowledge of `api_secret_key` is required — only reuse of a signature that was legitimately issued for the attacker's own shop.

### Recommendation
Include the shop domain (and ideally topic/webhook id) in the HMAC-signable content, or otherwise cryptographically bind the shop value to the signed body (e.g., verify `request.shop` against the shop the caller is expected to represent, or require the host app to look up an existing installed-shop record before trusting `WebhookMetadata#shop`). At minimum, document prominently that `shop`, `topic`, and `webhook_id` headers are NOT covered by the HMAC and must not be used for tenant authorization without an independent check.

### Proof of Concept
```ruby
# Attacker installs the app on their own shop and captures a real webhook delivery:
raw_body = '{"id":1,"note":"hello"}'
hmac = OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), api_secret_key, raw_body)

legit_headers = {
  "x-shopify-topic" => "orders/create",
  "x-shopify-hmac-sha256" => Base64.encode64(hmac),
  "x-shopify-shop-domain" => "attacker-shop.myshopify.com",
}

# Attacker replays the identical body+hmac but swaps the shop header to the victim's shop.
forged_headers = legit_headers.merge("x-shopify-shop-domain" => "victim-shop.myshopify.com")

forged_request = ShopifyAPI::Webhooks::Request.new(raw_body: raw_body, headers: forged_headers)

# HMAC validation succeeds because it only checks raw_body, not shop-domain.
ShopifyAPI::Webhooks::Registry.process(forged_request)
# => handler.handle is invoked with WebhookMetadata(shop: "victim-shop.myshopify.com", ...)
#    even though the payload/HMAC was never issued for that shop.
```

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
