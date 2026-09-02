### Title
Webhook `shop-domain`, `topic`, `api-version`, and `webhook-id` headers are trusted by `Registry.process` without being covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body [1](#0-0) , while `shop`, `topic`, `api_version`, and `webhook_id` are all read directly from unauthenticated HTTP headers [2](#0-1) . `Registry.process` validates only the body/HMAC pair via `Utils::HmacValidator.validate(request)` and then dispatches the handler using the header-derived `shop`, `topic`, `webhook_id`, and `api_version` values without any additional binding to what was signed [3](#0-2) .

### Finding Description
The equality that should hold is: `bytes verified by HMAC == bytes acted upon by the handler`. Here that equality is broken — the HMAC only binds `raw_body`, not the `shop-domain`, `topic`, `webhook-id`, or `api-version` headers, yet `Registry.process` treats a passing HMAC check as authenticating the shop/topic attribution as well:

```ruby
def process(request)
  raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)
  handler = @registry[request.topic]&.handler
  ...
  handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop,
    body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))
end
``` [4](#0-3) 

Because `HmacValidator.validate` only computes `HMAC(secret, to_signable_string)` and `to_signable_string` for `Webhooks::Request` returns solely `@raw_body` [1](#0-0) , `lib/shopify_api/utils/hmac_validator.rb` never sees or authenticates the header values [5](#0-4) . Any actor who obtains a genuine `(raw_body, hmac)` pair for one webhook delivery (e.g., a payload that is echoed back in an app UI, logged, exposed via a shared/test store, or otherwise observable) can replay that exact body+HMAC to the app's webhook endpoint while substituting an arbitrary `x-shopify-shop-domain`, `x-shopify-topic`, `x-shopify-webhook-id`, or `x-shopify-api-version` header. The library will report the HMAC as valid and hand the forged headers straight to the merchant's handler as trusted `WebhookMetadata`.

### Impact Explanation
This breaks the identity binding between "data verified as coming from Shopify" and "the shop/topic that data is attributed to," letting header values that were never part of the authenticated payload determine which tenant's data the handler processes. Any handler that keys its side effects (record updates, entitlement changes, data writes) off `WebhookMetadata#shop` without independent verification can be made to act on a different shop's identity than the one that actually produced the signed body — a cross-tenant confusion condition rooted directly in this gem's webhook verification logic, not in host-application misuse of a documented API (the gem's own `process` method performs this exact unsafe binding).

### Likelihood Explanation
Exploitation requires the attacker to first obtain one legitimate `(body, hmac)` pair for the target app (e.g., via a payload disclosed through logs, a shared development/test store, or a webhook the attacker's own shop received that has cross-tenant-relevant content). This is a real but non-trivial precondition, and it does not require possession of `api_secret_key` — only a captured signed body. Given this precondition, forging the shop/topic attribution is a straightforward header substitution.

### Recommendation
Include `shop`, `topic`, `webhook_id`, and `api_version` in the value covered by `to_signable_string` (or otherwise independently authenticate them, e.g., cross-check `shop` against the session/store expected to have registered the given `topic`/`webhook_id`) rather than relying solely on the raw body being HMAC-valid.

### Proof of Concept
1. Attacker (or a colluding low-privilege user) captures a legitimate webhook delivery for `topic: orders/create` addressed to `shop-a.myshopify.com`, including its raw body and `x-shopify-hmac-sha256` value (e.g., leaked via logs, exposed test tooling, or a shared endpoint).
2. Attacker replays the identical `raw_body` and `hmac` to the app's webhook endpoint, but sets `x-shopify-shop-domain: shop-b.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new(raw_body:, headers:)` parses this successfully [6](#0-5) .
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only checks `raw_body` against the HMAC [7](#0-6) .
5. The handler receives `WebhookMetadata` with `shop: "shop-b.myshopify.com"` even though the signed payload actually belongs to `shop-a`, and any app logic that trusts this attribution processes/attributes the data to the wrong tenant.

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

**File:** lib/shopify_api/webhooks/request.rb (L45-63)
```ruby
      sig { params(raw_body: String, headers: T::Hash[String, T.untyped]).void }
      def initialize(raw_body:, headers:)
        # normalize the headers by forcing lowercase, removing any prepended "http"s, and changing underscores to dashes
        headers = headers.to_h { |k, v| [k.to_s.downcase.sub("http_", "").gsub("_", "-"), v] }

        missing_headers = []
        ["topic", "hmac-sha256", "shop-domain"].each do |name|
          unless headers.key?("shopify-#{name}") || headers.key?("x-shopify-#{name}")
            missing_headers << "shopify-#{name} or x-shopify-#{name}"
          end
        end
        unless missing_headers.empty?
          raise Errors::InvalidWebhookError,
            "Missing one or more of the required HTTP headers to process webhooks: #{missing_headers}"
        end

        @headers = headers
        @raw_body = raw_body
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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
