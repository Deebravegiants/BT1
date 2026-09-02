### Title
Webhook shop-domain header is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` is documented as verifying "the request did indeed come from Shopify" before invoking the app's webhook handler with a `WebhookMetadata` object whose `shop` field is described as "The shop domain of the webhook." In reality, the HMAC signature only authenticates the raw request body — the `shop-domain` header used to populate `data.shop` is never included in the signed bytes. Anyone who can obtain one legitimately-signed `(body, hmac)` pair for the app (e.g. a merchant that has the app installed) can replay it to the app's public webhook endpoint with an arbitrary forged `shop-domain` header and still pass HMAC validation, causing the handler to process the webhook under an attacker-chosen shop identity.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw body: [1](#0-0) 

while `shop`, `topic`, `webhook_id`, and `api_version` are all read directly from unauthenticated HTTP headers: [2](#0-1) 

`HmacValidator.validate` computes and compares the HMAC only over `to_signable_string`: [3](#0-2) 

`Registry.process` verifies the HMAC and then, without any further check binding `shop`/`topic`/`webhook_id` to the verified body, hands them straight to the app's handler: [4](#0-3) 

The gem's own documentation promises this call "will verify the request did indeed come from Shopify," and instructs handler authors to trust `data.shop` as "the shop domain of the webhook": [5](#0-4) [6](#0-5) 

Since the app's webhook secret (`client_secret`) is shared across every shop that installs the app, and the HMAC never binds the shop header to the body, any party who can capture one valid `(raw_body, hmac)` pair (e.g. from a webhook delivered to their own installed shop) can resend it to the same public endpoint with a different `shop-domain` header value. The signature check still succeeds because it only covers `raw_body` — identically to the reported bug class where a value acted upon (`shop`) is not the value actually covered by the cryptographic check (`raw_body` only).

Equality that should hold but doesn't:
`shop header value trusted by handler == shop that produced/authorized the signed body`
Instead the gem only guarantees: `hmac(raw_body, client_secret) == received_hmac`, independent of the `shop` header.

### Impact Explanation
This breaks a tenant identity binding: the `shop` value handed to the app's business logic as "verified" is fully attacker-controlled while the HMAC-authenticated payload is unrelated to it. An app that (per the gem's documented contract) trusts `data.shop` for tenant-scoped side effects (e.g., enqueuing per-shop jobs, updating per-shop data, fulfilling `shop/redact`-type mandatory topics) can be made to attribute another shop's real webhook content, or attacker-selected content, to a victim shop, or vice versa — i.e., cross-tenant access/action across the app's multiple installed merchants.

### Likelihood Explanation
Exploitation requires only: (1) the app is a multi-tenant app whose `client_secret` is shared across installs (standard Shopify app model), and (2) the attacker can obtain any one legitimately signed webhook body+HMAC pair, which is trivially available to any merchant who has installed the app (an unprivileged relationship to other tenants of the same app) or intercepted in transit to their own endpoint. No access to `api_secret_key`, tokens, or privileged accounts is required.

### Recommendation
Bind the `shop` (and ideally `topic`/`webhook_id`) header into the HMAC-verified signable content, or otherwise cryptographically bind the shop domain to the payload before trusting it. At minimum, update `Request#to_signable_string` so verification covers the shop-domain header, and update the documentation to no longer claim that `Registry.process` fully "verifies the request did indeed come from Shopify" for the shop field, or require host apps to cross-check `data.shop` against a known/installed-shop store before acting.

### Proof of Concept
1. App `A` has two installed merchants: victim shop `victim.myshopify.com` and attacker-controlled shop `attacker.myshopify.com`, both sharing the same app `client_secret`.
2. Attacker's own shop receives a legitimate webhook: `raw_body = B`, header `X-Shopify-Hmac-Sha256 = HMAC(secret, B)`, header `X-Shopify-Shop-Domain = attacker.myshopify.com`.
3. Attacker POSTs the exact same `raw_body = B` and same HMAC header to the app's public webhook endpoint, but sets `X-Shopify-Shop-Domain: victim.myshopify.com`.
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only checks `HMAC(secret, B)` against the header — unaffected by the shop-domain header: [7](#0-6) 
5. The handler is invoked with `WebhookMetadata.new(... shop: "victim.myshopify.com" ...)`, causing the app to process attacker-controlled webhook content under the victim's tenant identity.

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

**File:** docs/usage/webhooks.md (L12-17)
```markdown
`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
- `api_version`, `String` - The api version of the webhook
```

**File:** docs/usage/webhooks.md (L125-125)
```markdown
To process an http webhook, you need to listen on the route(s) you provided during the Webhook registration process, then when the route is hit construct a `ShopifyAPI::Webhooks::Request` and call `ShopifyAPI::Webhooks::Registry.process`. This will verify the request did indeed come from Shopify and then call the specified handler for that webhook. An example in Rails is shown below:
```
