### Title
Webhook `shop` (and `topic`/`api_version`/`webhook_id`) header fields are not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable content from the raw request body only, while the shop-identifying `shop` field (and `topic`, `api_version`, `webhook_id`) are read from unauthenticated HTTP headers. `Registry.process` validates the HMAC over the body but then dispatches to the app's handler using the header-derived, unverified `shop` value, breaking the binding `hmac-authenticated bytes == bytes used to attribute the event to a tenant`.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

Meanwhile `shop`, `topic`, `api_version`, and `webhook_id` are all pulled straight from HTTP headers with no cryptographic binding to the body or to the HMAC: [2](#0-1) 

`Utils::HmacValidator.validate` verifies the signature only against `verifiable_query.to_signable_string`, i.e., the raw body: [3](#0-2) 

`Webhooks::Registry.process` performs that HMAC check and then immediately trusts `request.shop` (an unauthenticated header) to build the `WebhookMetadata` handed to the app's handler: [4](#0-3) 

Because a single `client_secret`/`api_secret_key` is shared across all shops installed on an app, any entity that has legitimately received one valid `(body, hmac)` pair from Shopify (e.g., its own store's webhook, or any topic with a fixed/predictable body such as `{}` for mandatory compliance topics) can replay that exact body/HMAC pair while substituting an arbitrary `shopify-shop-domain` header. The HMAC check in `HmacValidator.validate` still passes because it never inspected the header, yet `Registry.process` forwards the attacker-chosen `shop` value to the handler as authoritative tenant identity — mirroring the analog bound in the rules: "a shop authenticated versus the shop stored as a session key." This is structurally the same class of bug as the reported Solidity issue: a value used for accounting/authorization decisions (`shop`) is not covered by the same integrity check applied to the data that gates access (`hmac` over `raw_body`).

### Impact Explanation
Any app relying on `WebhookMetadata#shop` (populated straight from `request.shop`) to look up per-tenant sessions, offline tokens, or shop-scoped resources can be tricked into acting on shop B's data/session while processing an HMAC-valid payload that was never actually sent by Shopify for shop B. This is a cross-tenant boundary violation: the library asserts webhook authenticity ("Invalid webhook HMAC" check passed) while silently leaving the most security-critical field — which tenant this event belongs to — completely unauthenticated.

### Likelihood Explanation
Exploitation requires an attacker to possess at least one valid `(raw_body, hmac)` pair, which is trivially available to any merchant/developer who installs the app themselves (their own legitimate webhook deliveries), or for topics with a fixed empty/predictable payload (e.g., `shop/redact`, `customers/redact`, `customers/data_request` mandatory compliance topics, or any topic where the body is constant/guessable). No access to `api_secret_key` or any credential is required — only observing one's own legitimately-received webhook and re-POSTing it to the app's public webhook endpoint with a different `shopify-shop-domain` header.

### Recommendation
Include the `shop`, `topic`, and any other header-derived fields the application logic depends on in the signable content used by `to_signable_string`, or otherwise cryptographically bind them (e.g., verify the `shop` header against the shop associated with the session/offline token the app looks up, and reject if it mismatches). At minimum, document and enforce that `WebhookMetadata#shop` must never be trusted as authenticated tenant identity by itself.

### Proof of Concept
1. App developer installs their own app on `attacker-shop.myshopify.com` and receives a legitimate webhook, e.g., `customers/data_request` with body `{}` and a valid `shopify-hmac-sha256` header (computed by Shopify over `{}` using the app's `api_secret_key`).
2. Attacker crafts a new HTTP request to the app's webhook endpoint reusing the exact same `raw_body` (`{}`) and `shopify-hmac-sha256` value, but sets `shopify-shop-domain: victim-shop.myshopify.com` and `shopify-topic` to any registered topic whose handler acts on `data.shop`.
3. `Webhooks::Request.new` accepts the request (all required headers present), `Registry.process` calls `HmacValidator.validate`, which succeeds because it only checks `OpenSSL.secure_compare(computed_signature, hmac)` against the body `{}` — see [5](#0-4) .
4. The registered handler receives `WebhookMetadata.new(topic:, shop: "victim-shop.myshopify.com", ...)` and performs shop-scoped operations (e.g., session lookup, data deletion, redaction) against `victim-shop`, even though Shopify never sent this event for that shop.

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
