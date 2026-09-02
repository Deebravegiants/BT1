## Title
Shopify webhook shop/topic/webhook-id identity is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/utils/hmac_validator.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by HMAC-verifying the raw request **body**. The `shop`, `topic`, `webhook_id`, and `api_version` values that the handler subsequently trusts and acts on are taken straight from HTTP headers, which are **not** part of the signed material. An attacker who can obtain any single validly-signed webhook body (e.g. by triggering webhook delivery to a shop they control) can replay that exact body with forged `X-Shopify-Shop-Domain`/`X-Shopify-Topic`/`X-Shopify-Webhook-Id` headers, and the app will process it as an authentic event for an arbitrary shop and topic.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Utils::HmacValidator.validate` computes and compares the HMAC exclusively over that signable string: [2](#0-1) 

Yet `Registry.process` derives all routing/identity fields from unauthenticated headers and hands them to the app-provided handler: [3](#0-2) 

`request.shop`, `request.topic`, and `request.webhook_id` are read straight from headers with no cryptographic binding to the body: [4](#0-3) 

This is the same bug class as the report: a value the code acts on (`shop`, `topic`, `webhook_id`) is not covered by the integrity check (`hmac` over `raw_body` only), so verified bytes and trusted/parsed identity diverge. The equality that should hold — `hmac_verified(shop, topic, webhook_id, body) == shop/topic/webhook_id/body acted upon by handler` — breaks down to `hmac_verified(body) != {shop, topic, webhook_id}` used for dispatch.

Because the app's `client_secret`/`api_secret_key` used to compute the HMAC is shared across **all** shops that install the app (it is not shop-specific), any shop that can trigger a webhook delivery to itself (including an attacker's own free/dev store) obtains a body+HMAC pair that Shopify considers valid for that secret. The attacker can then replay that exact `(raw_body, hmac)` pair against the app's webhook endpoint while substituting the `shop-domain`, `topic`, and `webhook-id` headers to target a different (victim) shop and a different (attacker-chosen) topic — e.g. `app/uninstalled`, `shop/update`, or a mandatory GDPR topic like `customers/redact`/`shop/redact`. `HmacValidator.validate` will pass because it never inspects those headers, and `Registry.process` will invoke the registered handler believing the event genuinely originates from the victim shop.

### Impact Explanation
This breaks the tenant boundary the webhook signature is supposed to enforce: an unprivileged party can make the app believe an event (uninstall, shop update, customer/shop redaction, etc.) originated from a shop they do not control, which is cross-tenant access/spoofing of a merchant's identity within the app's webhook processing pipeline. Depending on what the host application's handlers do with `WebhookMetadata#shop`/`#topic` (e.g. deauthorizing a merchant, purging merchant data, updating billing/shop state), this can cause state corruption or data loss attributed to a victim tenant purely from an attacker-controlled request.

### Likelihood Explanation
Exploitation requires only: (1) the ability to install the app on any shop (including a free/dev store the attacker controls) to receive at least one genuinely-signed webhook body, and (2) the ability to send an arbitrary HTTP POST to the app's public webhook endpoint with custom headers — both are available to an unprivileged internet user with no access token, secret, or privileged account needed.

### Recommendation
Bind the identity fields to the signed payload instead of trusting headers independently: either include `shop`, `topic`, and `webhook_id` in the HMAC-signed material and verify them as part of `to_signable_string`, or cross-check the header-derived `shop`/`topic` against server-side webhook registration/subscription records (e.g., confirm the `webhook_id` belongs to a subscription actually created for the claimed `shop`) before dispatching to handlers.

### Proof of Concept
1. Install the target app on an attacker-controlled shop (`attacker.myshopify.com`) and subscribe to any webhook topic (e.g. `carts/create`).
2. Trigger the event so Shopify sends a legitimately HMAC-signed webhook: capture `raw_body` and the `X-Shopify-Hmac-Sha256` header value.
3. Replay a forged HTTP POST to the app's webhook endpoint using the captured `raw_body`/`hmac` unchanged, but with headers set to:
   - `X-Shopify-Shop-Domain: victim-shop.myshopify.com`
   - `X-Shopify-Topic: app/uninstalled` (or any topic registered by the app)
   - `X-Shopify-Webhook-Id: <arbitrary>`
4. `ShopifyAPI::Utils::HmacValidator.validate` passes (body/HMAC match), and `ShopifyAPI::Webhooks::Registry.process` invokes the app's handler with `shop: "victim-shop.myshopify.com"`, causing the app to act on behalf of a shop the attacker never controlled.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-33)
```ruby
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
