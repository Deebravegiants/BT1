### Title
Webhook Shop-Domain Header Is Not Covered by HMAC Verification, Enabling Cross-Tenant Webhook Spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` only returns the raw request body, so the HMAC computed by `HmacValidator` authenticates the body content alone. The `shop`, `topic`, `webhook_id`, and `api_version` values are all read from unauthenticated HTTP headers and are never bound into the signed material. `Registry.process` trusts `request.shop` from these headers as the tenant identifier passed to the app's handler after HMAC validation succeeds, creating a mismatch between "the bytes verified" (body only) and "the shop acted on" (header value).

### Finding Description
`Webhooks::Request` exposes `shop` straight from the `shopify-shop-domain`/`x-shopify-shop-domain` header: [1](#0-0) 

But the signable string used for HMAC verification is only the raw body: [2](#0-1) 

`HmacValidator.validate` recomputes the HMAC purely over `to_signable_string` (the body) and compares it to the `hmac` header: [3](#0-2) 

`Registry.process` performs this body-only HMAC check and then immediately trusts `request.shop` (and `request.topic`, `request.webhook_id`) as tenant/routing metadata delivered to the app's handler: [4](#0-3) 

Because the shop-domain header is not part of the signed data, any request carrying a *valid* `(raw_body, hmac)` pair for the configured `api_secret_key` will pass verification regardless of what shop-domain header accompanies it. An attacker who has legitimately received even one authentic webhook delivery for their own store (a valid `raw_body`/`hmac` pair signed by Shopify with the app's real secret) can replay that exact body and HMAC while substituting an arbitrary `shopify-shop-domain` header value. `HmacValidator.validate` still returns `true`, and `Registry.process` dispatches to the app's handler with `WebhookMetadata.shop` set to the attacker-chosen value instead of the shop that actually owns the data.

### Impact Explanation
This breaks the identity binding "the shop authenticated by the cryptographic check" (none — the check only authenticates body bytes) versus "the shop used to route/attribute the event to a tenant" (`request.shop`, taken from an unauthenticated header). Any downstream application logic that uses `data.shop` from `WebhookMetadata` to key persistence, enqueue jobs, or select per-tenant credentials (as shown in the gem's own webhook usage docs, `perform_later(topic: data.topic, shop_domain: data.shop, ...)`) can be tricked into attributing attacker-supplied webhook content to an arbitrary victim shop, resulting in cross-tenant data confusion/injection.

### Likelihood Explanation
Exploitation requires the attacker to possess at least one genuine `(body, hmac)` pair signed with the app's real `api_secret_key` — obtainable simply by installing the app on their own shop and receiving one legitimate webhook (or by reusing any historically captured delivery, since nothing time-binds the body to a specific shop either). No access to the merchant's or the app's credentials is required beyond what a normal (even free-tier) app install already grants. This is a documented, always-reachable code path (`Registry.process`) used by every consumer of the webhook feature.

### Recommendation
Include the shop domain (and ideally topic/webhook id/api version) in the HMAC-covered signable string, or independently verify that `request.shop` matches a shop actually subscribed/registered for the given `webhook_id`/topic before dispatching to the handler. At minimum, document and enforce that consumers must cross-check `data.shop` against their own webhook subscription records rather than trusting it as an authenticated value.

### Proof of Concept
1. Install the app on attacker-owned shop `attacker-shop.myshopify.com`; trigger any webhook event, capturing the raw POST body `B` and its `x-shopify-hmac-sha256` header `H` (a valid HMAC over `B` under the real `api_secret_key`).
2. Replay a POST to the app's webhook endpoint with the same body `B` and header `H`, but set `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses this, `HmacValidator.validate` succeeds because it only checks `B` against `H`: [5](#0-4) 
4. `Registry.process` calls the registered handler with `WebhookMetadata.new(... shop: "victim-shop.myshopify.com" ...)`, and the app processes attacker-controlled data as belonging to `victim-shop.myshopify.com`.

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
