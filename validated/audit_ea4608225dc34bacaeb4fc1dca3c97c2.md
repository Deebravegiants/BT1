## Title
Webhook `shop` (and `topic`, `api_version`, `webhook_id`) identity fields are not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant identity (`shop`) and other metadata purely from HTTP headers, while the HMAC signature that the gem verifies only covers the raw request body. An attacker who possesses one validly-signed webhook delivery (e.g. for their own shop, which they can freely install/trigger) can replay the exact same body/HMAC pair while altering the `shopify-shop-domain` header to claim a different tenant, and the gem's `Utils::HmacValidator.validate` will still report the signature as valid.

### Finding Description
`Request#to_signable_string` returns only the raw JSON body: [1](#0-0) 

`Utils::HmacValidator.validate` computes the HMAC exclusively over `verifiable_query.to_signable_string` (i.e., the body) and compares it to the `hmac` header: [2](#0-1) 

`Request#shop`, `#topic`, `#api_version`, and `#webhook_id` are read straight from headers with no cryptographic binding to the signed payload: [3](#0-2) 

`Registry.process` only checks `Utils::HmacValidator.validate(request)` (i.e., body authenticity) before dispatching `request.shop` to the app's handler as the trusted tenant identifier: [4](#0-3) 

This is precisely the analog class described in the report ("wrong conditions"/broken binding): the field the application acts on for tenant scoping (`shop`) is not the field verified by the HMAC (`body` only). The equality that should hold — `shop authenticated == shop bound by signature` — does not hold, because the signature binds nothing about `shop`.

### Impact Explanation
Since the app-facing `handler.handle` call receives `WebhookMetadata` built from `request.shop` and `request.topic` without any cryptographic tie to the signed body, an attacker capable of obtaining one legitimately signed webhook delivery (trivial: install the app on their own store and trigger any webhook) can replay the identical `raw_body`/`hmac` pair to the app's public webhook endpoint while substituting the `shopify-shop-domain` header for an arbitrary victim shop domain. The webhook passes HMAC validation and is dispatched to the handler labeled as coming from the victim shop — a cross-tenant identity-spoofing primitive that can corrupt or inject data attributed to another merchant's tenant.

### Likelihood Explanation
Webhook receiver endpoints are internet-facing by design (Shopify posts to them), and no credential beyond a legitimate (attacker-owned) shop installation is required to obtain a valid body/HMAC pair. Replaying with a modified `shop` header requires no secret knowledge, only the ability to send an arbitrary HTTP request with custom headers, which any unprivileged internet user controlling an HTTP client can do.

### Recommendation
Include the tenant-identifying fields (`shop`, `topic`, `webhook_id`, `api_version`) in the signable/verified representation, or otherwise cryptographically bind the header-derived shop to the signed body before it is trusted for tenant-scoped processing — analogous to the report's core recommendation to eliminate the mismatch between the checked condition and the value acted upon rather than merely patching the immediate symptom.

### Proof of Concept
1. Attacker installs the app on their own shop `attacker.myshopify.com` and captures a legitimate webhook delivery: body `B`, and header `x-shopify-hmac-sha256: H` (valid HMAC of `B` with the app's secret), along with `x-shopify-shop-domain: attacker.myshopify.com`.
2. Attacker POSTs the same body `B` and header `x-shopify-hmac-sha256: H` to the app's webhook endpoint, but sets `x-shopify-shop-domain: victim.myshopify.com`.
3. `Utils::HmacValidator.validate` recomputes the HMAC over `B` only, matches `H`, and returns `true`.
4. `Registry.process` dispatches the webhook to the handler with `WebhookMetadata.shop == "victim.myshopify.com"`, even though the payload never originated from Shopify for that shop, letting the attacker inject spoofed events attributed to a tenant they do not control.

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

**File:** lib/shopify_api/webhooks/request.rb (L35-43)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end

      sig { returns(T::Hash[String, T.untyped]) }
      def parsed_body
        JSON.parse(@raw_body)
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
