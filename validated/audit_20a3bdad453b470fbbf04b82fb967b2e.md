### Title
Webhook shop-domain identity spoofing via replay — HMAC covers only the raw body, not the `shop` field used for tenant attribution ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, while `shop` is read directly from the unsigned `x-shopify-shop-domain` / `shopify-shop-domain` HTTP header. `Utils::HmacValidator.validate` (used by `Webhooks::Registry.process`) verifies the HMAC solely against that raw body. Since the `shop` field is never part of the signed payload, it is not bound to the request's authenticity, and it is passed straight through to the handler as if it were verified.

### Finding Description
`Registry.process` performs a single authenticity check before dispatch: [1](#0-0) [2](#0-1) 

That check is: [3](#0-2) 

The signature is computed over `verifiable_query.to_signable_string`. For webhook requests, that is defined as: [4](#0-3) 

but `shop` is derived independently from an HTTP header that is never included in the signed string: [5](#0-4) 

The identity binding that should hold is:
`shop_used_by_handler == shop_that_the_HMAC_actually_authenticates`

But because `to_signable_string` only covers `@raw_body`, the actual invariant enforced is:
`HMAC(raw_body) == received_hmac`, with `shop` entirely outside that check.

This means any request whose raw body and HMAC are a genuine, previously-observed valid pair (e.g., a webhook the attacker legitimately received for their own store, or one sniffed from any exposed endpoint/log) remains "HMAC-valid" no matter what `x-shopify-shop-domain` value is attached to it. `Registry.process` will pass that forged/replayed request straight to the app's registered handler with `shop: request.shop` (the attacker-chosen header value), because the field-to-signature binding does not exist. The `webhook_id`, `topic`, and `api_version` headers are likewise unauthenticated, but `shop` is the most impactful since host applications commonly use it to determine which tenant's data to look up/update.

### Impact Explanation
This breaks a tenant-identity binding: a webhook attributed to shop A can be replayed with the shop header rewritten to shop B, while the HMAC check still succeeds. Any host application that uses `WebhookMetadata#shop` (built directly from `request.shop`) to select which merchant's records to act on will process attacker-controlled data under a victim shop's identity — a cross-tenant confusion driven entirely by this gem's verification gap, since the gem gives no way for the caller to know the `shop` value was not authenticated by the signature it just validated.

### Likelihood Explanation
Exploitation requires the attacker to possess at least one raw_body+HMAC pair that is valid under the app's shared `api_secret_key` for the app's shared endpoint — trivially obtainable by installing the app on their own (unprivileged) store and capturing one of their own inbound webhook deliveries. No access token, `client_secret`, or privileged access is required; the app's public webhook endpoint is the only thing touched, and the header can be freely modified in the replayed HTTP request.

### Recommendation
Include `shop` (and ideally `topic`/`webhook_id`) in the signed payload used by `to_signable_string`, or otherwise cryptographically bind the shop-domain header to the HMAC check before it is exposed via `WebhookMetadata`. At minimum, document prominently that `WebhookMetadata#shop` is not authenticated by `HmacValidator.validate` and that consuming applications must independently confirm the shop identity (e.g., against a known/registered shop list) before trusting it.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com` and receives one legitimate webhook delivery with body `B` and header `x-shopify-hmac-sha256: H` (valid for the app's shared `api_secret_key`).
2. Attacker sends a POST to the app's webhook endpoint with the same body `B` and header `x-shopify-hmac-sha256: H`, but sets `x-shopify-shop-domain: victim.myshopify.com`.
3. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `request.to_signable_string` (== `B`) — this matches `H`, so validation succeeds: [6](#0-5) 
4. The handler is invoked with `WebhookMetadata.new(shop: "victim.myshopify.com", body: parsed(B), ...)`: [7](#0-6) 
5. Any handler logic keyed on `data.shop` now operates on the victim's tenant using attacker-controlled body content, despite the HMAC check having "passed."

### Citations

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
