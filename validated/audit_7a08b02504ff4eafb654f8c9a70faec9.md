## Title
Webhook Shop-Domain Spoofing via HMAC Scope Mismatch Enables Cross-Tenant Webhook Processing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook by validating an HMAC computed only over the raw request body, then unconditionally trusts the `shopify-shop-domain` HTTP header — which is never covered by that HMAC — as the tenant identifier passed to the app's handler.

### Finding Description
`ShopifyAPI::Webhooks::Request#shop` reads the tenant identity directly from an HTTP header: [1](#0-0) 

The signable string used for HMAC verification is defined as only the raw body, deliberately excluding all headers (including `shop`, `topic`, `webhook-id`, `api-version`): [2](#0-1) 

`HmacValidator.validate` computes the signature strictly from `to_signable_string` (the raw body) and compares it to the `hmac` header via `OpenSSL.secure_compare`: [3](#0-2) 

`Registry.process` gates entirely on this body-only HMAC check, and then forwards `request.shop` — the unauthenticated, HMAC-uncovered header — into `WebhookMetadata` that is handed to the app's handler as the trusted tenant identity for the event: [4](#0-3) 

The root cause is an identity-binding break: the equality the library implicitly promises to the host app is `(shop that produced this HMAC-signed body) == (data.shop passed to the handler)`. In reality the HMAC binds only to body bytes; the `shop` field is parsed but never verified. A party that can obtain one validly-signed webhook body (e.g., from their own store where they've legitimately installed the app) can replay that exact body to the app's webhook endpoint while substituting the `shopify-shop-domain` header for any other shop. `HmacValidator.validate` still returns `true` because the signature check never inspects the header, and `Registry.process` calls the handler with `data.shop` set to the attacker-chosen value.

### Impact Explanation
Apps built on this gem commonly use `WebhookMetadata#shop` to select which merchant's offline session/access token to act on, or which tenant's records to mutate (this is exactly the field passed into the mandatory `shop/redact`, `customers/redact`, `customers/data_request` handlers, and any app-defined handler). Because `data.shop` is attacker-controllable independent of the signed body, an unprivileged user who can trigger a legitimate webhook for their own shop (any developer can install a public/dev app) can cause the host app to attribute that payload's processing to a different tenant, achieving cross-tenant action/confusion without ever possessing the target's credentials. This is a cross-tenant identity-binding bypass reachable purely through this gem's own webhook verification API.

### Likelihood Explanation
Likelihood is realistic: any developer can install the app on their own store to legitimately obtain one valid `(raw_body, hmac)` pair for a chosen topic, then replay it with an arbitrary `shopify-shop-domain` header value to the app's public webhook endpoint. No secrets, tokens, or privileged access are required — only observation of one legitimate webhook delivery to their own tenant.

### Recommendation
Bind the `shop` (and ideally `topic`/`webhook-id`) header into the HMAC-signable material, or otherwise cryptographically bind the claimed shop to the signed payload before exposing it via `WebhookMetadata`. At minimum, `Request#to_signable_string` should incorporate the shop domain header so `HmacValidator.validate` fails whenever the header is altered relative to the value used at signing time on Shopify's side (Shopify signs `HMAC(secret, raw_body)`, so parity requires the app to independently confirm `shop` against a known/registered tenant list rather than trusting the header verbatim). Document clearly that `data.shop` is unauthenticated unless additionally checked against the app's own shop registry before use in any privileged operation.

### Proof of Concept
1. Attacker installs the target app on their own development shop `attacker.myshopify.com`, triggering a legitimate webhook (e.g., `orders/create`) delivery with a valid `x-shopify-hmac-sha256` computed over the JSON body.
2. Attacker captures the raw body and the valid HMAC value.
3. Attacker resends the identical raw body and HMAC to the app's public webhook endpoint, but sets `shopify-shop-domain: victim-shop.myshopify.com`.
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only checks `raw_body` against the HMAC: [5](#0-4) 
5. The handler receives `WebhookMetadata` with `shop: "victim-shop.myshopify.com"` and the attacker's own body content, causing the app to process/act on data as if it originated from the victim tenant.

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
