### Title
Webhook shop-domain header is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` verifies webhook authenticity using `Utils::HmacValidator.validate(request)`, but the signature is computed only over the raw HTTP body (`to_signable_string` returns `@raw_body`). The `shop` (from the `X-Shopify-Shop-Domain` header) is never included in the signed material, so a valid HMAC for one shop's payload says nothing about which shop it actually belongs to.

### Finding Description
The binding that should hold is:
`hmac == HMAC(secret, body || shop)` (the authenticated tenant identity must be cryptographically bound to the payload the app acts on).

Instead, the gem implements:
`hmac == HMAC(secret, body)` only, per `to_signable_string`: [1](#0-0) 

and the `shop` value used by callers is read straight from an attacker-controllable header with no cryptographic tie to the signature: [2](#0-1) 

Verification happens in `Registry.process`, which only calls `HmacValidator.validate(request)` (i.e., validates body vs. secret) and then immediately trusts `request.shop` when dispatching to the app's handler: [3](#0-2) 

`HmacValidator.validate_signature` confirms the signature is computed purely from `to_signable_string` (the body), independent of shop: [4](#0-3) 

Because the app's webhook secret (`client_secret`) is shared across every shop that installs the app, any unprivileged merchant can install the app on their own store, capture a genuinely-signed webhook request Shopify sends them (valid HMAC, since it is computed with the real, shared secret and their own body), and replay that exact body/HMAC to the app's public webhook endpoint while substituting the `X-Shopify-Shop-Domain` (or `Shopify-Shop-Domain`) header with a victim shop's domain. `HmacValidator.validate` still succeeds because it never looks at the shop header, and `Registry.process` passes the attacker-chosen `shop` value into `WebhookMetadata`, which host applications use as the tenant key to route/store/act on the payload.

### Impact Explanation
This breaks the identity binding between "the body Shopify actually signed" and "the shop the app believes it's acting for," which is exactly the cross-tenant analog described in the rules (a field acted on but not covered by the HMAC). Any application built on this gem that uses `WebhookMetadata#shop` to select which tenant's records to update (a normal and expected usage pattern) can be made to apply an attacker-controlled but validly-signed payload to another merchant's tenant context — i.e., cross-tenant access/data injection, achievable by any user who can install the app on their own store and does not require the app's `client_secret`, an access token, or any privileged position. This meets the Critical bar ("cross-tenant access").

### Likelihood Explanation
High. No secrets are required beyond what any legitimate, unprivileged app installer already has (the ability to trigger and capture their own webhooks and to send arbitrary HTTP requests, including custom headers, to the app's public webhook endpoint). The only precondition is that the host application trusts `shop` from `WebhookMetadata` for tenant routing, which is the documented and intended use of that field.

### Recommendation
Bind the shop to the HMAC-verified material, e.g., include the `shop-domain` header (and/or `webhook-id`, `topic`) in `to_signable_string` if Shopify's webhook signing scheme is extended to support it, or — more robustly given Shopify signs only the body — require callers to independently confirm that `shop` corresponds to a shop with an active, stored session/install record for this app (reject webhooks for unknown/uninstalled shops) rather than trusting the header value verbatim once HMAC-on-body succeeds. At minimum, document prominently that `shop` in `WebhookMetadata` is unauthenticated and must be independently verified against known installed shops before being used for tenant-scoped operations.

### Proof of Concept
1. Install the target app on an attacker-controlled development shop `attacker.myshopify.com`. This is a legitimate installation using the app's real (shared) `client_secret`.
2. Trigger a webhook (e.g., `orders/create`) on `attacker.myshopify.com`; capture the raw POST body and the genuine `X-Shopify-Hmac-Sha256` header Shopify sends — both are valid and will pass `HmacValidator.validate`.
3. Replay this exact body and HMAC header to the app's webhook endpoint, but replace the `X-Shopify-Shop-Domain` header with `victim.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only checks `hmac(body, secret)`: [5](#0-4) 
5. The handler receives `WebhookMetadata` with `shop: "victim.myshopify.com"` and the attacker's order body, and any tenant-scoped logic in the host app (e.g., "look up victim's session/store victim's order data") is now operating on attacker-supplied data under the victim's tenant identity.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
