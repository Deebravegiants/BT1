### Title
Webhook Shop Identity Not Bound to HMAC Signature Enables Cross-Tenant Webhook Spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating the HMAC over the raw request body, but the `shop` identity that is subsequently trusted and handed to the app's webhook handler is taken from an unauthenticated HTTP header that is never included in the signed material. This breaks the identity binding `HMAC-covered bytes == bytes the shop identity is derived from`, allowing a legitimately-signed webhook payload (obtained by an unprivileged attacker who merely owns/installs the app on their own shop) to be replayed with a different `shop` header value and be accepted as valid, cross-tenant data.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

The `shop` value used downstream, however, is read directly from the `shopify-shop-domain` / `x-shopify-shop-domain` HTTP header, which is not part of the signed payload: [2](#0-1) 

`HmacValidator.validate` only ever verifies `verifiable_query.to_signable_string` (i.e., the raw body) against the received HMAC — it has no knowledge of, and does not check, the `shop`, `topic`, `webhook_id`, or `api_version` headers: [3](#0-2) 

`Registry.process` trusts this unauthenticated `shop` header once the body-only HMAC check passes, and forwards it straight into the handler as the tenant identity: [4](#0-3) 

The identity binding that should hold is:
`HMAC_valid(raw_body) == true` should imply `shop_header == shop_that_Shopify_actually_signed_for`.

In reality the equality only checks `raw_body` integrity; `shop` (and `topic`/`webhook_id`) can be swapped freely by whoever controls the HTTP request, because they are outside the HMAC's scope. Since `api_secret_key` is a single per-app secret, any shop that has installed the app (an unprivileged interaction — no elevated access, no leaked credentials, no access token required) will receive genuinely-signed webhook bodies for its own events. That attacker-owned shop can capture one of its own genuinely-signed webhook deliveries and re-POST the identical `raw_body` + `hmac` to the app's shared webhook endpoint while substituting the `shopify-shop-domain` (and/or `shopify-topic`/`shopify-webhook-id`) header value to point at a different, victim tenant. `HmacValidator.validate` still returns `true` (the body/HMAC pair is untouched), and `Registry.process` builds `WebhookMetadata` with the attacker-chosen `shop`, causing the host application's handler to process the attacker's own event data as if it belonged to the victim shop.

### Impact Explanation
This crosses a tenant boundary using only the app's single shared `api_secret_key`-derived signature over data the attacker legitimately possesses, without needing the secret itself, an access token, or any privileged credential. Depending on how the host application persists/act on webhook data keyed by `WebhookMetadata#shop` (e.g., updating order/inventory/subscription records, deactivating shops, billing state), this enables cross-tenant data injection/corruption — matching the Critical "cross-tenant access" impact category.

### Likelihood Explanation
Any Shopify merchant can install the target app for free/trial, which is sufficient to receive genuinely HMAC-signed webhook deliveries for their own shop. Capturing one such delivery (visible to the merchant via their own server logs, a proxy, or a webhook debugging tool) and replaying it with a modified `shop`/`topic`/`webhook_id` header against the shared public webhook endpoint requires no special access — it is directly reachable by any unprivileged internet user who has installed the app once.

### Recommendation
Bind the identity fields into the signed material, or otherwise re-verify them independently of the raw-body HMAC:
- Include `shop`, `topic`, and `webhook_id` in the value that is HMAC-verified (or verify them via a side channel that Shopify signs, if available), rather than trusting them as unauthenticated headers once the body-only signature passes.
- At minimum, cross-check the `shop` header against the shop associated with the `Session`/subscription the app expects to receive this webhook_id/topic for, before invoking the handler.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` (no special privilege beyond being a Shopify merchant).
2. Shopify delivers a legitimate webhook to the app's endpoint with headers `x-shopify-shop-domain: attacker-shop.myshopify.com`, `x-shopify-hmac-sha256: <valid-hmac-of-body>`, and some `raw_body`.
3. Attacker captures this request and replays it to the same endpoint, changing only `x-shopify-shop-domain` to `victim-shop.myshopify.com` (and optionally `x-shopify-webhook-id`/`x-shopify-topic` to match a topic they want to trigger for the victim).
4. `Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `@raw_body` only — unchanged — and returns `true`: [5](#0-4) 
5. The handler receives `WebhookMetadata` with `shop: "victim-shop.myshopify.com"` and the attacker-controlled body, and the host application processes it as legitimate data for the victim tenant.

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
