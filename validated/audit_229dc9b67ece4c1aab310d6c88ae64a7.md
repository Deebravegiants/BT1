### Title
Webhook `shop` (and `topic`/`webhook_id`) trusted from unauthenticated HTTP headers while HMAC only signs the raw body - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant-identifying `shop` field (along with `topic` and `webhook_id`) from raw HTTP headers that are never covered by the HMAC signature check. The HMAC only authenticates the request body, so any request with a validly-signed body but an attacker-controlled `shop-domain` header will pass verification and be dispatched to the app's webhook handler with the forged shop identity.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`, so `Utils::HmacValidator.validate` in `Registry.process` verifies the HMAC exclusively over the JSON body: [1](#0-0) 

But `Request#shop`, `#topic`, and `#webhook_id` are all read straight from HTTP headers, which are entirely outside the signed material: [2](#0-1) 

`Registry.process` validates the HMAC and then immediately trusts `request.shop` as the tenant identity handed to the app's handler: [3](#0-2) 

This is exactly the pattern in scope: "a field acted on but not covered by the HMAC" and "a shop authenticated versus the shop stored as a session key." The equality the gem is supposed to enforce is:
`shop used to authorize/process the webhook == shop cryptographically bound by the HMAC-signed payload`

but here `shop` is taken from `headers["shopify-shop-domain"]` / `headers["x-shopify-shop-domain"]`, never included in `to_signable_string`, so the equality does not actually hold — it is merely asserted by trusting an attacker-writable header.

### Impact Explanation
Because a single app's `client_secret` (used to compute webhook HMACs) is shared across every merchant that installs that app, any unprivileged user can install the target app on a shop they control and legitimately receive a webhook with a valid `hmac-sha256` signature for a body they influence (e.g. by triggering an event on their own store). They can then replay that exact `raw_body`/`hmac` pair to the app's webhook endpoint while substituting the `shopify-shop-domain` (or `x-shopify-shop-domain`) header with a victim shop's domain. `HmacValidator.validate` still succeeds (it only checks the body), and `Registry.process` passes the forged `shop` straight into `WebhookMetadata` for the app's handler: [4](#0-3) 

Any host application that uses this library's `shop` field (as documented/intended) to select which tenant's data to update, delete, or fulfill (e.g., mandatory `shop/redact`, `customers/redact`, `customers/data_request`, or any registered handler) will act on cross-tenant data under a spoofed shop identity — this is a cross-tenant access/data-confusion vector rooted entirely in this gem's `Request`/`Registry` implementation, not a host-app misuse of an undocumented API, since `shop` is the library's documented output for tenant identification.

### Likelihood Explanation
Exploitability only requires: (1) the ability to install the target app on an attacker-owned shop (unprivileged, self-service in Shopify), and (2) the ability to send an arbitrary HTTP POST to the app's public webhook endpoint with attacker-chosen headers — both trivially available to any unprivileged internet user. No access token, `client_secret`, or privileged account is needed.

### Recommendation
Include the `shop-domain`, `topic`, and `webhook_id` headers (or at minimum `shop`) as part of the HMAC-signed material verified in `Request#to_signable_string`/`HmacValidator`, or otherwise cryptographically bind them to the raw body before they are trusted as tenant identity in `Registry.process`.

### Proof of Concept
1. Install the target app on attacker-controlled shop `attacker.myshopify.com`; trigger any registered webhook topic to receive a request with headers `X-Shopify-Shop-Domain: attacker.myshopify.com`, `X-Shopify-Hmac-Sha256: <valid hmac>`, and body `B`.
2. Replay the captured request to the app's webhook endpoint, keeping body `B` and the valid HMAC header unchanged, but replacing `X-Shopify-Shop-Domain` with `victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` accepts the headers (all required headers present), `Utils::HmacValidator.validate(request)` succeeds because `to_signable_string` only checks body `B`.
4. `Registry.process` calls `handler.handle(data: WebhookMetadata.new(shop: "victim.myshopify.com", body: parsed_body_of_B, ...))`, causing the app to process attacker-supplied data under the victim shop's identity.

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
