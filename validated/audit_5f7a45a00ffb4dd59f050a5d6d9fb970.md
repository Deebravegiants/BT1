### Title
Webhook `shop` identity is trusted from an unauthenticated header while the HMAC only signs the request body - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#hmac` is verified against `to_signable_string`, which returns only the raw HTTP body [1](#0-0) . The `shop` domain that `Registry.process` hands to the app's webhook handler is read straight from the `shopify-shop-domain`/`x-shopify-shop-domain` header, which is never included in the signed bytes [2](#0-1) . This breaks the equality "shop authenticated == shop the payload is bound to": the HMAC proves the *body* came from someone holding `api_secret_key`, but proves nothing about which shop that body belongs to.

### Finding Description
`Registry.process` only calls `Utils::HmacValidator.validate(request)` before dispatching to the handler with `shop: request.shop`: [3](#0-2) 

`HmacValidator.validate` computes `HMAC(api_secret_key, verifiable_query.to_signable_string)` and compares it to the supplied `hmac`: [4](#0-3) 

For `Webhooks::Request`, `to_signable_string` is defined as the raw request body only: [1](#0-0) 

Meanwhile `shop`, `topic`, `webhook_id`, and `api_version` are all pulled from headers that are outside the HMAC's coverage: [5](#0-4) 

Because the same `api_secret_key` is shared across every shop that installs the app, any entity that has legitimately received one valid `(body, hmac)` pair from Shopify (e.g. by installing the app on their own store) can resend that exact body/HMAC pair to the app's webhook endpoint while substituting an arbitrary `shopify-shop-domain` header. `HmacValidator.validate` will still succeed because it only checks the body bytes, and `Registry.process` will hand the handler `shop: <attacker-chosen-domain>` together with the replayed body. Any app that uses `WebhookMetadata#shop` as the tenant/session key (exactly as the library's own docs and `shopify_app` reference implementation do) will attribute the replayed payload to the wrong tenant.

This is the same class of defect as the reported analog: a value that is *acted on* (here, the tenant-selecting `shop`) is not covered by the same integrity check (here, the HMAC) that is used to establish trust in the request. The report's `voucherIndexes`/`vouchees` mismatch and this `shop`-header/HMAC-body mismatch both stem from trusting a field whose binding to the "verified" data was never actually established.

### Impact Explanation
This allows cross-tenant confusion: an attacker who legitimately controls a shop that has installed the vulnerable app can capture one valid signed webhook and replay it with a forged `shop` header to make the host application process/store the payload under a victim shop's record. Depending on how the host app uses `WebhookMetadata#shop` (session/tenant lookup, data writes, triggering shop-scoped side effects), this can lead to cross-tenant data corruption or disclosure - matching the Critical "cross-tenant access" category in scope.

### Likelihood Explanation
Requires the attacker to have obtained at least one legitimately-signed `(body, hmac)` pair for the app (trivial: install the app on their own or a trial/dev shop and capture a webhook delivery), then send a normal unauthenticated POST to the app's webhook endpoint with a modified `shop` header and the replayed body/HMAC. No access to `api_secret_key`, tokens, or privileged accounts is needed. The gem performs no anti-replay (nonce/timestamp) check and no binding between `shop` and the HMAC.

### Recommendation
Include the shop domain (and ideally topic/webhook id) in the bytes that are HMAC-verified, or otherwise cryptographically bind the header-provided `shop` to the signed payload before it is trusted. At minimum, document that `WebhookMetadata#shop` is unauthenticated and must not be used as a sole tenant-selection key without additional verification (e.g., cross-checking against a known-shop list or requiring mTLS/allow-listed source IPs), and consider adding replay protection.

### Proof of Concept
1. Install the target app on shop `attacker.myshopify.com` and trigger a webhook (e.g. `orders/create`) to capture a valid `(raw_body, x-shopify-hmac-sha256)` pair signed with the app's shared `api_secret_key`.
2. Send a POST to the app's webhook endpoint with the exact same `raw_body` and `x-shopify-hmac-sha256`, but set `x-shopify-shop-domain: victim.myshopify.com`.
3. `Utils::HmacValidator.validate` succeeds (only the body bytes are checked): [6](#0-5) 
4. `Registry.process` dispatches the handler with `shop: "victim.myshopify.com"` and the attacker-originated body: [7](#0-6) 
5. Any host application logic keyed on `WebhookMetadata#shop` now operates on the victim's tenant using attacker-supplied data.

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
