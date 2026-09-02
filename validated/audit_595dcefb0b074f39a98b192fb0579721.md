### Title
Webhook shop-domain spoofing due to HMAC covering only the request body, not the `shop-domain` header - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
This is the same bug *class* as the Size report: a validation is performed on data that does not cover everything the code subsequently trusts. In `Size.sol`, the deposit-cap checks operate on aggregate/derived values that don't correspond 1:1 to the value that actually matters (debt emitted), causing a mismatch between what's checked and what's acted upon. In this gem, `ShopifyAPI::Webhooks::Registry.process` verifies a webhook's HMAC, but the HMAC signable string is only the raw body — the `shop-domain` header that is subsequently trusted and handed to the app's webhook handler is never covered by that signature.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`ShopifyAPI::Utils::HmacValidator.validate` verifies the HMAC exclusively against that signable string using the app's `client_secret` (`Context.api_secret_key`): [2](#0-1) 

`ShopifyAPI::Webhooks::Registry.process` gates on `Utils::HmacValidator.validate(request)` and, once it passes, forwards `request.shop` (read straight from the `X-Shopify-Shop-Domain` HTTP header, not from the signed body) to the handler as the tenant identifier: [3](#0-2) [4](#0-3) 

The binding that should hold is: `hmac == HMAC(secret, shop || body)` such that `shop` is cryptographically tied to the signature. Instead the actual binding enforced is only `hmac == HMAC(secret, body)`. Because `shop` is transported as a separate, unsigned HTTP header, it can be swapped for any value after a genuinely-signed `(body, hmac)` pair has been obtained — for example from a webhook a merchant/attacker legitimately received on their own store (any unprivileged internet user can install a public app on a store they control and receive real, correctly-signed webhooks for it, since the app's `client_secret` is shared across all installs of that app). Re-POSTing that same body/HMAC pair to the app's webhook endpoint with the `X-Shopify-Shop-Domain` header changed to a victim shop's domain passes `HmacValidator.validate` unchanged, and `Registry.process` dispatches to the handler believing the payload originated from the victim shop.

### Impact Explanation
This breaks the tenant/shop identity binding for inbound webhook data without needing the app's `client_secret`, an access token, or any privileged credential — it only requires the ability to install the app on any store (a normal, unprivileged action) to harvest one valid `(body, hmac)` pair, then a forged HTTP request to the app's own webhook receiver. Depending on how the host application's `handler.handle` uses `WebhookMetadata#shop` (e.g., to look up which merchant's data to update/delete, or to route webhook effects), this can enable cross-tenant data confusion/corruption inside the app that embeds this gem — matching the "cross-tenant access" High-impact category in scope.

### Likelihood Explanation
Likelihood is moderate-to-high in practice: this gem is the mechanism host apps rely on to authenticate webhooks (`ShopifyAPI::Webhooks::Registry.process`), and its documented contract implies `HmacValidator.validate` fully authenticates the webhook, including which shop it is for. Any app that trusts `WebhookMetadata#shop` for routing/authorization decisions (a very common pattern, since that's the field's evident purpose) is exposed. Obtaining a valid signed body/HMAC pair only requires installing the app once on an attacker-controlled store, which requires no special privilege.

### Recommendation
Include the `shop-domain` (and ideally `topic`/`webhook-id`) header values in the signable string used for HMAC verification, or otherwise cryptographically bind them (e.g., verify the shop against an out-of-band authoritative source such as a known/registered shop record) before trusting `request.shop`. At minimum, `to_signable_string` in `lib/shopify_api/webhooks/request.rb` should incorporate all headers whose values the handler subsequently trusts, not just the raw body.

### Proof of Concept
1. Attacker installs the target public app on `attacker.myshopify.com` and registers/triggers a webhook (e.g., `orders/create`) with an empty or attacker-chosen JSON body `B`.
2. Shopify sends the webhook with headers `X-Shopify-Hmac-Sha256: H = HMAC-SHA256(client_secret, B)` and `X-Shopify-Shop-Domain: attacker.myshopify.com`.
3. Attacker captures `B` and `H` (both are visible to them since it's their own server/store).
4. Attacker re-sends a POST to the victim app's webhook endpoint with body `B`, header `X-Shopify-Hmac-Sha256: H` unchanged, but `X-Shopify-Shop-Domain: victim.myshopify.com`.
5. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only hashes `@raw_body` (`B`) — validation succeeds because `H` still matches `HMAC(client_secret, B)`.
6. The handler is invoked with `WebhookMetadata.new(topic: ..., shop: "victim.myshopify.com", body: parsed(B), ...)` — the app now processes attacker-supplied data attributed to the victim shop.

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
