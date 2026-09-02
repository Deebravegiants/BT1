### Title
Webhook `shop` (and `topic`) identity is not bound by the HMAC signature, enabling cross-tenant webhook forgery - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw request body, but the tenant-identifying `shop` (and `topic`) values are read from separate, unsigned HTTP headers and are handed to the app's handler as if they were authenticated.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop`, `topic`, `api_version`, and `webhook_id` are all pulled from headers instead: [2](#0-1) 

`Registry.process` verifies the HMAC and, on success, treats `request.shop` as the authenticated tenant identifier for the dispatched event, without any additional check binding it to the signed body: [3](#0-2) 

`Utils::HmacValidator.validate` only compares `verifiable_query.hmac` against a signature computed from `to_signable_string` (the raw body), never incorporating the `shop` or `topic` headers: [4](#0-3) 

The identity binding that should hold is:
`hmac == HMAC(secret, raw_body || shop || topic)`

but what is actually enforced is:
`hmac == HMAC(secret, raw_body)` while `shop` and `topic` are trusted independently of that check.

Because every shop that installs the app shares the same `client_secret`/`api_secret_key` for HMAC computation, any merchant who installs the app on their own store legitimately receives real webhook deliveries — real `raw_body` + valid `hmac` pairs signed with the app's shared secret. That merchant (an unprivileged actor with respect to any other tenant of the app) can replay that exact `raw_body`/`hmac` pair to the app's webhook endpoint while substituting the `x-shopify-shop-domain` (and/or `x-shopify-topic`) header to name a victim shop. `HmacValidator.validate` still succeeds because it never looks at those headers, and `Registry.process` dispatches the handler with `WebhookMetadata` carrying the attacker-chosen `shop`.

### Impact Explanation
This breaks the tenant boundary the gem is supposed to guarantee for webhook processing: an attacker who has legitimately installed the app on their own store can forge webhook deliveries that host applications will process as originating from a different merchant's shop, injecting attacker-controlled body content (e.g., fabricated `app/uninstalled`, `orders/create`, `customers/data_request` events) attributed to the victim tenant. This is cross-tenant access/impersonation achieved without ever touching the victim's credentials or the app's `client_secret`.

### Likelihood Explanation
Any developer/merchant can install a public app to obtain valid HMAC-signed webhook traffic for their own shop, then trivially resend that request with a modified `shop-domain` header — no special access, leaked secrets, or privileged account is required, only normal app installation. The library gives no indication in its own API surface that `request.shop`/`request.topic` are unauthenticated relative to the HMAC, making misuse likely for any integrator who (reasonably) assumes a validated webhook implies a validated shop.

### Recommendation
Bind the tenant/topic identity into the authenticated signature domain rather than trusting bare headers post-hoc:
- Extend `VerifiableQuery`/`HmacValidator` (or add a dedicated check in `Registry.process`) to include `shop` and `topic` in the signable string, or otherwise cryptographically bind them, before they are trusted.
- Alternatively, cross-validate `request.shop` against an out-of-band trusted mapping (e.g., a stored session/shop expected to receive that specific `webhook_id`) before invoking the handler.
- Document clearly that `shop`/`topic` headers are not covered by the HMAC today, so consuming apps are not misled into treating `WebhookMetadata#shop` as authenticated.

### Proof of Concept
1. Install the target app on `attacker-shop.myshopify.com`; trigger a webhook (e.g., `orders/create`) and capture the raw POST: body `B`, headers including `x-shopify-hmac-sha256: H` (valid for `B` under the shared `api_secret_key`) and `x-shopify-shop-domain: attacker-shop.myshopify.com`.
2. Replay the exact request to the app's webhook endpoint, keeping body `B` and header `x-shopify-hmac-sha256: H` unchanged, but set `x-shopify-shop-domain: victim-shop.myshopify.com` (and optionally change `x-shopify-topic`).
3. `Utils::HmacValidator.validate` (lib/shopify_api/utils/hmac_validator.rb:13-22) succeeds because it only checks `B` against `H`.
4. `Registry.process` (lib/shopify_api/webhooks/registry.rb:188-200) dispatches the handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: parsed(B), ...)`, causing the host app to act on attacker-controlled data as if it came from `victim-shop.myshopify.com`.

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
