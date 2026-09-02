Based on my analysis, I found a valid analog: the webhook HMAC signature only covers the request body, but the `shop` field used for tenant identification is never included in the signed content, allowing a malicious merchant to replay a legitimately-signed webhook payload while spoofing the shop-domain header.

### Title
Webhook shop-domain header is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body [1](#0-0)  , and `HmacValidator.validate` verifies the received HMAC solely against that signable string [2](#0-1) . The `shop` (tenant identity) is read straight from the `x-shopify-shop-domain`/`shopify-shop-domain` header without any cryptographic binding to the signed payload [3](#0-2) . `Registry.process` validates the HMAC and then hands `request.shop` straight to the webhook handler as trusted tenant identity [4](#0-3) .

### Finding Description
The equality that should hold is: `shop_identity_used_by_handler == shop_that_actually_generated_the_signed_body`. Because the HMAC only signs the body bytes and the app's `api_secret_key` is shared across every shop that installs the app (it is not per-shop), any merchant who installs the app receives genuinely-signed webhooks for their own shop. That attacker-merchant can capture a real `(body, hmac)` pair from their own store's webhook deliveries, then POST the identical body and HMAC to the app's webhook endpoint while substituting the `x-shopify-shop-domain` header with a victim shop's domain. `HmacValidator.validate` passes because it only checks the body against the shared secret [5](#0-4) , and `Registry.process` then constructs `WebhookMetadata` using the forged `request.shop` value, dispatching it to the handler as if it originated from the victim tenant [4](#0-3) .

### Impact Explanation
This breaks the tenant-identity binding at the core of any multi-tenant webhook handler. A host application that trusts `WebhookMetadata#shop` (as documented and exercised in the library's own tests, e.g. `data.shop` in `test/webhooks/registry_test.rb`) to select which tenant's data to update will process forged events under a victim shop's identity — cross-tenant data injection/manipulation. This maps to the "Critical - cross-tenant access" impact category.

### Likelihood Explanation
Requires only that the attacker be a legitimate (unprivileged) merchant who installs the target app on their own store — a normal, self-service action requiring no special privileges, credentials, or access to the app's `client_secret`/`api_secret_key`. They only need to capture one of their own real webhook deliveries and replay it with a modified header.

### Recommendation
Bind the tenant identity into the verified signature surface (e.g., require the host application to cross-check `request.shop` against the shop that owns the specific `webhook_id`/subscription, or otherwise reject webhooks whose `shop` does not match a shop the app has an active session/installation for), rather than trusting the raw header once the body-only HMAC passes.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` (self-service, no privileges needed).
2. Shopify delivers a genuine webhook to the app: body `B`, header `x-shopify-hmac-sha256: HMAC(secret, B)`, `x-shopify-shop-domain: attacker-shop.myshopify.com`.
3. Attacker replays a POST to the app's webhook endpoint with the same body `B` and same HMAC, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `Utils::HmacValidator.validate` returns `true` (it only checks `B` against the secret) [6](#0-5) , and `Registry.process` invokes the handler with `WebhookMetadata` reporting `shop: "victim-shop.myshopify.com"` [7](#0-6) , causing the host app to act as though the event came from the victim tenant.

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
