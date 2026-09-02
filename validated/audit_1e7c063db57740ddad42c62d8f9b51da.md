## Title
Webhook shop-domain is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature over the raw request body only, while the `shop`, `topic`, `api_version`, and `webhook_id` values are read directly from unauthenticated HTTP headers. `ShopifyAPI::Webhooks::Registry.process` validates only that HMAC before handing the header-derived `shop` value to the application's handler as trusted tenant identity. This breaks the identity binding `shop verified by HMAC == shop delivered to handler`, letting an attacker who controls one shop replay a validly-signed payload from that shop while relabeling it as belonging to a different, victim shop.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop`, `#topic`, `#api_version`, and `#webhook_id` are all pulled straight from headers that are never fed into the signable string: [2](#0-1) 

`Registry.process` verifies the HMAC over the body via `HmacValidator.validate`, and if it passes, forwards `request.shop` (the unauthenticated header) directly to the app's handler as the tenant identifier: [3](#0-2) 

`HmacValidator.validate` only computes/compares `compute_signature(verifiable_query.to_signable_string, secret)`, i.e. purely over the raw body bytes: [4](#0-3) 

Because Shopify signs webhooks with the app's single shared `api_secret_key` across *all* shops that install the app, any merchant who installs the app on their own store can obtain a validly-HMAC'd `raw_body` from a real webhook delivery to their own shop. Since the `x-shopify-shop-domain` (or `shopify-shop-domain`) header is not part of the signed bytes, that same `raw_body`+`hmac` pair remains valid when replayed with the header changed to any other shop domain. The gem has no mechanism to bind the header-derived `shop` to the signature, so `Registry.process` will call the handler with `data.shop` set to the attacker-chosen (victim) shop while `data.body` is attacker-controlled content from their own shop's legitimate webhook.

This is the "bytes verified versus bytes parsed" identity-binding failure: the bytes cryptographically verified (raw body) are disjoint from the tenant-identifying bytes actually parsed and trusted (`shop-domain` header).

### Impact Explanation
Applications built on this gem are documented to treat `data.shop` as the authoritative tenant identifier for a webhook (per `docs/usage/webhooks.md`, `data.shop` is "The shop domain of the webhook"). A host app using this value to route persisted data, enqueue jobs, or update per-shop state (the exact pattern shown in the gem's own example: `perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)`) can be made to attribute a spoofed shop's data to another tenant, i.e. cross-tenant data injection/corruption — Critical impact per the given classification (cross-tenant access), since the attack requires no access token, no `api_secret_key`, and no privileged account beyond installing the app on one's own store.

### Likelihood Explanation
Any merchant who installs the target app (an ordinary, unprivileged action available to any internet user for public apps) can trigger a real event on their own shop, capture the resulting signed webhook, and replay it against the app's webhook endpoint with a forged `shop-domain` header. No secret material or elevated privilege is required beyond the attacker's own store, making this practically reachable.

### Recommendation
Include the shop domain (and ideally topic/webhook-id) in the signable payload used for HMAC verification, or otherwise cryptographically bind the header-derived `shop` to the request before trusting it — e.g., verify the shop against the session/access-token store for the topic, or require the HMAC to cover a canonical string composed of the shop, topic, and body rather than the body alone. At minimum, document that `data.shop` from `ShopifyAPI::Webhooks::Registry.process` is not covered by HMAC verification and must not be trusted for tenant attribution without independent verification (e.g., cross-checking against a known/installed shop list).

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker.myshopify.com`.
2. Attacker triggers a webhook event (e.g., `orders/create`) on their own store; Shopify delivers a POST with body `B` and header `x-shopify-hmac-sha256: HMAC(secret, B)` plus `x-shopify-shop-domain: attacker.myshopify.com`.
3. Attacker resends the exact same body `B` and `x-shopify-hmac-sha256` value to the app's webhook endpoint, but sets `x-shopify-shop-domain: victim.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: headers)` builds a request whose `hmac` is unchanged and whose `to_signable_string` is still `B`, so `Utils::HmacValidator.validate(request)` in `Registry.process` passes: [5](#0-4) 
5. The application's handler receives `WebhookMetadata` with `shop: "victim.myshopify.com"` and `body` fully controlled by the attacker, despite `victim.myshopify.com` never having sent this webhook.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-31)
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

        private

        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
