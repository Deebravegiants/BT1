### Title
Webhook payload/shop-domain mismatch enables cross-tenant webhook forgery - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by HMAC-verifying the raw request body, then unconditionally trusts the `shop` value taken from an unauthenticated HTTP header and hands it to the application's webhook handler as the tenant identifier. The HMAC signature never covers the shop domain, so the "which shop signed this" binding and the "which shop this event is attributed to" binding are never cryptographically linked.

### Finding Description
The equality that should hold for a webhook to be safely tenant-scoped is:

`shop_that_Shopify_signed_this_event_for == shop_value_delivered_to_the_handler`

In this gem, that equality is never enforced.

- `ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 
- `#shop` is read straight from the `shopify-shop-domain`/`x-shopify-shop-domain` header with no relation to the signed bytes: [2](#0-1) 
- `Utils::HmacValidator.validate` computes the HMAC only over `to_signable_string` (i.e. the body) and compares it against the `hmac` field, never touching `shop`: [3](#0-2) 
- `Registry.process` treats a valid body HMAC as sufficient authentication, then forwards `request.shop` (the unauthenticated header) directly to the app's handler as the tenant/session key: [4](#0-3) 

Because Shopify signs the webhook body with the app's single shared `api_secret_key` (the same key for every shop that installs the app), any shop can legitimately receive genuinely-signed webhook deliveries for events on its own store. An unprivileged merchant who has installed the app on their own store (no special privilege required — this is the ordinary, unprivileged-user scenario the analog rules call for) can capture one of these legitimate, correctly-HMAC'd webhook bodies and re-POST it to the app's webhook endpoint while substituting a different `shop`/`x-shopify-shop-domain` header value naming a *victim* shop. `HmacValidator.validate` will still pass, because the signature check never inspects the shop header, and `Registry.process` will call the handler with `WebhookMetadata#shop` set to the attacker-chosen victim domain.

### Impact Explanation
If the host application uses `WebhookMetadata#shop` (as documented/intended by this gem) to select which merchant's session/access-token/state to act on — e.g., to look up `SessionRepository` records, decrement inventory, mark an order paid, or trigger any per-tenant side effect — an attacker can cause the app to apply another tenant's data to actions attributed to a shop they don't own, or vice versa. This is a cross-tenant identity-binding bypass carried entirely through this gem's own webhook verification API (`Registry.process` / `HmacValidator.validate`), matching the reported bug class of "a field acted on but not covered by the HMAC."

### Likelihood Explanation
Any entity that can install the app on a store it controls (a normal, unprivileged onboarding flow for public apps) automatically receives correctly signed webhook deliveries for its own shop. Replaying the body with a modified `shop` header requires no secret material, no access token, and no privileged account — only the ability to send an HTTP POST to the app's public webhook endpoint, which is by definition internet-reachable. This satisfies the "unprivileged internet user" bar.

### Recommendation
Bind the `shop` value cryptographically to the signed payload before it is trusted:
- Include the `shop` (and ideally `topic`/`webhook-id`) in the HMAC-signed string in `Request#to_signable_string`/`HmacValidator`, or
- Independently verify that the header `shop` corresponds to the shop that actually owns the delivered `webhook_id`/topic (e.g., via a GraphQL lookup) before invoking the handler, rather than trusting the header outright in `Registry.process`.

### Proof of Concept
1. Install the target app on attacker-controlled store `attacker.myshopify.com`; trigger any subscribed event (e.g., `orders/create`) so Shopify sends a legitimately signed webhook: headers `x-shopify-hmac-sha256: <valid>`, `x-shopify-shop-domain: attacker.myshopify.com`, body `B`.
2. Capture `B` and the valid `hmac` value.
3. Re-POST to the app's webhook endpoint with the same body `B` and the same valid `hmac`, but with `x-shopify-shop-domain: victim.myshopify.com`.
4. `Utils::HmacValidator.validate` in `lib/shopify_api/utils/hmac_validator.rb:13-22` returns `true` (it only checks `B` against the secret, per `lib/shopify_api/utils/verifiable_query.rb`).
5. `Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-200`) invokes the handler with `WebhookMetadata.new(..., shop: "victim.myshopify.com", body: parsed(B), ...)`, causing the app to process attacker-controlled event data under the victim shop's identity.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
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
