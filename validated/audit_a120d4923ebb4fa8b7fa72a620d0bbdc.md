### Title
Webhook `shop` (tenant) identity is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant identity (`shop`) from the unauthenticated `x-shopify-shop-domain` header, while the HMAC signature verified by `ShopifyAPI::Utils::HmacValidator` is computed only over the raw request body. The `shop` field that `ShopifyAPI::Webhooks::Registry.process` hands to the application's webhook handler is therefore never bound to the cryptographic signature, breaking the identity equality that `verified_hmac == true` should imply `shop == the_shop_that_generated_this_payload`.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop` is read straight from the `shopify-shop-domain`/`x-shopify-shop-domain` header, which is not part of that signable string: [2](#0-1) 

`HmacValidator.validate` only checks the HMAC over `to_signable_string` (i.e., the body), never the headers: [3](#0-2) 

`Registry.process` verifies the HMAC and then dispatches to the handler using `request.shop` as the tenant identifier, treating it as trusted once the HMAC check passes: [4](#0-3) 

Because the shop header is excluded from the signed bytes, any `(raw_body, hmac)` pair that is valid for shop A remains valid if the `x-shopify-shop-domain` header is swapped to shop B — the signature check still succeeds, but the tenant binding is now attacker-controlled. This is exactly the "field acted on but not covered by the HMAC" identity-binding break called out in scope: the equality that should hold is `hmac_valid(raw_body) ⇒ shop_header == originating_shop`, but the code only proves `hmac_valid(raw_body)`, and `shop` is taken from an unsigned header.

### Impact Explanation
An attacker who controls any shop that has the target app installed (i.e., an ordinary merchant/unprivileged user of the app, no access to `api_secret_key` required) can obtain a genuine `(raw_body, hmac)` pair by triggering any webhook-eligible event on their own store and capturing the resulting webhook delivery to the app's public webhook endpoint. They can then resend that exact body/HMAC pair to the same public endpoint with the `x-shopify-shop-domain` header rewritten to a victim shop's domain. `HmacValidator.validate` will accept it, and `Registry.process` will hand the handler a `WebhookMetadata` object whose `shop` is the victim's domain but whose `body` is attacker-chosen content, causing the host application to process/persist attacker-controlled data under the victim shop's tenant scope — a cross-tenant data-integrity/confusion issue reachable purely through the gem's own webhook verification path.

### Likelihood Explanation
Any developer using the documented `ShopifyAPI::Webhooks::Registry.process(request)` flow with the standard `ShopifyAPI::Webhooks::Request` is exposed, since the vulnerability is entirely inside this gem's verification logic and not a misuse of the documented API. The prerequisite (installing the app on an attacker-controlled shop and replaying a captured genuine webhook against the public webhook endpoint with a modified header) requires no privileged credentials, tokens, or secrets — only normal merchant-level access to trigger one webhook event and network access to the app's public webhook URL.

### Recommendation
Bind the tenant identity into the verified signature material, or otherwise cryptographically tie `shop` to the payload before trusting it:
- Include `topic`, `shop-domain`, and `webhook-id` in the signable string used by `HmacValidator`, or
- After HMAC verification, cross-check `shop` against an out-of-band trusted source (e.g., look up the webhook subscription/session associated with `webhook_id` and confirm it belongs to the claimed shop) before dispatching to the handler in `Registry.process`.

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com` and triggers a webhook-eligible event (e.g., `orders/create`), causing Shopify to POST to the app's public webhook endpoint with a body `B` and header `x-shopify-hmac-sha256: H` where `H = HMAC_SHA256(api_secret_key, B)`.
2. Attacker captures this request (e.g., via a debugging proxy they control, or because the endpoint echoes/logs it).
3. Attacker resends the identical `B` and `H` to the same public webhook endpoint, but replaces the header:
   `x-shopify-shop-domain: victim-shop.myshopify.com`
4. `Utils::HmacValidator.validate` recomputes `HMAC_SHA256(api_secret_key, B)` and compares it to `H` — this still matches since `B` is unchanged, per [5](#0-4) .
5. `Registry.process` proceeds and invokes the handler with `shop: "victim-shop.myshopify.com"` and `body:` the attacker's own event data, per [4](#0-3) , causing the host application to act on the victim tenant using attacker-controlled data.

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
