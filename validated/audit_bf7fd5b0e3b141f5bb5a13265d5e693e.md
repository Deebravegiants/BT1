### Title
Webhook `shop` (and `topic`/`api_version`/`webhook_id`) tenant-identifying fields are not covered by the HMAC signature, allowing shop-domain spoofing on an otherwise-valid webhook - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, while `HmacValidator` uses that string to verify Shopify's HMAC signature. The `shop` value that the gem hands to app webhook handlers as the tenant identifier comes from the `x-shopify-shop-domain` header, which is never included in the signed bytes. This is the same class of bug as `AfEth.price()`: a value the code *acts on* (`shop`, used for tenant binding) is not the same value that was *cryptographically verified* (only `@raw_body`).

### Finding Description
`Request#to_signable_string` is defined as: [1](#0-0) 

and `shop` is read straight from a header, independent of the signed payload: [2](#0-1) 

`Registry.process` verifies the HMAC using `HmacValidator.validate(request)`, which computes the HMAC over `to_signable_string` (i.e. only `@raw_body`) and compares it to the `hmac` claim, then immediately forwards `request.shop` — untouched by that verification — to the app's handler as the identified tenant: [3](#0-2) 

`HmacValidator.validate_signature` confirms the signed bytes are exactly `verifiable_query.to_signable_string`, nothing else: [4](#0-3) 

The equality this breaks: the gem implicitly claims `hmac_verified(bytes) == true ⟺ shop_header == shop_that_produced(bytes)`. In reality, `hmac_verified` only binds `raw_body`; `shop`, `topic`, `api_version`, and `webhook_id` headers are completely outside that binding. Since any Shopify merchant/developer can register webhooks for their own store (a legitimate, unprivileged capability — no `api_secret_key` needed to *receive* a webhook, only to register one on their own shop), an attacker who operates their own store gets a stream of correctly-HMAC'd `(body, hmac)` pairs signed with the app's real `api_secret_key` (Shopify signs webhooks with the app's secret for every shop that installs the app). The attacker can then replay that valid `(body, hmac)` pair to the app's webhook endpoint while substituting the `x-shopify-shop-domain` header for a victim shop's domain. `HmacValidator.validate` still returns `true` (only `raw_body` is checked), and `WebhookMetadata.shop` will report the victim's shop even though the payload was never signed for or sent by that shop.

### Impact Explanation
This crosses a tenant boundary: an app relying on `WebhookMetadata.shop` (returned by this gem) to select which merchant's data/session/tokens to act on can be made to process attacker-controlled body content under a victim's `shop` identity. Depending on the handler (e.g. updating stored order/product data keyed by shop, or triggering internal side effects scoped by `shop`), this enables cross-tenant data corruption. It maps to the "High - scope or... check bypass" / cross-tenant category since the shop-identity check the app performs is effectively bypassed by the gem's incomplete binding.

### Likelihood Explanation
Requires the attacker to control a legitimate Shopify shop that installs the target app (readily available to any developer/merchant, no special privilege), and requires the app to trust `WebhookMetadata.shop` from this gem for tenant-scoped mutation without an independent cross-check (e.g. comparing against a shop already known/authorized for that webhook's `topic`/subscription id). This is a real, reachable analog, though its ultimate impact depends on how the consuming app uses `WebhookMetadata.shop`.

### Recommendation
Include the `shop-domain` (and ideally `topic`, `api_version`, `webhook-id`) headers in the signed/verifiable string, or otherwise cryptographically bind them to the payload before exposing them via `WebhookMetadata`, mirroring the `AfEth` fix of binding the previously-untracked value into the verified computation instead of trusting it separately.

### Proof of Concept
1. Attacker creates their own Shopify dev store and installs the target app, receiving a real, correctly-signed webhook: `raw_body = B`, `x-shopify-hmac-sha256 = HMAC(api_secret_key, B)`, `x-shopify-shop-domain = attacker-shop.myshopify.com`.
2. Attacker resends the exact same `raw_body` and `x-shopify-hmac-sha256` value to the app's webhook endpoint, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes `HMAC(api_secret_key, B)` (unchanged) and matches — validation passes.
4. The handler receives `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: parsed(B), ...)`, i.e., attacker-supplied body under the victim shop's identity, despite the HMAC never having verified the `shop` field at all.

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
