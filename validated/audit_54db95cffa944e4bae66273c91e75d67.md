## Title
Webhook `shop-domain` is not bound by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, never the `shop-domain` (or any other) header. `ShopifyAPI::Utils::HmacValidator.validate` and `ShopifyAPI::Webhooks::Registry.process` both accept a request as authentic solely because `HMAC(secret, raw_body)` matches, then trust `request.shop` — parsed straight from an attacker-controllable header — as the tenant identity handed to the app's webhook handler. The `shop` field is *acted on* (used to route/attribute the webhook to a specific merchant) but is not *covered* by the cryptographic check, breaking the intended binding `verified_bytes == shop_identity_used`.

### Finding Description [1](#0-0) 
`hmac` is computed by Shopify over the raw body only, and the class exposes `shop` purely by reading the `shopify-shop-domain`/`x-shopify-shop-domain` header: [2](#0-1) 
`to_signable_string` — the value that actually gets HMAC'd — is just `@raw_body`, with no header material mixed in.

Validation is performed generically via `VerifiableQuery`: [3](#0-2) 

And the registry trusts `request.shop` immediately after that check passes, handing it to the app-supplied handler as the tenant identity for the event: [4](#0-3) 

Because `api_secret_key` is the app's single client secret — shared across every merchant that installs the app, not derived per-shop — any merchant who has the app installed on their own store (Shop A) receives legitimately Shopify-signed webhook bytes: `raw_body` + valid `hmac-sha256`. That attacker fully controls the HTTP request they replay to the app's public webhook endpoint, including the `X-Shopify-Shop-Domain` header. Since the header is excluded from the signed content, the attacker can resend the exact same `raw_body`/`hmac-sha256` pair while substituting `X-Shopify-Shop-Domain: victim-shop.myshopify.com`. `HmacValidator.validate` still succeeds (same secret, same body ⇒ same digest), and `Registry.process` forwards `shop: "victim-shop.myshopify.com"` to the handler as if the event genuinely originated from the victim's store.

### Impact Explanation
This breaks the identity binding `hmac_verified(bytes) == shop_used_for_tenant_routing`. Any host application that uses `WebhookMetadata#shop` to look up/scope per-tenant records (the intended and documented usage pattern for this gem) can be tricked into writing, updating, or triggering side effects for a different merchant’s tenant using attacker-supplied webhook content that was never sent by Shopify for that shop. This is a cross-tenant data-integrity/isolation break directly enabled by this gem's webhook verification API, satisfying the "cross-tenant access" impact category.

### Likelihood Explanation
Exploitation only requires: (1) installing the target app on an attacker-controlled shop (the normal onboarding flow for any Shopify app), (2) triggering any webhook topic on that shop to obtain a valid `(raw_body, hmac-sha256)` pair, and (3) replaying that exact payload to the app's public webhook endpoint with a forged `shop-domain` header naming the victim shop. No knowledge of `api_secret_key` or the victim's credentials is needed. This is straightforward for any developer/merchant capable of installing the target app.

### Recommendation
Bind the claimed shop domain into the authenticated material before trusting it, e.g.:
- Include the `shop-domain` header in `to_signable_string` (not possible unilaterally since Shopify computes the digest over body only), or
- Cross-check `request.shop` against an app-side registry of `(webhook_id → shop)` pairs recorded at webhook registration time, or
- At minimum, document prominently that `WebhookMetadata#shop` is unauthenticated header data and that host applications must independently verify shop ownership (e.g., against the `webhook_id`, or an installed-shop table) before using it for tenant-scoped writes, and consider raising when the same `webhook_id` is seen for two different `shop` values.

### Proof of Concept
1. Install the target Shopify app on attacker-controlled shop `attacker.myshopify.com`.
2. Capture a legitimate webhook delivery, e.g. for `orders/create`:
   - `raw_body = '{"id":1,...}'`
   - `X-Shopify-Hmac-Sha256: <valid-signature-over-raw_body>`
   - `X-Shopify-Shop-Domain: attacker.myshopify.com`
3. Replay the identical `raw_body` and `X-Shopify-Hmac-Sha256` to the app's public webhook route, but set:
   - `X-Shopify-Shop-Domain: victim-shop.myshopify.com`
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks `HMAC(secret, raw_body)`, per: [2](#0-1) 
5. The app's registered handler is invoked with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...)`, causing it to act on the victim's tenant using attacker-supplied content.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-23)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end

      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

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
