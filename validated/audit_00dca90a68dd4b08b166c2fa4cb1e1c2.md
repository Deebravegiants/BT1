This confirms the analog. The gem's documented API explicitly instructs the host app to trust `data.shop` from `ShopifyAPI::Webhooks::Registry.process` for tenant identification (see `docs/usage/webhooks.md` lines 12-14, 25-26), while the HMAC only ever covers the raw request body.

### Title
Webhook tenant identity (`shop-domain` header) is not bound by the HMAC signature, enabling cross-tenant webhook confusion - ([File: lib/shopify_api/webhooks/request.rb], [File: lib/shopify_api/webhooks/registry.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` treats a webhook request as authentic once its HMAC validates, then unconditionally trusts `request.shop` (the `X-Shopify-Shop-Domain` header) as the tenant identity handed to the app's handler. But the HMAC signature only ever covers the raw body, never the headers, so the "shop" field acted upon for tenant routing is not cryptographically bound to the signature that authenticates the request.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`, and `hmac` is read straight from the `shopify-hmac-sha256` header: [1](#0-0) 

`shop` is read from the `shopify-shop-domain` header, which is completely outside the signed payload: [2](#0-1) 

`Registry.process` validates the HMAC via `Utils::HmacValidator.validate(request)` (which calls `to_signable_string`, i.e. body-only) and then immediately builds `WebhookMetadata` using `request.shop`, passing it to the app's handler as the authoritative tenant identifier: [3](#0-2) 

`Utils::HmacValidator#validate_signature` compares the HMAC over `verifiable_query.to_signable_string`: [4](#0-3) 

The identity binding that should hold is: **HMAC-verified bytes == bytes the request is acted upon**. Here it breaks down as: `HMAC(secret, raw_body) valid` is treated as proof that `shop-domain header == the shop the payload actually belongs to`, but the header is never part of `raw_body`. This is structurally the same class of bug as the M-Zero report: a piece of state used to make a security-relevant decision (there: `minTimestamp_`/collateral, computed from validator-controlled timestamps not tied to the true minimum; here: tenant identity) is accepted from a channel that the verification step does not actually cover.

The gem's own documentation instructs host apps to trust `data.shop` from the processed webhook as the shop the event is "for": [5](#0-4) [6](#0-5) 

### Impact Explanation
Any party capable of delivering a POST request to the app's public webhook endpoint (its route is by definition internet-reachable, since Shopify itself delivers webhooks over the open internet) can replay or forge a request where the `shopify-shop-domain` header does not match the shop whose data is in the body. Because `Registry.process` only checks the HMAC of the body, a request with a legitimately-signed body (e.g., captured from a previous delivery to shop A, or crafted with knowledge of any leaked/observed body+HMAC pair) combined with an attacker-supplied `shop-domain` header claiming shop B will pass validation and be handed to the handler as "shop B's webhook". Since apps are documented and expected to key persistence, authorization, and business logic off `data.shop`, this enables cross-tenant data confusion: shop A's order/customer/GDPR payload gets attributed and written under shop B's tenant record, or a malicious actor can trigger app-side actions scoped to a shop they don't own. This matches the Critical "cross-tenant access" impact category, mirroring the root cause pattern in the M-Zero report where an unauthenticated/unbound field silently overrides the identity that should have been fixed by the verified signature.

### Likelihood Explanation
No secret material is required to exploit the header confusion itself — the attacker only needs one previously-valid `raw_body` + `hmac` pair (which is plausible to obtain since webhook deliveries are ordinary HTTP POSTs that pass through app infrastructure, logs, proxies, or can be resent by a merchant/observer with network visibility) and the ability to set an arbitrary `shopify-shop-domain` header value on the replayed request, which the gem does nothing to prevent since that header is unauthenticated by design in this code path.

### Recommendation
Bind the tenant identity into the signed material, or independently verify it: include the `shop-domain` (and ideally `topic`, `webhook-id`) values in the HMAC-covered signable string, or require the host application to cross-check `request.shop` against an expected/allow-listed shop for that specific webhook subscription before acting on it. At minimum, the documentation and `WebhookMetadata` should make explicit that `shop` is unauthenticated header data and must not be used as a trust boundary on its own.

### Proof of Concept
1. Attacker observes (or is sent, e.g. via shared infra/logs) one legitimate webhook delivery for `shop-a.myshopify.com`: raw body `B` and header `X-Shopify-Hmac-Sha256: H` where `H = HMAC-SHA256(secret, B)`.
2. Attacker POSTs to the app's webhook endpoint with the same body `B`, the same header `X-Shopify-Hmac-Sha256: H`, but sets `X-Shopify-Shop-Domain: shop-b.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes `HMAC(secret, B)` and finds it matches `H` — validation passes because the check never looks at the `shop-domain` header: [7](#0-6) 
4. The handler is invoked with `WebhookMetadata` claiming `shop: "shop-b.myshopify.com"` even though the payload `B` actually belongs to `shop-a.myshopify.com`, causing the host app to process/store shop A's data under shop B's tenant context.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-38)
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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

**File:** docs/usage/webhooks.md (L12-16)
```markdown
`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
```

**File:** docs/usage/webhooks.md (L19-29)
```markdown
```ruby
module WebhookHandler
  extend ShopifyAPI::Webhooks::WebhookHandler

  class << self
    def handle(data:)
      puts "Received webhook! topic: #{data.topic} shop: #{data.shop} body: #{data.body} webhook_id: #{data.webhook_id} api_version: #{data.api_version}"
      perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)
    end
  end
end
```
