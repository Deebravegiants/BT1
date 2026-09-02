### Title
Webhook Shop Identity Not Bound to HMAC Signature Enables Cross-Tenant Webhook Spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable payload from the raw request body only, while the tenant-identifying `shop` value is read from an unsigned HTTP header. `Registry.process` validates the HMAC and then forwards this unauthenticated `shop` value directly to app handlers as the tenant scope for the webhook event, breaking the binding between "the HMAC that was verified" and "the shop the event is attributed to."

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0)  while `Request#shop` is read straight from the `x-shopify-shop-domain`/`shopify-shop-domain` header with no cryptographic tie to the signature: [2](#0-1) 

`Registry.process` validates only that `hmac` matches `request.to_signable_string` (i.e., the body) via `Utils::HmacValidator.validate(request)`, then immediately trusts `request.shop` (the header) as the tenant identity passed to the app's handler: [3](#0-2)  `HmacValidator.validate` computes the signature purely over `verifiable_query.to_signable_string`: [4](#0-3) 

This is exactly the binding-break pattern from the report: a field acted on (`shop`, used as the tenant scope for the delivered event) is not covered by the value that is cryptographically verified (`hmac`, which only covers the body). Anyone who possesses one genuine `(raw_body, hmac)` pair signed with the app's `client_secret` — trivially obtainable by installing the app on their own store and capturing/replaying their own legitimate webhook deliveries — can resend that exact body/HMAC pair to the app's public webhook endpoint while substituting an arbitrary `x-shopify-shop-domain` header. `Registry.process` will accept it as valid (the HMAC still matches the unchanged body) and hand the handler a `WebhookMetadata`/event tagged with the attacker-chosen victim shop.

### Impact Explanation
This crosses the tenant boundary this gem is responsible for enforcing: an unprivileged attacker who legitimately installed the app on their own shop can forge webhook events that the host application will process as if they came from a different (victim) merchant. Depending on the topic handled (e.g. `app/uninstalled`, `shop/redact`, order/customer topics), this can drive cross-tenant data mutation, deletion, or disclosure keyed off the spoofed `shop` value — meeting the Critical "cross-tenant access" bar.

### Likelihood Explanation
Exploitation requires only: (1) the attacker be a real installer of the target app on their own store (a normal, unprivileged relationship — no leaked secrets or privileged accounts needed), and (2) the app's webhook endpoint be reachable (it must be, by design, since Shopify posts to it). Capturing one's own valid webhook body+HMAC pair and replaying it with a different `shop` header requires no cryptography breaking, since the header was never part of the signed material.

### Recommendation
Bind the shop identity into the verified material instead of trusting the header value on faith:
- Include the shop domain (and ideally topic/webhook-id) as part of the HMAC-covered signable string in `Request#to_signable_string`, matching how `AuthQuery` binds `shop` into its own signable string (`lib/shopify_api/auth/oauth/auth_query.rb`), or
- Have `Registry.process` cross-check `request.shop` against an expected/allow-listed shop (e.g., a shop the host app knows it installed the app on) before invoking the handler, or
- Document explicitly that host applications must independently authenticate `data.shop` before using it as a tenant key, since this gem currently only guarantees body integrity, not shop authenticity.

### Proof of Concept
1. Attacker installs the target Shopify app on `attacker-shop.myshopify.com` and triggers a webhook topic the app handles (e.g., `orders/create`) by placing an order.
2. Attacker's own server (or a captured HTTP proxy) records the exact `raw_body` and the `x-shopify-hmac-sha256` header Shopify sent for that delivery.
3. Attacker crafts a new POST to the target app's webhook endpoint with the identical `raw_body` and `hmac-sha256` header, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes HMAC over `raw_body` only — matches — validation passes.
5. The handler receives `WebhookMetadata` with `shop == "victim-shop.myshopify.com"` [5](#0-4)  and performs whatever tenant-scoped action the app implements for that topic, attributed to the wrong shop.

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
