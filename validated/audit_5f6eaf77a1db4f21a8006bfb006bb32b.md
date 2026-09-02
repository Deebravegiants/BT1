### Title
Webhook `shop` identity not covered by HMAC allows cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes the HMAC-signable string from the raw request body only, while `shop`, `topic`, and `webhook_id` are read straight from HTTP headers with no cryptographic binding to that body/signature. Any caller who obtains one valid `(raw_body, hmac)` pair can resend it with an arbitrary `x-shopify-shop-domain` header, and `ShopifyAPI::Webhooks::Registry.process` will accept it as authentic and hand the spoofed shop identity to the app's webhook handler.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

but `shop` (and `topic`, `webhook_id`, `api_version`) are pulled directly from headers, independent of the signed content: [2](#0-1) 

`HmacValidator.validate` only verifies `verifiable_query.to_signable_string` against the HMAC, i.e. only the body bytes: [3](#0-2) 

`Registry.process` checks that HMAC and then immediately trusts `request.shop` as the tenant identity passed to the app-supplied handler, without any additional binding between `shop` and the signed body: [4](#0-3) 

The identity equality that should hold is: `shop_bound_by_hmac == shop_used_by_handler`. Here it does not — `shop` is verified==false while it is used==true. This is the concrete instance of the report's bug class: "a field acted on but not covered by the HMAC."

### Impact Explanation
Because the webhook endpoint is a public HTTP endpoint (any unprivileged internet user can POST to it) and the `shop` header is excluded from the HMAC, once an attacker has any single valid `(body, hmac)` pair — trivially obtainable by installing/uninstalling their own free/dev store and capturing their own real webhook delivery, or by intercepting any webhook whose body is generic/predictable — they can replay that exact body+hmac while substituting a victim shop's domain in `x-shopify-shop-domain`. `Registry.process` will pass this spoofed `shop` value straight into the handler via `WebhookMetadata`, so any app logic keyed off `shop` (e.g., updating stored session/state, disabling access, processing `app/uninstalled`, syncing shop-level data) executes under a shop identity that was never authenticated. This is a cross-tenant identity confusion at the library level — the app receives forged tenant attribution despite the HMAC check reporting success.

### Likelihood Explanation
Likelihood is meaningfully high in gems/apps that trust `WebhookMetadata#shop` for tenant-scoped actions (the intended and documented use of this field), since obtaining one valid signed payload only requires being any merchant (including a free dev store) that can trigger a real webhook, which is an unprivileged path with no secret leakage required. The remaining risk is bounded by what the specific host application does with `shop` (severity depends on the handler), but the library itself provides no protection against this class of spoofing.

### Recommendation
Bind `shop` (and ideally `topic`/`api_version`) into the signature verification decision, or explicitly document/deny use of the shop header as an authenticated tenant identifier unless corroborated by other means (e.g., cross-checking against the shop embedded in the JSON body where available, or maintaining per-webhook-id idempotency plus rejecting shop/body combinations that don't match a previously observed pairing for that shop). At minimum, `Registry.process` should not treat `request.shop` as trusted without further validation, and documentation should warn integrators that `WebhookMetadata#shop` is unauthenticated header data.

### Proof of Concept
1. Attacker installs the target app on their own shop (`attacker.myshopify.com`) and triggers any generic webhook (e.g. `app/uninstalled`), capturing the raw request body `B` and the valid `X-Shopify-Hmac-Sha256` header `H` that Shopify computed over `B` using the shared `api_secret_key`.
2. Attacker sends a new POST request to the app's webhook endpoint with body `B`, header `X-Shopify-Hmac-Sha256: H` (unchanged, still valid because it only signs `B`), but `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only checks `B` against `H`.
4. `request.shop` returns `"victim-shop.myshopify.com"` and is passed to the app's handler via `WebhookMetadata.new(... shop: request.shop ...)`, causing the app to process the webhook as if it legitimately originated from `victim-shop.myshopify.com`.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
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
