### Title
Cross-Tenant Webhook Spoofing via Unauthenticated `shop-domain` Header - (`lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating the HMAC over the raw request body, but the `shop` (merchant domain) that is handed to the app's webhook handler is taken from an HTTP header that is never covered by that HMAC. This breaks the identity binding `shop authenticated == shop acted upon`, allowing any party who can obtain one valid `(raw_body, hmac)` pair signed with the app's shared `api_secret_key` (e.g., by receiving a legitimate webhook for their own, attacker-controlled shop installation) to relabel it with an arbitrary victim shop domain and have the app process it as if it originated from that victim tenant.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw body: [1](#0-0) 

The `shop` accessor is derived purely from the `x-shopify-shop-domain`/`shopify-shop-domain` header, which is not part of the signed content at all: [2](#0-1) 

`Registry.process` validates the webhook exclusively via `Utils::HmacValidator.validate(request)` — which internally calls `verifiable_query.to_signable_string` (i.e., only `raw_body`) — and then immediately forwards the unauthenticated `request.shop` value to the app's handler: [3](#0-2) 

`HmacValidator.validate_signature` computes the signature purely over `verifiable_query.to_signable_string` and secure-compares it to the received HMAC — it never incorporates `shop`, `topic`, or `webhook_id`: [4](#0-3) 

Because the `api_secret_key` is a single value shared across every shop that installs the app (it is not per-shop), any shop that installs the app can, for its own genuine webhook traffic, obtain a `(raw_body, hmac)` pair that is valid for that shared secret. Since `shop` is not bound into that HMAC, the same `(raw_body, hmac)` pair remains valid no matter what value is placed in the `shop-domain` header. An attacker who controls the receiving endpoint of their own webhook deliveries (a normal, permitted action for any shop that installs the app) can therefore replay the exact body+HMAC while substituting a victim's shop domain, causing `Registry.process` to invoke the app's handler with `WebhookMetadata#shop` set to the victim tenant.

Binding broken (as an equality):
`hmac_valid(raw_body, api_secret_key) == true` is treated as proof that `request.shop == <the shop Shopify actually sent this webhook for>`, but the HMAC only proves `raw_body` integrity — it says nothing about `shop`.

Before attacker action: shop header and HMAC both correspond to the attacker's own shop; `Registry.process` accepts it and correctly attributes data to the attacker's tenant.
After attacker action: same `raw_body`/`hmac` pair, but `shop-domain` header rewritten to the victim's domain; `Registry.process` still accepts it (HMAC only checks `raw_body`) and attributes attacker-controlled data to the victim's tenant.

### Impact Explanation
Any downstream application logic that trusts `WebhookMetadata#shop` (returned by `Registry.process`) to select the tenant/session/record to update — which is exactly the intended usage of this field per the library's design — can be tricked into writing or acting on attacker-supplied webhook payloads under a victim shop's identity. This is a cross-tenant access vulnerability: an unprivileged internet user who is merely a legitimate installer of the app on their own store can inject falsified webhook events attributed to any other merchant using the same app.

### Likelihood Explanation
The only prerequisite is that the attacker be able to install the app on a shop they control (a normal, permissionless action for many app models) and observe at least one webhook delivery to their own endpoint (trivial, since it's delivered to infrastructure they own/control). No access to the app's `api_secret_key`, no privileged account, and no TLS interception of a third party is required — the attacker only inspects their own legitimately-delivered traffic.

### Recommendation
Bind `shop` (and ideally `topic`/`webhook_id`) into the authenticated signable content, or otherwise cryptographically tie the header-provided shop domain to the signed payload before it is trusted (e.g., validate the shop domain against the session/shop the client used for `Registry.register`, or verify it out-of-band). At minimum, document prominently that `WebhookMetadata#shop` is not authenticated and must not be used to select a tenant without additional verification.

### Proof of Concept
1. Install the target app on attacker-controlled shop `attacker.myshopify.com`; register a webhook handler for `orders/create`.
2. Configure the delivery endpoint to be an attacker-observable proxy (a normal setup step for the attacker's own store).
3. Trigger an event so Shopify sends a legitimate webhook to the attacker's proxy; capture `raw_body` and the `x-shopify-hmac-sha256` header — both valid for the app's shared `api_secret_key`.
4. Replay this exact `raw_body` + HMAC to the app's real production webhook endpoint, but replace the `x-shopify-shop-domain` header with `victim-shop.myshopify.com`.
5. `ShopifyAPI::Webhooks::Registry.process` computes the HMAC over `raw_body` only (`lib/shopify_api/webhooks/request.rb:35-43`, `lib/shopify_api/utils/hmac_validator.rb:26-31`), finds it valid, and calls the handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...)` (`lib/shopify_api/webhooks/registry.rb:198-199`), causing the app to process attacker-controlled data under the victim's tenant identity.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-23)
```ruby
      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L35-43)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end

      sig { returns(T::Hash[String, T.untyped]) }
      def parsed_body
        JSON.parse(@raw_body)
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
