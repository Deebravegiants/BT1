## Finding

### Title
Webhook shop-domain (and topic) headers are trusted for tenant routing without being covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable string from the raw request body alone, while the `shop-domain`, `topic`, `api-version`, and `webhook-id` values are read directly from unauthenticated HTTP headers. `ShopifyAPI::Webhooks::Registry.process` verifies only that the body's HMAC matches, then unconditionally trusts the `shop` header value to route the webhook to a handler as the identity of the tenant that produced the event. This breaks the binding `hmac_valid(body) == true` with `request.shop == <the shop that actually generated this event>` — the two are independent, since `shop` is never part of the signed material.

### Finding Description
`to_signable_string` in `lib/shopify_api/webhooks/request.rb` returns only `@raw_body`: [1](#0-0) 

The `shop` accessor is read straight from the `shopify-shop-domain`/`x-shopify-shop-domain` header, which is not part of the signed payload: [2](#0-1) 

`Registry.process` validates the HMAC over the body and, on success, immediately hands `request.shop` (and `request.topic`) to the registered handler as the trusted tenant identity, with no cross-check that this header actually corresponds to the shop that produced the signed body: [3](#0-2) 

The `api_secret_key` used to compute the webhook HMAC is a single shared secret for the whole app, not scoped per installing shop. Any merchant who has installed the app (an "unprivileged" party relative to the app owner, with no access to `api_secret_key` itself) can legitimately trigger a webhook for their own store and thereby obtain a genuinely-signed `(body, hmac)` pair. Because `shop` is not part of the signed string, that same attacker can resend the identical body/HMAC pair to the app's webhook endpoint while substituting the `x-shopify-shop-domain` header with a victim shop's domain. `HmacValidator.validate` will still succeed (it only checks the body against the secret) — see `lib/shopify_api/utils/hmac_validator.rb`: [4](#0-3) 

and the handler will process attacker-controlled event data tagged as belonging to the victim's shop.

### Impact Explanation
This is a cross-tenant data-integrity break: an attacker with no more privilege than "any merchant with the app installed" can make the library-provided webhook identity (`shop`) diverge from the actual signer of the event, causing the host application to attribute forged/attacker-chosen webhook data to another tenant. This matches the Critical "cross-tenant access" impact category, since host applications built on this gem (e.g. via `ShopifyApp`) key their per-shop side effects (order sync, inventory updates, billing state, uninstall handling, etc.) directly off `WebhookMetadata#shop`.

### Likelihood Explanation
Likelihood is not trivial-but-realistic: the attacker needs at least one genuine webhook body+HMAC pair, which any merchant installing a public app for their own store can obtain by simply performing an action that triggers a webhook (e.g. creating an order/product). No possession of `api_secret_key`, access tokens, or TLS interception is required — only observation of one's own legitimately delivered webhook and the ability to send an HTTP POST to the app's public webhook endpoint with a modified header.

### Recommendation
Bind the tenant identity into the verified material: either include the `shop`, `topic`, and `webhook_id` headers in the HMAC-signable string (requires coordinating with Shopify's signing scheme, which currently signs body-only, so this may not be feasible unilaterally), or, more practically, require host applications/the gem to cross-validate that the `shop` header matches an expected/known installed shop for that specific webhook delivery (e.g. via `webhook_id` uniqueness tracking, or comparing against the shop that owns the resource id inside the verified body) before trusting it for tenant-scoped side effects. At minimum, document prominently that `shop`/`topic` headers are unauthenticated and must not be used as the sole tenant-routing key without additional validation.

### Proof of Concept
```ruby
# Attacker's own shop legitimately triggers a webhook, capturing (body, hmac) that Shopify sends:
captured_body = '{"id": 123, "note": "attacker payload"}'
captured_hmac_header = "<value Shopify actually sent for captured_body, signed with the shared api_secret_key>"

# Attacker resends the identical signed body to the app's webhook endpoint,
# but swaps the shop-domain header to the victim's store:
forged_headers = {
  "x-shopify-topic" => "orders/create",
  "x-shopify-hmac-sha256" => captured_hmac_header,   # still valid for captured_body
  "x-shopify-shop-domain" => "victim-shop.myshopify.com", # attacker-controlled, unsigned
  "x-shopify-webhook-id" => "any-id",
  "x-shopify-api-version" => "2024-01",
}

request = ShopifyAPI::Webhooks::Request.new(raw_body: captured_body, headers: forged_headers)
ShopifyAPI::Webhooks::Registry.process(request)
# HmacValidator.validate(request) succeeds (it only checks captured_body against the secret),
# and the handler executes with data.shop == "victim-shop.myshopify.com",
# even though that shop never produced this event.
``` [5](#0-4)

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-23)
```ruby
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
