### Title
Webhook `shop-domain` header is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates a webhook solely by validating the HMAC over the raw request body, but the `shop-domain` header — which the app uses to attribute the payload to a specific tenant — is never included in the signed bytes. Anyone who can obtain one legitimately-signed `(body, hmac)` pair (e.g., by installing the public app on their own store and receiving a real webhook) can replay the exact same bytes to the app's webhook endpoint while swapping the `X-Shopify-Shop-Domain`/`shopify-shop-domain` header to a victim shop, and the gem will accept it as valid and hand the handler data tagged with the attacker-chosen shop.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

The `shop` accessor is read straight from an attacker-controllable HTTP header and is never mixed into the signed content: [2](#0-1) 

`Registry.process` validates the HMAC (over body only) and then immediately trusts `request.shop` to build the data handed to the app's handler, with no additional check binding shop to the signature: [3](#0-2) 

`Utils::HmacValidator.validate` confirms `verifiable_query.hmac` against `compute_signature(verifiable_query.to_signable_string, secret)` — i.e. it authenticates *bytes* (`raw_body`) but the caller (`Registry.process`) then acts on a *different* field (`shop`) that was never part of what was verified: [4](#0-3) 

The broken identity binding, expressed as an equality that the code fails to enforce:
`shop-domain header used by the handler == shop-domain implicitly authorized by the HMAC` — the right-hand side does not exist because the HMAC only covers `raw_body`. Any party who can obtain one valid `(raw_body, hmac)` pair signed with the app's shared `api_secret_key` (this happens automatically for every shop that installs the app — no secret leak required) can replay it with an arbitrary `shop-domain` header value and the gem will treat it as an authentic webhook "from" that arbitrary shop.

This differs from a benign design choice because the resulting `WebhookMetadata#shop` is the only tenant identifier the host application receives from this gem to decide which merchant's data/session/store record the payload belongs to; the gem provides no signed corroboration of that value.

### Impact Explanation
This is a cross-tenant confusion vector: an unprivileged internet user who has installed the target app on their own (attacker-controlled) store can capture a real webhook `(body, hmac)` pair sent by Shopify to the app for their own shop, then re-POST identical bytes to the app's public webhook endpoint with the `shop-domain` header changed to a victim merchant's domain. Because `HmacValidator.validate` only checks the body signature (which is still valid, since the app's `api_secret_key` is shared across all shops that install it) and never checks that the claimed `shop` matches anything cryptographically bound to the request, the handler executes believing the event originates from the victim shop. Depending on how the host application uses `WebhookMetadata#shop` (e.g., to look up per-shop settings, write per-tenant records, or trigger per-shop side effects), this enables cross-tenant data injection/confusion without possessing any of the victim's credentials.

### Likelihood Explanation
Any entity can install a public Shopify app on a store they control and will receive genuinely HMAC-signed webhook deliveries for events they can freely trigger (e.g., `orders/create` on their own store). Replaying that exact body with a modified shop header requires only basic HTTP tooling — no access token, no `api_secret_key`, and no privileged account for the victim shop is needed.

### Recommendation
Bind the tenant identity into the authenticated bytes rather than trusting an unauthenticated header for tenant attribution:
- Include `shop-domain` (and ideally `topic`/`webhook-id`) in the value that is HMAC-verified, or
- Cross-check the header-provided `shop` against the shop associated with the installed session/subscription that the webhook topic/id corresponds to before invoking the handler, and reject processing if they don't match.

### Proof of Concept
1. Attacker installs the target Shopify app on `attacker-shop.myshopify.com` (a normal, unprivileged install).
2. Attacker triggers an event (e.g., creates an order) causing Shopify to POST a webhook to the app's endpoint with body `B` and header `X-Shopify-Hmac-Sha256: H`, where `H = HMAC-SHA256(api_secret_key, B)`.
3. Attacker captures `(B, H)` from their own logs/proxy.
4. Attacker sends a new POST to the same webhook endpoint with the same raw body `B`, the same `H`, but `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
5. `HmacValidator.validate` (via `Registry.process`, `lib/shopify_api/webhooks/registry.rb:190`) succeeds because it only checks `B`/`H`; the handler is invoked with `WebhookMetadata.new(... shop: "victim-shop.myshopify.com" ...)` as shown in `lib/shopify_api/webhooks/registry.rb:198-199`, even though nothing in the signed payload ever referenced `victim-shop.myshopify.com`.

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
