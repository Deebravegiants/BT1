### Title
Webhook shop-domain header spoofing bypasses cross-tenant identity binding — HMAC signs only the raw body, not the shop/topic/webhook-id headers (`lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by verifying the HMAC over the raw request body via `HmacValidator.validate`, then dispatches the handler using `request.shop`, `request.topic`, and `request.webhook_id` taken straight from HTTP headers that are **not** covered by that HMAC. This breaks the binding `hmac_signed_bytes == tenant_identity_bytes`: the signature only authenticates the JSON body, while the tenant (`shop`) that the handler treats as authoritative comes from unauthenticated header bytes.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`HmacValidator.validate` computes the signature exclusively over `verifiable_query.to_signable_string` (i.e., the raw body) and compares it to the `hmac-sha256` header: [2](#0-1) 

`shop`, `topic`, `api_version`, and `webhook_id` are all read directly from headers with no cryptographic tie to the body or to each other: [3](#0-2) 

`Registry.process` validates the HMAC and then immediately trusts `request.shop` as the tenant identity passed into the app's handler: [4](#0-3) 

Because the app's `api_secret_key` is shared across **every** shop that installs the app (it is not shop-specific), any merchant who installs the app can register a custom webhook subscription pointing at a server they control, capture a legitimately-signed `(body, hmac)` pair for their own shop, and replay that exact body+HMAC to the app's real webhook endpoint while substituting the `x-shopify-shop-domain` (and optionally `x-shopify-topic`/`x-shopify-webhook-id`) header with a victim shop's domain. `HmacValidator.validate` still succeeds because it never inspects those headers, and `Registry.process` forwards the forged `shop` value to the app's handler as `WebhookMetadata#shop`, alongside the attacker's own (attacker-chosen) body content.

### Impact Explanation
This is a cross-tenant identity binding bypass: an app's webhook handler that keys any tenant-scoped action (e.g., looking up the victim's stored access token/session, updating victim shop records, triggering fulfillment/order/customer-data logic) off `WebhookMetadata#shop` can be made to execute attacker-controlled body content under a spoofed victim `shop` identity. Per the rubric this constitutes cross-tenant access — a Critical-impact class.

### Likelihood Explanation
Exploitation only requires being an ordinary (even free/dev) merchant who installs the target app — no privileged credentials, `api_secret_key`, leaked tokens, or TLS interception are needed. The attacker can trivially obtain a validly-signed body+HMAC pair by pointing a custom webhook subscription for their own shop at infrastructure they control, then replay it with a modified shop header against the app's public webhook endpoint.

### Recommendation
Include the identity-critical headers (`shop-domain`, `topic`, `api-version`, `webhook-id`) in the signed material that `HmacValidator` verifies, or otherwise cryptographically bind them to the body (e.g., derive/verify `shop` independently, such as cross-checking it against a shop identifier embedded in the payload, or require the app to independently authenticate the shop before trusting `WebhookMetadata#shop`). At minimum, document prominently that `WebhookMetadata#shop` is not covered by the HMAC and must not be trusted as tenant identity without additional verification.

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker.myshopify.com` and registers a custom webhook subscription (e.g., `orders/create`) pointed at `https://attacker-server.example/capture`.
2. Attacker triggers the event, Shopify sends a request to the attacker's server with a body `B` and header `x-shopify-hmac-sha256: HMAC(B, api_secret_key)` — attacker now possesses a valid `(B, hmac)` pair signed with the app's shared secret.
3. Attacker POSTs the captured body `B` and HMAC header unchanged to the real app's webhook endpoint, but sets:
   - `x-shopify-shop-domain: victim.myshopify.com`
   - `x-shopify-topic`/`x-shopify-webhook-id` as desired
4. `HmacValidator.validate` in `lib/shopify_api/utils/hmac_validator.rb` succeeds because it only checks `B` against the HMAC.
5. `Registry.process` in `lib/shopify_api/webhooks/registry.rb` dispatches the app's handler with `shop: "victim.myshopify.com"` and body `B` (attacker-controlled), causing the app to process attacker data under the victim shop's tenant context.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-33)
```ruby
      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
      end

      sig { returns(String) }
      def api_version
        T.cast(shopify_header("api-version"), String)
      end

      sig { returns(String) }
      def webhook_id
        T.cast(shopify_header("webhook-id"), String)
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
