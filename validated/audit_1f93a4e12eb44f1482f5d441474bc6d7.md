### Title
Webhook `shop` claim is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` binds the HMAC signature to the raw request body only, not to the `shop-domain` header. `ShopifyAPI::Webhooks::Registry.process` trusts `request.shop` to identify which merchant/tenant the payload belongs to after validating only that the body's HMAC is correct. Because the same app `client_secret` is used to sign webhooks for every shop that has installed the app, any unprivileged user who runs the app on their own store can capture a genuinely-signed webhook (body + HMAC) and replay it directly to the app's webhook endpoint with a forged `shop-domain` header naming a victim shop, and the gem will accept it as valid.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Webhooks::Request#shop` is read straight from an unauthenticated HTTP header, with no cryptographic tie to the signature: [2](#0-1) 

`Utils::HmacValidator.validate` only recomputes the HMAC over `verifiable_query.to_signable_string` (i.e., the raw body) and compares it to the received `hmac`; it never incorporates `shop`: [3](#0-2) 

`Webhooks::Registry.process` performs this HMAC check and then, once it passes, hands `request.shop` (the unverified header) to the app's handler as the authoritative tenant identifier: [4](#0-3) 

The identity binding that should hold is:
`shop claimed in the "shopify-shop-domain" header == shop whose data the HMAC actually authenticates`

But because the signable string is body-only, this equality is never enforced — the HMAC only proves "some shop that has this app installed, and knows the shared `client_secret`-derived signature for this exact body, produced this request." It does not prove which shop. Since Shopify uses the app's single `client_secret` to sign webhooks for every shop that installs the app, an attacker who installs the app on their own shop legitimately receives real webhook deliveries with valid `(body, hmac)` pairs for their own store. They can then send an HTTP request directly to the app's webhook endpoint reusing that exact valid `(body, hmac)` pair, but with the `shopify-shop-domain` header rewritten to a victim shop's domain. `HmacValidator.validate` still succeeds (only the body is checked), and `Registry.process` dispatches to the handler with `WebhookMetadata#shop` set to the victim's domain.

### Impact Explanation
If a host application uses `WebhookMetadata#shop` to select which tenant's session/data to act on (a very common pattern — e.g. looking up a stored session by shop domain and performing writes, deletions, or notifications for "that shop"), an attacker can trigger actions attributed to and affecting a victim merchant's tenant using data forged from the attacker's own shop. This is a cross-tenant access primitive built entirely from the gem's webhook verification logic, which is explicitly one of the qualifying High/Critical impacts.

### Likelihood Explanation
Likelihood is high for any unprivileged internet user: installing the app on their own store is the normal, unprivileged path to receive real webhook deliveries; capturing a legitimate `(raw_body, hmac)` pair requires no special access; and crafting an HTTP POST with an altered `shopify-shop-domain` header while keeping the same body/HMAC requires no cryptographic secret at all, since the header is completely outside the signed data.

### Recommendation
Include the shop domain (and ideally topic/webhook id) inside the value that is HMAC-verified, or otherwise cryptographically bind the claimed `shop-domain` header to the signed payload before trusting it in `Registry.process`/`WebhookMetadata`. At minimum, document/require that consuming applications cross-check `request.shop` against a shop known to have a stored, installed session before acting on the payload, since the gem itself does not perform this binding.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com` and triggers a normal webhook-eligible event (e.g. `orders/create`).
2. Shopify delivers a POST to the app's webhook endpoint with headers `x-shopify-shop-domain: attacker.myshopify.com`, `x-shopify-hmac-sha256: <valid-hmac-of-body>`, and some JSON `raw_body`.
3. Attacker captures this exact `raw_body` and `x-shopify-hmac-sha256` value.
4. Attacker sends their own POST directly to the app's webhook endpoint with the same `raw_body` and `x-shopify-hmac-sha256`, but sets `x-shopify-shop-domain: victim.myshopify.com`.
5. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only checks the body's HMAC (`lib/shopify_api/webhooks/request.rb` `to_signable_string`, `lib/shopify_api/utils/hmac_validator.rb` `validate`).
6. The registered handler is invoked with `WebhookMetadata#shop == "victim.myshopify.com"`, even though the payload actually originated from and describes the attacker's own store.

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
