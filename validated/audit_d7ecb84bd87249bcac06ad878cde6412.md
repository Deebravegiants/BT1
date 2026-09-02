### Title
Webhook HMAC validation covers only the raw body, not the `shop` header — cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` signs/verifies only the raw request body via HMAC, while the `shop` (tenant identifier) is read straight from an unauthenticated HTTP header and handed to application webhook handlers unchecked. Because the HMAC secret (`client_secret`) is shared across all shops that install a given app, any shop owner who legitimately installs the app can capture a valid `(body, hmac)` pair from their own webhook traffic and replay it with a forged `X-Shopify-Shop-Domain` header pointing at a victim shop. `Utils::HmacValidator.validate` will still report success because it never inspects the shop header, and `Registry.process` will invoke the app's handler believing the event originates from the victim tenant.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

The `shop` accessor is derived purely from the incoming header, independent of the signature: [2](#0-1) 

`HmacValidator.validate` computes the HMAC exclusively over `to_signable_string` (the body) and compares it to the `hmac` header — it never binds the `shop` field into the signed material: [3](#0-2) 

`Registry.process` trusts this validation and forwards `request.shop` straight into the handler's `WebhookMetadata`, using it as the tenant identity for the event: [4](#0-3) 

The equality that should hold is:
`shop_bound_by_signature == shop_delivered_to_handler`

but the code actually implements:
`hmac_valid_for(body) AND shop_delivered_to_handler = header value (unauthenticated)`

Since `body` and `hmac` are the only inputs verified, and the app's `client_secret` (the HMAC key) is identical for every shop that installs the app, a value that validates for shop A's webhook also validates for any header claiming to be shop B — the shop identity is never cryptographically bound to the signature.

### Impact Explanation
This breaks the tenant isolation boundary the HMAC check is meant to enforce. An attacker who installs the target app on their own store (an ordinary, unprivileged action any merchant can take) receives legitimate webhook deliveries with valid `(body, hmac)` pairs signed by the app's real `client_secret`. By replaying that exact body/HMAC pair while substituting the `X-Shopify-Shop-Domain` (or `Shopify-Shop-Domain`) header with a victim shop's domain, the attacker causes `ShopifyAPI::Webhooks::Registry.process` to accept the forged event as coming from the victim tenant, since `Utils::HmacValidator.validate` only checks the body/HMAC and never the shop header. Any host application logic that trusts `WebhookMetadata#shop` to select per-tenant state, credentials, or session data (which is the documented/expected usage pattern of this data) is exposed to cross-tenant data corruption or impersonation — this lands squarely in the "cross-tenant access" Critical impact bucket, since it is the gem's own verification routine, not host misuse, that fails to bind shop to the signature.

### Likelihood Explanation
Likelihood is high for any app built on this gem that relies on `Registry.process`/`Utils::HmacValidator.validate` as the sole authenticity check for webhooks (which is exactly the documented usage). No secrets beyond a normal app install are required — an attacker only needs to be a legitimate, unprivileged merchant who installs the target app once to harvest a valid signed payload, then can replay it indefinitely against arbitrary shop domains.

### Recommendation
Include the shop domain (and ideally the webhook id/topic) in the signed material verified by `HmacValidator`, or have `Registry.process` independently verify that the `shop` header corresponds to a shop actually associated with the webhook subscription that produced this specific `(body, hmac)` before dispatching to the handler. At minimum, document prominently that `request.shop` is unauthenticated and must not be trusted for tenant selection without additional verification.

### Proof of Concept
1. Install the target Shopify app on an attacker-controlled shop `attacker.myshopify.com`; trigger any webhook event (e.g., `orders/create`) and capture the raw POST body and the `X-Shopify-Hmac-Sha256` header — this pair is validly signed with the app's real `client_secret`.
2. Replay the exact same body and HMAC header to the app's webhook endpoint, but change `X-Shopify-Shop-Domain` to `victim.myshopify.com`.
3. Observe that `ShopifyAPI::Webhooks::Registry.process` (`lib/shopify_api/webhooks/registry.rb`, line 190) calls `Utils::HmacValidator.validate(request)` which returns `true` because only body+HMAC are checked (`lib/shopify_api/utils/hmac_validator.rb`, lines 27-31).
4. The handler is invoked with `WebhookMetadata.new(... shop: "victim.myshopify.com" ...)` (`lib/shopify_api/webhooks/registry.rb`, line 198), even though the payload never originated from that shop, confirming the shop identity is not bound to the signature.

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
