### Title
Webhook `shop` (tenant identifier) is trusted for routing but not covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant identity (`shop`) from the `X-Shopify-Shop-Domain` HTTP header, but the HMAC signature that authenticates the webhook only ever covers the raw request body. This breaks the equality that should hold between "the shop the HMAC authenticates" and "the shop the handler acts on," letting an attacker who controls a validly-signed webhook body from any shop relabel it as coming from a different shop.

### Finding Description
`Request#to_signable_string` returns only `@raw_body` [1](#0-0) , and `HmacValidator.validate` computes/compares the signature strictly against that signable string [2](#0-1) . Meanwhile `Request#shop` is read straight from the `shopify-shop-domain`/`x-shopify-shop-domain` header, which is not part of the signed material at all [3](#0-2) .

`Registry.process` validates the HMAC and then immediately builds `WebhookMetadata` using `request.shop` as the tenant identity handed to the app's own handler: [4](#0-3) . The header is included in the mandatory-header check [5](#0-4)  as required input, so consuming applications naturally treat it as the authenticated tenant of the payload, exactly the way `WebhookMetadata` is documented to be used.

The broken binding, stated as an equality that should hold but doesn't:
`shop_bound_by_hmac == shop_used_for_tenant_routing`
Here, `shop_bound_by_hmac` is undefined (the HMAC only covers the body), while `shop_used_for_tenant_routing = request.shop` is taken from an unauthenticated header.

### Impact Explanation
Any entity capable of producing one validly HMAC-signed webhook body/signature pair (e.g., a merchant/developer of their own store, who legitimately receives Shopify webhooks with a valid `X-Shopify-Hmac-Sha256` for their own shop's traffic) can replay that exact `(raw_body, hmac)` pair to the app's webhook endpoint while swapping only the `X-Shopify-Shop-Domain` header to a victim shop's domain. Because the header is outside the signed content, `Utils::HmacValidator.validate` still succeeds, and the app's registered handler receives `WebhookMetadata` claiming the payload originated from the victim shop. Depending on how the host application uses `WebhookMetadata#shop` (e.g., to look up/update per-tenant records, sessions, or trigger tenant-scoped side effects), this enables cross-tenant data corruption or disclosure — matching the "Critical: cross-tenant access" impact bucket.

### Likelihood Explanation
Requires only that the attacker be able to receive at least one legitimately signed webhook for some shop (trivial for a developer with their own dev store subscribed to the app, or any store that installs the app) and replay it with a modified header to the app's public webhook URL — no access to `api_secret_key`, tokens, or the app's other credentials is needed. This is a realistic, low-effort unprivileged-internet-facing scenario as long as the app exposes its webhook endpoint (the normal, required deployment configuration).

### Recommendation
Do not treat the `shop-domain` header as authenticated. Either:
- Include the shop domain (and ideally topic/webhook-id) inside the HMAC-signed material by validating it against a value independently confirmed via API lookup after HMAC success, or
- Cross-check `request.shop` against the shop associated with the specific `webhook_id` (obtained via an authenticated Admin API call) before dispatching to the handler, or
- At minimum, document prominently that `WebhookMetadata#shop` is unauthenticated and must not be used as a sole tenant key without further verification.

### Proof of Concept
1. Attacker's own store (or any store subscribed to the app) receives a legitimate webhook: `raw_body = B`, header `X-Shopify-Hmac-Sha256 = H` (valid for `B` under the app's `api_secret_key`), header `X-Shopify-Shop-Domain = attacker-shop.myshopify.com`.
2. Attacker POSTs the same `B` and `H` to the app's webhook endpoint, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: {..., "x-shopify-shop-domain" => "victim-shop.myshopify.com", "x-shopify-hmac-sha256" => H})` is constructed; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes HMAC over `B` only and succeeds [6](#0-5) .
4. The registered handler is invoked with `WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: parsed(B), ...)` [7](#0-6) , causing the app to act on `B`'s content as if it belongs to `victim-shop.myshopify.com`.

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

**File:** lib/shopify_api/webhooks/request.rb (L50-59)
```ruby
        missing_headers = []
        ["topic", "hmac-sha256", "shop-domain"].each do |name|
          unless headers.key?("shopify-#{name}") || headers.key?("x-shopify-#{name}")
            missing_headers << "shopify-#{name} or x-shopify-#{name}"
          end
        end
        unless missing_headers.empty?
          raise Errors::InvalidWebhookError,
            "Missing one or more of the required HTTP headers to process webhooks: #{missing_headers}"
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
