### Title
Webhook `shop-domain` header is not covered by the HMAC signature, allowing cross-tenant shop spoofing on replay - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant identity (`shop`) from the unauthenticated `x-shopify-shop-domain` HTTP header, while `Utils::HmacValidator` only verifies the raw request body. The `shop` field that host applications use to route data to a tenant is never bound to the HMAC that authenticates the webhook, breaking the equality `shop authenticated == shop covered by hmac`.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

The `shop` accessor, however, is read straight from the `shopify-shop-domain`/`x-shopify-shop-domain` header, completely independent of the signed payload: [2](#0-1) 

`Registry.process` validates the HMAC over the object via `Utils::HmacValidator.validate(request)`, which only ever calls `to_signable_string` (i.e. the body) and compares it against `request.hmac`: [3](#0-2) [4](#0-3) 

After the HMAC check passes, `request.shop` (the unauthenticated header value) is forwarded verbatim into `WebhookMetadata` and handed to the app's registered handler as the tenant identifier: [5](#0-4) 

Because the HMAC secret (`Context.api_secret_key`) is the same for every shop that has installed a given app, and the signature only covers the body bytes, any party who can obtain one validly-signed webhook payload (e.g. from a store where they control an install, or from a public webhook body they were able to observe/replay) can resend that exact body to the app's webhook endpoint while substituting the `x-shopify-shop-domain` header for a different, victim shop domain. The recomputed HMAC over the unchanged body still matches, `HmacValidator.validate` returns `true`, and the handler receives `WebhookMetadata` claiming the payload belongs to the victim shop.

### Impact Explanation
This breaks the identity binding "shop authenticated == shop the app acts on," letting an attacker attribute arbitrary webhook data to a tenant they do not control. Depending on how the host application keys its per-shop persistence/business logic off `WebhookMetadata#shop` (e.g., updating shop-scoped state, triggering shop-scoped side effects, invalidating caches, or writing to per-shop records), this is a cross-tenant data-integrity/confusion primitive delivered purely over the network with no credentials beyond one legitimately-signed webhook body. This matches the report's "field acted on but not covered by HMAC" analog and the in-scope "cross-tenant access" impact category.

### Likelihood Explanation
Exploitation requires only: (1) a valid HMAC-signed webhook body for the app's secret (attacker can obtain this via their own installed instance of the app or by capturing any request to the webhook endpoint), and (2) the ability to POST an HTTP request with a different `x-shopify-shop-domain` header value to the app's public webhook endpoint. No access token, `client_secret`, or privileged account is required — only network access to the endpoint, matching the "unprivileged internet user" threat model. Real-world exploitability further depends on the host application actually keying tenant-sensitive behavior off `WebhookMetadata#shop`, which is the gem's own documented usage pattern for webhook handlers.

### Recommendation
Bind the shop identity to the authenticated payload instead of trusting the header alone:
- Include the `shop-domain` header (and, ideally, `topic`/`webhook-id`) in the HMAC-signed string (`to_signable_string`), or
- Cross-check the header-derived `shop` against a shop value embedded in the JSON body where the topic guarantees one, and reject mismatches, or
- At minimum, document loudly that `request.shop` is unauthenticated and must be revalidated by the host app (e.g. against a known list of installed shops) before being used for any tenant-scoped action.

### Proof of Concept
1. App has two installed shops: `attacker-shop.myshopify.com` and `victim-shop.myshopify.com`, sharing the same `api_secret_key`.
2. Attacker triggers/observes a legitimately signed webhook for their own shop:
   ```
   POST /webhooks
   x-shopify-topic: orders/create
   x-shopify-hmac-sha256: <valid HMAC of body B computed with the app's secret>
   x-shopify-shop-domain: attacker-shop.myshopify.com
   Body: B
   ```
3. Attacker replays the identical body `B` and HMAC header, only changing the shop header:
   ```
   POST /webhooks
   x-shopify-topic: orders/create
   x-shopify-hmac-sha256: <same valid HMAC of body B>
   x-shopify-shop-domain: victim-shop.myshopify.com
   Body: B
   ```
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only checks `request.to_signable_string` (body `B`) against the HMAC — this still passes.
5. The registered handler receives `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: B, ...)`, i.e., attacker-controlled data now attributed to `victim-shop.myshopify.com`. [5](#0-4) [6](#0-5)

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-38)
```ruby
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
