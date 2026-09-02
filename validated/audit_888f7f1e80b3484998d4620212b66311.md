### Title
Webhook shop-domain header is not covered by HMAC verification, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by HMAC-verifying the raw request body. The `shop` value that is subsequently used to attribute the webhook to a specific merchant tenant is read from the `X-Shopify-Shop-Domain` HTTP header, which is never included in the bytes that are HMAC-verified. The identity binding "verified bytes == acted-upon tenant identity" does not hold, so any request whose body+HMAC pair is valid can be attributed to an arbitrary shop simply by changing the header.

### Finding Description
`ShopifyAPI::Utils::HmacValidator.validate` is called against a `Webhooks::Request` object in `Registry.process`: [1](#0-0) 

The validator computes and compares the signature only over `to_signable_string`, and for `Webhooks::Request` that method returns just the raw HTTP body: [2](#0-1) 

Meanwhile, the tenant-identifying `shop` accessor — which is handed straight to the app's webhook handler as the trusted tenant identity — is pulled from the unauthenticated `shopify-shop-domain` / `x-shopify-shop-domain` header: [3](#0-2) 

`HmacValidator.validate` and `validate_signature` never look at any header, only `verifiable_query.to_signable_string`: [4](#0-3) 

So the equality that the gem implicitly relies on — "the shop the HMAC vouches for == the shop passed to the handler" — is false: the HMAC vouches only for the body, not for `shop-domain`. `Registry.process` then unconditionally trusts `request.shop` as the tenant identity for the dispatched event: [5](#0-4) 

### Impact Explanation
Because the shop identity is not bound to the signed content, any request that supplies a body and HMAC that pass validation (e.g. a previously-observed/replayed body+HMAC pair, or a topic whose payload is static/generic across shops) can be re-submitted with an arbitrary `shop-domain` header value. The app's webhook handler will process the event and write/act on data as if it originated from a different, attacker-chosen tenant — a cross-tenant boundary crossing driven entirely by header manipulation that the gem does nothing to prevent. This matches the Critical "cross-tenant access" impact category, since the vulnerable code path (`Registry.process` → `WebhookMetadata.new(shop: request.shop, ...)`) is the gem's own trust boundary for multi-tenant webhook dispatch.

### Likelihood Explanation
Exploitation requires the attacker to already possess one valid (body, HMAC) pair for the target app (the HMAC itself cannot be forged without the app's `client_secret`). This limits practical exploitation to replay scenarios (e.g., a previously captured/queued/retried webhook, or a topic with a fixed/generic payload shared across installs). The root cause, however, is unconditional and independent of how such a pair is obtained: the gem's `Request#to_signable_string` never covers `shop-domain`, so there is no defense-in-depth against header spoofing once any valid signature exists.

### Recommendation
Include the shop-domain (and ideally topic/webhook-id) in the HMAC-signable representation, or at minimum have `Registry.process` cross-check that the `shop-domain` header is consistent with data embedded in the verified body/topic before dispatching to the handler, so that the verified bytes and the acted-upon tenant identity are the same value.

### Proof of Concept
1. Attacker obtains any single valid `(raw_body, X-Shopify-Hmac-Sha256)` pair for the target app (e.g., a replayed/retried delivery, or a topic like `app/uninstalled` whose body is static/generic).
2. Attacker POSTs the same `raw_body` and `X-Shopify-Hmac-Sha256` value to the app's webhook endpoint, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com` instead of the original shop.
3. `HmacValidator.validate` in `lib/shopify_api/utils/hmac_validator.rb:12-31` passes because it only checks `raw_body` against the HMAC.
4. `Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-200`) dispatches the event to the registered handler with `shop: "victim-shop.myshopify.com"`, even though that shop never sent this webhook — a cross-tenant identity spoof.

### Citations

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
