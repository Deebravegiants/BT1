### Title
Webhook `shop-domain` is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/utils/hmac_validator.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw request body, then dispatches the webhook to the app's handler using the `shop-domain` header value taken verbatim from the request. The `shop` field is never part of the signed material, so the equality the app relies on — *the shop attributed to the webhook == the shop whose payload actually produced the HMAC* — is never enforced.

### Finding Description
`Request#to_signable_string` returns only the raw body: [1](#0-0) 

`Request#shop` simply reads the `shop-domain`/`x-shopify-shop-domain` header without any cryptographic binding to the body or the HMAC: [2](#0-1) 

`Utils::HmacValidator.validate` computes the signature exclusively from `verifiable_query.to_signable_string` (i.e. the body) and the app's shared `api_secret_key`: [3](#0-2) 

`Registry.process` gates on that HMAC check and then trusts `request.shop` to build the `WebhookMetadata` passed to the handler, which is the value host apps use to attribute the webhook data to a tenant: [4](#0-3) 

Because a single `api_secret_key`/`client_secret` is shared across all shops that install the app, any merchant who has installed the app can capture one of their own genuine webhook deliveries (a legitimate `raw_body` + `hmac-sha256` pair, since they are a real, unprivileged user of their own store) and replay that exact `raw_body`/HMAC pair to the app's webhook endpoint while substituting the `x-shopify-shop-domain` header with an arbitrary victim shop's domain. `HmacValidator.validate` still succeeds because the header is not part of the signed string, and `Registry.process` forwards `request.shop` (attacker-controlled) unchanged to the handler. The app then processes data (e.g., order/product/customer payloads) as if it originated from the victim shop, i.e., a cross-tenant data injection.

### Impact Explanation
This breaks the tenant boundary: `shop_used_for_attribution (attacker-controlled header) != shop_that_authenticated_the_payload (never bound to HMAC)`. Any host application that keys handling logic (data storage, session lookup, business logic) off `WebhookMetadata#shop` inherits cross-tenant contamination — an attacker who is merely a legitimate, unprivileged installer of the app on their own store can inject arbitrary but correctly-signed webhook bodies attributed to a different merchant. This matches the Critical "cross-tenant access" impact category.

### Likelihood Explanation
Likelihood is high for any attacker who has installed the app on at least one store (a routine, unprivileged action) since they can legitimately receive real webhook deliveries with valid HMACs signed by the shared `api_secret_key`. No access to the `client_secret`, no privileged account, and no TLS interception is required — only capturing one's own webhook traffic and replaying it with a different `shop-domain` header.

### Recommendation
Include the `shop-domain` (and ideally `topic`, `webhook-id`, `api-version`) in the signed/verifiable material, or independently verify that the `shop-domain` header corresponds to a shop that is actually authorized/associated with the delivered payload before dispatching to handlers. At minimum, document and enforce that host applications must not trust `request.shop` for cross-tenant attribution without additional verification (e.g., matching against a known list of shops that installed the app), since the current HMAC scheme in this gem only authenticates the body, not the sender's identity.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com`.
2. Shopify delivers a legitimate webhook to the app with body `B` and header `x-shopify-hmac-sha256: HMAC(secret, B)` and `x-shopify-shop-domain: attacker.myshopify.com`.
3. Attacker captures `B` and the valid HMAC value.
4. Attacker sends a forged POST to the app's webhook endpoint with the same body `B`, the same valid `x-shopify-hmac-sha256`, but `x-shopify-shop-domain: victim.myshopify.com`.
5. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only checks `HMAC(secret, B)` — this still matches, so validation passes: [5](#0-4) 
6. The handler receives `WebhookMetadata` with `shop: "victim.myshopify.com"` even though the payload never touched Shopify's servers for that shop, demonstrating cross-tenant webhook spoofing.

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
