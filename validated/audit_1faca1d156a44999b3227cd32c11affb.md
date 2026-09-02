## Finding

### Title
Webhook `shop-domain` header is not covered by the HMAC signature, allowing cross-tenant shop-identity spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw request body. The `shop` value that is later handed to the consuming application's webhook handler as the tenant identifier is read from the `X-Shopify-Shop-Domain` header, which is never included in the signed material. This breaks the identity binding `hmac_covers(shop) == true`.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop` is read independently from the `shopify-shop-domain`/`x-shopify-shop-domain` header and is not part of that signable string: [2](#0-1) 

`Registry.process` validates the request using `Utils::HmacValidator.validate(request)`, which only checks the HMAC over `to_signable_string` (i.e., the raw body), and then unconditionally forwards `request.shop` (the unauthenticated header value) into `WebhookMetadata`, which is passed to the app's handler as the tenant identifier: [3](#0-2) 

`Utils::HmacValidator.validate` computes and compares the signature purely against `verifiable_query.to_signable_string`: [4](#0-3) 

Because the HMAC secret (`Context.api_secret_key`, the app's `client_secret`) is shared by the app across *all* shops that install it, any merchant who installs the app can trigger Shopify to send them a legitimately-signed webhook (valid `raw_body` + valid `hmac`) for their own shop. That attacker-controlled shop can then replay the exact same body+HMAC to the app's webhook endpoint while substituting the `X-Shopify-Shop-Domain` header with a victim shop's domain. `HmacValidator.validate` will still succeed (it only checks body integrity/authenticity, not origin), so `Registry.process` will call the handler with `WebhookMetadata#shop` set to the victim's domain while the body content is fully attacker-chosen (subject to whatever fields Shopify includes for that topic, e.g., customer/order free-text fields). Any handler that uses `data.shop` to select which tenant's records to create/update will write attacker-controlled data into the victim shop's tenant scope — a cross-tenant boundary violation rooted entirely in this gem's webhook verification, not application misuse.

### Impact Explanation
This is a genuine identity-binding break inside the gem's own webhook verification code: the field (`shop`) that the handler uses to scope per-tenant operations is not covered by the cryptographic check that is supposed to authenticate the request. It enables cross-tenant data injection/spoofing (an app-installing attacker forging webhook data attributed to another merchant's shop), matching the Critical "cross-tenant access" impact category.

### Likelihood Explanation
Any unprivileged user can install the target app on their own store (no special privileges beyond being a Shopify merchant), trigger events on their own shop to receive genuinely HMAC-signed webhook deliveries, then replay the captured body+HMAC pair against the app's public webhook endpoint with a forged `Shop-Domain` header. No access to `api_secret_key`, tokens, or the victim's credentials is required.

### Recommendation
Bind `shop` (and ideally `topic`/`webhook_id`/`api_version`) into the material verified by the HMAC check — e.g., require the consuming application to independently verify that the `shop` header corresponds to a shop with a stored, valid session/access token before trusting `WebhookMetadata#shop`, or extend `to_signable_string` to be computed the same way Shopify computes it (body only, per Shopify's spec) but require the gem's `Registry.process` to also confirm the requesting `shop` is one for which an active session/install exists, so an unrelated shop's replayed payload cannot be attributed to another tenant.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com`.
2. Attacker triggers a webhook-eligible event (e.g., customer update) on their own shop, capturing the raw POST body and the `X-Shopify-Hmac-Sha256` header Shopify sends — this is a validly signed `(body, hmac)` pair for the app's `client_secret`.
3. Attacker replays this exact `(body, hmac)` pair to the same app's webhook endpoint, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only checks HMAC over `raw_body` (see `lib/shopify_api/webhooks/request.rb:35-38` and `lib/shopify_api/utils/hmac_validator.rb:12-31`).
5. The handler is invoked with `WebhookMetadata.new(... shop: "victim-shop.myshopify.com", body: <attacker-controlled parsed body> ...)` (`lib/shopify_api/webhooks/registry.rb:198-199`), causing the app to process attacker-supplied content as if it originated from the victim's shop.

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
