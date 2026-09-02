Found: `Webhooks::Request#shop` in the webhooks handling code is a strong analog to the report's identity-binding break.

### Title
Webhook `shop` identity is trusted from an HTTP header that is not covered by the HMAC signature, allowing shop-spoofing on delivered webhooks - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` exposes a `shop` accessor that is read directly from the `X-Shopify-Shop-Domain` HTTP header, but the HMAC signature validated by `HmacValidator` only covers the raw request body, not this header. `Webhooks::Registry.process` verifies the HMAC and then hands `request.shop` straight to the app's webhook handler as the authoritative tenant identifier, without re-deriving or cross-checking it against any signed field.

### Finding Description
`Utils::HmacValidator.validate` computes the signature purely from `verifiable_query.to_signable_string`, and for `Webhooks::Request` that method returns only `@raw_body`: [1](#0-0) 
Meanwhile `shop` is pulled from the `shopify-shop-domain` (or `x-shopify-shop-domain`) header, a field that plays no part in the signable string: [2](#0-1) 
`Registry.process` validates the HMAC and then immediately trusts `request.shop` as the tenant for the delivered event: [3](#0-2) 

The binding that should hold is:
`shop_covered_by_hmac == shop_used_for_tenant_dispatch`

but in this gem it is:
`shop_covered_by_hmac (raw_body only) != shop_used_for_tenant_dispatch (shop-domain header)`

Because the header is outside the signed bytes, an attacker who can influence or forge a request against the app's webhook endpoint — while still supplying a body/HMAC pair (which itself can only be produced by knowing `client_secret`, so this alone doesn't grant a full auth bypass) — could present a mismatched `shop-domain` header. More importantly, if the raw body legitimately contains a `shop_id`/`shop_domain` field for one merchant, but the header names a different shop, the two are never cross-validated, so the app's own `handler.handle` call attributes the payload to whatever shop the header claims, not what was actually signed.

### Impact Explanation
This matches the "field acted on but not covered by the HMAC" analog class in the rules. Under this gem's design, `WebhookMetadata.shop` (built from `request.shop`) is the tenant key most host apps use to look up the merchant's session/access token and route webhook side effects (e.g., data deletion for `customers/redact`, or inventory sync). If the shop identity used for dispatch is not bound to the signed bytes, a crafted request with a valid HMAC-over-body but a manipulated `shop-domain` header can cause cross-tenant misattribution of the webhook payload — i.e., data intended/verified for shop A being processed under shop B's identity in the host app, without any check inside the gem that would catch the discrepancy. This is a High-severity class of issue (credential/session/tenant-binding bypass) analogous to the CoreCollection reinitialization bug, where a field that controls critical downstream behavior escapes the integrity check that was supposed to gate it.

### Likelihood Explanation
Exploitation still requires the attacker to produce a body whose HMAC matches `client_secret`-derived signature, which normally implies possessing the secret or replaying a legitimate Shopify-issued webhook. This significantly limits likelihood for a fully external, credential-less attacker. However, the described defect is real and structural: the gem itself never cross-checks the unsigned `shop` header against any signed content, so the security guarantee "the shop this webhook is attributed to is the shop that Shopify signed for" does not actually hold at the gem level — any caller (proxy, load balancer header injection, replay with header rewrite, or a Shopify infrastructure bug) that can decouple headers from body can flip tenant attribution. This is a design gap rather than a proven exploitable bypass purely from an anonymous internet request.

### Recommendation
Include `shop` (and ideally `topic`, `webhook_id`) in the HMAC-covered signable content, or, at minimum, have `Registry.process`/`Request` cross-validate the `shop-domain` header against a shop identifier embedded in the signed body before trusting it for dispatch. Document clearly that `Webhooks::Request#shop` is not itself authenticated by the HMAC check, and require host applications to independently confirm the shop is a known/installed shop before acting on the payload.

### Proof of Concept
1. An attacker with a valid Shopify-generated webhook body/HMAC pair for shop A (e.g., via a compromised proxy, testing harness, or CDN that lets headers be rewritten independently of the body) resends the same body with the `X-Shopify-Shop-Domain` header changed to shop B.
2. `HmacValidator.validate(request)` in [4](#0-3)  succeeds because the signature only covers `@raw_body`, unaffected by the header change.
3. `Registry.process` at [5](#0-4)  passes `request.shop` (now shop B) into `WebhookMetadata`, and the host app's handler executes tenant-specific logic (e.g., redaction, sync) against shop B's stored session, even though the signed payload was only ever verified as originating for shop A.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-13)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end
```

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
