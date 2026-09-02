### Title
Webhook `shop-domain` header is trusted for tenant identification but is not covered by the HMAC signature - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes and verifies the webhook HMAC over the raw request body only. The `shop-domain`, `topic`, `api-version`, and `webhook-id` headers are read directly from unauthenticated HTTP headers and are never part of the signed data, yet `Registry.process` hands `request.shop` straight to the app's handler as the tenant identifier.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop` is parsed straight from the `shopify-shop-domain`/`x-shopify-shop-domain` header with no cryptographic binding to the body or to the HMAC: [2](#0-1) 

`Utils::HmacValidator.validate` only recomputes the signature over `to_signable_string` (the body) and compares it to the `hmac` header: [3](#0-2) 

`Registry.process` treats a passing HMAC check as proof that the *entire request*, including `request.shop`, is authentic, and forwards `request.shop` unauthenticated into `WebhookMetadata` for the handler to act on: [4](#0-3) 

This breaks the intended identity binding: `hmac-covered bytes == bytes acted on`. The signature only proves "this body was signed with the app's secret at some point"; it says nothing about which shop it was signed for. A caller can pair a validly-HMAC'd body (from any webhook event the attacker can legitimately trigger on their own shop, since the app secret is shared across all shops installing the app) with an arbitrary `shop-domain` header, and the library will still report the request as HMAC-valid and pass the attacker-chosen `shop` value to the handler as if Shopify itself vouched for that shop/body pairing.

### Impact Explanation
Any app that uses `WebhookMetadata#shop` (as returned by this gem) to key per-tenant side effects (e.g., "update shop X's record with this body") can be made to apply attacker-supplied webhook content under a victim shop's identity, since the gem provides no assurance that the `shop` field is bound to the signed body. This is a cross-tenant identity-binding break stemming directly from this gem's `Webhooks::Request`/`Registry.process` contract, which callers rely on for authenticity of the `shop` field, not just the body.

### Likelihood Explanation
Likelihood is Medium-to-High for any app that installs on multiple shops (the normal case) and calls `Registry.process`: any user able to trigger a webhook-eligible event on their own installed shop can capture a validly-signed `raw_body` + `hmac` pair and replay it against the app's webhook endpoint with a modified `shop-domain` header, since nothing in this gem ties the header to the signature.

### Recommendation
Do not treat `request.shop` as authenticated solely because `HmacValidator.validate` passed. Either:
- Extend the signed payload check to bind `shop-domain` (and ideally `topic`/`webhook-id`) into the value verified against the HMAC, or
- Clearly document that `shop` is unauthenticated and require callers to cross-check it against a known/expected shop (e.g., the shop associated with the session/subscription that registered the webhook) before using it for tenant-scoped operations, and consider exposing a helper that performs this cross-check.

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker.myshopify.com` and triggers a webhook event, capturing the raw POST body `B` and the resulting `x-shopify-hmac-sha256` header `H` (valid because it's signed with the app's shared secret over `B`).
2. Attacker POSTs to the app's webhook endpoint with body `B`, header `x-shopify-hmac-sha256: H` (unchanged, still valid), but `x-shopify-shop-domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks `B` against `H`: [4](#0-3) 
4. The handler receives `WebhookMetadata` with `shop: "victim.myshopify.com"` and body `B`, even though `victim.myshopify.com` never sent this event, letting the attacker inject attacker-controlled webhook content under the victim shop's identity in any app logic keyed off `data.shop`.

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
