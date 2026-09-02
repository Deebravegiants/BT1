Based on the analysis, I found a valid identity binding issue in the webhook processing flow.

### Title
Webhook shop-domain header is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` derives `shop`, `topic`, `webhook_id`, and `api_version` entirely from unauthenticated HTTP headers, while `Utils::HmacValidator.validate` only checks the HMAC against `to_signable_string`, which returns the raw request body. The header that identifies the tenant (`shop`) is never part of the signed material, breaking the binding: `shop authenticated == shop used to attribute the webhook`.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

Meanwhile `shop`, `topic`, `webhook_id`, and `api_version` are all read straight from HTTP headers, none of which are included in the signable string: [2](#0-1) 

`Utils::HmacValidator.validate` computes and compares the HMAC solely over `to_signable_string` (i.e., the raw body) using the app's shared `api_secret_key`: [3](#0-2) 

`Registry.process` trusts `request.shop` for attribution to a merchant after only validating the HMAC (which never covered `shop`): [4](#0-3) 

Because `api_secret_key` is a single shared secret across all shops that install the app (not a per-shop key), and the HMAC only signs the body, any two webhook deliveries with an identical body (e.g., empty-body topics like `app/uninstalled`, `shop/redact`, or any topic whose payload can be predicted/observed by an installed shop) produce an identical, valid HMAC regardless of which shop it was sent for. An attacker who controls one shop that has the app installed can capture a legitimately-signed webhook delivery (body + `x-shopify-hmac-sha256`) sent to the app's webhook endpoint, then replay/craft an HTTP request to the same endpoint with the same body/HMAC but an altered `x-shopify-shop-domain` (and/or `x-shopify-topic`) header pointing at a victim shop. `HmacValidator.validate` still passes because it never inspects the shop or topic headers, and `Registry.process` dispatches the handler using the attacker-controlled `request.shop`/`request.topic` values.

### Impact Explanation
This breaks the tenant boundary the HMAC is supposed to enforce: `Registry.process` and the app's handler act on `request.shop`, `request.topic`, and `request.webhook_id`, none of which are covered by the verified signature. This enables cross-tenant confusion — a webhook attributable to shop A can be forged/replayed to appear as if it came from shop B, causing the app to invoke redaction/uninstall/data-request handlers or update shop-specific state (e.g., mark shop B as uninstalled, trigger `shop/redact` handling for shop B, or process fabricated data for the wrong tenant) — a direct cross-tenant access impact.

### Likelihood Explanation
Likelihood is Medium: it requires the attacker to control (or observe) at least one shop with the app installed and to know/predict a valid body+HMAC pair for a chosen topic (trivial for topics with empty or highly predictable JSON bodies), plus network reachability to the app's public webhook endpoint — no privileged credentials, access tokens, or `api_secret_key` knowledge are required.

### Recommendation
Include the tenant-identifying and topic-identifying headers (`shop`, `topic`, `webhook_id`, `api_version`) in the HMAC-signed material (or otherwise cryptographically bind them to the payload) before trusting them in `Registry.process`, or independently verify that `request.shop` corresponds to a shop with an active, known session/installation before dispatching the handler.

### Proof of Concept
1. App has two merchants installed: `attacker-shop.myshopify.com` and `victim-shop.myshopify.com`, both sharing the app's single `api_secret_key`.
2. Attacker's own shop triggers/receives a real webhook, e.g. `app/uninstalled` with body `"{}"`, headers:
   - `x-shopify-topic: app/uninstalled`
   - `x-shopify-hmac-sha256: <valid-hmac-of-"{}">`
   - `x-shopify-shop-domain: attacker-shop.myshopify.com`
3. Attacker resends the identical request to the app's webhook endpoint, only changing `x-shopify-shop-domain` to `victim-shop.myshopify.com` (and/or `x-shopify-topic` to another topic they want to trigger with a `"{}"` body, like `shop/redact`).
4. `ShopifyAPI::Webhooks::Request.new` parses the forged headers; `Utils::HmacValidator.validate(request)` in `Registry.process` (`lib/shopify_api/webhooks/registry.rb:190`) still returns true because it only hashes `"{}"` — the shop header was never part of the signed content.
5. `Registry.process` invokes the registered handler with `shop: "victim-shop.myshopify.com"`, causing the app to act on/for the victim tenant based on attacker-controlled input.

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
