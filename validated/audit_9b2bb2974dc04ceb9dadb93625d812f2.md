### Title
Webhook shop-domain and topic headers are trusted for tenant routing without being covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` and `ShopifyAPI::Webhooks::Registry.process` authenticate an inbound webhook solely by validating the HMAC over the raw request body, but then trust the `shop-domain` and `topic` headers — which are never part of the signed material — as the tenant identity handed to the app's webhook handler.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop` and `Request#topic` are read straight from HTTP headers, completely outside that signed string: [2](#0-1) 

`Registry.process` validates the HMAC and then immediately forwards `request.shop` and `request.topic` to the registered handler as authenticated tenant/topic context: [3](#0-2) 

The identity binding that should hold is:
`shop asserted to the handler == shop cryptographically bound to the verified payload`

but the implementation only proves `HMAC(secret, raw_body)` is valid; it never proves that `shop-domain` (or `topic`) corresponds to that specific signed body. `HmacValidator.validate` only checks `verifiable_query.hmac` against `to_signable_string`, and for `Request` that string is the body alone: [4](#0-3) 

Because a merchant who installs the app receives genuine, validly-signed webhooks for their *own* shop, they can capture a legitimate `(raw_body, hmac)` pair from their own tenant and resubmit it to the app's webhook endpoint with the `shop-domain` header rewritten to a victim shop. `Registry.process` will still pass `Utils::HmacValidator.validate(request)`, because the HMAC only covers the untouched body, and the handler will receive `WebhookMetadata` claiming the data belongs to the victim shop.

### Impact Explanation
This breaks the tenant boundary that host applications rely on `Webhooks::Registry`/`WebhookMetadata#shop` to enforce: an app that keys per-tenant state (e.g., order/customer records, GDPR redaction bookkeeping, billing) off `data.shop` can be made to apply another merchant's legitimate webhook body to a different merchant's tenant. This is a cross-tenant data-integrity issue reachable without any credential beyond operating one's own installed instance of the app (no `api_secret_key`, access token, or privileged account needed) — the attacker only needs a real webhook that Shopify already sent them.

### Likelihood Explanation
Moderate-to-high: any external developer using this gem receives a webhook via a standard Rack/Sinatra/Rails endpoint, builds a `Webhooks::Request` from raw headers/body, and calls `Registry.process`. The vulnerable header-trust behavior is baked into the gem itself (`Request#shop`, `Registry.process`), so every consuming app inherits it unless they add their own out-of-band shop verification (which the gem provides no API or guidance to do). The only prerequisite for exploitation is having received one genuine webhook for any shop, which happens automatically once an app is installed and subscribed to any topic.

### Recommendation
Bind `shop` (and ideally `topic`/`webhook-id`) into the material that is HMAC-verified, or otherwise cryptographically tie the header claims to the verified body:
- Change `Request#to_signable_string` to include a canonical representation of `shop`, `topic`, and `webhook_id` alongside `raw_body`, and require the caller to supply/verify these via a scheme Shopify itself signs (not just plain headers), or
- Have `Registry.process` cross-check `request.shop` against an expected/allow-listed shop context provided by the host app (e.g., a shop derived from a previously stored, HMAC-authenticated session) before dispatching to the handler, and document this requirement clearly so host apps don't unconditionally trust `WebhookMetadata#shop`.

### Proof of Concept
1. Attacker installs the app on `attacker.myshopify.com` and receives a legitimate webhook delivery from Shopify for topic `orders/create`, with a real, valid `x-shopify-hmac-sha256` computed by Shopify over the raw JSON body and headers `x-shopify-shop-domain: attacker.myshopify.com`, `x-shopify-topic: orders/create`.
2. Attacker resends the identical raw body and HMAC header to the app's webhook endpoint, but replaces `x-shopify-shop-domain` with `victim.myshopify.com`.
3. The host app builds `ShopifyAPI::Webhooks::Request.new(raw_body:, headers:)` and calls `ShopifyAPI::Webhooks::Registry.process(request)`.
4. `Utils::HmacValidator.validate(request)` succeeds because it only checks the HMAC of `raw_body`, which is unchanged: `lib/shopify_api/utils/hmac_validator.rb:12-22`.
5. The handler is invoked with `WebhookMetadata.new(topic: "orders/create", shop: "victim.myshopify.com", body: <attacker's order JSON>, ...)`, `lib/shopify_api/webhooks/registry.rb:198-199`, causing the host app to process attacker-controlled order data under the victim tenant's identity.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-23)
```ruby
      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

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
