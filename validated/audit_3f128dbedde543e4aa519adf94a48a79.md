Based on my review of the webhook processing code, I found a valid analog: the HMAC signature scope excludes fields that are subsequently trusted for tenant attribution.

### Title
Webhook shop/topic identity spoofing via HMAC that only covers the body, not the `shop-domain`/`topic` headers - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, so the HMAC verification performed by `Utils::HmacValidator.validate` proves nothing about the `shop`, `topic`, `webhook_id`, or `api_version` values, which are all read from unauthenticated headers and then handed directly to the host application's handler as if they were verified.

### Finding Description
`Webhooks::Registry.process` validates a webhook solely via `Utils::HmacValidator.validate(request)`, which computes the HMAC over `request.to_signable_string`. [1](#0-0) 

`Webhooks::Request#to_signable_string` is defined as just `@raw_body`, while `shop`, `topic`, `webhook_id`, and `api_version` are pulled from HTTP headers that are never included in the signed content: [2](#0-1) 

The identity-binding equality the gem implicitly claims to enforce is: `hmac-verified bytes == (shop, topic, body)` that the handler acts on. In reality it only enforces `hmac-verified bytes == raw_body`; `shop` (and `topic`/`webhook_id`/`api_version`) are unauthenticated header values smuggled into the trusted `WebhookMetadata` passed to the app's handler: [3](#0-2) 

Because the client_secret used to compute the HMAC is the same across every shop that has installed the app (it's the app's secret, not a per-shop one), any party who can obtain one valid `(raw_body, hmac)` pair — e.g. by installing the app on their own store and capturing a webhook Shopify sends them — can replay that exact body+HMAC to the app's webhook endpoint while substituting the `x-shopify-shop-domain` (and/or `x-shopify-topic`) header to claim the event belongs to a different, victim shop. The HMAC check still passes because it only validates the body bytes, not the header-derived shop identity.

### Impact Explanation
This breaks the tenant/identity binding the HMAC is meant to guarantee: `WebhookMetadata.shop` (and `topic`) delivered to the host app's handler can be forged to any value while still passing `HmacValidator.validate`. If the host application relies on `data.shop` from this gem to look up the corresponding merchant's session/access token or to attribute the webhook body to a tenant (a normal and expected usage pattern per the gem's own webhook handler API), an attacker can cause the host app to process forged data under another shop's identity — a cross-tenant confusion whose severity depends on the handler, but which the gem enables by not binding `shop`/`topic` into the verified signature.

### Likelihood Explanation
No privileged credentials, leaked secrets, or access tokens are required. Any user who can install the app on any shop (including a free/dev store) can capture at least one legitimate `(raw_body, hmac)` pair from Shopify's real webhook delivery to their own endpoint, then reuse it against the target app's public webhook endpoint with a modified `shop-domain` header. This is directly reachable through the gem's documented `Registry.process` API with no additional gating.

### Recommendation
Bind the shop (and ideally topic/webhook_id) into the signed material verified by `HmacValidator`, or perform an explicit secondary check that the `shop-domain` header value corresponds to a shop that is expected to be delivering this specific `raw_body`/HMAC pair (e.g., by validating the header shop against a known active session before trusting it, and rejecting requests where headers cannot be cryptographically tied to the body). At minimum, document prominently that `shop`/`topic`/`webhook_id` are NOT covered by the HMAC and must not be trusted for tenant attribution without additional verification.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` (no privilege required — any free/trial store works).
2. Shopify delivers a legitimate webhook to the attacker's own webhook endpoint (which the attacker controls), with a valid raw body `B` and header `x-shopify-hmac-sha256: H` computed by Shopify using the app's `client_secret`, plus `x-shopify-shop-domain: attacker-shop.myshopify.com`.
3. Attacker crafts a new HTTP request to the target application's real webhook endpoint, keeping body `B` and header `x-shopify-hmac-sha256: H` unchanged, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. The host app calls `ShopifyAPI::Webhooks::Registry.process(request)`; `Utils::HmacValidator.validate(request)` passes because it only checks `B` against `H` [4](#0-3) 
5. `request.shop` returns `"victim-shop.myshopify.com"` (forged header) and is passed into `WebhookMetadata` to the app's handler as verified tenant identity. [5](#0-4)

### Citations

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

**File:** lib/shopify_api/webhooks/request.rb (L15-43)
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

      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end

      sig { returns(T::Hash[String, T.untyped]) }
      def parsed_body
        JSON.parse(@raw_body)
      end
```

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-22)
```ruby
        sig { params(verifiable_query: VerifiableQuery).returns(T::Boolean) }
        def validate(verifiable_query)
          return false unless verifiable_query.hmac

          result = validate_signature(verifiable_query, Context.api_secret_key)
          if result || Context.old_api_secret_key.nil? || T.must(Context.old_api_secret_key).empty?
            result
          else
            validate_signature(verifiable_query, T.must(Context.old_api_secret_key))
          end
        end
```
