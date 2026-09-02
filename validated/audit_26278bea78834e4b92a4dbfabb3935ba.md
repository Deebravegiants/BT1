### Title
Webhook `shop` Identity Not Covered by HMAC Signature Enables Cross-Tenant Webhook Spoofing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC of the raw request body, then trusts the `shop-domain` header — which is not part of the signed material — as the tenant identity handed to the app's webhook handler.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`, and `hmac` is read from the `hmac-sha256` header: [1](#0-0) 

The `shop` accessor is populated directly from the unauthenticated `shop-domain` header: [2](#0-1) 

`Registry.process` validates only the HMAC of `request` (i.e., the body), and immediately afterward forwards `request.shop` into `WebhookMetadata` as the tenant identifier passed to the app's handler, with no separate binding between `shop` and the signed body: [3](#0-2) 

The binding that is broken is:
`shop authenticated (i.e., bytes covered by HMAC) == shop used for tenant attribution (WebhookMetadata#shop)`

Because the `shop-domain` header sits outside `to_signable_string`, any two values are accepted as long as they arrive together with a body whose HMAC matches the app's secret — but the header itself carries no cryptographic binding to that body or to a specific shop. A merchant who legitimately operates a shop connected to the app receives genuine webhook deliveries (valid body + valid HMAC) for their own shop. That merchant can replay the exact same body/HMAC pair to the app's webhook endpoint while substituting the `x-shopify-shop-domain` (or `shopify-shop-domain`) header with a victim shop's domain. `HmacValidator.validate` still succeeds because it only checks the body against the secret, and `Registry.process` passes the attacker-chosen `shop` value straight to the handler as the authenticated tenant.

### Impact Explanation
If the host application uses `WebhookMetadata#shop` (as returned by this gem after "HMAC validation") to key merchant records, apply the webhook payload to a shop's data, or route within a multi-tenant install base — as the gem's documented flow strongly implies is safe post-`process` — an attacker with access to genuine webhook traffic for one shop can inject or attribute a replayed payload to a different tenant. This is a cross-tenant data-integrity/access violation stemming directly from an identity field excluded from the cryptographic signature the gem asserts as its authenticity check.

### Likelihood Explanation
Requires an attacker to have legitimate access to real webhook deliveries for at least one shop connected to the target app (e.g., as an app-installing merchant) and the ability to POST to the app's public webhook receiver endpoint with modified headers — both are realistic for any multi-tenant Shopify app, since webhook endpoints are internet-reachable and merchants routinely receive real webhook traffic for their own shop.

### Recommendation
Bind the `shop` (and ideally `topic`/`webhook_id`) into the value that is actually verified, e.g. incorporate the `shop-domain` header into `to_signable_string`, or independently authenticate/authorize `request.shop` against the session/shop the webhook was registered for before handing it to the handler in `Registry.process`.

### Proof of Concept
1. App has two connected shops: `attacker-shop.myshopify.com` and `victim-shop.myshopify.com`.
2. Shopify sends a genuine webhook to the app for `attacker-shop.myshopify.com`: body `B`, header `x-shopify-hmac-sha256: HMAC(secret, B)`, `x-shopify-shop-domain: attacker-shop.myshopify.com`.
3. Attacker captures this request (e.g., by controlling the webhook receiver logs, a proxy, or an app that echoes webhook data) and replays it to the app's webhook endpoint with the same body `B` and same HMAC header, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `HmacValidator.validate` in `lib/shopify_api/utils/hmac_validator.rb` succeeds because it only re-computes the HMAC over `B`.
5. `Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-200`) calls the app's handler with `WebhookMetadata.new(... shop: "victim-shop.myshopify.com", body: parsed(B), ...)`, causing the app to process attacker-controlled data under the victim's tenant.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-23)
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
