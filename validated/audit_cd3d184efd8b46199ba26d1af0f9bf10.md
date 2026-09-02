Found a real analog: in `lib/shopify_api/webhooks/request.rb`, the `shop` field used by `Registry.process` to route webhook data to the handler (`request.shop`) is read directly from the `X-Shopify-Shop-Domain` header, but the HMAC signature (`to_signable_string`) only covers the raw request body — the shop-domain header is never part of the signed bytes.

### Title
Webhook `shop` identity is trusted from an unauthenticated header while only the raw body is HMAC-verified - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` exposes `shop` by reading the `X-Shopify-Shop-Domain` header directly, while `to_signable_string` (used by `HmacValidator.validate`) only signs `@raw_body`. `Registry.process` validates the HMAC and then dispatches the webhook using `request.shop`, which was never covered by the HMAC.

### Finding Description
`Request#shop` returns `shopify_header("shop-domain")` unmodified: [1](#0-0) 

The signable string used for HMAC verification is only the raw body: [2](#0-1) 

`Registry.process` validates the HMAC over the body and, on success, immediately trusts `request.shop` (from the header) to build `WebhookMetadata` and dispatch to the handler: [3](#0-2) 

This breaks the identity binding: `shop-domain header == shop bound inside the HMAC-signed payload` does not hold, because the shop-domain header is never included in `to_signable_string`. Only the raw body bytes are authenticated; the header asserting which shop the webhook came from is not.

### Impact Explanation
Because Shopify's actual webhook signing (server-side, outside this gem) computes the HMAC over the raw body using the app's `client_secret`, an attacker who can replay or forge a POST request with a *valid* body/HMAC pair for one shop (e.g., by capturing a legitimately-delivered webhook, or if any intermediary reflects/permits header tampering) could substitute the `X-Shopify-Shop-Domain` header with a different tenant's shop domain. Since this gem's `Request#shop` and `Registry.process` never check that the header value matches anything inside the signed body, the handler would be invoked believing the payload belongs to the attacker-chosen shop — a cross-tenant confusion at the point where the shop identity is established for the handler layer. This does not, by itself, forge a body's HMAC (that still requires knowledge of `client_secret`), but it does mean the shop-binding guarantee that consuming applications rely on (`HmacValidator.validate(request)` implies "this body genuinely came from `request.shop`") is false — the gem provides no cryptographic assurance for that specific claim.

### Likelihood Explanation
Exploitability depends on an attacker being able to influence/replay the `X-Shopify-Shop-Domain` header on an otherwise-valid signed body (e.g., via a proxy, a captured webhook resent with a modified header, or non-TLS-protected transport). This is a design gap in this gem's `Request`/`Registry` classes rather than a trivial unauthenticated bypass, but it is fully reachable through the gem's own public webhook-processing API (`Registry.process`) with no privileged credentials.

### Recommendation
Include `shop` (and ideally `topic`, `webhook_id`, `api_version`) in the value that is HMAC-verified, or otherwise cryptographically bind the shop-domain header to the signed body before trusting `request.shop` in `Registry.process`. At minimum, document that consuming applications must independently verify `request.shop` against session/tenant context and not rely on `HmacValidator.validate(request)` to authenticate the shop-domain header.

### Proof of Concept
1. Capture (or otherwise obtain) a legitimately Shopify-signed webhook POST: raw body `B` with header `X-Shopify-Hmac-Sha256: H` valid for `B`.
2. Resend the same body `B` and the same header `H`, but change `X-Shopify-Shop-Domain` to a different, victim shop's domain.
3. `Utils::HmacValidator.validate(request)` in `lib/shopify_api/utils/hmac_validator.rb` succeeds because it only hashes `to_signable_string` = `@raw_body`, which is unchanged.
4. `Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-200`) proceeds and calls the handler with `WebhookMetadata.new(..., shop: request.shop, ...)` using the attacker-modified shop domain, even though the signed body was never actually associated with that shop by Shopify.

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
