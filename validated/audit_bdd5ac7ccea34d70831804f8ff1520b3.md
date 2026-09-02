### Title
Webhook `shop` (and `topic`/`webhook_id`) identity fields are not covered by the HMAC signature, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC signature exclusively over the raw request body, while the shop-identifying header (`X-Shopify-Shop-Domain`) — along with `topic` and `webhook-id` — is read as a plain, unauthenticated HTTP header and passed straight through to the app's webhook handler. Because the shared app secret is not shop-specific, any party who has previously obtained one valid `(body, hmac)` pair (e.g. from a shop they legitimately control) can replay that exact body/HMAC pair against the app's webhook endpoint while substituting an arbitrary `shop` header, causing the receiving app to process the data as though it originated from a different, victim tenant.

### Finding Description
`Utils::HmacValidator.validate` verifies the HMAC by calling `verifiable_query.to_signable_string`, and for webhooks that method returns only `@raw_body`: [1](#0-0) 

The `shop`, `topic`, and `webhook_id` values, in contrast, are read straight from headers with no cryptographic binding to the signed body: [2](#0-1) 

`Registry.process` validates only that the body-HMAC is correct, then immediately hands the unauthenticated `shop`/`topic`/`webhook_id` fields to the registered handler: [3](#0-2) 

`HmacValidator.validate` computes the signature using `Context.api_secret_key`/`Context.old_api_secret_key`, which is a single secret shared by the app across **all** installed shops, not a per-shop secret: [4](#0-3) 

The equality this scheme is supposed to enforce is:
`{shop that the handler attributes the webhook to} == {shop that actually produced/authorized the signed body}`

Because `shop` is excluded from `to_signable_string`, that equality is never checked — only `{HMAC is valid for this body under the app secret}` is checked. Any attacker who can obtain one legitimately signed `(body, hmac)` pair — trivially, by installing the app on a shop they control and capturing one of its own webhook deliveries — can replay that identical body and HMAC to the app's webhook endpoint while swapping the `X-Shopify-Shop-Domain` header to a victim shop that also has the app installed. The signature check passes (it's the same secret, same body), and `WebhookMetadata.new(shop: request.shop, ...)` is constructed with the attacker-chosen shop, so the handler processes/records data as belonging to the victim tenant.

### Impact Explanation
This breaks the tenant-identity binding that `Utils::HmacValidator` is meant to provide, allowing a shop-level attacker (unprivileged relative to other tenants) to make an app falsely attribute webhook data/events to another shop. Depending on the handler's logic (e.g. order-created idempotency keys, inventory updates keyed by shop, billing/usage events, subscription state), this can enable cross-tenant data corruption or cross-tenant access to another shop's application state — matching the Critical "cross-tenant access" impact category.

### Likelihood Explanation
Exploitation only requires: (1) the attacker's own instance of the app installed on a shop they control (an ordinary, unprivileged capability for any merchant/developer who can install a public/custom app), and (2) the ability to POST arbitrary headers/body to the app's public webhook endpoint. No access token, `api_secret_key`, or privileged account is needed — the attacker only needs a body+HMAC pair they can legitimately generate for their own shop. This is a low-effort, realistic attack path.

### Recommendation
Bind the tenant/shop identity into the signed payload verification path: either (a) include the `shop` (and ideally `topic`/`webhook_id`) header value in `to_signable_string` so it becomes part of the HMAC-verified data, or (b) have `Registry.process`/the library's documented integration require the host application to independently verify `request.shop` against its own record of installed shops before invoking the handler, and make this an enforced (not merely documented) step in the `process` API.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and triggers/receives one legitimate webhook delivery, capturing `raw_body` and the `X-Shopify-Hmac-Sha256` header value (both valid because signed with the app's shared `api_secret_key`).
2. Attacker sends a forged HTTP POST to the app's webhook endpoint with:
   - `raw_body` = the exact captured body
   - `X-Shopify-Hmac-Sha256` = the exact captured HMAC
   - `X-Shopify-Topic` = same or attacker-chosen topic
   - `X-Shopify-Shop-Domain` = `victim-shop.myshopify.com` (any other shop that has the app installed)
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks the HMAC over `raw_body` — the `shop` header is irrelevant to the check: [5](#0-4) 
4. The handler receives `WebhookMetadata` with `shop: "victim-shop.myshopify.com"` and processes it as if it came from the victim, despite the payload actually originating from the attacker's own shop.

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
