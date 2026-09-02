### Title
Webhook Shop-Domain Spoofing via HMAC Binding Gap — Cross-Tenant Webhook Impersonation ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` signs and verifies only the raw request body over HMAC, while the tenant-identifying field (`shop-domain`) is read straight from an unauthenticated HTTP header and handed to the webhook handler as trusted tenant context. Because the app's `client_secret` (the HMAC key) is shared across every shop that installs the app, any merchant who installs the app can obtain a legitimately-signed webhook for their own store and replay it against the endpoint with the `shop-domain` header swapped to a victim shop, passing HMAC validation and causing the handler to process attacker-supplied data as if it originated from the victim tenant.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop` is read from the `shopify-shop-domain`/`x-shopify-shop-domain` header, which is not part of the signed content at all: [2](#0-1) 

`Registry.process` validates HMAC over the request and, once it passes, immediately trusts `request.shop` as the tenant identity passed into the handler: [3](#0-2) 

`HmacValidator.validate` computes the HMAC only over `verifiable_query.to_signable_string` (the body, for webhooks) and compares it to the `hmac` header: [4](#0-3) 

**The broken binding, as an equality:**
`HMAC_valid(body, client_secret) == true` is treated by `Registry.process` as if it meant `shop_header == originating_shop`. In reality the HMAC only proves `body` was produced by holders of `client_secret` — it says nothing about which shop the header claims to be. Since `client_secret` is the *same key for every shop that installs the app* (it is an app-level secret, not a per-shop secret), any merchant who installs the app can legitimately receive HMAC-signed webhook deliveries for their own store and then present that exact (`body`, `hmac`) pair to the app's webhook endpoint with an arbitrary `shop-domain` header. `Request#shop`, `Request#topic`, `Request#webhook_id`, and `Request#api_version` are all uncovered by the signature check, exactly mirroring the reported bug class of "a value acted on but not bound by the integrity check" (analogous to `baseSwapped` being rounded outside the range the check was meant to enforce).

### Impact Explanation
This is a cross-tenant identity-binding bypass: an unprivileged internet user (any merchant who can install the target app on their own store, including a free development store) can cause the host application's webhook handler to execute business logic under a spoofed `shop` value. Any host application that uses `WebhookMetadata#shop` as the tenant key (the pattern this gem's own docs/tests recommend, e.g. loading/activating a session for that shop before acting on the payload) will act on the victim shop's tenant context using attacker-controlled body content, meeting the "cross-tenant access" Critical impact criterion.

### Likelihood Explanation
Likelihood is high for any app that is installable by third parties (including via a free/dev store) since no privileged credentials, TLS interception, or social engineering are required — only installing the app once to harvest one legitimately-signed webhook body/HMAC pair, then replaying it with a different `shop-domain` header value.

### Recommendation
Extend the signable content (or perform an additional bound check) so the `shop-domain` (and ideally `topic`/`webhook_id`) values are cryptographically bound to the signature verification, or explicitly document/require host apps to independently verify that `request.shop` corresponds to a shop that installed the app before trusting it as tenant context — mirroring how the patch for the reported bug class bound the rounding operation to the actual constrained range instead of trusting an unchecked intermediate value.

### Proof of Concept
1. Attacker registers/installs the target Shopify app on their own store `attacker.myshopify.com`.
2. Shopify delivers a legitimate webhook to the app's endpoint:
   - Headers: `x-shopify-shop-domain: attacker.myshopify.com`, `x-shopify-hmac-sha256: <valid-HMAC-of-body>`, body: `{"id":123,...}`
3. Attacker captures this `(body, hmac)` pair and re-sends it to the same endpoint, only changing the header:
   - `x-shopify-shop-domain: victim.myshopify.com`
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only checks `HMAC(client_secret, body) == hmac` — unchanged from step 2: [3](#0-2) 
5. The handler executes with `WebhookMetadata.new(... shop: "victim.myshopify.com" ...)`, i.e., the app processes attacker-controlled body content under the victim's tenant identity.

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
