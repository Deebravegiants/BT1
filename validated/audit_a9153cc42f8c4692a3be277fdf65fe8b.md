This confirms the vulnerability. `Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , while `shop`, `topic`, `api_version`, and `webhook_id` are all read directly from HTTP headers with no cryptographic binding to the HMAC [2](#0-1) . `Registry.process` validates only `Utils::HmacValidator.validate(request)` (which checks `hmac(to_signable_string)`), then dispatches the handler using the unauthenticated `request.shop` and `request.topic` values [3](#0-2) .

### Title
Webhook `shop`/`topic` headers are not covered by HMAC, enabling cross-tenant webhook spoofing via replay - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable string from the raw body only [1](#0-0) , but `Registry.process` trusts the unsigned `shop`, `topic`, `api_version`, and `webhook_id` header values when routing the webhook to a handler and building `WebhookMetadata` [3](#0-2) .

### Finding Description
The equality that should hold is: `shop authenticated by HMAC == shop acted on by the handler`. In this gem it does not: `HmacValidator.validate_signature` recomputes `HMAC(secret, verifiable_query.to_signable_string)` and compares it against the `hmac` header [4](#0-3) . For `Webhooks::Request`, `to_signable_string` is `@raw_body` — the `shopify-shop-domain`, `shopify-topic`, `shopify-webhook-id`, and `shopify-api-version` headers are never part of the signed material [5](#0-4) . Since a Shopify app's webhook HMAC secret (`api_secret_key`) is shared across all shops/topics registered for that app, and a raw body such as `{}` (used for e.g. `shop/redact` mandatory topics, or any webhook whose body is content-independent/predictable) will always hash to the same valid HMAC regardless of which shop or topic it was originally sent for, an attacker who legitimately receives one authentic webhook (e.g., by installing the app on their own free/dev shop and triggering a webhook with a known/reproducible body) can replay that exact `(raw_body, hmac)` pair to the app's public webhook endpoint while substituting the `x-shopify-shop-domain` header for a victim shop and/or the `x-shopify-topic` header for a different registered topic. `Registry.process` will accept it as valid because `HmacValidator.validate` only checks body integrity [3](#0-2) , then invokes the corresponding handler with the forged `shop` claim inside `WebhookMetadata` [6](#0-5) .

### Impact Explanation
This breaks the tenant-isolation guarantee host applications rely on: application code typically uses `WebhookMetadata#shop` to decide which tenant's data to update/delete (e.g., GDPR redact handlers, order/product sync handlers). An attacker can trigger handler logic under an arbitrary victim shop identity without ever possessing that shop's credentials, which is a cross-tenant access vector as covered by the Critical impact category (cross-tenant access via the app's own webhook processing).

### Likelihood Explanation
Exploitation requires the attacker to obtain one authentic `(raw_body, hmac)` pair for the app (trivially available to anyone who can install the target app on their own shop and let it send any webhook with a static/predictable body, e.g. `{}`), and requires the webhook HTTP endpoint to be reachable directly from the internet, which is the standard deployment model for Shopify app webhooks. No access to `api_secret_key` or any victim credential is needed.

### Recommendation
Include `shop`, `topic`, and other routing-relevant headers in the signed/verified material — or, at minimum, cross-check the `shop-domain` header against an independently known/authenticated identifier (e.g., validate it corresponds to a shop for which the app currently holds an active, stored session/access token) before dispatching to a handler, rather than trusting it purely because the raw body's HMAC checks out.

### Proof of Concept
```ruby
# Step 1: Attacker installs the target app on their own dev shop "attacker.myshopify.com"
# and receives a real webhook whose body is content-independent, e.g. a
# mandatory GDPR topic with raw_body == "{}" (as used throughout the test suite):
hmac = OpenSSL::HMAC.digest(OpenSSL::Digest.new("sha256"), api_secret_key, "{}")
encoded_hmac = Base64.encode64(hmac)   # attacker captures this valid signature for body "{}"

# Step 2: Attacker replays the same body+hmac but swaps the shop-domain / topic headers
forged_headers = {
  "x-shopify-topic" => "customers/data_request",       # or any registered topic
  "x-shopify-hmac-sha256" => encoded_hmac,               # still valid: HMAC only covers "{}"
  "x-shopify-shop-domain" => "victim-shop.myshopify.com" # attacker-chosen victim shop
}

# Step 3: Send POST to the app's webhook endpoint with body "{}" and forged_headers.
ShopifyAPI::Webhooks::Registry.process(
  ShopifyAPI::Webhooks::Request.new(raw_body: "{}", headers: forged_headers)
)
# => Registry.process only calls Utils::HmacValidator.validate(request), which recomputes
#    HMAC(secret, "{}") and matches encoded_hmac, so validation passes.
# => The handler for "customers/data_request" is invoked with
#    WebhookMetadata(shop: "victim-shop.myshopify.com", ...), even though this webhook
#    was never actually sent by Shopify for victim-shop.
``` [3](#0-2) [5](#0-4) [7](#0-6)

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-38)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end

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
