### Title
Webhook shop/topic/api-version/webhook-id headers are not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb, lib/shopify_api/utils/hmac_validator.rb, lib/shopify_api/webhooks/registry.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, so `HmacValidator.validate` authenticates the JSON payload bytes but not the `shop-domain`, `topic`, `api-version`, or `webhook-id` headers. `Registry.process` nonetheless treats `request.shop` as the trusted tenant identifier and forwards it unmodified to the app's webhook handler. This is the same class of bug as the reported StRSR issue: a value that is acted upon as an authenticated identity binding (there, `name` in the domain separator; here, `shop` in the webhook metadata) is not actually covered by the cryptographic check that is supposed to authenticate it.

### Finding Description
The webhook verification flow is: [1](#0-0) 

`to_signable_string` returns only `@raw_body`. The header-derived `shop`, `topic`, `api_version`, and `webhook_id` accessors read straight from attacker-suppliable headers: [2](#0-1) 

`HmacValidator.validate` computes the HMAC only over `verifiable_query.to_signable_string`, i.e. the body: [3](#0-2) 

`Registry.process` checks this body-only HMAC, then unconditionally trusts `request.shop`, `request.topic`, `request.webhook_id`, and `request.api_version` — none of which were part of the signed material — and hands them to the app's handler as `WebhookMetadata`: [4](#0-3) 

The equality the code implicitly assumes but never enforces is:

`hmac_verified_shop == request.shop`

but in reality only `hmac_verified_body == request.body` holds; `request.shop` (and topic/webhook_id/api_version) is taken from an unauthenticated header. Since Shopify computes the webhook HMAC using the app's single, cross-tenant `api_secret_key` (the same secret is used for every shop that installs the app), any unprivileged user who installs the app on their own store can trigger a webhook event, capture the resulting `(body, hmac)` pair that Shopify sends them, and then POST that same body+HMAC to the app's public webhook endpoint while swapping the `x-shopify-shop-domain` header to a victim shop's domain. `HmacValidator.validate` still succeeds because it never looked at the shop header, and `Registry.process` dispatches the handler with `WebhookMetadata.new(shop: <victim shop>, ...)`, i.e. attacker-controlled data now appears to the app as an authenticated event for the victim tenant.

### Impact Explanation
Any handler logic that keys off `WebhookMetadata#shop` (looking up the victim's stored session/access token, updating per-shop state, deleting/uninstall handling, order/inventory processing, etc.) can be triggered with forged data attributed to a shop the attacker does not control. This is a cross-tenant confusion/access primitive: the identity binding between the HMAC-authenticated payload and the shop it is attributed to is broken, letting one tenant (the attacker, who legitimately obtained one valid signed payload for their own store) inject fabricated events into another tenant's processing pipeline.

### Likelihood Explanation
The precondition is only that the attacker can install the target app on any shop they control (typical for public apps with free/dev stores) to obtain one legitimately-signed `(body, hmac)` pair, and that the app's webhook endpoint is reachable over the internet (a documented requirement of using this gem's webhook processing). No access token, `client_secret`, or victim credentials are required — only network access to the app's callback URL and a header rewrite, both squarely within an unprivileged internet user's capability.

### Recommendation
Bind the shop (and ideally topic/webhook id) into the value that is HMAC-verified, or otherwise cryptographically tie the header-derived shop to the authenticated request, e.g.:
- Include `shop`, `topic`, and `webhook_id` in `to_signable_string` if Shopify's signature scheme supports it, or
- After body-HMAC validation, cross-check the header `shop` against an out-of-band trusted source (e.g., only accept shops that have an active, previously-stored session/installation record) before invoking the handler, and document that consumers must not trust `WebhookMetadata#shop` as authenticated by the HMAC alone.

### Proof of Concept
1. Attacker installs the target app on their own development shop `attacker.myshopify.com` and triggers a webhook (e.g. `orders/create`), capturing the exact raw body Shopify posts and the corresponding `x-shopify-hmac-sha256` header (both are valid because Shopify signed them with the app's shared `api_secret_key`).
2. Attacker sends that identical body and HMAC header to the app's webhook endpoint again, but this time sets `x-shopify-shop-domain: victim.myshopify.com` (and any desired `x-shopify-topic`, e.g. `app/uninstalled`).
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only checks `OpenSSL::HMAC.hexdigest(sha256, api_secret_key, raw_body)` against the supplied HMAC — the forged `shop` header is never examined: [5](#0-4) 
4. The handler receives `WebhookMetadata` with `shop: "victim.myshopify.com"` and attacker-chosen body content, and performs whatever tenant-scoped action the app implements for that webhook topic — now against the victim's data/session instead of the attacker's own.

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
