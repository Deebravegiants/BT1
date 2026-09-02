This confirms the finding: `docs/usage/webhooks.md` explicitly documents `data.shop` as an authoritative field for tenant routing (`shop_domain: data.shop` in the example handler), while the actual signature computation only covers the raw body.### Title
Webhook Shop-Domain Header Not Covered by HMAC Signature — Cross-Tenant Webhook Spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant-identifying `shop` field from an HTTP header that is never included in the HMAC-signed material, while `ShopifyAPI::Webhooks::Registry.process` trusts that same unverified header when dispatching webhook data to the app's handler. This breaks the identity binding: `hmac == HMAC(secret, raw_body)` while `shop == header["shopify-shop-domain"]` — the tenant field that downstream handlers use to route/authorize work is disjoint from the bytes that are actually verified.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw body: [1](#0-0) 

`shop` is read straight from a header, entirely outside the signed payload: [2](#0-1) 

`Registry.process` verifies only the HMAC over the body via `HmacValidator.validate`, and then immediately forwards `request.shop` — the unverified header — to the app's handler: [3](#0-2) 

`HmacValidator.validate` and `validate_signature` compute the digest solely from `verifiable_query.to_signable_string` (i.e., the raw body for webhooks), never touching headers such as shop-domain, topic, or webhook-id: [4](#0-3) 

Because the app's `api_secret_key` (client secret) is shared across every shop that installs the app, any merchant who installs the app on their own store legitimately receives correctly-signed webhook deliveries (valid `hmac-sha256` header for a given raw body) for their own shop. Since the signature never binds the `shop-domain` header, an attacker who controls a webhook request en route to the app's own callback endpoint (e.g., by replaying/forwarding a captured, validly-signed delivery through a proxy they control, or through any app-side ingress that lets them set/forward the shop header independently of body verification) can swap the `x-shopify-shop-domain` value to a victim shop's domain while keeping the same body and unaltered HMAC. `Registry.process` will still accept the HMAC as valid (it only checks the body) and hands the handler a `WebhookMetadata` claiming to originate from the victim shop: [5](#0-4) 

The gem's own documentation instructs integrators to treat `data.shop` as the authoritative tenant identifier for routing work (e.g., `shop_domain: data.shop`), reinforcing that host apps are expected to trust this field as if it were verified: [6](#0-5) 

This is the same bug class as the FireToken report: a security-relevant field (`shop`) is *acted upon* by downstream logic, but the verification step (HMAC) covers a different, disjoint set of bytes (only `raw_body`), so the acted-upon field can be manipulated independently of the check that is supposed to authenticate the request.

### Impact Explanation
If a host application uses `data.shop` from `WebhookMetadata` to look up/select which shop's session, tenant data, or database record to mutate (exactly as the gem's documented example does), an attacker can cause the app to process attacker-supplied webhook payloads under a victim shop's identity — a cross-tenant data-integrity/confidentiality issue purely through this gem's own trust boundary (HMAC-verifies body only, not the shop header it hands to the handler).

### Likelihood Explanation
The attacker must be able to deliver an HTTP request to the app's public webhook endpoint with a validly signed body for *some* shop (trivially obtained by installing the app themselves, since the same `api_secret_key` signs webhooks for every shop) and control the `x-shopify-shop-domain`/`shopify-shop-domain` header independent of that signed body. Because header values are not covered by the signature at all, this only requires the ability to modify or forge headers on the delivered request — no secret material is needed. This aligns with "unprivileged-internet-user" analog: no access token, no `api_secret_key`, no privileged account required beyond becoming a normal (attacker-controlled) merchant/app installer.

### Recommendation
Include the `shop-domain` (and ideally `topic`/`webhook-id`) header values in the HMAC-signed material, or otherwise cryptographically bind them to the verified payload, before exposing `shop` on `WebhookMetadata`. Failing that, explicitly document that `data.shop` is unauthenticated and must be cross-checked against a known/installed shop record by the host application before being used for tenant routing.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com`, triggering a legitimate webhook delivery with body `B` and header `x-shopify-hmac-sha256: HMAC(secret, B)` and `x-shopify-shop-domain: attacker-shop.myshopify.com`.
2. Attacker intercepts/replays this request to the app's webhook endpoint, changing only `x-shopify-shop-domain` to `victim-shop.myshopify.com`, keeping `B` and the HMAC header unchanged.
3. `ShopifyAPI::Webhooks::Request.new` parses the modified headers; `Registry.process` calls `Utils::HmacValidator.validate`, which recomputes `HMAC(secret, B)` — still valid since `B` is unchanged — and dispatches to the handler with `shop: "victim-shop.myshopify.com"`, per [7](#0-6) .
4. The host app's handler processes attacker-controlled body content as if it came from `victim-shop.myshopify.com`.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
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
