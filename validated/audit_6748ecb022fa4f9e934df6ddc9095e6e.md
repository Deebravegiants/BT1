### Title
Webhook shop-domain header is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its signable string from the raw body only, while `shop`, `topic`, `webhook_id`, and `api_version` are read directly from unauthenticated HTTP headers. `Registry.process` accepts any request whose body/HMAC pair is valid and then hands the handler the header-derived `shop` value as the tenant identifier, without ever checking that this `shop` matches the shop the HMAC was actually issued for.

### Finding Description
`HmacValidator.validate` only signs/verifies `to_signable_string`, and for webhooks that method returns just `@raw_body`: [1](#0-0) 

The `shop`, `topic`, `webhook_id`, and `api_version` values are pulled straight from headers, which are not part of the signed material: [2](#0-1) 

`Registry.process` validates the HMAC and then immediately trusts `request.shop` as the tenant identity passed to the handler: [3](#0-2) 

The equality the gem is implicitly claiming is: `hmac_valid(body, secret) == true` implies `shop_header == shop_that_actually_owns_this_body`. That equality does not hold, because the HMAC never binds `shop`, `topic`, or `webhook_id` to the body. Any request whose body/HMAC pair is valid for the app's secret (e.g. one obtained legitimately by an attacker who installs the app on their own store and receives a real webhook) can be replayed with an arbitrary `x-shopify-shop-domain` (or `shopify-shop-domain`) header. `HmacValidator.validate` will still return `true` because it only re-computes the HMAC over the untouched raw body, and `Registry.process` will forward the attacker-chosen `shop` to the handler as if it were authentic.

### Impact Explanation
Any host application that uses `request.shop` (as returned by this gem) to select which merchant/tenant record to update based on the webhook payload is exposed to cross-tenant data confusion: an unprivileged attacker who can obtain one valid signed webhook body (trivial — install the app on their own store, or capture any publicly triggerable webhook) can attribute that body's contents to a victim shop's identifier by simply changing the shop header, since the gem's own HMAC check does not fail. This satisfies the "cross-tenant access" critical-impact category, since no credential, and no access to the victim shop, is required — the attacker only needs one legitimately signed payload attributable to any shop plus control over the raw HTTP headers of their own request to the app's webhook endpoint.

### Likelihood Explanation
Likelihood is moderate-to-high in any deployment that forwards attacker-influenceable headers as-is to this gem's `Webhooks::Request.new`/`Registry.process` (which is the documented usage pattern, since the gem's own tests construct `Request` directly from raw header hashes). Obtaining a validly HMAC-signed body requires no elevated privilege — any user who can trigger a webhook to their own installation (order create, product update, app uninstalled, etc.) has one, and can then attach it to a forged shop header.

### Recommendation
Include the shop domain (and ideally topic/webhook id) in the signable material `Webhooks::Request#to_signable_string`, or otherwise cryptographically bind the header-derived tenant identity to the verified payload before it is forwarded to handlers, so that a validly-signed body cannot be replayed under a different shop's identity.

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com` and receives a legitimate webhook, capturing the raw body `B` and its valid `x-shopify-hmac-sha256` header `H` (computed with the app's `api_secret_key` over `B`).
2. Attacker sends a POST to the app's webhook endpoint with the same body `B`, the same `H`, but `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` builds a `Request` whose `to_signable_string` is still just `B`; `HmacValidator.validate` recomputes the HMAC over `B` and it matches `H`, so `Registry.process` (`lib/shopify_api/webhooks/registry.rb:190`) does not raise `InvalidWebhookError`.
4. The handler is invoked with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: parsed(B), ...)`, i.e., attacker-controlled data attributed to a shop the attacker does not control.

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
