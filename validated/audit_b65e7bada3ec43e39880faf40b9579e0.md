### Title
Webhook `shop-domain` header is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` signs only the raw request body for HMAC validation, while the `shop` value that identifies which merchant/tenant the webhook belongs to is read from an unsigned HTTP header. `ShopifyAPI::Webhooks::Registry.process` trusts `Utils::HmacValidator.validate(request)` to prove authenticity, then forwards `request.shop` (from the unsigned header) straight to the app's handler as the tenant identity. This breaks the identity binding: **the shop the HMAC cryptographically authenticates ≠ the shop the handler is told the event belongs to.**

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop` is read from the `shopify-shop-domain`/`x-shopify-shop-domain` header, which is not part of the signed content at all: [2](#0-1) 

`HmacValidator.validate` only verifies `verifiable_query.to_signable_string` (i.e., the body) against the HMAC secret — it never checks that the `hmac` was computed for the specific `shop` header value presented: [3](#0-2) 

`Registry.process` gates on this same HMAC check and then hands `request.shop` (unsigned, attacker-controllable) to the handler as the authoritative tenant identity: [4](#0-3) 

Because the app's `client_secret` (used to compute the HMAC) is shared across **every shop that has installed the app**, any merchant who installs the app can trigger a real, validly-signed webhook to their own store (e.g., by updating a product, triggering `products/update`, etc.), capture the `(raw_body, hmac)` pair Shopify sends, and then replay that exact body/HMAC pair to the app's webhook endpoint while substituting the `shopify-shop-domain` header with a victim shop's domain. `HmacValidator.validate` will still pass, because it never verifies the header is bound to the signature, and `Registry.process` will invoke the handler with `WebhookMetadata.new(... shop: request.shop ...)` claiming the event is for the victim shop.

### Impact Explanation
This is a cross-tenant identity-binding failure: an unprivileged actor who is merely a legitimate (even free-trial) installer of the app — requiring no access to the `client_secret`, no access token, and no privileged account — can make the host application believe a webhook payload originated from a different, victim shop. Any host application logic that keys off `data.shop` from `WebhookMetadata` (e.g., updating per-shop state, invalidating data, writing to a per-shop record, or triggering redaction/compliance actions for `shop/redact`, `customers/redact`, `customers/data_request`) can be manipulated to act on the wrong tenant using attacker-supplied body content, which is a cross-tenant access/injection primitive.

### Likelihood Explanation
The only precondition is installing the app on any shop (or otherwise obtaining one legitimately-signed webhook body/HMAC pair), which is trivial and requires no leaked secrets or privileged access — attackers fully control the header while the signature check ignores it.

### Recommendation
Include the `shop-domain` (and ideally `topic`/`webhook-id`) values in the HMAC-signed content, or otherwise cryptographically bind the presented shop header to the signature validation, so that a signature computed for shop A's payload cannot be replayed while claiming to be shop B. At minimum, `HmacValidator`/`Registry.process` should reject requests where the shop is not verified as part of the signed material.

### Proof of Concept
1. Install the target app on attacker-controlled shop `attacker.myshopify.com`.
2. Trigger any subscribed webhook topic (e.g. update a product) so Shopify sends a legitimately HMAC-signed webhook: `POST /webhooks` with headers `x-shopify-shop-domain: attacker.myshopify.com`, `x-shopify-hmac-sha256: <valid-hmac-of-body>`, and some `raw_body`.
3. Replay the identical `raw_body` and `x-shopify-hmac-sha256` value to the same endpoint, but change `x-shopify-shop-domain` to `victim.myshopify.com`.
4. `Utils::HmacValidator.validate` in `lib/shopify_api/utils/hmac_validator.rb` returns `true` (it only checks the body against the secret), so `Registry.process` in `lib/shopify_api/webhooks/registry.rb` invokes the handler with `WebhookMetadata.new(shop: "victim.myshopify.com", body: <attacker-controlled>, ...)`, causing the app to process attacker-controlled data under the victim shop's identity.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-22)
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
