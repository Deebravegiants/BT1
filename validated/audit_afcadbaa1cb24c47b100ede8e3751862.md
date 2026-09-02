### Title
Webhook `shop-domain` header is trusted without HMAC coverage, enabling cross-tenant webhook forgery - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-verifiable signature from the raw request body only, while the `shop` (and `topic`, `webhook_id`, `api_version`) values are read directly from HTTP headers that are never included in the signed content. This breaks the intended binding "shop authenticated == shop the webhook is attributed to," analogous to the reported `updatePhase`/`endRoundId` issue where a value used downstream was not bound to the identifier that should govern it.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) . The `shop` accessor, however, is derived independently from the `shopify-shop-domain`/`x-shopify-shop-domain` header: [2](#0-1) .

`Utils::HmacValidator.validate` verifies the HMAC strictly against `to_signable_string` (i.e., the raw body), never touching `shop`, `topic`, or `webhook_id`: [3](#0-2) .

`Webhooks::Registry.process` calls this validator and, once it passes, unconditionally trusts `request.shop` (and `request.topic`, `request.webhook_id`) to construct the `WebhookMetadata` handed to the app's handler: [4](#0-3) .

Because the shop-identifying header is not part of the signed bytes, the equality the system implicitly relies on — "HMAC-verified bytes == the tenant (`shop`) the payload is attributed to" — does not actually hold. Anyone who possesses one valid `(raw_body, hmac)` pair for topic X (which an app owner/merchant with their own store legitimately receives from Shopify) can resubmit that exact body/HMAC pair to the app's webhook endpoint while substituting an arbitrary `shopify-shop-domain` header value. `HmacValidator.validate` will still succeed because it only checks the untouched raw body, and the registry will process the request as if it originated from the victim shop.

### Impact Explanation
This crosses the tenant boundary this gem is supposed to enforce: an app's webhook handlers key merchant-specific side effects (session teardown, data sync, `app/uninstalled` cleanup, order/GDPR processing, etc.) on `WebhookMetadata#shop`. An attacker with a legitimate account on the platform can forge a webhook event that the host application will process under a different shop's identity, corrupting that shop's data/session state or triggering shop-scoped business logic without any authorization for that shop. This is a cross-tenant access issue.

### Likelihood Explanation
Exploitability requires the attacker to obtain at least one genuine `(raw_body, hmac)` pair, which any merchant installing the app receives automatically as part of normal webhook delivery for their own store — no leaked secret or privileged access is needed. The attacker only needs to be able to POST to the app's public webhook endpoint with a modified `shop-domain` header, which is standard unauthenticated internet access to that endpoint (the same as the real Shopify webhook delivery path). This makes the analog straightforward to exploit for any topic whose body content is attacker-influenced or replayable (e.g., topics with static/predictable bodies, or bodies the attacker directly generated in their own shop).

### Recommendation
Include `shop` (and ideally `topic`/`webhook_id`) in the HMAC-signed content, or otherwise cryptographically bind these header-derived identifiers to the signed payload before trusting them in `Registry.process`. At minimum, the shop attributed to a webhook must be verified as part of the same HMAC-protected value set, not read from an independently-controllable header.

### Proof of Concept
1. Attacker installs the app on their own shop `attacker.myshopify.com` and receives a legitimate webhook, e.g., topic `orders/create`, with headers:
   - `x-shopify-hmac-sha256: <valid HMAC over raw_body>`
   - `x-shopify-shop-domain: attacker.myshopify.com`
   - raw body: `{"id":123,...}` (attacker-controlled content, since it's their own order)
2. Attacker resends the exact same `raw_body` and `x-shopify-hmac-sha256` value to the app's public webhook endpoint, but sets `x-shopify-shop-domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses `shop` from the tampered header [2](#0-1) .
4. `HmacValidator.validate` recomputes the HMAC over `@raw_body` only, which matches, so validation passes [5](#0-4) .
5. `Registry.process` proceeds and invokes the registered handler with `WebhookMetadata` carrying `shop: "victim.myshopify.com"` and the attacker-crafted body [4](#0-3) , causing the host application to process attacker-controlled data as though it belongs to the victim shop.

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
