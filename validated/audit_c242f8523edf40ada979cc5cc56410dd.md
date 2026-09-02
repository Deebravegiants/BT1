### Title
Webhook `shop`, `topic`, and `webhook_id` fields are trusted for tenant attribution despite not being covered by the HMAC signature - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` exposes `shop`, `topic`, `webhook_id`, and `api_version` purely from unauthenticated HTTP headers, while the HMAC signature verified by `ShopifyAPI::Webhooks::Registry.process` only covers the raw request body. This breaks the intended binding `hmac == HMAC(secret, body + shop-attribution)`, since only `HMAC(secret, body)` is actually checked. Any party capable of obtaining one valid `(body, hmac)` pair for the shared app secret can replay it with a forged `shop-domain` header to attribute webhook data to an arbitrary victim shop.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop`, `#topic`, and `#webhook_id` are read straight from headers, which are never included in the signed material: [2](#0-1) 

`Registry.process` verifies only that the body's HMAC matches, then unconditionally trusts `request.shop`, `request.topic`, and `request.webhook_id` to build the `WebhookMetadata` object passed to the app's handler: [3](#0-2) 

`HmacValidator.validate` calls `verifiable_query.to_signable_string`, which for `Request` is just the body: [4](#0-3) 

Because every shop installed on a given app shares the same `api_secret_key` (there is no per-shop signing key in this gem), a genuine webhook delivered to the attacker's *own* store (which the attacker legitimately controls as an unprivileged merchant) yields a valid `(raw_body, hmac)` pair signed with the app's secret. The attacker can replay that exact body/HMAC to the app's webhook endpoint while substituting the `x-shopify-shop-domain` (and `x-shopify-topic`/`x-shopify-webhook-id`) headers to point at a victim shop. `Registry.process` will still find `Utils::HmacValidator.validate(request)` to be true — because it never inspected the headers — and will hand the handler a `WebhookMetadata` claiming the data came from the victim shop.

This is exactly the "field acted on but not covered by the HMAC" analog: the equality that should hold is `verified_bytes == bytes_used_for_tenant_attribution`, but in this code `verified_bytes = raw_body` while `bytes_used_for_tenant_attribution = headers["shop-domain"]`.

### Impact Explanation
Any host application that uses `request.shop` from `WebhookMetadata` (the value the gem hands off) to decide which tenant's session/data store to write into can be tricked into cross-tenant data confusion/injection: an attacker-controlled webhook body, HMAC-authenticated only against the shared secret, gets attributed to and processed as if it belongs to an arbitrary victim shop. This crosses the tenant boundary the gem is documented to enforce via HMAC validation, matching the "cross-tenant access" impact class.

### Likelihood Explanation
Likelihood is credible but bounded: it requires the attacker to (a) be a legitimate merchant who has installed the target app (no elevated privilege, freely available to any internet user who installs a public app), and (b) be able to trigger and capture at least one genuine webhook delivery to their own store (trivial — e.g., updating a product they own fires `products/update`), then replay it with modified headers to the app's public webhook receiver endpoint. No possession of `api_secret_key` or an access token is required — only observation of one legitimately-signed body/HMAC pair belonging to the attacker's own tenant.

### Recommendation
Include the tenant-identifying fields (`shop`, `topic`, `webhook_id`) in the HMAC-signed material, or otherwise cryptographically bind them to the request (e.g., verify the shop domain against Shopify's own webhook delivery guarantees by also checking it against a per-shop signing key, or reject any header/body mismatch that the app has independently confirmed via a follow-up API call). At minimum, document clearly that the `shop`/`topic`/`webhook_id` header values are unauthenticated and must not be used by host applications for tenant attribution without additional verification.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker-shop.myshopify.com`.
2. Attacker triggers a real webhook (e.g., updates a product), causing Shopify to POST a body `B` with a valid header `x-shopify-hmac-sha256: H = HMAC-SHA256(api_secret_key, B)` and `x-shopify-shop-domain: attacker-shop.myshopify.com` to the app's webhook endpoint.
3. Attacker captures `B` and `H`, then re-sends a request to the same endpoint with identical body `B` and header `x-shopify-hmac-sha256: H`, but replaces `x-shopify-shop-domain` with `victim-shop.myshopify.com` (and optionally forges `x-shopify-topic`/`x-shopify-webhook-id`).
4. `Utils::HmacValidator.validate` in `lib/shopify_api/utils/hmac_validator.rb` recomputes HMAC over `B` only and it matches `H`, so `Registry.process` in `lib/shopify_api/webhooks/registry.rb` proceeds and calls the app's handler with `WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: parsed_body, ...)`, causing the host application to process attacker-controlled data as belonging to the victim shop.

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
