### Title
Webhook `shop`, `topic`, `webhook_id` and `api_version` are not covered by HMAC verification, allowing cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` only returns the raw request body, so the HMAC verified by `ShopifyAPI::Utils::HmacValidator.validate` authenticates the payload bytes only. The `shop`, `topic`, `webhook_id`, and `api_version` values that `ShopifyAPI::Webhooks::Registry.process` hands to the app's webhook handler are all pulled from unauthenticated HTTP headers, so an attacker who can produce (or capture) one valid `(body, hmac)` pair can replay it with an arbitrary `shop-domain` header and have it accepted as coming from a different, victim tenant.

### Finding Description
`ShopifyAPI::Webhooks::Request` exposes several fields derived purely from request headers: [1](#0-0) 

None of these header-derived fields are part of the signed content. `to_signable_string`, which is what `HmacValidator` actually verifies, returns only the raw body: [2](#0-1) 

`Registry.process` validates the HMAC against `request` (i.e. against the raw body only) and then unconditionally trusts `request.shop`, `request.topic`, `request.webhook_id`, and `request.api_version` to build the `WebhookMetadata` passed to the app's handler: [3](#0-2) 

This breaks the intended identity binding `verified_content == processed_tenant_identity`. The HMAC secret (`Context.api_secret_key`) is the app's single client secret shared across every shop that installs the app — it is not shop-specific — so `HmacValidator.validate` only proves "this body was signed with this app's secret," not "this body came from shop X." Because the `shop-domain` header sits outside the HMAC, any request with a valid `(body, hmac)` pair — for example one legitimately received by the attacker's own shop's webhook endpoint — can be replayed to the app's public webhook route with the `shop-domain` (and `topic`/`webhook-id`) header rewritten to a different, victim shop. `HmacValidator.validate` still passes because it only recomputes the HMAC over `@raw_body`, and `Registry.process` will call the handler with `shop: <victim shop>`.

### Impact Explanation
Apps built on this gem use `WebhookMetadata#shop` to determine which tenant's data a webhook body applies to (this is the documented purpose of the `shop` field, consistent with how `shop` is used elsewhere in the gem, e.g. `ShopifyAPI::Auth::Session`). Since the header is not authenticated, an attacker can cause the app to process attacker-controlled webhook content while attributing it to an arbitrary victim shop domain — i.e., cross-tenant access/data injection through the app's own trusted webhook-processing pipeline. This matches the Critical impact category "cross-tenant access."

### Likelihood Explanation
The webhook endpoint is, by design, a public, unauthenticated HTTP endpoint (verified only by HMAC per the gem's own documentation). Any unprivileged internet user who can obtain one valid `(body, hmac)` pair — trivially available to any merchant who installs the app and receives even a single real webhook to their own shop — can freely rewrite the `shop-domain`/`topic`/`webhook-id` headers and resend the request, since none of those fields affect the HMAC check. No access token, `client_secret`, or privileged account is required.

### Recommendation
Include `shop`, `topic`, `webhook_id`, and `api_version` in the signed content (or otherwise cryptographically bind them to the payload before hashing), or require the app-facing API to independently authenticate the shop identity, so that verifying the HMAC also verifies the tenant/topic/version the payload is attributed to. At minimum, the gem should document prominently that these header fields are unauthenticated and must not be trusted for tenant routing without additional verification.

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker.myshopify.com` and receives a legitimate webhook request, e.g. body `"{}"` with headers:
   - `x-shopify-hmac-sha256: <valid HMAC of "{}">`
   - `x-shopify-shop-domain: attacker.myshopify.com`
   - `x-shopify-topic: orders/create`
2. Attacker resends the exact same body and HMAC to the app's public webhook endpoint, but changes the header to:
   - `x-shopify-shop-domain: victim-shop.myshopify.com`
3. `ShopifyAPI::Utils::HmacValidator.validate(request)` still returns `true` because it only hashes `@raw_body` (`lib/shopify_api/webhooks/request.rb:35-38`).
4. `ShopifyAPI::Webhooks::Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-200`) calls the app's handler with `shop: "victim-shop.myshopify.com"`, causing the attacker-controlled payload to be processed as if it originated from the victim shop.

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
